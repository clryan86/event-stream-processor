from pathlib import Path
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

def test_api_publish_process_metrics(tmp_path: Path):
    client = TestClient(create_app(Settings(tmp_path / "events.db", 2)))
    response = client.post("/api/events", json={
        "event_type": "telemetry.received",
        "payload": {"sensor": "temp", "value": 12.5},
        "idempotency_key": "x",
    })
    assert response.status_code == 201
    event_id = response.json()["id"]
    processed = client.post("/api/process")
    assert processed.status_code == 200
    assert client.get(f"/api/events/{event_id}").json()["status"] == "PROCESSED"
    assert client.get("/api/metrics").json()["processed"] == 1
