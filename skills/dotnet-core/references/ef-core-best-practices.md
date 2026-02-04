# EF Core Best Practices (Condensed)

- Use explicit `AsNoTracking` for read-only queries.
- Avoid N+1 with `Include` or projection.
- Prefer migrations for schema changes.
