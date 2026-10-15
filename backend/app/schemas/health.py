from datetime import datetime
from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    db: str
    collector: dict[str, Any]


class ReadyResponse(BaseModel):
    status: str
    database: str
