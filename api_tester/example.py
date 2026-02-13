"""
Example usage of API Client Tester as a library.

Demonstrates how to use the client programmatically in your own scripts.
"""

from api_tester.client import APIClient
from api_tester.models import APIRequest, TestConfig


def example_single_request():
    """Example: Make a single API request."""
    print("=" * 60)
    print("Example 1: Single Request")
    print("=" * 60)

    request = APIRequest(url="https://api.github.com/users/octocat", method="GET")

    config = TestConfig(retry_attempts=3)
    client = APIClient(config)

    response = client.make_request(request)
    print(f"Status: {response.status_code}")
    print(f"Time: {response.elapsed_ms:.2f}ms")
    print(f"Success: {response.success}")
    print()


def example_with_retry():
    """Example: Request with retry configuration."""
    print("=" * 60)
    print("Example 2: Request with Retry")
    print("=" * 60)

    request = APIRequest(
        url="https://httpbin.org/status/500", method="GET"  # Will fail
    )

    config = TestConfig(retry_attempts=3, retry_delay=0.5)
    client = APIClient(config)

    try:
        response = client.make_request(request)
        print(f"Status: {response.status_code}")
        print(f"Error: {response.error}")
    except Exception as e:
        print(f"Failed after retries: {e}")
    print()


def example_benchmark():
    """Example: Benchmark an endpoint."""
    print("=" * 60)
    print("Example 3: Benchmark")
    print("=" * 60)

    request = APIRequest(url="https://httpbin.org/get", method="GET")

    config = TestConfig(retry_attempts=1)
    client = APIClient(config)

    result = client.benchmark(request, num_requests=10)
    print(f"Total Requests: {result.total_requests}")
    print(f"Successful: {result.successful_requests} ({result.success_rate:.1f}%)")
    print(f"Avg Time: {result.avg_time*1000:.2f}ms")
    print(f"Min Time: {result.min_time*1000:.2f}ms")
    print(f"Max Time: {result.max_time*1000:.2f}ms")
    print(f"Throughput: {result.requests_per_second:.2f} req/s")
    print()


def example_rate_limited():
    """Example: Rate-limited requests."""
    print("=" * 60)
    print("Example 4: Rate Limited Requests")
    print("=" * 60)

    request = APIRequest(url="https://httpbin.org/get", method="GET")

    config = TestConfig(retry_attempts=1, rate_limit=2.0)  # 2 requests per second
    client = APIClient(config)

    print("Making 5 requests at 2 req/s...")
    import time

    start = time.time()

    for i in range(5):
        response = client.make_request(request)
        print(f"Request {i+1}: {response.status_code} ({response.elapsed_ms:.0f}ms)")

    elapsed = time.time() - start
    print(f"Total time: {elapsed:.2f}s (should be ~2.5s with rate limiting)")
    print()


def example_post_request():
    """Example: POST request with JSON body."""
    print("=" * 60)
    print("Example 5: POST Request")
    print("=" * 60)

    request = APIRequest(
        url="https://httpbin.org/post",
        method="POST",
        body={"name": "example", "value": 123, "items": [1, 2, 3]},
        headers={"X-Custom-Header": "test"},
    )

    client = APIClient()
    response = client.make_request(request)

    print(f"Status: {response.status_code}")
    print(f"Time: {response.elapsed_ms:.2f}ms")
    print(f"Body preview: {response.body[:200]}...")
    print()


def example_validation():
    """Example: Configuration validation with dataclasses."""
    print("=" * 60)
    print("Example 6: Validation")
    print("=" * 60)

    # This will raise ValueError due to invalid method
    try:
        request = APIRequest(url="https://example.com", method="INVALID")
    except ValueError as e:
        print(f"✓ Caught validation error: {e}")

    # This will raise ValueError due to invalid URL
    try:
        request = APIRequest(url="not-a-valid-url", method="GET")
    except ValueError as e:
        print(f"✓ Caught validation error: {e}")

    # This will raise ValueError due to negative timeout
    try:
        config = TestConfig(retry_attempts=0)
    except ValueError as e:
        print(f"✓ Caught validation error: {e}")

    print()


if __name__ == "__main__":
    example_single_request()
    example_benchmark()
    example_post_request()
    example_rate_limited()
    example_with_retry()
    example_validation()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
