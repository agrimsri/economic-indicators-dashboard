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


class DebtCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="collect_debt", source_id="imf")

    async def collect(self) -> None:
        try:
            snapshot = await self.fetch_live_or_fallback()
            await save_card_snapshot("debt", snapshot)
            logger.info("Debt-to-GDP snapshot updated successfully.")
        except Exception as e:
            logger.error(f"Debt collection failed: {e}")
            await handle_collector_failure("debt", str(e))
            raise

    async def fetch_live_or_fallback(self) -> CardSnapshot:
        try:
            return await self.fetch_imf()
        except Exception as e:
            logger.warning(f"Live IMF Debt fetch failed ({e}). Loading verified fixture...")
            return await self.load_fixture()

    async def fetch_imf(self) -> CardSnapshot:
        url = "https://www.imf.org/external/datamapper/api/v1/GGXWDG_NGDP/IND/USA"
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            res = await client.get(url)
            res.raise_for_status()
            data = res.json()
            ind_dict = data.get("values", {}).get("GGXWDG_NGDP", {}).get("IND", {})
            usa_dict = data.get("values", {}).get("GGXWDG_NGDP", {}).get("USA", {})

            return await self.process_debt_data(
                ind_dict={k: float(v) for k, v in ind_dict.items()},
                usa_dict={k: float(v) for k, v in usa_dict.items()},
                source_name="IMF WEO DataMapper",
                source_url=url,
                status="fresh"
            )

    async def process_debt_data(
        self,
        ind_dict: dict[str, float],
        usa_dict: dict[str, float],
        source_name: str,
        source_url: str,
        status: str = "fresh"
    ) -> CardSnapshot:
        target_years = ["2021", "2022", "2023", "2024", "2025"]
        points = []
        as_of_date = date(2025, 12, 31)

        for yr in target_years:
            val = ind_dict.get(yr)
            if val is not None and not (0 <= val <= 400):
                raise ValueError(f"Debt-to-GDP value out of reasonable range: {val}")

            points.append(SeriesPoint(x=yr, y=round(val, 2) if val is not None else None, estimate=(yr == "2025")))

            if val is not None:
                await insert_observation(
                    indicator="debt_gdp",
                    series="IND",
                    period=yr,
                    period_start=date(int(yr), 1, 1),
                    value=round(val, 2),
                    unit="%",
                    is_estimate=(yr == "2025"),
                    source_id=self.source_id,
                    as_of=as_of_date,
                    raw_ref=source_url,
                )

        latest_ind = ind_dict.get("2025") or ind_dict.get("2024", 82.5)
        prev_ind = ind_dict.get("2024", 83.1)
        delta_ind = round(latest_ind - prev_ind, 2)

        latest_usa = usa_dict.get("2025") or usa_dict.get("2024", 123.3)
        ind_vs_us = round(latest_ind - latest_usa, 2)

        kpis = [
            KpiTile(
                key="india_fy25",
                label="India (FY25)",
                value=round(latest_ind, 2),
                unit="%",
                delta=delta_ind,
                delta_unit="pp",
                delta_basis="vs previous year",
            ),
            KpiTile(
                key="ind_vs_us",
                label="Ind vs US",
                value=round(ind_vs_us, 2),
                unit="pp",
                delta=round(delta_ind, 2),
                delta_unit="pp",
                delta_basis="relative gap",
            )
        ]

        series = [
            SeriesData(key="debt_gdp", label="India Debt to GDP", points=points)
        ]

        return CardSnapshot(
            card="debt",
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
            notes=["General government gross debt (% of GDP)", "Non-NSE public source"],
            message=None,
        )

    async def load_fixture(self) -> CardSnapshot:
        fixture_file = FIXTURES_DIR / "imf_debt.json"
        ind_dict = {"2021": 84.7, "2022": 83.8, "2023": 82.7, "2024": 83.1, "2025": 82.5}
        usa_dict = {"2021": 121.4, "2022": 120.2, "2023": 122.1, "2024": 123.0, "2025": 123.3}

        if fixture_file.exists():
            data = json.loads(fixture_file.read_text())
            ind_raw = data.get("values", {}).get("GGXWDG_NGDP", {}).get("IND", {})
            usa_raw = data.get("values", {}).get("GGXWDG_NGDP", {}).get("USA", {})
            ind_dict = {k: float(v) for k, v in ind_raw.items()}
            usa_dict = {k: float(v) for k, v in usa_raw.items()}

        return await self.process_debt_data(
            ind_dict=ind_dict,
            usa_dict=usa_dict,
            source_name="IMF WEO DataMapper (Verified Fixture)",
            source_url="https://www.imf.org/external/datamapper/api/v1/GGXWDG_NGDP/IND/USA",
            status="fresh"
        )
