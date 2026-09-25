from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from stream.processor import EventProcessor
from stream.store import EventStore
from .config import Settings
from .schemas import EventCreate

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = Jinja2Templates(directory=str(ROOT / "templates"))

def create_app(settings: Settings | None = None):
    settings = settings or Settings.from_env()
    store = EventStore(settings.database_path)
    processor = EventProcessor(store, settings.max_attempts)
    app = FastAPI(title=settings.app_name, version="1.0.0")
    app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

    @app.get("/healthz")
    def health():
        return {"ok": True, "service": settings.app_name}

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        return TEMPLATES.TemplateResponse(
            request=request,
            name="index.html",
            context={"app_name": settings.app_name, "events": store.recent(20), "metrics": store.metrics()},
        )

    @app.post("/api/events", status_code=201)
    def publish(req: EventCreate):
        return store.publish(req.event_type, req.payload, req.idempotency_key)

    @app.post("/api/process")
    def process(limit: int = 100):
        return {"processed": processor.process_batch(max(1, min(limit, 500)))}

    @app.get("/api/events")
    def events(limit: int = 50):
        return store.recent(max(1, min(limit, 500)))

    @app.get("/api/events/{event_id}")
    def event(event_id: str):
        item = store.get(event_id)
        if not item:
            raise HTTPException(404, "Event not found")
        return item

    @app.post("/api/events/{event_id}/replay")
    def replay(event_id: str):
        if not store.replay(event_id):
            raise HTTPException(409, "Event is not dead-lettered or does not exist")
        return {"ok": True}

    @app.get("/api/metrics")
    def metrics():
        return store.metrics()

    return app

app = create_app()
