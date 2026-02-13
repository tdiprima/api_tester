"""
Command-line interface for API Client Tester.
"""

import argparse
import json
import sys
from typing import Optional

from .models import APIRequest, TestConfig
from .client import APIClient


def format_response(response, verbose: bool = False):
    """Format API response for display."""
    status_icon = "✓" if response.success else "✗"
    status_color = "\033[92m" if response.success else "\033[91m"
    reset_color = "\033[0m"

    print(f"\n{status_color}{status_icon} Status: {response.status_code}{reset_color}")
    print(f"⏱  Time: {response.elapsed_ms:.2f}ms")

    if response.error:
        print(f"❌ Error: {response.error}")

    if verbose:
        print(f"\n📋 Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        print(f"\n📄 Body:")
        try:
            parsed = json.loads(response.body)
            print(json.dumps(parsed, indent=2))
        except json.JSONDecodeError:
            print(response.body[:500])
            if len(response.body) > 500:
                print(f"... ({len(response.body) - 500} more characters)")


def format_benchmark(result):
    """Format benchmark results for display."""
    print(f"\n{'='*60}")
    print(f"🎯 BENCHMARK RESULTS: {result.url}")
    print(f"{'='*60}")
    print(f"Total Requests:     {result.total_requests}")
    print(f"Successful:         {result.successful_requests} ({result.success_rate:.1f}%)")
    print(f"Failed:             {result.failed_requests}")
    print(f"\n⏱  TIMING STATISTICS")
    print(f"Average:            {result.avg_time*1000:.2f}ms")
    print(f"Median:             {result.median_time*1000:.2f}ms")
    print(f"Min:                {result.min_time*1000:.2f}ms")
    print(f"Max:                {result.max_time*1000:.2f}ms")
    print(f"\n🚀 THROUGHPUT")
    print(f"Total Duration:     {result.total_duration:.2f}s")
    print(f"Requests/Second:    {result.requests_per_second:.2f}")
    print(f"{'='*60}\n")


def parse_headers(header_strings: Optional[list]) -> dict:
    """Parse header strings in format 'Key: Value'."""
    headers = {}
    if header_strings:
        for h in header_strings:
            if ':' in h:
                key, value = h.split(':', 1)
                headers[key.strip()] = value.strip()
    return headers


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="API Client Tester - Test and benchmark HTTP APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  api-test https://api.github.com/users/octocat
  api-test https://httpbin.org/get --verbose
  api-test https://api.example.com --benchmark 100
  api-test https://httpbin.org/post -X POST -d '{"key":"value"}'
  api-test https://api.example.com --retry 5 --rate-limit 10
        """
    )

    parser.add_argument('url', help='URL to test')
    parser.add_argument('-X', '--method', default='GET',
                       help='HTTP method (default: GET)')
    parser.add_argument('-H', '--header', action='append', dest='headers',
                       help='Add header (format: "Key: Value")')
    parser.add_argument('-d', '--data', help='Request body as JSON string')
    parser.add_argument('-t', '--timeout', type=float, default=30.0,
                       help='Request timeout in seconds (default: 30)')

    parser.add_argument('--retry', type=int, default=3,
                       help='Number of retry attempts (default: 3)')
    parser.add_argument('--retry-delay', type=float, default=0.5,
                       help='Initial retry delay in seconds (default: 0.5)')
    parser.add_argument('--rate-limit', type=float,
                       help='Rate limit in requests per second')

    parser.add_argument('--benchmark', type=int, metavar='N',
                       help='Run benchmark with N requests')
    parser.add_argument('--no-verify-ssl', action='store_true',
                       help='Disable SSL certificate verification')

    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')

    args = parser.parse_args()

    try:
        # Build request
        headers = parse_headers(args.headers)
        body = json.loads(args.data) if args.data else None

        request = APIRequest(
            url=args.url,
            method=args.method,
            headers=headers,
            body=body,
            timeout=args.timeout
        )

        # Build config
        config = TestConfig(
            retry_attempts=args.retry,
            retry_delay=args.retry_delay,
            rate_limit=args.rate_limit,
            verify_ssl=not args.no_verify_ssl
        )

        # Create client
        client = APIClient(config)

        # Execute request(s)
        if args.benchmark:
            print(f"🚀 Benchmarking {args.url} with {args.benchmark} requests...")
            result = client.benchmark(request, args.benchmark)

            if args.json:
                output = {
                    'url': result.url,
                    'total_requests': result.total_requests,
                    'successful_requests': result.successful_requests,
                    'failed_requests': result.failed_requests,
                    'success_rate': result.success_rate,
                    'avg_time_ms': result.avg_time * 1000,
                    'median_time_ms': result.median_time * 1000,
                    'min_time_ms': result.min_time * 1000,
                    'max_time_ms': result.max_time * 1000,
                    'total_duration_s': result.total_duration,
                    'requests_per_second': result.requests_per_second
                }
                print(json.dumps(output, indent=2))
            else:
                format_benchmark(result)
        else:
            if not args.json:
                print(f"🌐 Testing {args.url}...")
            response = client.make_request(request)

            if args.json:
                output = {
                    'status_code': response.status_code,
                    'success': response.success,
                    'elapsed_ms': response.elapsed_ms,
                    'headers': response.headers,
                    'body': response.body,
                    'error': response.error
                }
                print(json.dumps(output, indent=2))
            else:
                format_response(response, args.verbose)

    except ValueError as e:
        print(f"❌ Validation Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
