# Architecture

```mermaid
flowchart LR
    P[Producer API] --> S[(Durable Event Store)]
    S --> C[Consumer Processor]
    C --> R[Handler Registry]
    R --> H1[Order Handler]
    R --> H2[User Handler]
    R --> H3[Telemetry Handler]
    C --> D[(Delivery Audit)]
    C --> DLQ[Dead Letter State]
    DLQ -->|Replay| S
    S --> M[Metrics Dashboard]
```

The event record and each delivery attempt are separate. That distinction makes retries auditable and preserves the original message even after multiple failures.

Producer idempotency prevents duplicate events when callers retry a publish request. Handler failures do not delete events; they transition state until the retry budget is exhausted.
