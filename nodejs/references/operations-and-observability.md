# Operations and Observability

## Logging

- Use structured logs with request identifiers.
- Redact secrets or tokens from logs.

## Metrics and health checks

- Add a `/health` endpoint that validates dependencies.
- Expose service metrics if the deployment platform consumes them.

## Configuration

- Centralize environment variables in a config module.
- Validate required config at startup and fail fast if missing.

## Graceful shutdown

- Close HTTP servers and database/queue connections on termination signals.
- Stop accepting new requests before shutdown completes.
