from api_tester.models import APIRequest, TestConfig
from api_tester.client import APIClient

# Configure the client
config = TestConfig(
    retry_attempts=3,
    retry_delay=0.5,
    rate_limit=10.0  # 10 requests per second
)

client = APIClient(config)

# Make a single request
request = APIRequest(
    url="https://api.github.com/users/octocat",
    method="GET"
)

response = client.make_request(request)
print(f"Status: {response.status_code}")
print(f"Time: {response.elapsed_ms:.2f}ms")
print(f"Success: {response.success}")

# Run a benchmark
result = client.benchmark(request, num_requests=100)
print(f"Average time: {result.avg_time*1000:.2f}ms")
print(f"Success rate: {result.success_rate:.1f}%")
print(f"Throughput: {result.requests_per_second:.2f} req/s")
