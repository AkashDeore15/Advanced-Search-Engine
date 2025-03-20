"""
Tests for the SearchEngine class with caching functionality.
Note: These tests require a running Redis server.
"""
import time
import pytest
import redis
from search_engine.engine import SearchEngine


@pytest.fixture
def engine_with_cache():
    """Create and return a SearchEngine instance with caching for testing."""
    try:
        # Create an engine with caching enabled
        engine = SearchEngine(enable_cache=True)
        # Test Redis connection
        if engine.cache_manager and engine.cache_manager.redis.is_connected():
            # Clear any existing data
            engine.clear_cache()
            yield engine
            # Clean up
            engine.clear_cache()
            engine.close()
        else:
            pytest.skip("Redis connection failed")
    except (redis.RedisError, ConnectionError):
        pytest.skip("Redis server not available")


@pytest.fixture
def engine_no_cache():
    """Create and return a SearchEngine instance without caching for testing."""
    engine = SearchEngine(enable_cache=False)
    yield engine

def test_engine_initialization_with_cache(engine_with_cache):
    """Test that a SearchEngine can be properly initialized with caching."""
    assert engine_with_cache.indexer is not None
    assert engine_with_cache.ranker is not None
    assert engine_with_cache.ranker_factory is not None
    assert engine_with_cache.enable_cache is True
    assert engine_with_cache.cache_manager is not None


def test_engine_initialization_without_cache(engine_no_cache):
    """Test that a SearchEngine can be properly initialized without caching."""
    assert engine_no_cache.indexer is not None
    assert engine_no_cache.ranker is not None
    assert engine_no_cache.ranker_factory is not None
    assert engine_no_cache.enable_cache is False
    assert engine_no_cache.cache_manager is None


def test_document_caching(engine_with_cache):
    """Test that documents are properly cached."""
    # Index a document
    engine_with_cache.index_document('test_doc', 'Test document content.', {'author': 'Test'})
    # Get the document - should come from cache
    start_time = time.time()
    doc = engine_with_cache.get_document('test_doc')
    first_retrieval_time = time.time() - start_time
    assert doc is not None
    assert doc.doc_id == 'test_doc'
    # Get it again - should be faster
    start_time = time.time()
    doc = engine_with_cache.get_document('test_doc')
    second_retrieval_time = time.time() - start_time
    # The second retrieval should be faster or comparable (due to cache)
    # but in small tests the difference might be negligible
    assert doc is not None
    assert second_retrieval_time <= first_retrieval_time * 1.5  # Allow some margin


def test_query_caching(engine_with_cache, sample_docs):
    """Test that query results are properly cached."""
    # Index some documents
    engine_with_cache.index_documents(sample_docs)
    # Search for a query
    start_time = time.time()
    results1 = engine_with_cache.search('python programming')
    first_search_time = time.time() - start_time
    assert len(results1) > 0
    # Search again - should come from cache
    start_time = time.time()
    results2 = engine_with_cache.search('python programming')
    second_search_time = time.time() - start_time
    # Results should be the same
    assert len(results1) == len(results2)
    assert results1[0]['doc_id'] == results2[0]['doc_id']
    # The second search should be faster (due to cache)
    assert second_search_time < first_search_time


def test_cache_invalidation(engine_with_cache, sample_docs):
    """Test that cache is properly invalidated when documents change."""
    # Index some documents
    engine_with_cache.index_documents(sample_docs)
    # Search for a query
    results1 = engine_with_cache.search('search engines')
    assert len(results1) > 0
    # Store the top result
    top_doc_id = results1[0]['doc_id']
    # Remove the top document
    engine_with_cache.remove_document(top_doc_id)
    # Search again - should not return the removed document
    results2 = engine_with_cache.search('search engines')
    # Check that the removed document is not in the results
    for result in results2:
        assert result['doc_id'] != top_doc_id


def test_enable_disable_cache(engine_with_cache, sample_docs):
    """Test enabling and disabling the cache."""
    # Index some documents
    engine_with_cache.index_documents(sample_docs)
    # Search with cache enabled
    results1 = engine_with_cache.search('python')
    assert len(results1) > 0
    # Disable caching
    engine_with_cache.disable_caching()
    assert not engine_with_cache.enable_cache
    # Search again - should bypass cache
    results2 = engine_with_cache.search('python')
    assert len(results2) > 0
    # Enable caching again
    engine_with_cache.enable_caching()
    assert engine_with_cache.enable_cache
    # Search again - should use cache
    results3 = engine_with_cache.search('python')
    assert len(results3) > 0


def test_get_stats_with_cache(engine_with_cache, sample_docs):
    """Test getting stats with cache."""
    # Index some documents
    engine_with_cache.index_documents(sample_docs)
    # Get stats
    stats = engine_with_cache.get_stats()
    # Check stats
    assert stats['num_documents'] == len(sample_docs)
    assert 'cache' in stats
    assert 'hit_ratio' in stats['cache']
    # Get stats again - should come from cache
    stats2 = engine_with_cache.get_stats()
    assert stats2['num_documents'] == len(sample_docs)


def test_performance_stats(engine_with_cache, sample_docs):
    """Test getting performance stats."""
    # Index some documents
    engine_with_cache.index_documents(sample_docs)
    # Do some searches to generate cache metrics
    engine_with_cache.search('python')
    engine_with_cache.search('python')  # Should hit cache
    engine_with_cache.search('nonexistent')  # Should miss cache
    # Get performance stats
    stats = engine_with_cache.get_performance_stats()
    # Check stats
    assert 'index_size' in stats
    assert 'cache' in stats
    assert stats['cache']['hits'] > 0
    assert stats['cache']['misses'] > 0


def test_clear_cache(engine_with_cache, sample_docs):
    """Test clearing the cache."""
    # Index some documents
    engine_with_cache.index_documents(sample_docs)
    # Do a search to cache results
    engine_with_cache.search('python')
    # Clear the cache
    engine_with_cache.clear_cache()
    # Reset metrics
    engine_with_cache.reset_cache_metrics()
    # Search again - should be a cache miss
    engine_with_cache.search('python')
    # Check metrics
    stats = engine_with_cache.get_performance_stats()
    assert stats['cache']['hits'] == 0
    assert stats['cache']['misses'] == 1
