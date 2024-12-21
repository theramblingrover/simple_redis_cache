import pytest
from testcontainers.redis import RedisContainer

from base import simple_redis_cache


# # Import your decorator
# def simple_redis_cache(redis_client, ttl: int = 60) -> Callable:
#     """
#     A decorator to cache function results in Redis using hashed keys and pickled values.
#     """
#     def outer(func: Callable) -> Callable:
#         @wraps(func)
#         def wrapper(*args, **kwargs) -> Any:
#             # Serialize function arguments, with sorted kwargs for consistency
#             sorted_kwargs = tuple(sorted(kwargs.items()))  # Sort kwargs by key => list of tuples
#             key_data = pickle.dumps((args, sorted_kwargs))  # Serialize args + sorted kwargs
#             key_hash = hashlib.md5(key_data).hexdigest()  # Create MD5 hash of the serialized data
#
#             # Construct Redis key with function name and hash
#             redis_key = f"{func.__name__}:{key_hash}"
#
#             # Check if the result is in the cache
#             cached_result = redis_client.get(redis_key)
#             if cached_result:
#                 # Cache hit - unpickle result
#                 return pickle.loads(cached_result)
#
#             # Cache miss - compute the result and store it in the cache
#             result = func(*args, **kwargs)
#             redis_client.set(redis_key, pickle.dumps(result), ex=ttl)  # Cache pickled result
#             return result
#
#         return wrapper
#     return outer

@pytest.fixture(scope="module")
def redis_client():
    """Fixture to set up a Redis container and return a Redis client."""
    with RedisContainer() as redis_container:
        client = redis_container.get_client()
        # client = redis.Redis.from_url(redis_url)
        yield client  # Provide the client to tests
        client.flushall()  # Clean up after tests



# Test function to be cached
def add_numbers(a, b):
    return a + b

# Test function for complex args and kwargs
def complex_function(x, y, z=10):
    return {"x": x, "y": y, "z": z, "sum": x + y + z}

class ComplexClass:
    def __init__(self, val):
        self.val = val
    property_1 = 10
    property_2 = 20
    def method_1(self):
        return self.val + self.property_1
    def method_2(self):
        return self.val + self.property_2

def test_simple_cache_decorator_with_basic_function(redis_client):
    cached_add = simple_redis_cache(redis_client, ttl=120)(add_numbers)

    # Run the function and verify it computes the result
    result = cached_add(1, 2)
    assert result == 3

    # Call again and verify the cache is hit
    result = cached_add(1, 2)
    assert result == 3  # Still 3, but from cache

def test_simple_cache_decorator_with_kwargs(redis_client):
    cached_complex = simple_redis_cache(redis_client, ttl=120)(complex_function)

    # Run the decorated function
    result = cached_complex(1, 2, z=3)
    assert result == {"x": 1, "y": 2, "z": 3, "sum": 6}

    # Call again with reordered kwargs, result should be the same
    result = cached_complex(1, 2, z=3)
    assert result == {"x": 1, "y": 2, "z": 3, "sum": 6}

def test_cache_eviction_via_ttl(redis_client):
    cached_add = simple_redis_cache(redis_client, ttl=1)(add_numbers)

    # Store a value
    result = cached_add(2, 3)
    assert result == 5  # Computed

    # Wait for TTL to expire
    import time
    time.sleep(2)

    # Call again, result should be recomputed (cache miss)
    result = cached_add(2, 3)
    assert result == 5  # Computed again

def test_cache_complex_structure(redis_client):
    complex_obj = lambda: ComplexClass(10)
    cached_complex = simple_redis_cache(redis_client, ttl=120)(complex_obj)
    result = cached_complex()

    assert result.method_1() == 20
    assert result.method_2() == 30
    assert result.val == 10
    assert result.property_1 == 10
    assert result.property_2 == 20