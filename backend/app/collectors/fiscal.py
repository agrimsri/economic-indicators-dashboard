import csv
import logging
from datetime import UTC, date, datetime
from pathlib import Path

from app.collectors.base import BaseCollector
from app.db.queries import insert_observation
from app.schemas.dashboard import CardSnapshot, KpiTile, SeriesData, SeriesPoint, SourceInfo
from app.services.snapshot_service import handle_collector_failure, save_card_snapshot

logger = logging.getLogger(__name__)

SEED_DIR = Path(__file__).resolve().parent.parent.parent / "seed"


class FiscalCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="collect_fiscal", source_id="cga")

    async def collect(self) -> None:
        try:
            snapshot = await self.process_fiscal_seed()
            await save_card_snapshot("fiscal", snapshot)
            logger.info("Government Expenditure snapshot updated successfully.")
        except Exception as e:
            logger.error(f"Fiscal collection failed: {e}")
            await handle_collector_failure("fiscal", str(e))
            raise

    async def process_fiscal_seed(self) -> CardSnapshot:
        seed_file = SEED_DIR / "gov_expenditure_annual.csv"
        if not seed_file.exists():
            raise FileNotFoundError(f"Missing Government Expenditure seed file: {seed_file}")

        rows = []
        with open(seed_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append({
                    "fy": r["fy"],
                    "revenue_exp": float(r["revenue_exp_lakh_cr"]),
                    "capital_exp": float(r["capital_exp_lakh_cr"]),
                    "total_exp": float(r["total_exp_lakh_cr"]),
                    "source_url": r["source_url"],
                })

        rev_pts = []
        cap_pts = []
        tot_pts = []

        as_of_date = date(2025, 3, 31)

        for row in rows:
            fy_label = row["fy"]  # e.g. "2021-22"
            # Map to 2021..2025 tick label to match Figma
            yr = fy_label.split("-")[0]
            r_val = row["revenue_exp"]
            c_val = row["capital_exp"]
            t_val = row["total_exp"]

            rev_pts.append(SeriesPoint(x=yr, y=r_val, estimate=(yr >= "2024")))
            cap_pts.append(SeriesPoint(x=yr, y=c_val, estimate=(yr >= "2024")))
            tot_pts.append(SeriesPoint(x=yr, y=t_val, estimate=(yr >= "2024")))

            await insert_observation(
                indicator="gov_exp_revenue",
                series="IND",
                period=fy_label,
                period_start=date(int(yr), 4, 1),
                value=r_val,
                unit="₹ lakh cr",
                is_estimate=(yr >= "2024"),
                source_id=self.source_id,
                as_of=as_of_date,
                raw_ref=row["source_url"],
            )
            await insert_observation(
                indicator="gov_exp_capital",
                series="IND",
                period=fy_label,
                period_start=date(int(yr), 4, 1),
                value=c_val,
                unit="₹ lakh cr",
                is_estimate=(yr >= "2024"),
                source_id=self.source_id,
                as_of=as_of_date,
                raw_ref=row["source_url"],
            )

        latest = rows[-1]
        prev = rows[-2]

        total_growth = round(((latest["total_exp"] - prev["total_exp"]) / prev["total_exp"]) * 100, 2)
        capex_growth = round(((latest["capital_exp"] - prev["capital_exp"]) / prev["capital_exp"]) * 100, 2)

        kpis = [
            KpiTile(
                key="total_expenditure",
                label="Total Expenditure",
                value=latest["total_exp"],
                unit="₹ lakh cr",
                delta=total_growth,
                delta_unit="%",
                delta_basis="YoY Growth",
            ),
            KpiTile(
                key="capital_expenditure",
                label="Capital Expenditure",
                value=latest["capital_exp"],
                unit="₹ lakh cr",
                delta=capex_growth,
                delta_unit="%",
                delta_basis="YoY Growth",
            )
        ]

        series = [
            SeriesData(key="capital_expenditure", label="Capital Expenditure", points=cap_pts),
            SeriesData(key="revenue_expenditure", label="Revenue Expenditure", points=rev_pts),
            SeriesData(key="total_expenditure", label="Total Expenditure", points=tot_pts),
        ]

        return CardSnapshot(
            card="fiscal",
            status="fresh",
            as_of=as_of_date,
            fetched_at=datetime.now(UTC),
            source=SourceInfo(
                id=self.source_id,
                name="Union Budget / CGA (Ministry of Finance)",
                url="https://www.indiabudget.gov.in/",
                is_nse=False,
            ),
            kpis=kpis,
            series=series,
            notes=[
                "Union Government Accounts: Revenue and Capital Expenditure (₹ lakh crore)",
                "Non-NSE public source"
            ],
            message=None,
        )
