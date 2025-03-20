"""
Tests for the RedisClient class.
Note: These tests require a running Redis server.
"""
import pytest
import redis
from search_engine.cache.redis_client import RedisClient


@pytest.fixture
def redis_client():
    """Create and return a RedisClient instance for testing."""
    client = RedisClient(decode_responses=True)
    # Check if Redis is available
    try:
        client.connect()
        # Clean up any previous test data
        client.flush_db()
        yield client
        # Clean up after tests
        client.flush_db()
        client.close()
    except (redis.RedisError, ConnectionError):
        pytest.skip("Redis server not available")


def test_connection(redis_client):
    """Test connection to Redis."""
    assert redis_client.is_connected()
    # Test reconnection
    redis_client.close()
    assert not redis_client.is_connected()
    assert redis_client.connect()
    assert redis_client.is_connected()


def test_set_get(redis_client):
    """Test setting and getting values."""
    # Test with string
    assert redis_client.set("test_key", "test_value")
    assert redis_client.get("test_key") == "test_value"
    # Test with dictionary
    test_dict = {"name": "test", "value": 123}
    assert redis_client.set("test_dict", test_dict)
    assert redis_client.get("test_dict") == test_dict
    # Test with expiry
    assert redis_client.set("expiring_key", "expiring_value", 1)
    assert redis_client.get("expiring_key") == "expiring_value"


def test_delete_exists(redis_client):
    """Test deleting keys and checking existence."""
    # Set a key
    redis_client.set("test_key", "test_value")
    # Check existence
    assert redis_client.exists("test_key")
    assert not redis_client.exists("nonexistent_key")
    # Delete the key
    assert redis_client.delete("test_key")
    assert not redis_client.exists("test_key")
    # Try deleting a non-existent key
    assert not redis_client.delete("nonexistent_key")


def test_keys_pattern(redis_client):
    """Test getting keys matching a pattern."""
    # Set some keys
    redis_client.set("test:1", "value1")
    redis_client.set("test:2", "value2")
    redis_client.set("other:1", "value3")
    # Get keys by pattern
    test_keys = redis_client.keys_pattern("test:*")
    assert len(test_keys) == 2
    assert "test:1" in test_keys
    assert "test:2" in test_keys
    # Get all keys
    all_keys = redis_client.keys_pattern("*")
    assert len(all_keys) == 3


def test_hash_operations(redis_client):
    """Test hash operations."""
    # Set hash fields
    assert redis_client.hset("test_hash", "field1", "value1")
    assert redis_client.hset("test_hash", "field2", 123)
    # Get hash fields
    assert redis_client.hget("test_hash", "field1") == "value1"
    assert redis_client.hget("test_hash", "field2") == 123
    # Get all hash fields
    hash_data = redis_client.hgetall("test_hash")
    assert len(hash_data) == 2
    assert hash_data["field1"] == "value1"
    assert hash_data["field2"] == 123
    # Delete hash field
    assert redis_client.hdel("test_hash", "field1")
    assert redis_client.hget("test_hash", "field1") is None
    # Get non-existent hash
    assert redis_client.hgetall("nonexistent_hash") == {}


def test_flush_db(redis_client):
    """Test flushing the database."""
    # Set some keys
    redis_client.set("key1", "value1")
    redis_client.set("key2", "value2")
    # Flush the database
    assert redis_client.flush_db()
    # Check that keys are gone
    assert not redis_client.exists("key1")
    assert not redis_client.exists("key2")
