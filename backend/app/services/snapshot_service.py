import logging
from datetime import UTC, datetime, timedelta

from app.db.queries import get_snapshot_by_card, upsert_snapshot
from app.schemas.dashboard import CardSnapshot, CardStatus, TickerPayload
from app.services.sse_broker import sse_broker

logger = logging.getLogger(__name__)

# Staleness thresholds
STALENESS_LIMITS = {
    "ticker": timedelta(minutes=2),
    "gdp": timedelta(days=180),
    "debt": timedelta(days=180),
    "trade": timedelta(days=60),
    "gst": timedelta(days=45),
    "inflation": timedelta(days=45),
    "fiscal": timedelta(days=45),
}


def calculate_status(
    card: str, fetched_at: datetime, explicit_status: CardStatus | None = None
) -> CardStatus:
    if explicit_status:
        return explicit_status

    limit = STALENESS_LIMITS.get(card, timedelta(days=30))
    now = datetime.now(UTC)
    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=UTC)

    if now - fetched_at > limit:
        return "stale"
    return "fresh"


async def save_card_snapshot(
    card: str,
    snapshot: CardSnapshot,
    publish_sse: bool = True
) -> None:
    # Validate against Pydantic schema
    validated_dict = snapshot.model_dump(mode="json")

    await upsert_snapshot(
        card=card,
        payload=validated_dict,
        as_of=snapshot.as_of,
        status=snapshot.status,
        last_error=snapshot.message,
    )

    if publish_sse:
        await sse_broker.publish(
            event="card-update",
            data={"card": card, "snapshot": validated_dict}
        )


async def handle_collector_failure(card: str, error_msg: str) -> None:
    """When a collector fails, keep existing snapshot payload intact and mark status='stale'."""
    existing = await get_snapshot_by_card(card)
    if existing:
        logger.warning(
            f"Collector failed for '{card}'. Retaining last valid snapshot and flagging as stale. Error: {error_msg}"
        )
        payload = existing["payload"]
        as_of = existing.get("as_of")
        payload["status"] = "stale"
        payload["message"] = f"Upstream refresh failed: {error_msg}. Serving last valid observation."

        await upsert_snapshot(
            card=card,
            payload=payload,
            as_of=as_of,
            status="stale",
            last_error=error_msg,
        )

        await sse_broker.publish(
            event="card-update",
            data={"card": card, "snapshot": payload}
        )
    else:
        logger.error(f"Collector failed for '{card}' and no prior snapshot exists. Marking unavailable.")
        unavailable_payload = {
            "card": card,
            "status": "unavailable",
            "as_of": None,
            "fetched_at": datetime.now(UTC).isoformat(),
            "source": {"id": "unknown", "name": "Unknown", "url": "", "is_nse": False},
            "kpis": [],
            "series": [],
            "notes": [],
            "message": f"Data currently unavailable: {error_msg}",
        }
        await upsert_snapshot(
            card=card,
            payload=unavailable_payload,
            as_of=None,
            status="unavailable",
            last_error=error_msg,
        )


async def save_ticker_snapshot(
    ticker_payload: TickerPayload,
    status: CardStatus = "fresh",
    error_msg: str | None = None
) -> None:
    validated_dict = ticker_payload.model_dump(mode="json")
    await upsert_snapshot(
        card="ticker",
        payload=validated_dict,
        as_of=datetime.now(UTC).date(),
        status=status,
        last_error=error_msg,
    )

    await sse_broker.publish(
        event="ticker",
        data=validated_dict
    )
