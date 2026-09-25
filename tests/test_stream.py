from pathlib import Path

from stream.processor import EventProcessor
from stream.store import EventStore

def test_idempotent_publish_and_success(tmp_path: Path):
    store = EventStore(tmp_path / "e.db")
    first = store.publish("order.created", {"order_id": 42, "amount": 15}, "key1")
    second = store.publish("order.created", {"order_id": 99}, "key1")
    assert first["id"] == second["id"]
    output = EventProcessor(store, 3).process_batch()
    assert output[0]["status"] == "PROCESSED"
    assert store.metrics()["processed"] == 1

def test_dead_letter_and_replay(tmp_path: Path):
    store = EventStore(tmp_path / "e.db")
    event = store.publish("user.signed_up", {"email": "bad"})
    processor = EventProcessor(store, 2)
    processor.process_batch()
    assert store.get(event["id"])["status"] == "RETRY"
    processor.process_batch()
    assert store.get(event["id"])["status"] == "DEAD_LETTER"
    assert store.replay(event["id"]) is True
    assert store.get(event["id"])["status"] == "PENDING"

def test_unknown_handler_dead_letters(tmp_path: Path):
    store = EventStore(tmp_path / "e.db")
    event = store.publish("unknown.event", {})
    EventProcessor(store, 1).process_batch()
    assert store.get(event["id"])["status"] == "DEAD_LETTER"
