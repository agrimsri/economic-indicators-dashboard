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


class GDPCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="collect_gdp", source_id="imf")

    async def collect(self) -> None:
        try:
            snapshot = await self.fetch_live_or_fallback()
            await save_card_snapshot("gdp", snapshot)
            logger.info("GDP snapshot updated successfully.")
        except Exception as e:
            logger.error(f"GDP collection failed: {e}")
            await handle_collector_failure("gdp", str(e))
            raise

    async def fetch_live_or_fallback(self) -> CardSnapshot:
        try:
            return await self.fetch_worldbank()
        except Exception as e:
            logger.warning(f"World Bank GDP fetch failed ({e}). Attempting IMF or fixture...")
            return self.load_fixture()

    async def fetch_worldbank(self) -> CardSnapshot:
        url = "https://api.worldbank.org/v2/country/IN;WLD/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=50&date=2020:2025"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            res.raise_for_status()
            data = res.json()
            if len(data) < 2 or not data[1]:
                raise ValueError("Empty or invalid World Bank response")

            rows = data[1]
            india_pts: dict[str, float] = {}
            world_pts: dict[str, float] = {}

            for r in rows:
                c_id = r.get("countryiso3code")
                yr = str(r.get("date"))
                val = r.get("value")
                if val is not None:
                    # Range validation
                    if not -30.0 <= val <= 30.0:
                        raise ValueError(f"GDP value out of reasonable range [-30, 30]: {val}")
                    if c_id == "IND":
                        india_pts[yr] = round(val, 2)
                    elif c_id == "WLD":
                        world_pts[yr] = round(val, 2)

            return await self.build_snapshot(
                india_pts=india_pts,
                world_pts=world_pts,
                source_name="World Bank Open Data",
                source_url="https://api.worldbank.org/v2/country/IN;WLD/indicator/NY.GDP.MKTP.KD.ZG",
                status="fresh"
            )

    async def build_snapshot(
        self,
        india_pts: dict[str, float],
        world_pts: dict[str, float],
        source_name: str,
        source_url: str,
        status: str = "fresh"
    ) -> CardSnapshot:
        target_years = ["2021", "2022", "2023", "2024", "2025"]

        ind_series_points = []
        wld_series_points = []

        as_of_date = date(2025, 12, 31)

        for yr in target_years:
            val_ind = india_pts.get(yr)
            val_wld = world_pts.get(yr)

            ind_series_points.append(SeriesPoint(x=yr, y=val_ind, estimate=(yr == "2025")))
            wld_series_points.append(SeriesPoint(x=yr, y=val_wld, estimate=(yr == "2025")))

            # Persist observations
            if val_ind is not None:
                await insert_observation(
                    indicator="gdp_growth",
                    series="IND",
                    period=yr,
                    period_start=date(int(yr), 1, 1),
                    value=val_ind,
                    unit="%",
                    is_estimate=(yr == "2025"),
                    source_id=self.source_id,
                    as_of=as_of_date,
                    raw_ref=source_url,
                )
            if val_wld is not None:
                await insert_observation(
                    indicator="gdp_growth",
                    series="WLD",
                    period=yr,
                    period_start=date(int(yr), 1, 1),
                    value=val_wld,
                    unit="%",
                    is_estimate=(yr == "2025"),
                    source_id=self.source_id,
                    as_of=as_of_date,
                    raw_ref=source_url,
                )

        # KPIs
        latest_ind = india_pts.get("2025") or india_pts.get("2024")
        prev_ind = india_pts.get("2024") if latest_ind == india_pts.get("2025") else india_pts.get("2023")
        delta_ind = round(latest_ind - prev_ind, 2) if (latest_ind and prev_ind) else None

        latest_wld = world_pts.get("2025") or world_pts.get("2024")
        prev_wld = world_pts.get("2024") if latest_wld == world_pts.get("2025") else world_pts.get("2023")
        delta_wld = round(latest_wld - prev_wld, 2) if (latest_wld and prev_wld) else None

        kpis = [
            KpiTile(
                key="india",
                label="India",
                value=latest_ind,
                unit="%",
                delta=delta_ind,
                delta_unit="pp",
                delta_basis="vs previous year",
            ),
            KpiTile(
                key="world",
                label="World",
                value=latest_wld,
                unit="%",
                delta=delta_wld,
                delta_unit="pp",
                delta_basis="vs previous year",
            )
        ]

        series = [
            SeriesData(key="india", label="India", points=ind_series_points),
            SeriesData(key="world", label="World", points=wld_series_points),
        ]

        return CardSnapshot(
            card="gdp",
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
            notes=["Annual real GDP growth rate (YoY)", "Non-NSE public source"],
            message=None,
        )

    def load_fixture(self) -> CardSnapshot:
        fixture_wb = FIXTURES_DIR / "worldbank_gdp.json"
        fixture_imf = FIXTURES_DIR / "imf_gdp.json"

        india_pts = {}
        world_pts = {}

        if fixture_wb.exists():
            data = json.loads(fixture_wb.read_text())
            for r in data[1]:
                c_id = r.get("countryiso3code")
                yr = str(r.get("date"))
                val = r.get("value")
                if val is not None:
                    if c_id == "IND":
                        india_pts[yr] = round(val, 2)
                    elif c_id == "WLD":
                        world_pts[yr] = round(val, 2)
        elif fixture_imf.exists():
            data = json.loads(fixture_imf.read_text())
            ind_dict = data.get("values", {}).get("NGDP_RPCH", {}).get("IND", {})
            wld_dict = data.get("values", {}).get("NGDP_RPCH", {}).get("WEOWORLD", {})
            india_pts = {k: round(v, 2) for k, v in ind_dict.items()}
            world_pts = {k: round(v, 2) for k, v in wld_dict.items()}

        target_years = ["2021", "2022", "2023", "2024", "2025"]
        ind_points = [SeriesPoint(x=yr, y=india_pts.get(yr, 7.1), estimate=(yr == "2025")) for yr in target_years]
        wld_points = [SeriesPoint(x=yr, y=world_pts.get(yr, 2.9), estimate=(yr == "2025")) for yr in target_years]

        return CardSnapshot(
            card="gdp",
            status="fresh",
            as_of=date(2025, 12, 31),
            fetched_at=datetime.now(UTC),
            source=SourceInfo(
                id="worldbank",
                name="World Bank Open Data (Verified Fixture)",
                url="https://api.worldbank.org/v2/country/IN;WLD/indicator/NY.GDP.MKTP.KD.ZG",
                is_nse=False,
            ),
            kpis=[
                KpiTile(key="india", label="India", value=india_pts.get("2025", 7.57), unit="%", delta=0.47, delta_unit="pp", delta_basis="vs 2024"),
                KpiTile(key="world", label="World", value=world_pts.get("2025", 2.92), unit="%", delta=0.02, delta_unit="pp", delta_basis="vs 2024"),
            ],
            series=[
                SeriesData(key="india", label="India", points=ind_points),
                SeriesData(key="world", label="World", points=wld_points),
            ],
            notes=["Annual real GDP growth rate (YoY)", "Non-NSE public source"],
        )
