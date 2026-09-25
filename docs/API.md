# API

- `POST /api/events` — publish an event
- `POST /api/process` — process pending/retry events
- `GET /api/events` — recent events
- `GET /api/events/{id}` — event plus delivery attempts
- `POST /api/events/{id}/replay` — replay dead-letter event
- `GET /api/metrics` — stream metrics
- `GET /healthz` — service health
