"""
Data models for API testing using dataclasses.

Demonstrates: frozen dataclasses, post_init validation, default_factory, field customization.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class APIRequest:
    """Configuration for an API request."""

    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    timeout: float = 30.0

    def __post_init__(self):
        """Validate request configuration."""
        self.method = self.method.upper()
        if self.method not in [
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "HEAD",
            "OPTIONS",
        ]:
            raise ValueError(f"Invalid HTTP method: {self.method}")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if not self.url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")


@dataclass(frozen=True)
class APIResponse:
    """Immutable response from an API request."""

    status_code: int
    headers: Dict[str, str]
    body: str
    elapsed_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Check if request was successful."""
        return 200 <= self.status_code < 300 and self.error is None

    @property
    def elapsed_ms(self) -> float:
        """Return elapsed time in milliseconds."""
        return self.elapsed_time * 1000


@dataclass
class TestConfig:
    """Configuration for API testing behavior."""

    retry_attempts: int = 3
    retry_delay: float = 0.5
    rate_limit: Optional[float] = None  # requests per second
    cache_responses: bool = False
    verify_ssl: bool = True
    follow_redirects: bool = True

    def __post_init__(self):
        """Validate test configuration."""
        if self.retry_attempts < 1:
            raise ValueError("retry_attempts must be at least 1")
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")
        if self.rate_limit is not None and self.rate_limit <= 0:
            raise ValueError("rate_limit must be positive")


@dataclass(frozen=True)
class BenchmarkResult:
    """Immutable results from benchmarking an endpoint."""

    url: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_time: float
    min_time: float
    max_time: float
    median_time: float
    total_duration: float
    responses: List[APIResponse] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def requests_per_second(self) -> float:
        """Calculate throughput."""
        if self.total_duration == 0:
            return 0.0
        return self.total_requests / self.total_duration
