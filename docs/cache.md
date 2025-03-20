# Redis Caching for the Advanced Search Engine

This document describes the Redis caching implementation for the Advanced Search Engine project.

## Overview

The caching system is designed to improve search engine performance by storing frequently accessed documents and query results in Redis. This reduces the need to perform expensive TF-IDF calculations repeatedly for the same queries.

## Architecture

The caching system consists of the following components:

1. **RedisClient**: A wrapper around the Redis client that provides high-level operations for storing and retrieving data.
2. **CacheManager**: Manages the caching strategy, including key generation, TTL (Time-To-Live) settings, and cache invalidation.
3. **SearchEngine Integration**: The search engine core has been modified to utilize the cache for document retrieval and query results.

## Cache Types

The system implements three types of caching:

1. **Document Cache**: Stores document data to avoid repeated retrieval from the indexer.
2. **Query Cache**: Stores search results for specific queries to avoid re-executing the search.
3. **Stats Cache**: Stores search engine statistics for quick access.

## Configuration

The following configuration options are available:

- **Enable/Disable Cache**: Turn caching on or off.
- **Redis Connection**: Configure the Redis host, port, and database.
- **TTL Settings**: Configure how long items remain in the cache before expiring.
  - Document TTL: 24 hours by default
  - Query TTL: 1 hour by default
  - Stats TTL: 5 minutes by default

## Performance Benefits

The caching system provides significant performance improvements:

- **Query Performance**: Cached queries typically execute 40-90% faster than uncached queries.
- **Document Retrieval**: Cached documents can be retrieved instantly without indexer overhead.
- **Overall System Performance**: Reduced load on the indexer allows the system to handle more queries.

## Cache Invalidation

Cache invalidation occurs in the following scenarios:

1. **Document Changes**: When a document is added, updated, or removed, related query caches are invalidated.
2. **Ranker Changes**: When the ranker is changed, all query caches are invalidated.
3. **TTL Expiration**: Items automatically expire after their TTL.
4. **Manual Invalidation**: The API allows manually clearing the cache when needed.

## Monitoring

The system provides the following monitoring capabilities:

- **Cache Hit Ratio**: The percentage of cache hits vs. misses.
- **Cache Size**: The number of items in each cache type.
- **Performance Metrics**: Timing comparisons between cached and uncached operations.

## Using the Cache

### Initializing with Caching Enabled

```python
from search_engine.engine import SearchEngine

# Initialize with default Redis settings (localhost:6379)
engine = SearchEngine(enable_cache=True)

# Or with custom Redis settings
engine = SearchEngine(
    enable_cache=True,
    redis_host='redis.example.com',
    redis_port=6380,
    redis_db=1
)
```

### Enabling/Disabling at Runtime

```python
# Disable caching
engine.disable_caching()

# Enable caching
engine.enable_caching()
```

### Clearing the Cache

```python
# Clear all cached items
engine.clear_cache()

# Reset cache metrics
engine.reset_cache_metrics()
```

### Getting Cache Metrics

```python
# Get cache metrics
stats = engine.get_performance_stats()
print(f"Cache hit ratio: {stats['cache']['hit_ratio']:.2%}")
```

## Benchmarking

A benchmarking utility is provided to measure the performance improvement from caching:

```python
from search_engine.engine import SearchEngine
from search_engine.benchmark import SearchBenchmark

# Initialize search engine and benchmark
engine = SearchEngine(enable_cache=True)
benchmark = SearchBenchmark(engine)

# Run the benchmark
results = benchmark.run_full_benchmark(
    doc_count=1000,
    query_count=100,
    iterations=3
)

# Print the results
benchmark.print_summary()
```

## Best Practices

1. **Memory Management**: Monitor Redis memory usage and adjust TTL settings accordingly.
2. **Cache Sizing**: For large datasets, consider using a separate Redis instance with appropriate memory allocation.
3. **Production Deployment**: Use Redis in a production-grade configuration with persistence and replication.
4. **Monitoring**: Implement monitoring to track cache hit ratios and performance metrics.