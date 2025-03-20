"""
Redis client wrapper for the Advanced Search Engine.
Provides a high-level interface for Redis operations used in caching.
"""
import json
import logging
from typing import Any, Dict, List, Optional
import redis

logger = logging.getLogger(__name__)


class RedisClient:
    """
    A wrapper around Redis client to provide caching functionality.
    """

    def __init__(self, host='172.31.80.1', port=6379, db=0, *, password=None, \
                 socket_timeout=5, decode_responses=True):
        """

        Initialize the Redis client connection.
        
        Args:
            host (str): Redis server hostname
            port (int): Redis server port
            db (int): Redis database number
            password (str, optional): Redis password
            socket_timeout (int): Socket timeout in seconds
            decode_responses (bool): Whether to decode responses to strings
        """
        self.connection_params = {
            'host': host,
            'port': port,
            'db': db,
            'password': password,
            'socket_timeout': socket_timeout,
            'decode_responses': decode_responses
        }
        self._client = None
        self.connect()

    def connect(self) -> bool:
        """
        Establish a connection to Redis.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self._client = redis.Redis(**self.connection_params)
            # Test the connection with a ping
            self._client.ping()
            logger.info("Successfully connected to Redis")
            return True
        except redis.RedisError as e:
            logger.error("Failed to connect to Redis: %s", e)
            self._client = None
            return False

    @property
    def client(self) -> redis.Redis:
        """
        Get the Redis client instance.
        
        Returns:
            redis.Redis: Redis client instance
        
        Raises:
            ConnectionError: If not connected to Redis
        """
        if self._client is None:
            if not self.connect():
                raise ConnectionError("Not connected to Redis")
        return self._client

    def is_connected(self) -> bool:
        """
        Check if connected to Redis.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if self._client is None:
            return False
        try:
            self._client.ping()
            return True
        except redis.RedisError:
            return False

    def get(self, key: str) -> Any:
        """
        Get a value from Redis.
        
        Args:
            key (str): The key to retrieve
            
        Returns:
            Any: The value or None if not found
        """
        try:
            value = self.client.get(key)
            if value:
                try:
                    # Try to decode JSON
                    return json.loads(value)
                except json.JSONDecodeError:
                    # Return as is if not JSON
                    return value
            return None
        except redis.RedisError as e:
            logger.error("Redis get error: %s", e)
            return None

    def set(self, key: str, value: Any, expiry: Optional[int] = None) -> bool:
        """
        Set a value in Redis with optional expiry.
        
        Args:
            key (str): The key to set
            value (Any): The value to store
            expiry (int, optional): Expiry time in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert non-string values to JSON
            if not isinstance(value, (str, bytes)):
                value = json.dumps(value)
            if expiry:
                return bool(self.client.setex(key, expiry, value))
            return bool(self.client.set(key, value))
        except redis.RedisError as e:
            logger.error("Redis set error: %s", e)
            return False
        except (TypeError, ValueError) as e:
            logger.error("Error serializing value: %s", e)
            return False

    def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.
        
        Args:
            key (str): The key to delete
            
        Returns:
            bool: True if key was deleted, False otherwise
        """
        try:
            return bool(self.client.delete(key))
        except redis.RedisError as e:
            logger.error("Redis delete error: %s", e)
            return False

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.
        
        Args:
            key (str): The key to check
            
        Returns:
            bool: True if key exists, False otherwise
        """
        try:
            return bool(self.client.exists(key))
        except redis.RedisError as e:
            logger.error("Redis exists error: %s", e)
            return False

    def flush_db(self) -> bool:
        """
        Clear all keys in the current database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.flushdb()
            return True
        except redis.RedisError as e:
            logger.error("Redis flushdb error: %s", e)
            return False

    def keys_pattern(self, pattern: str) -> List[str]:
        """
        Get all keys matching a pattern.
        
        Args:
            pattern (str): Pattern to match keys against
            
        Returns:
            List[str]: List of matching keys
        """
        try:
            return self.client.keys(pattern)
        except redis.RedisError as e:
            logger.error("Redis keys error: %s", e)
            return []

    def hset(self, name: str, key: str, value: Any) -> bool:
        """
        Set a hash field to a value.
        
        Args:
            name (str): Name of the hash
            key (str): Key in the hash
            value (Any): Value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert non-string values to JSON
            if not isinstance(value, (str, bytes)):
                value = json.dumps(value)
            return bool(self.client.hset(name, key, value))
        except redis.RedisError as e:
            logger.error("Redis hset error: %s", e)
            return False

    def hget(self, name: str, key: str) -> Any:
        """
        Get the value of a hash field.
        
        Args:
            name (str): Name of the hash
            key (str): Key in the hash
            
        Returns:
            Any: Value of the field or None if it doesn't exist
        """
        try:
            value = self.client.hget(name, key)
            if value:
                try:
                    # Try to decode JSON
                    return json.loads(value)
                except json.JSONDecodeError:
                    # Return as is if not JSON
                    return value
            return None
        except redis.RedisError as e:
            logger.error("Redis hget error: %s", e)
            return None

    def hgetall(self, name: str) -> Dict[str, Any]:
        """
        Get all fields and values in a hash.
        
        Args:
            name (str): Name of the hash
            
        Returns:
            Dict[str, Any]: Dictionary of fields and values
        """
        try:
            result = self.client.hgetall(name)
            # Try to decode JSON values
            decoded = {}
            for k, v in result.items():
                try:
                    decoded[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    decoded[k] = v
            return decoded
        except redis.RedisError as e:
            logger.error("Redis hgetall error: %s", e)
            return {}

    def hdel(self, name: str, key: str) -> bool:
        """
        Delete a hash field.
        
        Args:
            name (str): Name of the hash
            key (str): Key in the hash
            
        Returns:
            bool: True if the field was deleted, False otherwise
        """
        try:
            return bool(self.client.hdel(name, key))
        except redis.RedisError as e:
            logger.error("Redis hdel error: %s", e)
            return False

    def close(self) -> None:
        """Close the Redis connection."""
        if self._client:
            try:
                self._client.close()
                logger.info("Redis connection closed")
            except redis.RedisError as e:
                logger.error("Error closing Redis connection: %s", e)
            finally:
                self._client = None
