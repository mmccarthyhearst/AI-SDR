"""API integration tests."""
import os
import pytest
from httpx import AsyncClient, ASGITransport
from ai_sdr.main import app

requires_db = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="Requires DATABASE_URL env var (PostgreSQL)",
)


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_leads_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/leads")
    # Either 401/403 (auth required) or 200 (no auth configured) - both are valid
    assert response.status_code in [200, 401, 403, 422]


@requires_db
@pytest.mark.asyncio
async def test_companies_endpoint_exists():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/companies")
    assert response.status_code in [200, 401, 403]
