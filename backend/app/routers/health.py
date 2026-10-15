from datetime import UTC, datetime

from fastapi import APIRouter, Response, status

from app.config import settings
from app.db.pool import check_db_health
from app.schemas.health import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    db_ok = await check_db_health()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        timestamp=datetime.now(UTC),
        db="ok" if db_ok else "down",
        collector={
            "enabled": settings.enable_scheduler,
            "status": "active" if settings.enable_scheduler else "disabled"
        }
    )


@router.get("/health/ready", response_model=ReadyResponse)
async def readiness_check(response: Response):
    db_ok = await check_db_health()
    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadyResponse(status="not_ready", database="down")
    return ReadyResponse(status="ready", database="ok")
