import pytest
import pytest_asyncio

from app.collectors.cpi import CPICollector
from app.collectors.debt import DebtCollector
from app.collectors.fiscal import FiscalCollector
from app.collectors.gdp import GDPCollector
from app.collectors.gst import GSTCollector
from app.collectors.trade import TradeCollector
from app.db.migrator import run_migrations
from app.db.pool import close_db_pool, init_db_pool
from app.db.queries import get_snapshot_by_card
from app.services.snapshot_service import handle_collector_failure


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await run_migrations()
    await init_db_pool()
    yield
    await close_db_pool()


@pytest.mark.asyncio
async def test_gdp_collector_success():
    collector = GDPCollector()
    ok = await collector.run()
    assert ok is True
    snap = await get_snapshot_by_card("gdp")
    assert snap is not None
    assert snap["status"] == "fresh"
    payload = snap["payload"]
    assert len(payload["kpis"]) == 2
    assert len(payload["series"]) == 2


@pytest.mark.asyncio
async def test_debt_collector_success():
    collector = DebtCollector()
    ok = await collector.run()
    assert ok is True
    snap = await get_snapshot_by_card("debt")
    assert snap is not None
    assert snap["status"] == "fresh"


@pytest.mark.asyncio
async def test_trade_collector_success():
    collector = TradeCollector()
    ok = await collector.run()
    assert ok is True
    snap = await get_snapshot_by_card("trade")
    assert snap is not None
    assert snap["status"] == "fresh"


@pytest.mark.asyncio
async def test_gst_collector_success():
    collector = GSTCollector()
    ok = await collector.run()
    assert ok is True
    snap = await get_snapshot_by_card("gst")
    assert snap is not None
    assert snap["status"] == "fresh"


@pytest.mark.asyncio
async def test_cpi_collector_success():
    collector = CPICollector()
    ok = await collector.run()
    assert ok is True
    snap = await get_snapshot_by_card("inflation")
    assert snap is not None
    assert snap["status"] == "fresh"


@pytest.mark.asyncio
async def test_fiscal_collector_success():
    collector = FiscalCollector()
    ok = await collector.run()
    assert ok is True
    snap = await get_snapshot_by_card("fiscal")
    assert snap is not None
    assert snap["status"] == "fresh"


@pytest.mark.asyncio
async def test_failure_injection_retains_stale_data():
    """
    Failure-Injection Test:
    1. First, establish a fresh valid snapshot for GDP.
    2. Inject a simulated network/upstream failure.
    3. Verify that the previous valid data payload is RETAINED.
    4. Verify that status is updated to 'stale' and last_error is recorded.
    5. Verify no data is wiped or fabricated.
    """
    collector = GDPCollector()
    # 1. Successful baseline run
    await collector.run()
    fresh_snap = await get_snapshot_by_card("gdp")
    assert fresh_snap["status"] == "fresh"
    original_kpis = fresh_snap["payload"]["kpis"]
    original_series = fresh_snap["payload"]["series"]

    # 2. Inject failure
    error_msg = "Upstream server returned HTTP 503 Service Unavailable"
    await handle_collector_failure("gdp", error_msg)

    # 3. Read snapshot after failure
    stale_snap = await get_snapshot_by_card("gdp")
    assert stale_snap is not None
    assert stale_snap["status"] == "stale"
    assert stale_snap["last_error"] == error_msg

    # 4. Payload retention check: data is NOT lost
    stale_payload = stale_snap["payload"]
    assert stale_payload["kpis"] == original_kpis
    assert stale_payload["series"] == original_series
    assert "Upstream refresh failed" in stale_payload["message"]
