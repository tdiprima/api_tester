# API Client Tester

A practical CLI tool for testing and benchmarking HTTP APIs. Built to showcase Python decorators, dataclasses, and functools in action.

## Features

- 🔄 **Automatic retry** with exponential backoff for flaky endpoints
- 🚦 **Rate limiting** to control request frequency
- ⏱️ **Performance timing** for all requests
- 📊 **Benchmark mode** with detailed statistics
- 🎯 **Response validation** and error handling
- 📝 **Flexible output** formats (pretty print or JSON)
- 🔒 **SSL verification** control
- 📈 **Request counting** and tracking

## Patterns Demonstrated

### Decorators
- `@retry` - Exponential backoff for failed requests
- `@rate_limit` - Control request frequency
- `@timeit` - Measure execution time
- `@log_request` - Request/response logging
- `CallCounter` - Class-based decorator for counting calls

### Dataclasses
- `APIRequest` - Request configuration with `__post_init__` validation
- `APIResponse` - Immutable (frozen) response data
- `TestConfig` - Test configuration with validation
- `BenchmarkResult` - Frozen results with computed properties

## Usage

### As a Python module

```bash
# Simple GET request
python -m api_tester https://api.github.com/users/octocat

# Verbose output
python -m api_tester https://httpbin.org/get --verbose

# POST request with JSON body
python -m api_tester https://httpbin.org/post -X POST -d '{"name":"test"}'

# With custom headers
python -m api_tester https://api.example.com -H "Authorization: Bearer token"

# Benchmark mode (100 requests)
python -m api_tester https://api.example.com --benchmark 100

# With retry and rate limiting
python -m api_tester https://flaky-api.com --retry 5 --rate-limit 10

# JSON output for scripting
python -m api_tester https://api.example.com --json

# Disable SSL verification (use with caution!)
python -m api_tester https://self-signed.badssl.com --no-verify-ssl
```

### As a Python library

```python
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
```

## Command Line Options

```
positional arguments:
  url                   URL to test

optional arguments:
  -h, --help            show this help message and exit
  -X METHOD, --method METHOD
                        HTTP method (default: GET)
  -H HEADER, --header HEADER
                        Add header (format: "Key: Value")
  -d DATA, --data DATA  Request body as JSON string
  -t TIMEOUT, --timeout TIMEOUT
                        Request timeout in seconds (default: 30)
  --retry RETRY         Number of retry attempts (default: 3)
  --retry-delay RETRY_DELAY
                        Initial retry delay in seconds (default: 0.5)
  --rate-limit RATE_LIMIT
                        Rate limit in requests per second
  --benchmark N         Run benchmark with N requests
  --no-verify-ssl       Disable SSL certificate verification
  -v, --verbose         Verbose output
  --json                Output results as JSON
```

## Examples

### Test a public API
```bash
python -m api_tester https://api.github.com/users/octocat
```

### Benchmark an endpoint
```bash
python -m api_tester https://httpbin.org/delay/1 --benchmark 10
```

### Test with retry on flaky endpoint
```bash
python -m api_tester https://httpbin.org/status/500 --retry 5
```

### Rate-limited requests
```bash
python -m api_tester https://api.example.com --rate-limit 5 --benchmark 20
```

## Architecture

```
api_tester/
├── __init__.py       # Package initialization
├── __main__.py       # Module entry point
├── models.py         # Dataclass models (Request, Response, Config, Results)
├── decorators.py     # Decorator implementations
├── client.py         # HTTP client with decorator application
└── cli.py            # Command-line interface
```

## Design Principles

1. **Immutability**: Response and result objects are frozen dataclasses
2. **Validation**: Configuration validated in `__post_init__`
3. **Composability**: Decorators can be stacked and combined
4. **Type Safety**: Full type hints throughout
5. **Single Responsibility**: Each module has a clear purpose
6. **Practical**: Built to solve real problems, not just demonstrate patterns

## Dependencies

None! Uses only Python standard library:

- `urllib` for HTTP requests
- `dataclasses` for data models
- `functools` for decorator utilities
- `statistics` for benchmark calculations
- `argparse` for CLI parsing

## License

MIT License - See LICENSE file in repository root
