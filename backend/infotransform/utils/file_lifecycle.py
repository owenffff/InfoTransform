"""
File lifecycle management for proper cleanup without fixed delays
"""

import asyncio
import os
import logging
from typing import Dict, List, Optional, Any
import contextlib
from datetime import datetime

from infotransform.config import config

logger = logging.getLogger(__name__)


class FileLifecycleManager:
    """Manages file lifecycle with reference counting and proper cleanup"""

    def __init__(self):
        # File reference counting
        self.file_refs: Dict[str, int] = {}
        self.file_locks: Dict[str, asyncio.Lock] = {}

        # Cleanup tracking
        self.cleanup_events: Dict[str, asyncio.Event] = {}
        self.file_creation_times: Dict[str, datetime] = {}

        # Configuration
        self.cleanup_strategy = config.get_performance(
            "file_management.cleanup_strategy", "stream_complete"
        )
        self.max_retention = float(
            config.get_performance("file_management.max_file_retention", 300)
        )
        self.cleanup_interval = float(
            config.get_performance("file_management.cleanup_check_interval", 10)
        )

        # Background cleanup task
        self.cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start the background cleanup task"""
        if not self._running:
            self._running = True
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("FileLifecycleManager started")

    async def stop(self):
        """Stop the background cleanup task"""
        self._running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("FileLifecycleManager stopped")

    async def acquire_file(self, file_path: str) -> None:
        """
        Increment reference count for a file

        Args:
            file_path: Path to the file
        """
        # Ensure we have a lock for this file
        if file_path not in self.file_locks:
            self.file_locks[file_path] = asyncio.Lock()

        async with self.file_locks[file_path]:
            self.file_refs[file_path] = self.file_refs.get(file_path, 0) + 1

            # Track creation time if first reference
            if self.file_refs[file_path] == 1:
                self.file_creation_times[file_path] = datetime.now()

            logger.debug(
                f"Acquired file {file_path}, refs: {self.file_refs[file_path]}"
            )

    async def release_file(self, file_path: str) -> None:
        """
        Decrement reference count and cleanup if zero

        Args:
            file_path: Path to the file
        """
        if file_path not in self.file_locks:
            logger.warning(f"Attempting to release untracked file: {file_path}")
            return

        async with self.file_locks[file_path]:
            if file_path in self.file_refs:
                self.file_refs[file_path] -= 1
                logger.debug(
                    f"Released file {file_path}, refs: {self.file_refs[file_path]}"
                )

                # Mark for cleanup if no more references
                if self.file_refs[file_path] <= 0:
                    if self.cleanup_strategy == "reference_counting":
                        await self._cleanup_file(file_path)
                    else:
                        # Mark as ready for cleanup
                        if file_path not in self.cleanup_events:
                            self.cleanup_events[file_path] = asyncio.Event()
                        self.cleanup_events[file_path].set()

    @contextlib.asynccontextmanager
    async def file_context(self, file_path: str):
        """
        Context manager for file usage

        Args:
            file_path: Path to the file

        Yields:
            The file path
        """
        await self.acquire_file(file_path)
        try:
            yield file_path
        finally:
            await self.release_file(file_path)

    @contextlib.asynccontextmanager
    async def batch_context(self, files: List[Dict[str, str]]):
        """
        Context manager for batch file usage

        Args:
            files: List of file info dictionaries

        Yields:
            The files list
        """
        file_paths = [f["file_path"] for f in files]

        # Acquire all files
        for file_path in file_paths:
            await self.acquire_file(file_path)

        try:
            yield files
        finally:
            # Release all files
            for file_path in file_paths:
                await self.release_file(file_path)

    async def mark_stream_complete(self, file_paths: List[str]):
        """
        Mark that streaming is complete for a set of files.
        Files will NOT be cleaned up immediately - they will be retained
        for the configured max_retention period to allow users to create
        multiple review sessions from the same processing results.

        Args:
            file_paths: List of file paths
        """
        for file_path in file_paths:
            # Track the file if not already tracked
            if file_path not in self.file_creation_times:
                self.file_creation_times[file_path] = datetime.now()
                logger.info(
                    f"File tracked for retention: {file_path} (will be deleted after {self.max_retention}s)"
                )

            # Do NOT set cleanup event - let files age naturally
            # They will only be cleaned up when they exceed max_retention time
            # This allows users to create multiple review sessions from the same files

    async def _cleanup_file(self, file_path: str):
        """
        Actually delete a file from disk

        Args:
            file_path: Path to the file
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")

            # Remove from tracking
            self.file_refs.pop(file_path, None)
            self.file_locks.pop(file_path, None)
            self.cleanup_events.pop(file_path, None)
            self.file_creation_times.pop(file_path, None)

        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {e}")

    async def _cleanup_loop(self):
        """Background task to clean up old files"""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)

                now = datetime.now()
                files_to_cleanup = []

                # Check for files that should be cleaned up
                # Priority: Only cleanup files that have exceeded max_retention time
                # AND have no active references
                for file_path, creation_time in list(self.file_creation_times.items()):
                    age = (now - creation_time).total_seconds()

                    # Only cleanup if file is too old AND has no active references
                    if (
                        age > self.max_retention
                        and self.file_refs.get(file_path, 0) <= 0
                    ):
                        files_to_cleanup.append(file_path)
                        logger.debug(
                            f"File {file_path} marked for cleanup (age: {age:.1f}s)"
                        )

                # Clean up identified files
                for file_path in files_to_cleanup:
                    await self._cleanup_file(file_path)

                if files_to_cleanup:
                    logger.info(f"Cleaned up {len(files_to_cleanup)} old files")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get lifecycle manager statistics"""
        return {
            "tracked_files": len(self.file_refs),
            "active_references": sum(self.file_refs.values()),
            "pending_cleanup": len(
                [f for f, e in self.cleanup_events.items() if e.is_set()]
            ),
            "oldest_file_age": max(
                [
                    (datetime.now() - t).total_seconds()
                    for t in self.file_creation_times.values()
                ]
            )
            if self.file_creation_times
            else 0,
        }


# Global instance
_file_manager: Optional[FileLifecycleManager] = None


def get_file_manager() -> FileLifecycleManager:
    """Get or create the global file manager instance"""
    global _file_manager
    if _file_manager is None:
        _file_manager = FileLifecycleManager()
    return _file_manager


class ManagedStreamingResponse:
    """
    Streaming response that handles cleanup after completion
    """

    def __init__(self, content_generator, file_paths: List[str], **kwargs):
        self.content_generator = content_generator
        self.file_paths = file_paths
        self.file_manager = get_file_manager()
        self.response_kwargs = kwargs

    async def generate_with_cleanup(self):
        """Generate content and handle cleanup"""
        try:
            async for chunk in self.content_generator:
                yield chunk
        finally:
            # Mark files for cleanup after streaming completes
            await self.file_manager.mark_stream_complete(self.file_paths)

    def create_response(self):
        """Create the FastAPI StreamingResponse"""
        from fastapi.responses import StreamingResponse

        return StreamingResponse(self.generate_with_cleanup(), **self.response_kwargs)
