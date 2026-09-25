from __future__ import annotations
from typing import Any

from .handlers import HANDLERS
from .store import EventStore

class EventProcessor:
    def __init__(self, store: EventStore, max_attempts=3):
        self.store = store
        self.max_attempts = max(1, max_attempts)

    def process_one(self, event: dict[str, Any]):
        attempts = int(event["attempts"]) + 1
        pair = HANDLERS.get(event["event_type"])
        if not pair:
            error = f"No handler for {event['event_type']}"
            status = "DEAD_LETTER" if attempts >= self.max_attempts else "RETRY"
            self.store.delivery(event["id"], "unmapped", status, attempts, error)
            self.store.update(event["id"], status, attempts, error)
            return self.store.get(event["id"])
        name, handler = pair
        try:
            result = handler(event["payload"])
            self.store.delivery(event["id"], name, "SUCCEEDED", attempts)
            self.store.update(event["id"], "PROCESSED", attempts)
            out = self.store.get(event["id"])
            out["handler_result"] = result
            return out
        except Exception as exc:
            status = "DEAD_LETTER" if attempts >= self.max_attempts else "RETRY"
            self.store.delivery(event["id"], name, status, attempts, str(exc))
            self.store.update(event["id"], status, attempts, str(exc))
            return self.store.get(event["id"])

    def process_batch(self, limit=100):
        return [self.process_one(event) for event in self.store.pending(limit)]
