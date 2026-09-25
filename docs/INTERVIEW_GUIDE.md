# Interview Guide

## 30-second explanation

> Event Stream Processor models the reliability mechanics behind an event-driven service without requiring Kafka. Producers can publish idempotently, events are durably stored, a consumer routes types to handlers, each attempt is audited, failures move through retry state into a dead-letter queue, and dead-letter events can be replayed.

## Why a local durable store?

It makes the architecture runnable in an interview or CI environment. The important abstractions—event identity, delivery attempts, retry state and handlers—remain applicable if SQLite is replaced with a real broker.

## What is idempotency protecting?

A producer may retry after a timeout without knowing if the original publish succeeded. A unique idempotency key lets the service return the existing event rather than creating a duplicate.

## Resume bullets

- Built a durable event-processing service with idempotent publishing, typed handler routing, retries, dead-letter state, replay and delivery auditing.
- Modeled event lifecycle/consumer reliability in SQLite behind a broker-like adapter, with FastAPI producer/operations endpoints and metrics.
- Added deterministic API/processor tests, Docker, CI, security and architecture documentation.
