import asyncio
import logging
import random
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

import httpx

from app.config import settings
from app.db.queries import record_collector_run

logger = logging.getLogger(__name__)

ALLOWED_UPSTREAM_DOMAINS = {
    "www.nseindia.com",
    "nseindia.com",
    "api.worldbank.org",
    "data.worldbank.org",
    "www.imf.org",
    "imf.org",
    "api.bseindia.com",
    "www.bseindia.com",
    "bseindia.com",
    "query1.finance.yahoo.com",
    "query2.finance.yahoo.com",
    "api.data.gov.in",
    "data.gov.in",
    "www.indiabudget.gov.in",
    "indiabudget.gov.in",
    "pib.gov.in",
    "mospi.gov.in",
    "localhost",
    "127.0.0.1",
}


def validate_upstream_url(url: str) -> bool:
    """SSRF Guard: Validates that outbound requests only target approved domains."""
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if not hostname or hostname not in ALLOWED_UPSTREAM_DOMAINS:
        raise ValueError(f"SSRF Guard: Request to unauthorized domain '{hostname}' blocked.")
    return True


class CircuitBreakerOpenException(Exception):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.last_state_change = time.time()

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_state_change = time.time()
            logger.warning(f"Circuit breaker tripped to OPEN after {self.failure_count} consecutive failures")

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_state_change >= self.recovery_timeout:
                self.state = "HALF-OPEN"
                logger.info("Circuit breaker entered HALF-OPEN state (probing)")
                return True
            return False
        if self.state == "HALF-OPEN":
            return True
        return False


class BaseCollector:
    def __init__(self, name: str, source_id: str):
        self.name = name
        self.source_id = source_id
        self.circuit_breaker = CircuitBreaker()
        self._lock = asyncio.Lock()

    async def get_http_client(self, headers: dict[str, str] | None = None) -> httpx.AsyncClient:
        default_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        if headers:
            default_headers.update(headers)

        return httpx.AsyncClient(
            headers=default_headers,
            timeout=httpx.Timeout(
                connect=settings.http_timeout_connect,
                read=settings.http_timeout_read,
                write=10.0,
                pool=10.0,
            ),
            follow_redirects=True,
            http2=True,
        )

    async def fetch_with_retry(
        self,
        fetch_fn: Callable[[], Any],
        max_retries: int = 3,
        base_delay: float = 1.0,
    ) -> Any:
        if not self.circuit_breaker.can_execute():
            raise CircuitBreakerOpenException(
                f"Circuit breaker is OPEN for collector '{self.name}'. Skipping remote request."
            )

        attempt = 0
        while attempt < max_retries:
            try:
                result = await fetch_fn()
                self.circuit_breaker.record_success()
                return result
            except Exception as e:
                attempt += 1
                self.circuit_breaker.record_failure()
                if attempt >= max_retries:
                    logger.error(f"Collector '{self.name}' failed after {attempt} attempts: {e}")
                    raise
                # Exponential backoff with jitter
                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0.1, 0.5)
                logger.warning(
                    f"Collector '{self.name}' attempt {attempt} failed ({e}). Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)

    async def run(self) -> bool:
        """Single-flight locked execution wrapping collector implementation."""
        if self._lock.locked():
            logger.info(f"Collector '{self.name}' is already executing. Skipping concurrent run.")
            return False

        async with self._lock:
            started_at = datetime.now(UTC)
            start_time = time.time()
            ok = False
            http_status = None
            note = None

            try:
                logger.info(f"Starting collector job: {self.name}")
                await self.collect()
                ok = True
                note = "Collector completed successfully"
                logger.info(f"Collector job '{self.name}' completed successfully.")
            except Exception as e:
                ok = False
                note = f"Error: {e}"
                logger.error(f"Collector job '{self.name}' encountered error: {e}")
            finally:
                finished_at = datetime.now(UTC)
                duration_ms = int((time.time() - start_time) * 1000)
                try:
                    await record_collector_run(
                        job=self.name,
                        started_at=started_at,
                        finished_at=finished_at,
                        ok=ok,
                        http_status=http_status,
                        duration_ms=duration_ms,
                        note=note,
                    )
                except Exception as db_err:
                    logger.error(f"Failed to record collector run in DB: {db_err}")

            return ok

    async def collect(self) -> None:
        raise NotImplementedError("Subclasses must implement collect()")
