"""
SQLite database for storing processing run logs with WAL mode enabled for production
"""

import sqlite3
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from infotransform.config import config

logger = logging.getLogger(__name__)


class ProcessingLogsDB:
    """
    SQLite database for storing processing run logs

    Features:
    - WAL mode for better concurrency
    - Async operations (non-blocking)
    - Graceful error handling (never crashes processing pipeline)
    - Single table design for simplicity
    """

    def __init__(self, db_path: str = None):
        """
        Initialize the database

        Args:
            db_path: Path to the SQLite database file
        """
        if db_path is None:
            db_path = config.get('database.processing_logs.path',
                                'backend/infotransform/data/processing_logs.db')

        self.db_path = Path(db_path)
        self.enabled = config.get('database.processing_logs.enabled', True)
        self.wal_mode = config.get('database.processing_logs.wal_mode', True)

        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        if self.enabled:
            self._init_database()
            logger.info(f"ProcessingLogsDB initialized at {self.db_path} (WAL mode: {self.wal_mode})")

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with proper settings"""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row  # Enable dict-like access

        # Enable WAL mode for production
        if self.wal_mode:
            conn.execute("PRAGMA journal_mode=WAL")

        # Performance settings for single-server deployment
        conn.execute("PRAGMA synchronous=NORMAL")  # Good balance for WAL mode
        conn.execute("PRAGMA cache_size=-64000")    # 64MB cache
        conn.execute("PRAGMA temp_store=MEMORY")    # Use memory for temp tables

        return conn

    def _init_database(self):
        """Initialize database schema"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Create main table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_runs (
                    -- Run identification
                    run_id TEXT PRIMARY KEY,

                    -- Timestamps (ISO 8601 format)
                    start_timestamp TEXT NOT NULL,
                    end_timestamp TEXT,
                    duration_seconds REAL,

                    -- File counts
                    total_files INTEGER NOT NULL,
                    successful_files INTEGER DEFAULT 0,
                    failed_files INTEGER DEFAULT 0,

                    -- Model information
                    model_key TEXT NOT NULL,
                    model_name TEXT,
                    ai_model_used TEXT,
                    custom_instructions TEXT,

                    -- Token usage
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    cache_read_tokens INTEGER DEFAULT 0,
                    cache_write_tokens INTEGER DEFAULT 0,
                    api_requests INTEGER DEFAULT 0,

                    -- Status
                    status TEXT DEFAULT 'running',

                    -- Metadata
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)

            # Create indexes for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_start_timestamp
                ON processing_runs(start_timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_status
                ON processing_runs(status)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_model_key
                ON processing_runs(model_key)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_created_at
                ON processing_runs(created_at)
            """)

            conn.commit()
            conn.close()

            logger.info("Database schema initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            # Don't raise - we don't want to crash the app if DB fails

    async def insert_run_start(
        self,
        run_id: str,
        start_timestamp: str,
        total_files: int,
        model_key: str,
        model_name: str = None,
        ai_model_used: str = None,
        custom_instructions: str = None
    ) -> bool:
        """
        Insert a new processing run record at start

        Args:
            run_id: Unique run identifier (UUID)
            start_timestamp: ISO 8601 timestamp
            total_files: Total number of files to process
            model_key: Model key being used
            model_name: Human-readable model name
            ai_model_used: AI model identifier
            custom_instructions: Custom instructions provided

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            # Run in thread pool to avoid blocking
            await asyncio.to_thread(self._insert_run_start_sync,
                                  run_id, start_timestamp, total_files,
                                  model_key, model_name, ai_model_used,
                                  custom_instructions)
            return True

        except Exception as e:
            logger.error(f"Error inserting run start for {run_id}: {e}")
            return False

    def _insert_run_start_sync(self, run_id, start_timestamp, total_files,
                               model_key, model_name, ai_model_used, custom_instructions):
        """Synchronous implementation of insert_run_start"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO processing_runs (
                run_id, start_timestamp, total_files,
                model_key, model_name, ai_model_used, custom_instructions,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'running')
        """, (run_id, start_timestamp, total_files, model_key,
              model_name, ai_model_used, custom_instructions))

        conn.commit()
        conn.close()

        logger.debug(f"Inserted run start: {run_id}")

    async def update_run_complete(
        self,
        run_id: str,
        end_timestamp: str,
        duration_seconds: float,
        successful_files: int,
        failed_files: int,
        token_usage: Dict[str, int],
        status: str = 'completed'
    ) -> bool:
        """
        Update processing run record at completion

        Args:
            run_id: Unique run identifier
            end_timestamp: ISO 8601 timestamp
            duration_seconds: Total duration
            successful_files: Number of successful files
            failed_files: Number of failed files
            token_usage: Dict with token usage metrics
            status: Final status ('completed' or 'failed')

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            await asyncio.to_thread(self._update_run_complete_sync,
                                  run_id, end_timestamp, duration_seconds,
                                  successful_files, failed_files, token_usage, status)
            return True

        except Exception as e:
            logger.error(f"Error updating run completion for {run_id}: {e}")
            return False

    def _update_run_complete_sync(self, run_id, end_timestamp, duration_seconds,
                                 successful_files, failed_files, token_usage, status):
        """Synchronous implementation of update_run_complete"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE processing_runs
            SET end_timestamp = ?,
                duration_seconds = ?,
                successful_files = ?,
                failed_files = ?,
                input_tokens = ?,
                output_tokens = ?,
                total_tokens = ?,
                cache_read_tokens = ?,
                cache_write_tokens = ?,
                api_requests = ?,
                status = ?
            WHERE run_id = ?
        """, (end_timestamp, duration_seconds, successful_files, failed_files,
              token_usage.get('input_tokens', 0),
              token_usage.get('output_tokens', 0),
              token_usage.get('total_tokens', 0),
              token_usage.get('cache_read_tokens', 0),
              token_usage.get('cache_write_tokens', 0),
              token_usage.get('requests', 0),
              status, run_id))

        conn.commit()
        conn.close()

        logger.debug(f"Updated run completion: {run_id}")

    async def get_recent_runs(self, limit: int = 100, model_key: str = None) -> list:
        """
        Get recent processing runs

        Args:
            limit: Maximum number of runs to return
            model_key: Optional filter by model key

        Returns:
            List of run records as dicts
        """
        if not self.enabled:
            return []

        try:
            return await asyncio.to_thread(self._get_recent_runs_sync, limit, model_key)
        except Exception as e:
            logger.error(f"Error getting recent runs: {e}")
            return []

    def _get_recent_runs_sync(self, limit, model_key):
        """Synchronous implementation of get_recent_runs"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if model_key:
            cursor.execute("""
                SELECT * FROM processing_runs
                WHERE model_key = ?
                ORDER BY start_timestamp DESC
                LIMIT ?
            """, (model_key, limit))
        else:
            cursor.execute("""
                SELECT * FROM processing_runs
                ORDER BY start_timestamp DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    async def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get aggregate statistics for the last N days

        Args:
            days: Number of days to look back

        Returns:
            Dict with aggregate statistics
        """
        if not self.enabled:
            return {}

        try:
            return await asyncio.to_thread(self._get_stats_sync, days)
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

    def _get_stats_sync(self, days):
        """Synchronous implementation of get_stats"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total_runs,
                SUM(total_files) as total_files_processed,
                SUM(successful_files) as total_successful,
                SUM(failed_files) as total_failed,
                SUM(total_tokens) as total_tokens,
                AVG(duration_seconds) as avg_duration,
                SUM(api_requests) as total_api_requests
            FROM processing_runs
            WHERE start_timestamp >= datetime('now', '-' || ? || ' days')
                AND status = 'completed'
        """, (days,))

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else {}


# Global instance
_logs_db: Optional[ProcessingLogsDB] = None


def get_logs_db() -> ProcessingLogsDB:
    """Get or create the global ProcessingLogsDB instance"""
    global _logs_db
    if _logs_db is None:
        _logs_db = ProcessingLogsDB()
    return _logs_db
