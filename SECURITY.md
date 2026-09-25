# Security Policy

This portfolio build accepts arbitrary JSON event payloads but never executes payload content as code. A production broker-facing API should add authentication, authorization by event type, payload-size limits, JSON schema validation, rate limiting, encryption, tenant isolation and controls around dead-letter replay.
