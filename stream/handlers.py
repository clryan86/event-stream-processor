from __future__ import annotations
from typing import Any, Callable

class HandlerError(RuntimeError):
    pass

def order_created(payload: dict[str, Any]):
    if not payload.get("order_id"):
        raise HandlerError("order_id is required")
    return {"normalized_order_id": str(payload["order_id"]), "amount": float(payload.get("amount", 0))}

def user_signed_up(payload):
    email = str(payload.get("email", ""))
    if "@" not in email:
        raise HandlerError("valid email is required")
    return {"email": email.lower(), "welcome_queued": True}

def telemetry_received(payload):
    value = float(payload.get("value"))
    if value < 0:
        raise HandlerError("telemetry value cannot be negative")
    return {"sensor": str(payload.get("sensor", "unknown")), "value": value}

HANDLERS: dict[str, tuple[str, Callable]] = {
    "order.created": ("order-created-handler", order_created),
    "user.signed_up": ("user-signup-handler", user_signed_up),
    "telemetry.received": ("telemetry-handler", telemetry_received),
}
