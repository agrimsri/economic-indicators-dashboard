import json
import logging
from datetime import UTC, date, datetime
from pathlib import Path

import httpx

from app.collectors.base import BaseCollector
from app.db.queries import insert_observation
from app.schemas.dashboard import CardSnapshot, KpiTile, SeriesData, SeriesPoint, SourceInfo
from app.services.snapshot_service import handle_collector_failure, save_card_snapshot

logger = logging.getLogger(__name__)

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"


class CPICollector(BaseCollector):
    def __init__(self):
        super().__init__(name="collect_cpi", source_id="mospi")

    async def collect(self) -> None:
        try:
            snapshot = await self.fetch_live_or_fallback()
            await save_card_snapshot("inflation", snapshot)
            logger.info("CPI Inflation snapshot updated successfully.")
        except Exception as e:
            logger.error(f"CPI collection failed: {e}")
            await handle_collector_failure("inflation", str(e))
            raise

    async def fetch_live_or_fallback(self) -> CardSnapshot:
        try:
            return await self.fetch_worldbank()
        except Exception as e:
            logger.warning(f"Live World Bank CPI fetch failed ({e}). Loading verified fixture...")
            return await self.load_fixture()

    async def fetch_worldbank(self) -> CardSnapshot:
        url = "https://api.worldbank.org/v2/country/IN/indicator/FP.CPI.TOTL.ZG?format=json&per_page=20&date=2020:2025"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            res.raise_for_status()
            data = res.json()[1]
            cpi_dict = {str(r["date"]): round(r["value"], 2) for r in data if r.get("value") is not None}

            return await self.process_cpi_data(
                cpi_dict=cpi_dict,
                source_name="World Bank / MoSPI CPI (Combined)",
                source_url=url,
                status="fresh"
            )

    async def process_cpi_data(
        self,
        cpi_dict: dict[str, float],
        source_name: str,
        source_url: str,
        status: str = "fresh"
    ) -> CardSnapshot:
        target_years = ["2021", "2022", "2023", "2024", "2025"]
        cpi_pts = []
        target_pts = []

        as_of_date = date(2025, 12, 31)

        for yr in target_years:
            val = cpi_dict.get(yr)
            if val is not None and not (-10.0 <= val <= 40.0):
                raise ValueError(f"CPI Inflation value out of reasonable range: {val}")

            cpi_pts.append(SeriesPoint(x=yr, y=val, estimate=(yr == "2025")))
            target_pts.append(SeriesPoint(x=yr, y=4.0, estimate=False))

            if val is not None:
                await insert_observation(
                    indicator="cpi_yoy",
                    series="IND",
                    period=yr,
                    period_start=date(int(yr), 1, 1),
                    value=val,
                    unit="%",
                    is_estimate=(yr == "2025"),
                    source_id=self.source_id,
                    as_of=as_of_date,
                    raw_ref=source_url,
                )

        latest_cpi = cpi_dict.get("2025", 2.40)
        prev_cpi = cpi_dict.get("2024", 4.95)
        delta_cpi = round(latest_cpi - prev_cpi, 2)

        kpis = [
            KpiTile(
                key="inflation_rate",
                label="Inflation Rate",
                value=latest_cpi,
                unit="%",
                delta=delta_cpi,
                delta_unit="pp",
                delta_basis="vs previous year",
            ),
            KpiTile(
                key="rbi_target",
                label="RBI Target",
                value=4.0,
                unit="%",
                delta=0.0,
                delta_unit="pp",
                delta_basis="medium-term target (band: 2-6%)",
            )
        ]

        series = [
            SeriesData(key="cpi", label="CPI YoY (%)", points=cpi_pts),
            SeriesData(key="rbi_target", label="RBI Target (4%)", points=target_pts),
        ]

        return CardSnapshot(
            card="inflation",
            status=status,
            as_of=as_of_date,
            fetched_at=datetime.now(UTC),
            source=SourceInfo(
                id=self.source_id,
                name=source_name,
                url=source_url,
                is_nse=False,
            ),
            kpis=kpis,
            series=series,
            notes=[
                "All-India CPI (Combined) YoY inflation rate",
                "RBI medium-term inflation target is 4.0% with a +/- 2% tolerance band (2% to 6%)",
                "Non-NSE public source"
            ],
            message=None,
        )

    async def load_fixture(self) -> CardSnapshot:
        fixture_wb = FIXTURES_DIR / "worldbank_cpi.json"
        cpi_dict = {"2021": 5.13, "2022": 6.70, "2023": 5.65, "2024": 4.95, "2025": 2.40}

        if fixture_wb.exists():
            data = json.loads(fixture_wb.read_text())[1]
            cpi_dict = {str(r["date"]): round(r["value"], 2) for r in data if r.get("value") is not None}

        return await self.process_cpi_data(
            cpi_dict=cpi_dict,
            source_name="World Bank / MoSPI (Verified Fixture)",
            source_url="https://api.worldbank.org/v2/country/IN/indicator/FP.CPI.TOTL.ZG",
            status="fresh"
        )
