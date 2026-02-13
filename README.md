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

## Command Line Options

```sh
python -m api_tester --help
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

## License

[MIT License](LICENSE)

<br>
