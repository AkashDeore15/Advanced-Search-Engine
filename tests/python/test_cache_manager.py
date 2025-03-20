"""
Tests for the CacheManager class.
Note: These tests require a running Redis server.
"""
import pytest
import redis
from search_engine.cache.redis_client import RedisClient
from search_engine.cache.cache_manager import CacheManager


@pytest.fixture
def cache_manager():
    """Create and return a CacheManager instance for testing."""
    try:
        redis_client = RedisClient(decode_responses=True)
        redis_client.connect()
        # Use short TTLs for testing
        cache_manager = CacheManager(
            redis_client=redis_client,
            doc_ttl=5,
            query_ttl=5,
            stats_ttl=5
        )
        # Clean up any previous test data
        cache_manager.invalidate_all()
        cache_manager.reset_metrics()
        yield cache_manager
        # Clean up after tests
        cache_manager.invalidate_all()
        redis_client.close()
    except (redis.RedisError, ConnectionError):
        pytest.skip("Redis server not available")


def test_cache_document(cache_manager):
    """Test caching and retrieving documents."""
    # Create a test document
    doc_id = "test_doc"
    document_data = {
        "doc_id": doc_id,
        "content": "Test document content",
        "metadata": {"author": "Test"}
    }
    # Cache the document
    assert cache_manager.cache_document(doc_id, document_data)
    # Retrieve the document
    cached_doc = cache_manager.get_cached_document(doc_id)
    assert cached_doc is not None
    assert cached_doc["doc_id"] == doc_id
    assert cached_doc["content"] == "Test document content"
    assert cached_doc["metadata"]["author"] == "Test"
    # Check cache metrics
    metrics = cache_manager.get_cache_metrics()
    assert metrics["hits"] == 1
    assert metrics["misses"] == 0
    assert metrics["hit_ratio"] == 1.0


def test_cache_query_results(cache_manager):
    """Test caching and retrieving query results."""
    # Create test query and results
    query = "test query"
    results = [
        {"doc_id": "doc1", "content": "Content 1", "metadata": {}, "score": 0.9},
        {"doc_id": "doc2", "content": "Content 2", "metadata": {}, "score": 0.8}
    ]
    # Cache the query results
    assert cache_manager.cache_query_results(query, results)
    # Retrieve the results
    cached_results = cache_manager.get_cached_query_results(query)
    assert cached_results is not None
    assert len(cached_results) == 2
    assert cached_results[0]["doc_id"] == "doc1"
    assert cached_results[1]["doc_id"] == "doc2"
    # Check cache metrics
    metrics = cache_manager.get_cache_metrics()
    assert metrics["hits"] == 1
    assert metrics["misses"] == 0
    # Try with a different top_n
    assert cache_manager.get_cached_query_results(query, top_n=5) is None
    # Check that miss was counted
    metrics = cache_manager.get_cache_metrics()
    assert metrics["hits"] == 1
    assert metrics["misses"] == 1


def test_invalidate_document(cache_manager):
    """Test invalidating a cached document."""
    # Cache some documents
    cache_manager.cache_document("doc1", {"doc_id": "doc1", "content": "Content 1"})
    cache_manager.cache_document("doc2", {"doc_id": "doc2", "content": "Content 2"})
    # Invalidate one document
    assert cache_manager.invalidate_document("doc1")
    # Check that it's gone but the other remains
    assert cache_manager.get_cached_document("doc1") is None
    assert cache_manager.get_cached_document("doc2") is not None
    # Invalidate a non-existent document
    assert cache_manager.invalidate_document("nonexistent")


def test_invalidate_all_documents(cache_manager):
    """Test invalidating all cached documents."""
    # Cache some documents
    cache_manager.cache_document("doc1", {"doc_id": "doc1", "content": "Content 1"})
    cache_manager.cache_document("doc2", {"doc_id": "doc2", "content": "Content 2"})
    # Cache some queries too
    cache_manager.cache_query_results("query1", [{"doc_id": "doc1"}])
    # Invalidate all documents
    assert cache_manager.invalidate_all_documents()
    # Check that documents are gone but queries remain
    assert cache_manager.get_cached_document("doc1") is None
    assert cache_manager.get_cached_document("doc2") is None
    assert cache_manager.get_cached_query_results("query1") is not None


def test_invalidate_all_queries(cache_manager):
    """Test invalidating all cached queries."""
    # Cache some queries
    cache_manager.cache_query_results("query1", [{"doc_id": "doc1"}])
    cache_manager.cache_query_results("query2", [{"doc_id": "doc2"}])
    # Cache some documents too
    cache_manager.cache_document("doc1", {"doc_id": "doc1", "content": "Content 1"})
    # Invalidate all queries
    assert cache_manager.invalidate_all_queries()
    # Check that queries are gone but documents remain
    assert cache_manager.get_cached_query_results("query1") is None
    assert cache_manager.get_cached_query_results("query2") is None
    assert cache_manager.get_cached_document("doc1") is not None


def test_invalidate_all(cache_manager):
    """Test invalidating all cached items."""
    # Cache documents and queries
    cache_manager.cache_document("doc1", {"doc_id": "doc1", "content": "Content 1"})
    cache_manager.cache_query_results("query1", [{"doc_id": "doc1"}])
    # Invalidate all
    assert cache_manager.invalidate_all()
    # Check that everything is gone
    assert cache_manager.get_cached_document("doc1") is None
    assert cache_manager.get_cached_query_results("query1") is None


def test_cache_stats(cache_manager):
    """Test caching and retrieving statistics."""
    # Create test stats
    stats_data = {
        "num_documents": 100,
        "is_index_built": True,
        "ranker_type": "TF-IDF"
    }
    # Cache the stats
    assert cache_manager.cache_stats(stats_data)
    # Retrieve the stats
    cached_stats = cache_manager.get_cached_stats()
    assert cached_stats is not None
    assert cached_stats["num_documents"] == 100
    assert cached_stats["is_index_built"] is True
    assert cached_stats["ranker_type"] == "TF-IDF"


def test_cache_enable_disable(cache_manager):
    """Test enabling and disabling caching."""
    # Cache a document
    cache_manager.cache_document("doc1", {"doc_id": "doc1", "content": "Content 1"})
    assert cache_manager.get_cached_document("doc1") is not None
    # Disable caching
    cache_manager.disable_cache()
    assert not cache_manager.is_cache_enabled()
    # Try to get from cache - should return None
    assert cache_manager.get_cached_document("doc1") is None
    # Try to cache something - should not work
    cache_manager.cache_document("doc2", {"doc_id": "doc2", "content": "Content 2"})
    # Enable caching again
    cache_manager.enable_cache()
    assert cache_manager.is_cache_enabled()
    # Check doc1 is still in cache
    assert cache_manager.get_cached_document("doc1") is not None
    # But doc2 shouldn't be there
    assert cache_manager.get_cached_document("doc2") is None


def test_metrics_reset(cache_manager):
    """Test resetting cache metrics."""
    # Generate some cache hits and misses
    cache_manager.cache_document("doc1", {"doc_id": "doc1", "content": "Content 1"})
    cache_manager.get_cached_document("doc1")  # Hit
    cache_manager.get_cached_document("doc2")  # Miss
    # Check the metrics
    metrics = cache_manager.get_cache_metrics()
    assert metrics["hits"] == 1
    assert metrics["misses"] == 1
    # Reset metrics
    cache_manager.reset_metrics()
    # Check that metrics are zeroed
    metrics = cache_manager.get_cache_metrics()
    assert metrics["hits"] == 0
    assert metrics["misses"] == 0
