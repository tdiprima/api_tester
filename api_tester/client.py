"""
HTTP client for API testing with decorator support.

Combines decorators and dataclasses for a practical API testing tool.
"""

import json
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import List, Optional

from .decorators import CallCounter, rate_limit, retry
from .models import APIRequest, APIResponse, BenchmarkResult, TestConfig


class APIClient:
    """HTTP client with support for retry, rate limiting, and caching."""

    def __init__(self, config: Optional[TestConfig] = None):
        """
        Initialize API client with test configuration.

        Args:
            config: Test configuration (uses defaults if not provided)
        """
        self.config = config or TestConfig()
        self._call_counter = CallCounter(self._make_request_internal)

    def _make_request_internal(self, request: APIRequest) -> APIResponse:
        """
        Internal method to make HTTP request.

        Args:
            request: API request configuration

        Returns:
            APIResponse with results
        """
        start_time = time.perf_counter()
        error_msg = None

        try:
            # Prepare request
            data = None
            if request.body:
                data = json.dumps(request.body).encode("utf-8")
                request.headers.setdefault("Content-Type", "application/json")

            # Build URL with query parameters
            url = request.url
            if request.params:
                params = urllib.parse.urlencode(request.params)
                url = f"{url}?{params}"

            # Create request object
            req = urllib.request.Request(
                url, data=data, headers=request.headers, method=request.method
            )

            # Make request
            with urllib.request.urlopen(
                req,
                timeout=request.timeout,
                context=(
                    None if self.config.verify_ssl else self._get_unverified_context()
                ),
            ) as response:
                body = response.read().decode("utf-8")
                status_code = response.status
                headers = dict(response.headers)

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8") if e.fp else ""
            status_code = e.code
            headers = dict(e.headers) if e.headers else {}
            error_msg = f"HTTP {e.code}: {e.reason}"

        except urllib.error.URLError as e:
            body = ""
            status_code = 0
            headers = {}
            error_msg = f"URL Error: {e.reason}"

        except Exception as e:
            body = ""
            status_code = 0
            headers = {}
            error_msg = f"{type(e).__name__}: {str(e)}"

        elapsed_time = time.perf_counter() - start_time

        return APIResponse(
            status_code=status_code,
            headers=headers,
            body=body,
            elapsed_time=elapsed_time,
            timestamp=datetime.now(),
            error=error_msg,
        )

    @staticmethod
    def _get_unverified_context():
        """Create SSL context that doesn't verify certificates."""
        import ssl

        return ssl._create_unverified_context()

    def make_request(self, request: APIRequest) -> APIResponse:
        """
        Make a single API request with configured retry and rate limiting.

        Args:
            request: API request configuration

        Returns:
            APIResponse with results
        """
        # Build decorated function based on config
        fn = self._call_counter

        # Apply retry decorator if configured
        if self.config.retry_attempts > 1:
            fn = retry(
                attempts=self.config.retry_attempts, delay=self.config.retry_delay
            )(fn)

        # Apply rate limiting if configured
        if self.config.rate_limit:
            fn = rate_limit(self.config.rate_limit)(fn)

        return fn(request)

    def benchmark(self, request: APIRequest, num_requests: int = 10) -> BenchmarkResult:
        """
        Benchmark an endpoint by making multiple requests.

        Args:
            request: API request configuration
            num_requests: Number of requests to make

        Returns:
            BenchmarkResult with aggregated statistics
        """
        responses: List[APIResponse] = []
        start_time = time.perf_counter()

        for _ in range(num_requests):
            response = self.make_request(request)
            responses.append(response)

        total_duration = time.perf_counter() - start_time

        # Calculate statistics
        successful = [r for r in responses if r.success]
        failed = [r for r in responses if not r.success]

        times = [r.elapsed_time for r in responses]
        avg_time = statistics.mean(times) if times else 0.0
        min_time = min(times) if times else 0.0
        max_time = max(times) if times else 0.0
        median_time = statistics.median(times) if times else 0.0

        return BenchmarkResult(
            url=request.url,
            total_requests=num_requests,
            successful_requests=len(successful),
            failed_requests=len(failed),
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            total_duration=total_duration,
            responses=responses,
        )

    @property
    def call_count(self) -> int:
        """Get total number of requests made."""
        return self._call_counter.count

    def reset_counter(self):
        """Reset the request counter."""
        self._call_counter.reset()
