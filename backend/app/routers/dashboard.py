from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.queries import (
    get_all_snapshots,
    get_all_sources,
    get_observations,
    get_snapshot_by_card,
)
from app.deps import get_current_user
from app.schemas.dashboard import (
    CardSnapshot,
    DashboardPayload,
    SourceInfo,
    TickerPayload,
)

router = APIRouter(prefix="/api/v1", tags=["Dashboard"])


@router.get("/dashboard", response_model=DashboardPayload)
async def get_dashboard(current_user: dict[str, Any] = Depends(get_current_user)):
    snapshots = await get_all_snapshots()
    card_map = {}
    ticker_payload = TickerPayload()

    for s in snapshots:
        card_name = s["card"]
        payload = s["payload"]
        if card_name == "ticker":
            ticker_payload = TickerPayload(**payload)
        else:
            card_map[card_name] = CardSnapshot(**payload)

    # If cards are still missing, cold start / fallback
    expected_cards = ["gdp", "debt", "trade", "gst", "inflation", "fiscal"]
    for c in expected_cards:
        if c not in card_map:
            # Return unavailable placeholder
            card_map[c] = CardSnapshot(
                card=c,
                status="unavailable",
                as_of=None,
                fetched_at=date.today(),
                source=SourceInfo(id="unknown", name="Pending Collector", url="", is_nse=False),
                kpis=[],
                series=[],
                notes=[],
                message="Data currently loading or unavailable"
            )

    return DashboardPayload(
        ticker=ticker_payload,
        cards=card_map
    )


@router.get("/ticker", response_model=TickerPayload)
async def get_ticker(current_user: dict[str, Any] = Depends(get_current_user)):
    snap = await get_snapshot_by_card("ticker")
    if not snap:
        return TickerPayload(items=[], market_status="Closed", as_of=None)
    return TickerPayload(**snap["payload"])


@router.get("/indicators/{card}", response_model=CardSnapshot)
async def get_indicator_card(
    card: str,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    valid_cards = {"gdp", "debt", "trade", "gst", "inflation", "fiscal"}
    if card not in valid_cards:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CARD_NOT_FOUND", "message": f"Indicator card '{card}' not found"}}
        )

    snap = await get_snapshot_by_card(card)
    if not snap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "DATA_UNAVAILABLE", "message": f"No data recorded for indicator '{card}'"}}
        )

    return CardSnapshot(**snap["payload"])


@router.get("/indicators/{card}/history")
async def get_indicator_history(
    card: str,
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    current_user: dict[str, Any] = Depends(get_current_user)
):
    card_indicator_map = {
        "gdp": "gdp_growth",
        "debt": "debt_gdp",
        "trade": "exports",
        "gst": "gst_gross",
        "inflation": "cpi_yoy",
        "fiscal": "gov_exp_total",
    }
    indicator = card_indicator_map.get(card)
    if not indicator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CARD_NOT_FOUND", "message": f"Indicator card '{card}' not found"}}
        )

    records = await get_observations(indicator, from_date=from_date, to_date=to_date)
    return {
        "card": card,
        "indicator": indicator,
        "from": from_date.isoformat() if from_date else None,
        "to": to_date.isoformat() if to_date else None,
        "observations": records
    }


@router.get("/sources", response_model=list[SourceInfo])
async def list_sources(current_user: dict[str, Any] = Depends(get_current_user)):
    sources = await get_all_sources()
    return [SourceInfo(**s) for s in sources]
