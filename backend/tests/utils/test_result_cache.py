"""
Unit tests for result cache manager
"""

import pytest
import asyncio
import tempfile
import os

from infotransform.utils.result_cache import ResultCache


@pytest.fixture
async def temp_cache():
    """Create a temporary cache instance for testing"""
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    temp_db = os.path.join(temp_dir, "test_cache.db")

    # Create cache instance with test database
    cache = ResultCache()
    cache.db_path = temp_db
    cache.enabled = True
    cache.ttl_hours = 1  # 1 hour TTL for testing
    cache.max_entries = 100

    await cache.start()

    yield cache

    await cache.stop()

    # Cleanup
    if os.path.exists(temp_db):
        os.remove(temp_db)
    os.rmdir(temp_dir)


@pytest.mark.asyncio
async def test_cache_initialization(temp_cache):
    """Test cache initializes correctly"""
    assert temp_cache.enabled is True
    assert temp_cache.ttl_hours == 1
    assert temp_cache.max_entries == 100
    assert os.path.exists(temp_cache.db_path)


@pytest.mark.asyncio
async def test_cache_set_and_get(temp_cache):
    """Test basic cache set and get operations"""
    content = "This is test content for caching"
    model_key = "test_model"
    ai_model = "gpt-4"
    structured_data = {"field1": "value1", "field2": "value2"}

    # Set cache entry
    result = await temp_cache.set(
        content, model_key, ai_model, structured_data, processing_time=1.5
    )
    assert result is True

    # Get cache entry
    cached_data = await temp_cache.get(content, model_key, ai_model)
    assert cached_data is not None
    assert cached_data == structured_data

    # Verify metrics
    metrics = temp_cache.get_metrics()
    assert metrics["hits"] == 1
    assert metrics["misses"] == 0
    assert metrics["sets"] == 1


@pytest.mark.asyncio
async def test_cache_miss(temp_cache):
    """Test cache miss when content not cached"""
    content = "Uncached content"
    model_key = "test_model"
    ai_model = "gpt-4"

    # Try to get non-existent entry
    cached_data = await temp_cache.get(content, model_key, ai_model)
    assert cached_data is None

    # Verify metrics
    metrics = temp_cache.get_metrics()
    assert metrics["misses"] == 1
    assert metrics["hits"] == 0


@pytest.mark.asyncio
async def test_cache_different_models(temp_cache):
    """Test that different models create different cache entries"""
    content = "Same content"
    structured_data_1 = {"model": "gpt-4", "result": "data1"}
    structured_data_2 = {"model": "gpt-3.5", "result": "data2"}

    # Cache with model 1
    await temp_cache.set(content, "schema1", "gpt-4", structured_data_1)

    # Cache with model 2 (same content, different model)
    await temp_cache.set(content, "schema1", "gpt-3.5", structured_data_2)

    # Get both - should be different
    cached_1 = await temp_cache.get(content, "schema1", "gpt-4")
    cached_2 = await temp_cache.get(content, "schema1", "gpt-3.5")

    assert cached_1 == structured_data_1
    assert cached_2 == structured_data_2
    assert cached_1 != cached_2


@pytest.mark.asyncio
async def test_cache_different_schemas(temp_cache):
    """Test that different schemas create different cache entries"""
    content = "Same content"
    structured_data_1 = {"schema": "invoice", "result": "data1"}
    structured_data_2 = {"schema": "receipt", "result": "data2"}

    # Cache with schema 1
    await temp_cache.set(content, "invoice", "gpt-4", structured_data_1)

    # Cache with schema 2 (same content, different schema)
    await temp_cache.set(content, "receipt", "gpt-4", structured_data_2)

    # Get both - should be different
    cached_1 = await temp_cache.get(content, "invoice", "gpt-4")
    cached_2 = await temp_cache.get(content, "receipt", "gpt-4")

    assert cached_1 == structured_data_1
    assert cached_2 == structured_data_2


@pytest.mark.asyncio
async def test_cache_content_hashing(temp_cache):
    """Test that identical content gets same cache entry"""
    content = "Test content for hashing"
    model_key = "test_model"
    ai_model = "gpt-4"
    structured_data = {"field": "value"}

    # Set cache entry
    await temp_cache.set(content, model_key, ai_model, structured_data)

    # Get with identical content
    cached_data = await temp_cache.get(content, model_key, ai_model)
    assert cached_data == structured_data

    # Get with modified content - should miss
    modified_content = content + " modified"
    cached_data_miss = await temp_cache.get(modified_content, model_key, ai_model)
    assert cached_data_miss is None


@pytest.mark.asyncio
async def test_cache_expiration(temp_cache):
    """Test that expired cache entries are not returned"""
    # Set very short TTL
    temp_cache.ttl_hours = 0.0001  # ~0.36 seconds

    content = "Expiring content"
    model_key = "test_model"
    ai_model = "gpt-4"
    structured_data = {"field": "value"}

    # Set cache entry
    await temp_cache.set(content, model_key, ai_model, structured_data)

    # Should be available immediately
    cached_data = await temp_cache.get(content, model_key, ai_model)
    assert cached_data == structured_data

    # Wait for expiration
    await asyncio.sleep(1)

    # Should be expired now
    cached_data_expired = await temp_cache.get(content, model_key, ai_model)
    assert cached_data_expired is None


@pytest.mark.asyncio
async def test_cache_hit_count(temp_cache):
    """Test that cache hit count increments correctly"""
    content = "Hit count test"
    model_key = "test_model"
    ai_model = "gpt-4"
    structured_data = {"field": "value"}

    # Set cache entry
    await temp_cache.set(content, model_key, ai_model, structured_data)

    # Get multiple times
    for _ in range(5):
        cached_data = await temp_cache.get(content, model_key, ai_model)
        assert cached_data == structured_data

    # Verify hit metrics
    metrics = temp_cache.get_metrics()
    assert metrics["hits"] == 5


