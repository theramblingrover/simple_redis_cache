import hashlib
import pickle
from functools import wraps
from typing import Callable, Any

def simple_redis_cache(redis_client, ttl: int = 60) -> Callable:
    """
    A decorator to cache function results in Redis using hashed keys and pickled values.
    The `kwargs` are always sorted to guarantee consistent hashes regardless of argument order.

    Args:
        redis_client: The Redis client used for caching.
        ttl: Time-to-live (in seconds) for cached results.

    Returns:
        A decorator for caching function results.
    """
    def outer(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Serialize function arguments, with sorted kwargs for consistency
            sorted_kwargs = tuple(sorted(kwargs.items()))  # Sort kwargs by key => list of tuples
            key_data = pickle.dumps((args, sorted_kwargs))  # Serialize args + sorted kwargs
            key_hash = hashlib.sha256(key_data).hexdigest()  # Create MD5 hash of the serialized data

            # Construct Redis key with function name and hash
            redis_key = f"{func.__name__}:{key_hash}"

            # Check if the result is in the cache
            cached_result = redis_client.get(redis_key)
            if cached_result:
                # Cache hit - unpickle result
                return pickle.loads(cached_result)

            # Cache miss - compute the result and store it in the cache
            result = func(*args, **kwargs)
            redis_client.set(redis_key, pickle.dumps(result), ex=ttl)  # Cache pickled result
            return result

        return wrapper
    return outer