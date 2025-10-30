"""
Result caching system for InfoTransform

This module provides hash-based caching of AI analysis results to avoid
re-processing identical files. Cache entries are stored in SQLite with
automatic expiration based on TTL.

Usage:
    cache = ResultCache()

    # Check for cached result
    cached = await cache.get(content, model_key, ai_model)
    if cached:
        return cached

    # Process and store new result
    result = await process_file(content)
    await cache.set(content, model_key, ai_model, result)
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from pathlib import Path

import aiosqlite

from infotransform.config import config

logger = logging.getLogger(__name__)


class ResultCache:
    """Hash-based result cache with automatic expiration"""

    def __init__(self):
        # Load configuration
        self.enabled = config.get("result_cache.enabled", True)
        self.ttl_hours = float(config.get("result_cache.ttl_hours", 24))
        self.max_entries = int(config.get("result_cache.max_entries", 10000))
        self.cleanup_interval_hours = float(
            config.get("result_cache.cleanup_interval_hours", 6)
        )
        self.hash_algorithm = config.get("result_cache.hash_algorithm", "sha256")
        self.invalidation_strategy = config.get(
            "result_cache.invalidation_strategy", "ttl_only"
        )

        # Monitoring settings
        self.enable_metrics = config.get("monitoring.enable_metrics", True)
        self.log_operations = config.get("monitoring.log_cache_operations", False)

        # Advanced settings
        self.compress_results = config.get("advanced.compress_results", False)
        self.max_entry_size = int(
            config.get("advanced.max_entry_size_bytes", 1048576)
        )  # 1MB

        # Database path
        db_path = config.get(
            "database.processing_logs.path",
            "backend/infotransform/data/processing_logs.db",
        )
        self.db_path = str(Path(db_path).resolve())

        # Metrics
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0,
            "total_retrieval_time": 0.0,
            "total_storage_time": 0.0,
        }

        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

        if not self.enabled:
            logger.info("Result cache is disabled")
        else:
            logger.info(
                f"Result cache initialized: TTL={self.ttl_hours}h, "
                f"max_entries={self.max_entries}, db={self.db_path}"
            )

    async def start(self):
        """Start the cache and background cleanup task"""
        if not self.enabled:
            return

        self._running = True

        # Ensure cache table exists
        await self._ensure_table()

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Result cache started")

    async def stop(self):
        """Stop the cache and cleanup task"""
        self._running = False

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("Result cache stopped")

    def _compute_hash(self, content: str) -> str:
        """Compute content hash"""
        if self.hash_algorithm == "sha256":
            return hashlib.sha256(content.encode("utf-8")).hexdigest()
        elif self.hash_algorithm == "sha1":
            return hashlib.sha1(content.encode("utf-8")).hexdigest()
        elif self.hash_algorithm == "md5":
            return hashlib.md5(content.encode("utf-8")).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {self.hash_algorithm}")

    def _make_cache_key(self, content_hash: str, model_key: str, ai_model: str) -> str:
        """Create unique cache key from hash and model config"""
        # Include model configuration in cache key to prevent cross-contamination
        key_data = f"{content_hash}:{model_key}:{ai_model}"
        return hashlib.sha256(key_data.encode("utf-8")).hexdigest()

    async def _ensure_table(self):
        """Ensure cache table exists in database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS result_cache (
                    cache_key TEXT PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    model_key TEXT NOT NULL,
                    ai_model TEXT NOT NULL,
                    structured_data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    file_size_bytes INTEGER,
                    processing_time REAL
                )
            """)

            # Create indices for performance
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_expires
                ON result_cache(expires_at)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_content_hash
                ON result_cache(content_hash)
            """)

            await db.commit()

    async def get(
        self, content: str, model_key: str, ai_model: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached result if available

        Args:
            content: Markdown content to look up
            model_key: Document schema key
            ai_model: AI model used

        Returns:
            Cached structured data or None if not found/expired
        """
        if not self.enabled:
            return None

        start_time = time.time()

        try:
            # Compute hashes
            content_hash = self._compute_hash(content)
            cache_key = self._make_cache_key(content_hash, model_key, ai_model)

            # Query database
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    """
                    SELECT structured_data, expires_at, hit_count
                    FROM result_cache
                    WHERE cache_key = ?
                    """,
                    (cache_key,),
                ) as cursor:
                    row = await cursor.fetchone()

                if row is None:
                    # Cache miss
                    self.metrics["misses"] += 1
                    if self.log_operations:
                        logger.debug(f"Cache MISS: {cache_key[:16]}...")
                    return None

                structured_data_json, expires_at_str, hit_count = row

                # Check expiration
                expires_at = datetime.fromisoformat(expires_at_str)
                now = datetime.now(timezone.utc)

                if now >= expires_at:
                    # Expired entry
                    self.metrics["misses"] += 1
                    if self.log_operations:
                        logger.debug(f"Cache EXPIRED: {cache_key[:16]}...")

                    # Delete expired entry
                    await db.execute(
                        "DELETE FROM result_cache WHERE cache_key = ?", (cache_key,)
                    )
                    await db.commit()
                    return None

                # Cache hit - increment hit count
                await db.execute(
                    "UPDATE result_cache SET hit_count = ? WHERE cache_key = ?",
                    (hit_count + 1, cache_key),
                )
                await db.commit()

            # Deserialize result
            structured_data = json.loads(structured_data_json)

            # Update metrics
            retrieval_time = time.time() - start_time
            self.metrics["hits"] += 1
            self.metrics["total_retrieval_time"] += retrieval_time

            if self.log_operations:
                logger.info(
                    f"Cache HIT: {cache_key[:16]}... (retrieved in {retrieval_time * 1000:.1f}ms, "
                    f"hit_count={hit_count + 1})"
                )

            return structured_data

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.metrics["errors"] += 1
            return None

    async def set(
        self,
        content: str,
        model_key: str,
        ai_model: str,
        structured_data: Dict[str, Any],
        processing_time: float = 0.0,
    ) -> bool:
        """
        Store result in cache

        Args:
            content: Markdown content (used for hashing)
            model_key: Document schema key
            ai_model: AI model used
            structured_data: Extracted structured data to cache
            processing_time: Time taken to process (for metrics)

        Returns:
            True if cached successfully, False otherwise
        """
        if not self.enabled:
            return False

        start_time = time.time()

        try:
            # Serialize structured data
            structured_data_json = json.dumps(structured_data)

            # Check size limit
            if self.max_entry_size > 0:
                size_bytes = len(structured_data_json.encode("utf-8"))
                if size_bytes > self.max_entry_size:
                    logger.warning(
                        f"Cache entry too large ({size_bytes} bytes), skipping cache"
                    )
                    return False

            # Compute hashes
            content_hash = self._compute_hash(content)
            cache_key = self._make_cache_key(content_hash, model_key, ai_model)

            # Calculate expiration
            now = datetime.now(timezone.utc)
            if self.ttl_hours > 0:
                expires_at = now + timedelta(hours=self.ttl_hours)
            else:
                # TTL=0 means session-only (very far future date)
                expires_at = now + timedelta(days=365 * 10)  # 10 years

            # Store in database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO result_cache
                    (cache_key, content_hash, model_key, ai_model, structured_data,
                     created_at, expires_at, hit_count, file_size_bytes, processing_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                    """,
                    (
                        cache_key,
                        content_hash,
                        model_key,
                        ai_model,
                        structured_data_json,
                        now.isoformat(),
                        expires_at.isoformat(),
                        len(content.encode("utf-8")),
                        processing_time,
                    ),
                )
                await db.commit()

            # Update metrics
            storage_time = time.time() - start_time
            self.metrics["sets"] += 1
            self.metrics["total_storage_time"] += storage_time

            if self.log_operations:
                logger.debug(
                    f"Cache SET: {cache_key[:16]}... (stored in {storage_time * 1000:.1f}ms, "
                    f"expires: {expires_at.isoformat()})"
                )

            # Check if we need cleanup
            await self._check_max_entries()

            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.metrics["errors"] += 1
            return False

    async def _check_max_entries(self):
        """Check if cache has exceeded max entries and cleanup oldest if needed"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Count entries
                async with db.execute("SELECT COUNT(*) FROM result_cache") as cursor:
                    row = await cursor.fetchone()
                    count = row[0] if row else 0

                if count > self.max_entries:
                    # Remove oldest entries
                    to_remove = count - self.max_entries
                    await db.execute(
                        """
                        DELETE FROM result_cache
                        WHERE cache_key IN (
                            SELECT cache_key FROM result_cache
                            ORDER BY created_at ASC
                            LIMIT ?
                        )
                        """,
                        (to_remove,),
                    )
                    await db.commit()
                    logger.info(
                        f"Removed {to_remove} oldest cache entries (exceeded max_entries)"
                    )
        except Exception as e:
            logger.error(f"Error checking max entries: {e}")

    async def _cleanup_loop(self):
        """Background task to cleanup expired cache entries"""
        while self._running:
            try:
                # Wait for cleanup interval
                await asyncio.sleep(self.cleanup_interval_hours * 3600)

                if not self._running:
                    break

                # Cleanup expired entries
                await self.cleanup_expired()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def cleanup_expired(self) -> int:
        """
        Remove expired cache entries

        Returns:
            Number of entries removed
        """
        if not self.enabled:
            return 0

        try:
            now = datetime.now(timezone.utc).isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                # Count expired entries
                async with db.execute(
                    "SELECT COUNT(*) FROM result_cache WHERE expires_at < ?", (now,)
                ) as cursor:
                    row = await cursor.fetchone()
                    count = row[0] if row else 0

                if count > 0:
                    # Delete expired entries
                    await db.execute(
                        "DELETE FROM result_cache WHERE expires_at < ?", (now,)
                    )
                    await db.commit()
                    logger.info(f"Cleaned up {count} expired cache entries")

                return count
        except Exception as e:
            logger.error(f"Error cleaning up expired entries: {e}")
            return 0

    async def clear_all(self) -> int:
        """
        Clear all cache entries

        Returns:
            Number of entries removed
        """
        if not self.enabled:
            return 0

        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Count all entries
                async with db.execute("SELECT COUNT(*) FROM result_cache") as cursor:
                    row = await cursor.fetchone()
                    count = row[0] if row else 0

                # Delete all
                await db.execute("DELETE FROM result_cache")
                await db.commit()

                logger.info(f"Cleared all {count} cache entries")
                return count
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        total_requests = self.metrics["hits"] + self.metrics["misses"]
        hit_rate = self.metrics["hits"] / total_requests if total_requests > 0 else 0
        miss_rate = self.metrics["misses"] / total_requests if total_requests > 0 else 0

        avg_retrieval_time = (
            self.metrics["total_retrieval_time"] / self.metrics["hits"]
            if self.metrics["hits"] > 0
            else 0
        )

        avg_storage_time = (
            self.metrics["total_storage_time"] / self.metrics["sets"]
            if self.metrics["sets"] > 0
            else 0
        )

        return {
            "enabled": self.enabled,
            "hits": self.metrics["hits"],
            "misses": self.metrics["misses"],
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 3),
            "miss_rate": round(miss_rate, 3),
            "sets": self.metrics["sets"],
            "errors": self.metrics["errors"],
            "average_retrieval_time_ms": round(avg_retrieval_time * 1000, 2),
            "average_storage_time_ms": round(avg_storage_time * 1000, 2),
            "ttl_hours": self.ttl_hours,
            "max_entries": self.max_entries,
        }

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics from database"""
        if not self.enabled:
            return {"enabled": False}

        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total entries
                async with db.execute("SELECT COUNT(*) FROM result_cache") as cursor:
                    row = await cursor.fetchone()
                    total_entries = row[0] if row else 0

                # Total hits across all entries
                async with db.execute(
                    "SELECT SUM(hit_count) FROM result_cache"
                ) as cursor:
                    row = await cursor.fetchone()
                    total_db_hits = row[0] if row and row[0] else 0

                # Expired entries
                now = datetime.now(timezone.utc).isoformat()
                async with db.execute(
                    "SELECT COUNT(*) FROM result_cache WHERE expires_at < ?", (now,)
                ) as cursor:
                    row = await cursor.fetchone()
                    expired_entries = row[0] if row else 0

                # Most hit entries
                async with db.execute(
                    """
                    SELECT model_key, hit_count
                    FROM result_cache
                    ORDER BY hit_count DESC
                    LIMIT 5
                    """
                ) as cursor:
                    top_hits = await cursor.fetchall()

            return {
                "enabled": True,
                "total_entries": total_entries,
                "total_database_hits": total_db_hits,
                "expired_entries": expired_entries,
                "active_entries": total_entries - expired_entries,
                "top_hit_models": [
                    {"model_key": row[0], "hit_count": row[1]} for row in top_hits
                ],
                "session_metrics": self.get_metrics(),
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}


# Global cache instance
_cache: Optional[ResultCache] = None


async def get_result_cache() -> ResultCache:
    """Get or create the global cache instance"""
    global _cache
    if _cache is None:
        _cache = ResultCache()
        await _cache.start()
    return _cache