@pytest.mark.asyncio
async def test_cache_max_entries(temp_cache):
    """Test that cache respects max entries limit"""
    temp_cache.max_entries = 5

    # Add more entries than max
    for i in range(10):
        content = f"Content {i}"
        await temp_cache.set(content, "test_model", "gpt-4", {"index": i})

    # Manually trigger cleanup check
    await temp_cache._check_max_entries()

    # Count entries in database
    import aiosqlite

    async with aiosqlite.connect(temp_cache.db_path) as db:
        async with db.execute("SELECT COUNT(*) FROM result_cache") as cursor:
            row = await cursor.fetchone()
            count = row[0]

    # Should have only max_entries
    assert count <= temp_cache.max_entries


@pytest.mark.asyncio
async def test_cache_cleanup_expired(temp_cache):
    """Test manual cleanup of expired entries"""
    # Set very short TTL
    temp_cache.ttl_hours = 0.0001

    # Add some entries
    for i in range(5):
        content = f"Content {i}"
        await temp_cache.set(content, "test_model", "gpt-4", {"index": i})

    # Wait for expiration
    await asyncio.sleep(1)

    # Cleanup expired entries
    removed_count = await temp_cache.cleanup_expired()

    # Should have removed all entries
    assert removed_count == 5


@pytest.mark.asyncio
async def test_cache_clear_all(temp_cache):
    """Test clearing all cache entries"""
    # Add some entries
    for i in range(5):
        content = f"Content {i}"
        await temp_cache.set(content, "test_model", "gpt-4", {"index": i})

    # Clear all
    removed_count = await temp_cache.clear_all()

    # Should have removed all entries
    assert removed_count == 5

    # Verify cache is empty
    cached_data = await temp_cache.get("Content 0", "test_model", "gpt-4")
    assert cached_data is None


@pytest.mark.asyncio
async def test_cache_metrics(temp_cache):
    """Test cache metrics calculation"""
    # Perform various operations
    await temp_cache.set("content1", "model1", "gpt-4", {"data": 1})
    await temp_cache.set("content2", "model2", "gpt-4", {"data": 2})

    await temp_cache.get("content1", "model1", "gpt-4")  # Hit
    await temp_cache.get("content1", "model1", "gpt-4")  # Hit
    await temp_cache.get("content3", "model3", "gpt-4")  # Miss

    metrics = temp_cache.get_metrics()

    assert metrics["hits"] == 2
    assert metrics["misses"] == 1
    assert metrics["sets"] == 2
    assert metrics["total_requests"] == 3
    assert metrics["hit_rate"] == pytest.approx(2 / 3, 0.01)
    assert metrics["miss_rate"] == pytest.approx(1 / 3, 0.01)


@pytest.mark.asyncio
async def test_cache_disabled():
    """Test that cache operations work when disabled"""
    cache = ResultCache()
    cache.enabled = False

    # Operations should return False/None when disabled
    result = await cache.set("content", "model", "gpt-4", {"data": 1})
    assert result is False

    cached_data = await cache.get("content", "model", "gpt-4")
    assert cached_data is None


@pytest.mark.asyncio
async def test_cache_stats(temp_cache):
    """Test cache statistics retrieval"""
    # Add some entries with hits
    await temp_cache.set("content1", "model1", "gpt-4", {"data": 1})
    await temp_cache.get("content1", "model1", "gpt-4")  # Hit
    await temp_cache.get("content1", "model1", "gpt-4")  # Hit

    stats = await temp_cache.get_stats()

    assert stats["enabled"] is True
    assert stats["total_entries"] == 1
    assert stats["total_database_hits"] == 2
    assert stats["active_entries"] >= 1


@pytest.mark.asyncio
async def test_cache_large_entry_limit(temp_cache):
    """Test that large entries are rejected"""
    temp_cache.max_entry_size = 100  # 100 bytes limit

    # Create large structured data
    large_data = {"data": "x" * 200}  # Exceeds limit

    # Should be rejected
    result = await temp_cache.set("content", "model", "gpt-4", large_data)
    assert result is False

    # Should not be in cache
    cached_data = await temp_cache.get("content", "model", "gpt-4")
    assert cached_data is None


@pytest.mark.asyncio
async def test_cache_hash_algorithms(temp_cache):
    """Test different hash algorithms"""
    content = "Test content"

    # Test SHA-256 (default)
    temp_cache.hash_algorithm = "sha256"
    hash_sha256 = temp_cache._compute_hash(content)
    assert len(hash_sha256) == 64  # SHA-256 produces 64 hex characters

    # Test SHA-1
    temp_cache.hash_algorithm = "sha1"
    hash_sha1 = temp_cache._compute_hash(content)
    assert len(hash_sha1) == 40  # SHA-1 produces 40 hex characters

    # Test MD5
    temp_cache.hash_algorithm = "md5"
    hash_md5 = temp_cache._compute_hash(content)
    assert len(hash_md5) == 32  # MD5 produces 32 hex characters


@pytest.mark.asyncio
async def test_cache_concurrent_access(temp_cache):
    """Test concurrent cache access"""
    content = "Concurrent test"
    model_key = "test_model"
    ai_model = "gpt-4"
    structured_data = {"field": "value"}

    # Set cache entry
    await temp_cache.set(content, model_key, ai_model, structured_data)

    # Concurrent reads
    tasks = [temp_cache.get(content, model_key, ai_model) for _ in range(10)]
    results = await asyncio.gather(*tasks)

    # All should return the same data
    assert all(r == structured_data for r in results)
    assert len(results) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
