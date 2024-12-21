# Mock Redis client
import pickle
import time

from base import simple_redis_cache


class MockRedis:
    def __init__(self):
        self.store = {}
    def get(self, key):
        return self.store.get(key)
    def set(self, key, value, ex=None):
        self.store[key] = value  # Ignoring expiration in this mock.
redis_client = MockRedis()


# Example function to cache
@simple_redis_cache(redis_client, ttl=1)
def example_function(x, y, z):
    print("Function executed!")
    return x + y + z

# Function calls with the same arguments, different kwargs order
print(example_function(1, 2, z=3))  # First call, cache miss
print(example_function(1, 2, z=3))  # Second call, cache hit
time.sleep(2)
print(example_function(1, 2, z=3))  # Another call, but kwargs reordered
print(example_function(1, 2, z=3))  # Same hash!

# Check Redis keys
for key, value in redis_client.store.items():
    print(f"Key: {key}, Value: {pickle.loads(value)}")

class MyClass:
    def __init__(self, val):
        self.val = val

    # Addition method
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return self.val + other
        raise TypeError(f"Unsupported operand type for +: MyClass and {type(other)}")

    # String representation (optional, for better debugging)
    def __repr__(self):
        return f"MyClass(val={self.val})"

example_obj = MyClass(10)

print(example_function(1, 2, z=example_obj))  # Function executed!
print(example_function(1, 2, z=example_obj))  # Cache hit - no execution