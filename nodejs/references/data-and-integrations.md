# Data and Integrations

## Database access

- Isolate database logic in repositories or data-access modules.
- Use connection pooling and per-request transactions where needed.
- Normalize error handling so database errors map to user-safe messages.

## Caching

- Cache read-heavy endpoints or expensive computations.
- Include cache invalidation rules alongside write operations.
- Prefer short TTLs when data is frequently updated.

## Queues and background jobs

- Use background workers for email, file processing, or long-running tasks.
- Define a consistent job payload schema and retry strategy.
- Track job status for observability and user feedback.
