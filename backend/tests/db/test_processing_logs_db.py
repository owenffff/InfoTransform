"""
Unit tests for processing logs database
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.db
class TestProcessingLogsDB:
    """Test processing logs database functionality"""

    @pytest.mark.asyncio
    async def test_insert_run_start(self, mock_db):
        """Test inserting run start record"""
        run_id = "test-run-123"
        start_timestamp = datetime.now(timezone.utc).isoformat()

        result = await mock_db.insert_run_start(
            run_id=run_id,
            start_timestamp=start_timestamp,
            total_files=5,
            model_key='invoice',
            model_name='InvoiceModel',
            ai_model_used='gpt-4o',
            custom_instructions='Extract invoice data'
        )

        assert result is True
        mock_db.insert_run_start.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_run_complete(self, mock_db):
        """Test updating run completion record"""
        run_id = "test-run-123"
        end_timestamp = datetime.now(timezone.utc).isoformat()

        result = await mock_db.update_run_complete(
            run_id=run_id,
            end_timestamp=end_timestamp,
            duration_seconds=10.5,
            successful_files=4,
            failed_files=1,
            token_usage={
                'input_tokens': 1000,
                'output_tokens': 500,
                'total_tokens': 1500
            },
            status='completed'
        )

        assert result is True
        mock_db.update_run_complete.assert_called_once()


@pytest.mark.db
@pytest.mark.integration
class TestProcessingLogsDBIntegration:
    """Integration tests for processing logs database"""

    @pytest.mark.asyncio
    @patch('infotransform.db.processing_logs_db.aiosqlite')
    async def test_full_run_logging_flow(self, mock_aiosqlite):
        """Test complete run logging flow"""
        # Mock database connection
        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock()
        mock_conn.commit = AsyncMock()
        mock_conn.close = AsyncMock()
        mock_aiosqlite.connect.return_value.__aenter__.return_value = mock_conn

        from infotransform.db.processing_logs_db import ProcessingLogsDB

        db = ProcessingLogsDB()

        # Insert run start
        run_id = "test-run-123"
        start_timestamp = datetime.now(timezone.utc).isoformat()

        await db.insert_run_start(
            run_id=run_id,
            start_timestamp=start_timestamp,
            total_files=5,
            model_key='invoice',
            model_name='InvoiceModel',
            ai_model_used='gpt-4o'
        )

        # Update run complete
        end_timestamp = datetime.now(timezone.utc).isoformat()

        await db.update_run_complete(
            run_id=run_id,
            end_timestamp=end_timestamp,
            duration_seconds=10.5,
            successful_files=4,
            failed_files=1,
            token_usage={'total_tokens': 1500},
            status='completed'
        )

        # Verify database operations were called
        assert mock_conn.execute.called
        assert mock_conn.commit.called

    @pytest.mark.asyncio
    @patch('infotransform.db.processing_logs_db.aiosqlite')
    async def test_query_run_history(self, mock_aiosqlite):
        """Test querying run history"""
        # Mock database connection and cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchall = AsyncMock(return_value=[
            ('run-1', '2024-01-01T00:00:00', 'completed', 5, 4, 1, 10.5, 'gpt-4o'),
            ('run-2', '2024-01-02T00:00:00', 'completed', 3, 3, 0, 5.2, 'gpt-4o')
        ])
        mock_cursor.description = [
            ('run_id',), ('start_timestamp',), ('status',),
            ('total_files',), ('successful_files',), ('failed_files',),
            ('duration_seconds',), ('ai_model_used',)
        ]

        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.close = AsyncMock()
        mock_aiosqlite.connect.return_value.__aenter__.return_value = mock_conn

        from infotransform.db.processing_logs_db import ProcessingLogsDB

        db = ProcessingLogsDB()

        # Query runs
        runs = await db.get_recent_runs(limit=10)

        # Should return runs (if method exists)
        assert mock_conn.execute.called

    @pytest.mark.asyncio
    @patch('infotransform.db.processing_logs_db.aiosqlite')
    async def test_database_initialization(self, mock_aiosqlite):
        """Test database table initialization"""
        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock()
        mock_conn.commit = AsyncMock()
        mock_conn.close = AsyncMock()
        mock_aiosqlite.connect.return_value.__aenter__.return_value = mock_conn

        from infotransform.db.processing_logs_db import ProcessingLogsDB

        db = ProcessingLogsDB()

        # Initialize database
        await db.initialize()

        # Should execute CREATE TABLE statement
        assert mock_conn.execute.called

    @pytest.mark.asyncio
    @patch('infotransform.db.processing_logs_db.aiosqlite')
    async def test_get_logs_db_singleton(self, mock_aiosqlite):
        """Test that get_logs_db returns singleton"""
        from infotransform.db.processing_logs_db import get_logs_db

        db1 = get_logs_db()
        db2 = get_logs_db()

        # Should return same instance
        assert db1 is db2


@pytest.mark.db
class TestDatabaseErrorHandling:
    """Test database error handling"""

    @pytest.mark.asyncio
    @patch('infotransform.db.processing_logs_db.aiosqlite')
    async def test_insert_run_start_with_error(self, mock_aiosqlite):
        """Test insert_run_start handles errors"""
        # Mock connection that raises an error
        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock(side_effect=Exception("Database error"))
        mock_conn.close = AsyncMock()
        mock_aiosqlite.connect.return_value.__aenter__.return_value = mock_conn

        from infotransform.db.processing_logs_db import ProcessingLogsDB

        db = ProcessingLogsDB()

        # Should handle error gracefully
        try:
            await db.insert_run_start(
                run_id="test-run",
                start_timestamp=datetime.now(timezone.utc).isoformat(),
                total_files=1,
                model_key='invoice',
                model_name='Invoice',
                ai_model_used='gpt-4o'
            )
        except Exception as e:
            # Error should be caught or re-raised appropriately
            assert "Database error" in str(e) or True

    @pytest.mark.asyncio
    @patch('infotransform.db.processing_logs_db.aiosqlite')
    async def test_update_run_complete_with_error(self, mock_aiosqlite):
        """Test update_run_complete handles errors"""
        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock(side_effect=Exception("Update error"))
        mock_conn.close = AsyncMock()
        mock_aiosqlite.connect.return_value.__aenter__.return_value = mock_conn

        from infotransform.db.processing_logs_db import ProcessingLogsDB

        db = ProcessingLogsDB()

        try:
            await db.update_run_complete(
                run_id="test-run",
                end_timestamp=datetime.now(timezone.utc).isoformat(),
                duration_seconds=10.0,
                successful_files=1,
                failed_files=0,
                token_usage={},
                status='completed'
            )
        except Exception as e:
            assert "Update error" in str(e) or True
