"""
SEC EDGAR API utilities for rate limiting and request management.

This module provides utilities for managing HTTP requests to the SEC EDGAR API,
including rate limiting to comply with SEC's fair access policy and handling
of retry scenarios when rate limits are exceeded.

Attributes:
    user_agent: The User-Agent string for SEC EDGAR requests, read from
        DATAMULE_SEC_USER_AGENT environment variable or defaulting to a placeholder.
    headers: Default HTTP headers for SEC EDGAR requests, including User-Agent.
"""

import asyncio
import time
from collections import deque
from types import TracebackType
from typing import Optional, Tuple, Type
import os


class RetryException(Exception):
    """
    Exception raised when an SEC EDGAR request should be retried.

    This exception is raised when the SEC's rate limit is exceeded or when
    the server requests a retry. It includes information about how long
    to wait before retrying.

    Attributes:
        url: The URL that triggered the retry condition.
        retry_after: Seconds to wait before retrying. Defaults to 601 seconds
            (just over 10 minutes) as SEC rate limits are typically 10 minutes.
    """

    def __init__(self, url: str, retry_after: int = 601) -> None:
        """
        Initialize a RetryException.

        Args:
            url: The URL that triggered the retry condition.
            retry_after: Seconds to wait before retrying. Defaults to 601.
        """
        self.url = url
        self.retry_after = retry_after

class PreciseRateLimiter:
    """
    An async rate limiter using token bucket algorithm for precise request timing.

    This rate limiter ensures requests are evenly distributed across time,
    rather than allowing bursts. It's designed for compliance with SEC EDGAR's
    rate limiting policy which monitors requests per second.

    The limiter can be used as an async context manager for convenient usage:
        async with rate_limiter:
            await make_request()

    Attributes:
        rate: Maximum number of requests allowed per interval.
        interval: Time interval in seconds for rate calculation.
        token_time: Minimum time between requests (interval / rate).
        last_time: Timestamp of the last request.
        lock: Asyncio lock for thread-safe operation.
    """

    def __init__(self, rate: float, interval: float = 1.0) -> None:
        """
        Initialize the rate limiter.

        Args:
            rate: Number of requests allowed per interval.
            interval: Time interval in seconds. Defaults to 1.0.
        """
        self.rate = rate  # requests per interval
        self.interval = interval  # in seconds
        self.token_time = self.interval / self.rate  # time per token
        self.last_time = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Acquire permission to make a request, waiting if necessary.

        This method blocks until sufficient time has passed since the last
        request to maintain the configured rate limit.

        Returns:
            True when permission is granted to proceed.
        """
        async with self.lock:
            now = time.time()
            wait_time = self.last_time + self.token_time - now
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self.last_time = time.time()
            return True

    async def __aenter__(self) -> "PreciseRateLimiter":
        """
        Enter the async context manager, acquiring rate limit permission.

        Returns:
            The rate limiter instance.
        """
        await self.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """
        Exit the async context manager.

        Args:
            exc_type: Exception type if an exception was raised.
            exc: Exception instance if an exception was raised.
            tb: Traceback if an exception was raised.
        """
        pass

class RateMonitor:
    """
    Monitor and track request rates within a sliding time window.

    This class tracks both request count and data transfer rates over
    a configurable time window. It's useful for monitoring compliance
    with SEC EDGAR rate limits and for debugging purposes.

    Attributes:
        window_size: Size of the sliding window in seconds.
        requests: Deque storing (timestamp, size_bytes) tuples for recent requests.
    """

    def __init__(self, window_size: float = 1.0) -> None:
        """
        Initialize the rate monitor.

        Args:
            window_size: Size of the sliding window in seconds. Defaults to 1.0.
        """
        self.window_size = window_size
        self.requests: deque = deque()
        self._lock = asyncio.Lock()

    async def add_request(self, size_bytes: int) -> None:
        """
        Record a completed request.

        This method adds a request to the monitoring window and cleans up
        expired entries. It is thread-safe using an async lock.

        Args:
            size_bytes: Size of the response in bytes.
        """
        async with self._lock:
            now = time.time()
            self.requests.append((now, size_bytes))
            while self.requests and self.requests[0][0] < now - self.window_size:
                self.requests.popleft()

    def get_current_rates(self) -> Tuple[float, float]:
        """
        Get current request and data transfer rates.

        Calculates the request rate (requests per second) and data transfer
        rate (megabytes per second) based on requests within the sliding window.

        Returns:
            A tuple of (requests_per_second, megabytes_per_second), both rounded
            for readability. Returns (0, 0) if no requests are in the window.
        """
        now = time.time()
        while self.requests and self.requests[0][0] < now - self.window_size:
            self.requests.popleft()

        if not self.requests:
            return 0, 0

        request_count = len(self.requests)
        byte_count = sum(size for _, size in self.requests)

        requests_per_second = request_count / self.window_size
        mb_per_second = (byte_count / 1024 / 1024) / self.window_size

        return round(requests_per_second, 1), round(mb_per_second, 2)


user_agent = os.environ.get('DATAMULE_SEC_USER_AGENT')
if user_agent is None:
    user_agent = 'John Smith johnsmith@gmail.com'

headers = {'User-Agent': user_agent}
