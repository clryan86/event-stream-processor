from __future__ import annotations
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

def now():
    return datetime.now(timezone.utc).isoformat()

class EventStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.conn() as c:
            c.executescript("""CREATE TABLE IF NOT EXISTS events(
                id TEXT PRIMARY KEY,event_type TEXT NOT NULL,payload_json TEXT NOT NULL,idempotency_key TEXT UNIQUE,
                status TEXT NOT NULL,attempts INTEGER NOT NULL DEFAULT 0,error TEXT,created_at TEXT NOT NULL,processed_at TEXT);
                CREATE INDEX IF NOT EXISTS idx_events_status ON events(status,id);
                CREATE TABLE IF NOT EXISTS deliveries(
                id INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT,handler TEXT,status TEXT,attempt INTEGER,error TEXT,created_at TEXT);""")

    @contextmanager
    def conn(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        try:
            yield c
            c.commit()
        finally:
            c.close()

    def publish(self, event_type, payload, idempotency_key=None):
        with self.conn() as c:
            if idempotency_key:
                old = c.execute("SELECT * FROM events WHERE idempotency_key=?", (idempotency_key,)).fetchone()
                if old:
                    return self._event(old)
            eid = str(uuid.uuid4())
            c.execute(
                "INSERT INTO events(id,event_type,payload_json,idempotency_key,status,created_at) VALUES(?,?,?,?,?,?)",
                (eid, event_type, json.dumps(payload), idempotency_key, "PENDING", now()),
            )
            row = c.execute("SELECT * FROM events WHERE id=?", (eid,)).fetchone()
            return self._event(row)

    def pending(self, limit=100):
        with self.conn() as c:
            rows = c.execute(
                "SELECT * FROM events WHERE status IN ('PENDING','RETRY') ORDER BY created_at LIMIT ?", (limit,)
            ).fetchall()
        return [self._event(r) for r in rows]

    def update(self, eid, status, attempts, error=None):
        with self.conn() as c:
            c.execute(
                "UPDATE events SET status=?,attempts=?,error=?,processed_at=? WHERE id=?",
                (status, attempts, error, now() if status in ("PROCESSED", "DEAD_LETTER") else None, eid),
            )

    def delivery(self, eid, handler, status, attempt, error=None):
        with self.conn() as c:
            c.execute(
                "INSERT INTO deliveries(event_id,handler,status,attempt,error,created_at) VALUES(?,?,?,?,?,?)",
                (eid, handler, status, attempt, error, now()),
            )

    def recent(self, limit=50):
        with self.conn() as c:
            rows = c.execute("SELECT * FROM events ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [self._event(r) for r in rows]

    def get(self, eid):
        with self.conn() as c:
            row = c.execute("SELECT * FROM events WHERE id=?", (eid,)).fetchone()
            deliveries = c.execute("SELECT * FROM deliveries WHERE event_id=? ORDER BY id", (eid,)).fetchall()
        if not row:
            return None
        event = self._event(row)
        event["deliveries"] = [dict(x) for x in deliveries]
        return event

    def replay(self, eid):
        with self.conn() as c:
            c.execute(
                "UPDATE events SET status='PENDING',attempts=0,error=NULL,processed_at=NULL WHERE id=? AND status='DEAD_LETTER'",
                (eid,),
            )
            return c.total_changes > 0

    def metrics(self):
        with self.conn() as c:
            rows = c.execute("SELECT status,COUNT(*) n FROM events GROUP BY status").fetchall()
            total = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        counts = {r["status"]: r["n"] for r in rows}
        return {
            "total": total,
            "pending": counts.get("PENDING", 0) + counts.get("RETRY", 0),
            "processed": counts.get("PROCESSED", 0),
            "dead_letter": counts.get("DEAD_LETTER", 0),
        }

    @staticmethod
    def _event(row):
        item = dict(row)
        item["payload"] = json.loads(item.pop("payload_json"))
        return item
