import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.migrator import run_migrations
from app.db.pool import close_db_pool, init_db_pool
from app.db.queries import create_user
from app.main import app
from app.security import create_access_token, hash_password
from app.services.scheduler import run_all_collectors_once


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await run_migrations()
    await init_db_pool()
    hashed = hash_password("test_pass_123")
    user = await create_user(username="dash_user", password_hash=hashed, role="viewer")
    # Warm up collectors once
    await run_all_collectors_once()
    yield user
    await close_db_pool()


@pytest.mark.asyncio
async def test_dashboard_authenticated():
    token = create_access_token(user_id=1, username="dash_user")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/dashboard", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "ticker" in data
        assert "cards" in data
        cards = data["cards"]

        # All 6 cards must exist
        for card_name in ["gdp", "debt", "trade", "gst", "inflation", "fiscal"]:
            assert card_name in cards
            c = cards[card_name]
            assert c["card"] == card_name
            assert c["status"] in ["fresh", "stale", "unavailable"]
            assert "kpis" in c
            assert len(c["kpis"]) >= 2
            assert "series" in c
            assert "source" in c
            assert "is_nse" in c["source"]


@pytest.mark.asyncio
async def test_ticker_authenticated():
    token = create_access_token(user_id=1, username="dash_user")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/ticker", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert len(data["items"]) >= 1
        symbols = [item["symbol"] for item in data["items"]]
        assert "SENSEX" in symbols or "NIFTY 50" in symbols


@pytest.mark.asyncio
async def test_indicator_cards_and_history():
    token = create_access_token(user_id=1, username="dash_user")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Fetch individual card
        res = await ac.get("/api/v1/indicators/gdp", headers=headers)
        assert res.status_code == 200
        assert res.json()["card"] == "gdp"

        # 2. Fetch history
        res_hist = await ac.get("/api/v1/indicators/gdp/history", headers=headers)
        assert res_hist.status_code == 200
        data_hist = res_hist.json()
        assert data_hist["card"] == "gdp"
        assert len(data_hist["observations"]) > 0

        # 3. Invalid card 404
        bad_card = await ac.get("/api/v1/indicators/invalid_card", headers=headers)
        assert bad_card.status_code == 404
        assert "CARD_NOT_FOUND" in bad_card.text


@pytest.mark.asyncio
async def test_sources_endpoint():
    token = create_access_token(user_id=1, username="dash_user")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/sources", headers=headers)
        assert res.status_code == 200
        sources = res.json()
        assert len(sources) >= 5
        source_ids = [s["id"] for s in sources]
        assert "nse" in source_ids
        assert "imf" in source_ids
        assert "worldbank" in source_ids
