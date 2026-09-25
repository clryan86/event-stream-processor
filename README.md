# Event Stream Processor

[![CI](https://github.com/clryan86/event-stream-processor/actions/workflows/ci.yml/badge.svg)](https://github.com/clryan86/event-stream-processor/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Events](https://img.shields.io/badge/Architecture-event--driven-43C59E)
![FastAPI](https://img.shields.io/badge/FastAPI-producer%20API-009688)

A durable event-processing portfolio project demonstrating **idempotent producers, persisted stream state, handler routing, bounded retries, dead-letter queues, delivery audit history, replay, and operational metrics**.

The implementation uses SQLite as a lightweight durable broker so the whole system can run locally without Kafka or cloud infrastructure while preserving the same reliability concepts.

## Event lifecycle

```text
PENDING -> PROCESSED
   |
   +-> RETRY -> PROCESSED
          |
          +-> DEAD_LETTER -> replay -> PENDING
```

## Included handlers

- `order.created`
- `user.signed_up`
- `telemetry.received`

Unknown event types and handler validation failures enter retry/dead-letter state according to `MAX_ATTEMPTS`.

## Reliability features

- UUID event IDs
- producer idempotency keys
- durable event persistence
- handler registry
- per-attempt delivery records
- bounded retries
- dead-letter isolation
- replay endpoint
- backlog/processed/DLQ metrics
- API and dashboard
- deterministic automated tests

## Quick start

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Why SQLite instead of Kafka?

The goal is to make event-processing mechanics inspectable and immediately runnable. The store is an adapter: a production evolution could replace it with Kafka, AWS SQS/SNS, Azure Service Bus, RabbitMQ, or Redis Streams while retaining handler/retry/idempotency semantics.

## Tests

```bash
pytest
ruff check .
```

## Roadmap

- async worker loop
- exponential retry scheduling
- consumer groups
- partition keys and ordered streams
- event schemas/versioning
- Kafka adapter
- outbox pattern example
- OpenTelemetry traces
- dead-letter replay filters
- poison-message alerting

## Author

**Christopher Ryan**  
Python • Event-Driven Systems • Automation • Backend

## License

MIT
