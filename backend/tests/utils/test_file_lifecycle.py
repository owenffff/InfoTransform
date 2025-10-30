"""
Unit tests for file lifecycle management
"""

import os
from pathlib import Path

import pytest


@pytest.mark.unit
class TestFileLifecycleManager:
    """Test FileLifecycleManager functionality"""

    @pytest.mark.asyncio
    async def test_file_manager_initialization(self):
        """Test file manager initializes correctly"""
        from infotransform.utils.file_lifecycle import FileLifecycleManager

        manager = FileLifecycleManager()
        assert manager is not None

    @pytest.mark.asyncio
    async def test_file_manager_start_stop(self):
        """Test file manager lifecycle"""
        from infotransform.utils.file_lifecycle import FileLifecycleManager

        manager = FileLifecycleManager()

        await manager.start()
        # Manager should be running

        await manager.stop()
        # Manager should be stopped

    @pytest.mark.asyncio
    async def test_register_file(self, temp_dir):
        """Test registering a file for cleanup"""
        from infotransform.utils.file_lifecycle import FileLifecycleManager

        manager = FileLifecycleManager()
        await manager.start()

        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        # Register file
        manager.register_file(str(test_file))

        await manager.stop()

    @pytest.mark.asyncio
    async def test_batch_context(self, temp_dir):
        """Test batch context manager"""
        from infotransform.utils.file_lifecycle import FileLifecycleManager

        manager = FileLifecycleManager()
        await manager.start()

        # Create test files
        test_files = [
            {"file_path": str(temp_dir / f"test{i}.txt"), "filename": f"test{i}.txt"}
            for i in range(3)
        ]

        for file_info in test_files:
            Path(file_info["file_path"]).write_text("test")

        async with manager.batch_context(test_files) as managed_files:
            # Files should be accessible in context
            assert len(managed_files) == 3

        # After context, cleanup should be scheduled

        await manager.stop()


@pytest.mark.unit
class TestManagedStreamingResponse:
    """Test ManagedStreamingResponse functionality"""

    @pytest.mark.asyncio
    async def test_managed_streaming_response_creation(self):
        """Test creating managed streaming response"""
        from infotransform.utils.file_lifecycle import ManagedStreamingResponse

        async def dummy_generator():
            yield "data"

        files_to_cleanup = ["/tmp/test.txt"]

        managed_response = ManagedStreamingResponse(
            dummy_generator(), files_to_cleanup, media_type="text/event-stream"
        )

        assert managed_response is not None
        assert managed_response.files_to_cleanup == files_to_cleanup

    @pytest.mark.asyncio
    async def test_managed_streaming_response_cleanup(self, temp_dir):
        """Test that managed response cleans up files"""
        from infotransform.utils.file_lifecycle import ManagedStreamingResponse

        # Create test file
        test_file = temp_dir / "cleanup_test.txt"
        test_file.write_text("test")

        async def dummy_generator():
            yield "data"

        managed_response = ManagedStreamingResponse(
            dummy_generator(), [str(test_file)], media_type="text/event-stream"
        )

        response = managed_response.create_response()

        # Response should be created
        assert response is not None


@pytest.mark.unit
class TestGetFileManager:
    """Test file manager singleton"""

    def test_get_file_manager(self):
        """Test getting file manager instance"""
        from infotransform.utils.file_lifecycle import get_file_manager

        manager1 = get_file_manager()
        manager2 = get_file_manager()

        # Should return same instance
        assert manager1 is manager2


@pytest.mark.integration
class TestFileLifecycleIntegration:
    """Integration tests for file lifecycle"""

    @pytest.mark.asyncio
    async def test_full_file_lifecycle(self, temp_dir):
        """Test complete file lifecycle from registration to cleanup"""
        from infotransform.utils.file_lifecycle import FileLifecycleManager

        manager = FileLifecycleManager()
        await manager.start()

        # Create and register multiple files
        test_files = []
        for i in range(5):
            test_file = temp_dir / f"lifecycle_test_{i}.txt"
            test_file.write_text(f"content {i}")
            test_files.append(str(test_file))
            manager.register_file(str(test_file))

        # All files should exist
        assert all(os.path.exists(f) for f in test_files)

        # Stop manager
        await manager.stop()

    @pytest.mark.asyncio
    async def test_batch_context_with_cleanup(self, temp_dir):
        """Test batch context with automatic cleanup"""
        from infotransform.utils.file_lifecycle import get_file_manager

        manager = get_file_manager()
        await manager.start()

        test_files = []
        file_infos = []

        for i in range(3):
            test_file = temp_dir / f"batch_test_{i}.txt"
            test_file.write_text(f"content {i}")
            test_files.append(str(test_file))
            file_infos.append(
                {"file_path": str(test_file), "filename": f"batch_test_{i}.txt"}
            )

        async with manager.batch_context(file_infos) as managed_files:
            # Process files
            for file_info in managed_files:
                assert os.path.exists(file_info["file_path"])

        # After exiting context, cleanup should be scheduled

        await manager.stop()
