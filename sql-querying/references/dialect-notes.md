# Dialect Notes

This repo’s skills are generally Postgres-friendly, but agents may encounter multiple SQL dialects.

## General Guidance

- Always confirm the target database first.
- Prefer ANSI SQL when portability matters.
- Avoid relying on implicit casts; be explicit.

## Common Differences (Examples)

### Auto-increment keys

- Postgres: `GENERATED AS IDENTITY` (modern) or `SERIAL` (legacy)
- MySQL: `AUTO_INCREMENT`
- SQL Server: `IDENTITY(1,1)`

### String concatenation

- Postgres/Oracle: `a || b`
- MySQL: `CONCAT(a, b)`
- SQL Server: `a + b` (string context)

### LIMIT/OFFSET

- Postgres/MySQL: `LIMIT ... OFFSET ...`
- SQL Server: `OFFSET ... FETCH NEXT ...`

### Upsert

- Postgres: `INSERT ... ON CONFLICT ... DO UPDATE`
- MySQL: `INSERT ... ON DUPLICATE KEY UPDATE`
- SQL Server: `MERGE` (use carefully)
