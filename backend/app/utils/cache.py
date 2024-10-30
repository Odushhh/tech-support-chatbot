import os
import time
from typing import Any, Callable, Dict, Optional, Union
from functools import wraps
import json
import hashlib
import logging
from redis import Redis
import redis
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

r = redis.Redis(
  host='redis-19722.c11.us-east-1-3.ec2.redns.redis-cloud.com',
  port=19722,
  password='*******')

class Cache:
    def __init__(self):
        self.redis_client = Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            db=os.getenv("REDIS_DB"),
            password=os.getenv("REDIS_PASSWORD")
        )

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """
        Set a key-value pair in the cache
        """
        try:
            serialized_value = json.dumps(value)
            return self.redis_client.setex(key, expire, serialized_value)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {str(e)}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache
        """
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {str(e)}")
            return None

    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache
        """
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {str(e)}")
            return False

    def clear(self) -> bool:
        """
        Clear all keys from the cache
        """
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False

    def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a key's value
        """
        try:
            return self.redis_client.incr(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {str(e)}")
            return 0

    def decrement(self, key: str, amount: int = 1) -> int:
        """
        Decrement a key's value
        """
        try:
            return self.redis_client.decr(key, amount)
        except Exception as e:
            logger.error(f"Error decrementing cache key {key}: {str(e)}")
            return 0

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache
        """
        try:
            return self.redis_client.exists(key)
        except Exception as e:
            logger.error(f"Error checking existence of cache key {key}: {str(e)}")
            return False

    def ttl(self, key: str) -> int:
        """
        Get the time-to-live for a key
        """
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL for cache key {key}: {str(e)}")
            return -2  # -2 indicates key does not exist

    def keys(self, pattern: str = "*") -> list:
        """
        Get all keys matching a pattern
        """
        try:
            return [key.decode() for key in self.redis_client.keys(pattern)]
        except Exception as e:
            logger.error(f"Error getting keys with pattern {pattern}: {str(e)}")
            return []

# Initialize the cache
cache = Cache()

def cached(expire: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache function results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a unique cache key based on the function name, arguments, and key prefix
            key_parts = [key_prefix, func.__name__] + [str(arg) for arg in args]
            key_parts += [f"{k}:{v}" for k, v in sorted(kwargs.items())]
            key = hashlib.md5(":".join(key_parts).encode()).hexdigest()

            # Try to get the result from cache
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result

            # If not in cache, call the function and cache the result
            result = func(*args, **kwargs)
            cache.set(key, result, expire)
            return result
        return wrapper
    return decorator

def cache_clear_prefix(prefix: str):
    """
    Clear all cache keys with a given prefix
    """
    keys = cache.keys(f"{prefix}*")
    for key in keys:
        cache.delete(key)

def rate_limit(limit: int, period: int):
    """
    Decorator to implement rate limiting
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"rate_limit:{func.__name__}"
            current = cache.get(key) or 0
            if current >= limit:
                raise Exception("Rate limit exceeded")
            cache.increment(key)
            if cache.ttl(key) == -1:  # Key exists but has no expiry
                cache.expire(key, period)
            return func(*args, **kwargs)
        return wrapper
    return decorator

class CacheManager:
    """
    A class to manage different cache regions
    """
    def __init__(self):
        self.regions: Dict[str, Dict[str, Union[int, str]]] = {}

    def create_region(self, name: str, expire: int = 3600, key_prefix: str = ""):
        """
        Create a new cache region
        """
        self.regions[name] = {"expire": expire, "key_prefix": key_prefix}

    def cached_region(self, region_name: str):
        """
        Decorator to cache function results in a specific region
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if region_name not in self.regions:
                    raise ValueError(f"Cache region '{region_name}' does not exist")
                region = self.regions[region_name]
                return cached(expire=region["expire"], key_prefix=region["key_prefix"])(func)(*args, **kwargs)
            return wrapper
        return decorator

    def clear_region(self, region_name: str):
        """
        Clear all cache keys in a specific region
        """
        if region_name not in self.regions:
            raise ValueError(f"Cache region '{region_name}' does not exist")
        region = self.regions[region_name]
        cache_clear_prefix(region["key_prefix"])

# Initialize the cache manager
cache_manager = CacheManager()

# Example usage
if __name__ == "__main__":
    # Basic cache usage
    cache.set("example_key", "example_value", 60)
    print(cache.get("example_key"))

    # Using the cached decorator
    @cached(expire=300, key_prefix="example")
    def slow_function(x, y):
        time.sleep(2)  # Simulate a slow operation
        return x + y

    print(slow_function(2, 3))  # This will take 2 seconds
    print(slow_function(2, 3))  # This will be instant (cached)

    # Using rate limiting
    @rate_limit(limit=5, period=60)
    def limited_function():
        return "Hello, World!"

    for _ in range(6):
        try:
            print(limited_function())
        except Exception as e:
            print(str(e))

    # Using cache regions
    cache_manager.create_region("short_term", expire=60, key_prefix="short")
    cache_manager.create_region("long_term", expire=3600, key_prefix="long")

    @cache_manager.cached_region("short_term")
    def short_lived_function():
        return "I'll be cached for 60 seconds"

    @cache_manager.cached_region("long_term")
    def long_lived_function():
        return "I'll be cached for 1 hour"

    print(short_lived_function())
    print(long_lived_function())

    # Clear a specific region
    cache_manager.clear_region("short_term")

