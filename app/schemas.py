from typing import Any
from pydantic import BaseModel, Field

class EventCreate(BaseModel):
    event_type: str = Field(min_length=3, max_length=120)
    payload: dict[str, Any]
    idempotency_key: str | None = Field(default=None, max_length=160)
