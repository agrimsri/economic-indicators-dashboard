import pytest
from httpx import ASGITransport, AsyncClient

from app.collectors.base import validate_upstream_url
from app.main import app


@pytest.mark.asyncio
async def test_security_headers_present():
    """Verify security headers are applied to HTTP responses."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.headers.get("X-Content-Type-Options") == "nosniff"
        assert res.headers.get("X-Frame-Options") == "DENY"
        assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert "geolocation=()" in res.headers.get("Permissions-Policy", "")


@pytest.mark.asyncio
async def test_request_payload_limit():
    """Verify payload size limit rejects requests exceeding 1MB with 413."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        oversized_headers = {"content-length": str(2 * 1024 * 1024)}  # 2MB header
        res = await client.post("/auth/login", headers=oversized_headers)
        assert res.status_code == 413
        data = res.json()
        assert data["error"]["code"] == "PAYLOAD_TOO_LARGE"


def test_ssrf_guard_allowed_and_blocked():
    """Verify SSRF guard only allows approved upstream domains."""
    # Allowed domains
    assert validate_upstream_url("https://www.nseindia.com/api/allIndices") is True
    assert validate_upstream_url("https://api.worldbank.org/v2/country/IN/indicator/NY.GDP.MKTP.KD.ZG") is True
    assert validate_upstream_url("https://www.imf.org/external/datamapper/api/v1/GGXWDG_NGDP_PT") is True

    # Blocked domains
    with pytest.raises(ValueError, match="SSRF Guard: Request to unauthorized domain 'evil.com' blocked."):
        validate_upstream_url("https://evil.com/leak-data")

    with pytest.raises(ValueError, match="SSRF Guard: Request to unauthorized domain '169.254.169.254' blocked."):
        validate_upstream_url("http://169.254.169.254/latest/meta-data/")


@pytest.mark.asyncio
async def test_standard_error_envelope():
    """Verify 404 and other HTTP errors conform to standard envelope."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/nonexistent-route")
        assert res.status_code == 404
        data = res.json()
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
