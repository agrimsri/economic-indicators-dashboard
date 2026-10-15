import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.collectors.cpi import CPICollector
from app.collectors.debt import DebtCollector
from app.collectors.fiscal import FiscalCollector
from app.collectors.gdp import GDPCollector
from app.collectors.gst import GSTCollector
from app.collectors.nse import NSETickerCollector
from app.collectors.trade import TradeCollector
from app.config import settings

logger = logging.getLogger(__name__)

# Instantiate collectors
ticker_collector = NSETickerCollector()
gdp_collector = GDPCollector()
debt_collector = DebtCollector()
trade_collector = TradeCollector()
gst_collector = GSTCollector()
cpi_collector = CPICollector()
fiscal_collector = FiscalCollector()

ALL_COLLECTORS = [
    ticker_collector,
    gdp_collector,
    debt_collector,
    trade_collector,
    gst_collector,
    cpi_collector,
    fiscal_collector,
]

_scheduler: AsyncIOScheduler | None = None


async def run_all_collectors_once():
    logger.info("Executing cold start initial collection across all 7 indicators...")
    tasks = [c.run() for c in ALL_COLLECTORS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for c, res in zip(ALL_COLLECTORS, results, strict=False):
        if isinstance(res, Exception):
            logger.error(f"Initial run failed for {c.name}: {res}")
        else:
            logger.info(f"Initial run completed for {c.name}: success={res}")


def init_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

        # Ticker: every 20s
        _scheduler.add_job(
            ticker_collector.run,
            trigger=IntervalTrigger(seconds=settings.nse_poll_seconds_open),
            id="collect_ticker",
            name="NSE Ticker Collector",
            replace_existing=True,
            max_instances=1,
        )

        # Macro indicators: daily
        _scheduler.add_job(
            gdp_collector.run,
            trigger=IntervalTrigger(hours=24),
            id="collect_gdp",
            name="GDP Collector",
            replace_existing=True,
            max_instances=1,
        )
        _scheduler.add_job(
            debt_collector.run,
            trigger=IntervalTrigger(hours=24),
            id="collect_debt",
            name="Debt Collector",
            replace_existing=True,
            max_instances=1,
        )
        _scheduler.add_job(
            trade_collector.run,
            trigger=IntervalTrigger(hours=24),
            id="collect_trade",
            name="Trade Collector",
            replace_existing=True,
            max_instances=1,
        )
        _scheduler.add_job(
            gst_collector.run,
            trigger=IntervalTrigger(hours=24),
            id="collect_gst",
            name="GST Collector",
            replace_existing=True,
            max_instances=1,
        )
        _scheduler.add_job(
            cpi_collector.run,
            trigger=IntervalTrigger(hours=24),
            id="collect_cpi",
            name="CPI Collector",
            replace_existing=True,
            max_instances=1,
        )
        _scheduler.add_job(
            fiscal_collector.run,
            trigger=IntervalTrigger(hours=24),
            id="collect_fiscal",
            name="Fiscal Collector",
            replace_existing=True,
            max_instances=1,
        )

    return _scheduler


def start_scheduler():
    sched = init_scheduler()
    if not sched.running:
        sched.start()
        logger.info("APScheduler background scheduler started.")


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler background scheduler stopped.")
        _scheduler = None
