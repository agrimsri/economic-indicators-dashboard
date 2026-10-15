from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class SourceInfo(BaseModel):
    id: str
    name: str
    url: str
    is_nse: bool


class KpiTile(BaseModel):
    key: str
    label: str
    value: float | None = None
    unit: str
    delta: float | None = None
    delta_unit: str | None = None
    delta_basis: str | None = None


class SeriesPoint(BaseModel):
    x: str
    y: float | None = None
    estimate: bool = False


class SeriesData(BaseModel):
    key: str
    label: str
    points: list[SeriesPoint] = []


CardStatus = Literal["fresh", "stale", "unavailable"]


class CardSnapshot(BaseModel):
    card: str
    status: CardStatus
    as_of: date | None = None
    fetched_at: datetime
    source: SourceInfo
    kpis: list[KpiTile] = []
    series: list[SeriesData] = []
    notes: list[str] = []
    message: str | None = None


class TickerItem(BaseModel):
    symbol: str
    last: float | None = None
    variation: float | None = None
    percent_change: float | None = None
    is_nse: bool = True
    status: CardStatus = "fresh"


class TickerPayload(BaseModel):
    items: list[TickerItem] = []
    market_status: str = "Closed"
    as_of: str | None = None


class DashboardPayload(BaseModel):
    ticker: TickerPayload
    cards: dict[str, CardSnapshot] = {}
