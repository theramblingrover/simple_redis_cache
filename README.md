# Simple Redis Cache Decorator

This repository demonstrates a Python decorator `simple_redis_cache` that provides caching for function results using a Redis backend. The decorator uses hashed and pickled keys and values to store results, ensuring efficient caching, even for complex function arguments like `kwargs`. 

This README provides an overview of how to use `simple_redis_cache`, a mock implementation of Redis for testing, and tips for extending the decorator for real-world scenarios.

---

## Features
- **Redis Backend**: Uses Redis (or a mock Redis client) to store cache results.
- **Hash-Based Key Management**: Ensures unique, consistent Redis keys based on function arguments (even when `kwargs` are unordered).
- **Pickle Serialization**: Handles complex Python objects seamlessly for caching.
- **TTL Support**: Each cached result has a configurable expiry (time-to-live).
- **Robust Functionality**: Works with positional, keyword arguments, and complex objects.
- **Mocks for Testing**: Provides a mock Redis client for testing environments without requiring an actual Redis server.

---

## How It Works

The `simple_redis_cache` decorator:
1. Serializes a function’s input arguments (`args` and `kwargs`).
2. Converts `kwargs` into a sorted order for consistency.
3. Generates a unique key using the MD5 hash of serialized arguments.
4. Checks Redis for cached results using the key:
   - If a result exists, the cached value is returned.
   - If a result does not exist, the function is executed, and the result is cached in Redis with a specified TTL (or default of 60 seconds).

---

## Usage

### 1. Prerequisites

To use the library, you need:
- A Python Redis-compatible client such as `redis-py` (`pip install redis`).
- Access to a running Redis server or a mock Redis client for testing purposes.
- Python 3.9+.

---

### 2. Installation

Clone the repository and install the dependencies.

For production use:
```bash
pip install redis
```

For testing with mocks:
```bash
pip install pytest testcontainers
```

---

### 3. Example Usage

Here's an example showcasing the decorator's functionality:

```python
# Redis (or mock Redis) client
class MockRedis:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ex=None):
        self.store[key] = value

# Initialize Redis client
redis_client = MockRedis()

# Example function to be cached
@simple_redis_cache(redis_client, ttl=10)
def compute_sum(x, y, z=5):
    print("Function executed!")
    return x + y + z

# Function calls
print(compute_sum(1, 2, z=3))  # First call computes and caches
print(compute_sum(1, 2, z=3))  # Second call retrieves from cache

```

**Expected Output**:
```plaintext
Function executed!
6
6
```

---

### 4. Advanced Caching with Complex Input Arguments

The decorator is robust for functions with complex input types, such as custom objects. Here's an example:

```python
class CustomObject:
    def __init__(self, value):
        self.value = value

complex_obj = CustomObject(20)

# Function with complex arguments
@simple_redis_cache(redis_client, ttl=10)
def compute_with_complex_input(x, y, obj):
    print("Complex Function executed!")
    return obj.value + x + y

print(compute_with_complex_input(1, 2, obj=complex_obj))  # Cache miss
print(compute_with_complex_input(1, 2, obj=complex_obj))  # Cache hit
```

**Output**:
```plaintext
Complex Function executed!
23
23
```

---

### 5. Tests with `pytest` and `testcontainers`

You can easily test your caching logic using `pytest` and `testcontainers` to spin up an isolated Redis container for your tests.

#### Example Test Suite

```python
import pytest
from testcontainers.redis import RedisContainer
import redis
from base import simple_redis_cache

@pytest.fixture(scope="module")
def redis_client():
    """Fixture to create a Redis container."""
    with RedisContainer() as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(6379)
        
        client = redis.Redis(host=host, port=port)
        yield client

def test_simple_cache(redis_client):
    @simple_redis_cache(redis_client)
    def example_function(x, y):
        return x + y

    # Cache miss
    assert example_function(1, 2) == 3
    
    # Cache hit
    assert example_function(1, 2) == 3  # Retrieved from Redis
```

Run the test with:
```bash
pytest
```

---

## Notes & Best Practices

### 1. Security
- **Use Pickle Cautiously**: Pickle is a powerful serialization tool but can execute arbitrary code if untrusted data is deserialized. Ensure that Redis is in a trusted environment to avoid malicious code injection.
- **Secure Redis**: Deploy Redis with proper authentication and access controls in production.

---

## Limitations

1. **Large Objects**:
   Redis may not be suitable for extremely large objects due to memory constraints. Test the maximum size of your serialized data before deploying.

2. **Pickle Dependency**:
   If your application needs strict security, avoid using `pickle` and rely on a safer serialization mechanism like JSON (but only for objects compatible with JSON).

3. **TTL Handling**:
   Expired keys are evicted immediately upon their TTL expiration. For long-lived caches, ensure the TTL is appropriately configured based on function usage.

---

## Next Steps

You can further extend this library by:
1. **Using `json` Instead of `pickle`**: For stricter security or lighter object serialization.
2. **Adding Asynchronous Support**: Adapting the decorator to work with asynchronous functions.
3. **Distributed Caching**: Incorporating libraries like `aioredis` for multi-node caching setups.

---

## Contributing

Feel free to open an issue or submit a pull request for improvements, features, or bug fixes. Contributions are always welcome!

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
