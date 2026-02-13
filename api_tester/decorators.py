"""
Decorators for API testing.

Reuses patterns from the decorator examples: retry, rate limiting, timing, logging.
"""

import time
from functools import wraps
from typing import Any, Callable


def retry(attempts: int = 3, delay: float = 0.5, backoff: float = 2.0):
    """
    Retry decorator with exponential backoff.

    Args:
        attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff

            raise last_exception

        return wrapper

    return decorator


def rate_limit(requests_per_second: float):
    """
    Rate limiting decorator to control request frequency.

    Args:
        requests_per_second: Maximum requests allowed per second
    """
    min_interval = 1.0 / requests_per_second
    last_called = [0.0]

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)

            last_called[0] = time.time()
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def timeit(fn: Callable) -> Callable:
    """
    Timing decorator that measures function execution time.
    Returns tuple of (result, elapsed_time).
    """

    @wraps(fn)
    def wrapper(*args, **kwargs) -> tuple[Any, float]:
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return result, elapsed

    return wrapper


def log_request(verbose: bool = False):
    """
    Logging decorator for API requests.

    Args:
        verbose: If True, log detailed request/response info
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            if verbose:
                print(
                    f"[REQUEST] {fn.__name__} called with args={args}, kwargs={kwargs}"
                )

            try:
                result = fn(*args, **kwargs)
                if verbose:
                    print(f"[RESPONSE] {fn.__name__} returned successfully")
                return result
            except Exception as e:
                if verbose:
                    print(f"[ERROR] {fn.__name__} raised {type(e).__name__}: {e}")
                raise

        return wrapper

    return decorator


class CallCounter:
    """
    Class-based decorator to count function calls.
    Demonstrates class-based decorator pattern.
    """

    def __init__(self, fn: Callable):
        self.fn = fn
        self.count = 0
        wraps(fn)(self)

    def __call__(self, *args, **kwargs) -> Any:
        self.count += 1
        return self.fn(*args, **kwargs)

    def reset(self):
        """Reset the counter."""
        self.count = 0
