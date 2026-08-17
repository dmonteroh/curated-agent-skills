# Extensions

Enable an extension only against a named requirement. Each one is a dependency the target environment has to carry — a managed-Postgres provider may not offer it, and a major-version upgrade has to account for it — so an extension chosen for convenience is a migration cost paid later.

| Extension | Reach for it when |
| --- | --- |
| `pgcrypto` | password hashing (`crypt()`), and UUID generation on versions without a built-in generator |
| `pg_trgm` | fuzzy matching, similarity ranking, and accelerating `LIKE '%pattern%'` via a GIN or GiST index on the trigram operator class |
| `citext` | a column needs case-insensitive equality as a *constraint* (PK/FK/UNIQUE). For case-insensitive lookup alone, an expression index on `lower(col)` is lighter and needs no extension |
| `btree_gin` / `btree_gist` | one index or `EXCLUDE` constraint has to span a GIN/GiST-indexable column and a plain scalar column |
| `hstore` | flat string key/value maps; JSONB supersedes it for new work, so prefer it only when an existing schema already uses it |
| `timescaledb` | time-series at scale — automated time or ID partitioning, retention policies, compression, continuous aggregates |
| `postgis` | geospatial work beyond the built-in geometric types |
| `pgvector` | vector similarity search over embeddings |
| `pgaudit` | audit logging of database activity for a compliance requirement |
| `uuid-ossp` | legacy UUID generation functions; prefer `pgcrypto` or a built-in generator for anything new |

Record the extension, the requirement it serves, and the alternative rejected, in the operational-features section of the report. "It was available" is not a reason.
