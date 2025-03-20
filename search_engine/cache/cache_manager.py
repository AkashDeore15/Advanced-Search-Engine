"""
Cache Manager module for the Advanced Search Engine.
Implements caching strategies for query results and documents.
"""
import hashlib
import logging
import time
from typing import Any, Dict, List, Optional

from .redis_client import RedisClient

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages caching for the search engine using Redis.
    Implements strategies for caching both documents and query results.
    """
    # Cache key prefixes
    DOC_PREFIX = "doc:"
    QUERY_PREFIX = "query:"
    STATS_PREFIX = "stats:"
    # Default TTL values (in seconds)
    DEFAULT_DOC_TTL = 86400  # 24 hours
    DEFAULT_QUERY_TTL = 3600  # 1 hour
    DEFAULT_STATS_TTL = 300  # 5 minutes

    def __init__(self, redis_client: Optional[RedisClient] = None,\
                 doc_ttl: int = DEFAULT_DOC_TTL,\
                 query_ttl: int = DEFAULT_QUERY_TTL,\
                 stats_ttl: int = DEFAULT_STATS_TTL):
        """
        Initialize the CacheManager.
        
        Args:
            redis_client (RedisClient, optional): Redis client instance.
                If None, a new client will be created with default settings.
            doc_ttl (int): Time-to-live for document cache entries in seconds
            query_ttl (int): Time-to-live for query cache entries in seconds
            stats_ttl (int): Time-to-live for stats cache entries in seconds
        """
        self.redis = redis_client or RedisClient()
        self.doc_ttl = doc_ttl
        self.query_ttl = query_ttl
        self.stats_ttl = stats_ttl
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_enabled = True

    def enable_cache(self) -> None:
        """Enable caching."""
        self.cache_enabled = True
        logger.info("Cache enabled")

    def disable_cache(self) -> None:
        """Disable caching."""
        self.cache_enabled = False
        logger.info("Cache disabled")

    def is_cache_enabled(self) -> bool:
        """
        Check if caching is enabled.
        
        Returns:
            bool: True if caching is enabled, False otherwise
        """
        return self.cache_enabled

    def _generate_query_key(self, query: str, top_n: int = 10) -> str:
        """
        Generate a Redis key for a query.
        
        Args:
            query (str): The search query
            top_n (int): Maximum number of results
            
        Returns:
            str: Redis key for the query
        """
        # Normalize the query (lowercase, trim whitespace)
        normalized_query = query.lower().strip()
        # Create a hash of the query and top_n
        query_hash = hashlib.md5(f"{normalized_query}:{top_n}".encode()).hexdigest()
        return f"{self.QUERY_PREFIX}{query_hash}"

    def _generate_doc_key(self, doc_id: str) -> str:
        """
        Generate a Redis key for a document.
        
        Args:
            doc_id (str): Document ID
            
        Returns:
            str: Redis key for the document
        """
        return f"{self.DOC_PREFIX}{doc_id}"

    def cache_document(self, doc_id: str, document_data: Dict[str, Any]) -> bool:
        """
        Cache a document.
        
        Args:
            doc_id (str): Document ID
            document_data (dict): Document data to cache
            
        Returns:
            bool: True if successfully cached, False otherwise
        """
        if not self.cache_enabled:
            return False
        key = self._generate_doc_key(doc_id)
        return self.redis.set(key, document_data, self.doc_ttl)

    def get_cached_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document from the cache.
        
        Args:
            doc_id (str): Document ID
            
        Returns:
            dict: Document data if found, None otherwise
        """
        if not self.cache_enabled:
            return None
        key = self._generate_doc_key(doc_id)
        result = self.redis.get(key)
        if result:
            self.cache_hits += 1
            logger.debug("Cache hit for document %s", doc_id)
            return result
        self.cache_misses += 1
        logger.debug("Cache miss for document %s", doc_id)
        return None

    def cache_query_results(self, query: str, results: List[Dict[str, Any]],\
                            top_n: int = 10) -> bool:
        """
        Cache query results.
        
        Args:
            query (str): The search query
            results (list): Search results to cache
            top_n (int): Maximum number of results
            
        Returns:
            bool: True if successfully cached, False otherwise
        """
        if not self.cache_enabled:
            return False
        key = self._generate_query_key(query, top_n)
        # Create cache entry with timestamp
        cache_entry = {
            'results': results,
            'timestamp': time.time(),
            'query': query,
            'top_n': top_n
        }
        return self.redis.set(key, cache_entry, self.query_ttl)

    def get_cached_query_results(self, query: str, top_n: int = 10) ->\
          Optional[List[Dict[str, Any]]]:
        """
        Retrieve query results from the cache.
        
        Args:
            query (str): The search query
            top_n (int): Maximum number of results
            
        Returns:
            list: Search results if found, None otherwise
        """
        if not self.cache_enabled:
            return None
        key = self._generate_query_key(query, top_n)
        cache_entry = self.redis.get(key)
        if cache_entry and isinstance(cache_entry, dict) and 'results' in cache_entry:
            self.cache_hits += 1
            logger.debug("Cache hit for query: %s", query)
            return cache_entry['results']
        self.cache_misses += 1
        logger.debug("Cache miss for query: %s", query)
        return None

    def invalidate_document(self, doc_id: str) -> bool:
        """
        Invalidate a cached document.
        
        Args:
            doc_id (str): Document ID
            
        Returns:
            bool: True if invalidated, False otherwise
        """
        key = self._generate_doc_key(doc_id)
        return self.redis.delete(key)

    def invalidate_all_documents(self) -> bool:
        """
        Invalidate all cached documents.
        
        Returns:
            bool: True if invalidated, False otherwise
        """
        keys = self.redis.keys_pattern("%s*", self.DOC_PREFIX)
        if not keys:
            return True
        for key in keys:
            self.redis.delete(key)
        return True

    def invalidate_all_queries(self) -> bool:
        """
        Invalidate all cached queries.
        
        Returns:
            bool: True if invalidated, False otherwise
        """
        keys = self.redis.keys_pattern("%s*", self.QUERY_PREFIX)
        if not keys:
            return True
        for key in keys:
            self.redis.delete(key)
        return True

    def invalidate_all(self) -> bool:
        """
        Invalidate all cached items.
        
        Returns:
            bool: True if invalidated, False otherwise
        """
        return (self.invalidate_all_documents() and self.invalidate_all_queries())

    def cache_stats(self, stats_data: Dict[str, Any]) -> bool:
        """
        Cache search engine statistics.
        
        Args:
            stats_data (dict): Statistics data to cache
            
        Returns:
            bool: True if successfully cached, False otherwise
        """
        if not self.cache_enabled:
            return False
        key = "%s engine_stats", self.STATS_PREFIX
        return self.redis.set(key, stats_data, self.stats_ttl)

    def get_cached_stats(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached search engine statistics.
        
        Returns:
            dict: Statistics data if found, None otherwise
        """
        if not self.cache_enabled:
            return None
        key = "%s engine_stats", self.STATS_PREFIX
        return self.redis.get(key)

    def get_cache_metrics(self) -> Dict[str, Any]:
        """
        Get cache performance metrics.
        
        Returns:
            dict: Cache metrics including hits, misses and hit ratio
        """
        total = self.cache_hits + self.cache_misses
        hit_ratio = self.cache_hits / total if total > 0 else 0
        return {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'total': total,
            'hit_ratio': hit_ratio,
            'cache_enabled': self.cache_enabled
        }

    def reset_metrics(self) -> None:
        """Reset cache metrics."""
        self.cache_hits = 0
        self.cache_misses = 0

    def close(self) -> None:
        """Close Redis connection."""
        self.redis.close()
