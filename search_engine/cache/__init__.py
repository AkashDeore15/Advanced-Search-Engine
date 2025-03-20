"""
Cache package for the Advanced Search Engine.
Provides Redis-based caching functionality.
"""

from .redis_client import RedisClient
from .cache_manager import CacheManager

__all__ = ['RedisClient', 'CacheManager']
