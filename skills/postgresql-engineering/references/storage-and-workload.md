# Table storage and workload-shaped tactics

## Choosing the table storage type

- **Regular** — durable and WAL-logged. The default, and the only correct answer for anything that is a source of truth.
- **`TEMPORARY`** — visible to one session, dropped when it ends, not WAL-logged. For intermediate result sets inside a single job or transaction.
- **`UNLOGGED`** — persists across a clean restart but is truncated after a crash, and is not replicated to standbys. Writes skip the WAL, so they are materially cheaper. Use for caches, import/staging tables, and anything that can be rebuilt from a source; never for data that cannot be regenerated.

State the choice explicitly in the schema proposal. An `UNLOGGED` table that quietly becomes a source of truth is a data-loss incident waiting for the next crash.

## Large values and TOAST

Values above the engine's TOAST threshold (roughly 2 KB by default — confirm the exact figure for the target version rather than relying on this number) are compressed and moved out of line automatically, per column. Control the strategy with `ALTER TABLE t ALTER COLUMN c SET STORAGE <strategy>`:

- `EXTENDED` (default) — compress, then move out of line if still oversized. Correct for almost everything.
- `EXTERNAL` — out of line, no compression. Faster substring and prefix access on large text, at the cost of size.
- `MAIN` — compress, keep in line where it fits.
- `PLAIN` — neither compressed nor out of line; only valid for fixed-length types.

Shift the per-table threshold with `ALTER TABLE t SET (toast_tuple_target = 4096)`. Change either setting only against a measured problem — a wide row that no longer fits in a page, or a profile showing decompression cost on a hot read path.

## Update-heavy tables

- **Separate hot columns from cold ones.** A row updated frequently rewrites in full under MVCC, including the large stable columns riding along with it. Splitting the churning columns into their own table shrinks each new row version.
- **Leave free space in each page for HOT updates.** A heap-only-tuple update writes the new row version into the same page and skips index maintenance entirely; it needs free space to land in. `ALTER TABLE t SET (fillfactor = 90)` reserves it. The 90 is a chosen starting point with no measurement behind it — the table default is 100, meaning no reserved space — so tune it from observed bloat and update rate rather than adopting it as a fact.
- **Avoid updating indexed columns.** A HOT update is only possible when no indexed column changes, so an index on a frequently-updated column forfeits the optimization for every update of that row.
- **Partition by update pattern** where rows have distinct lifecycles, keeping churning rows out of the same partitions as stable ones.

## Insert-heavy tables

- **Every index is paid on every insert.** Create only the ones a real query uses; an index kept "just in case" is a permanent write tax.
- **Use `COPY` or multi-row `INSERT`** rather than row-at-a-time inserts.
- **Defer index creation for bulk loads.** Drop the non-essential indexes, load, then rebuild them: building an index once over the finished data is cheaper than maintaining it per row. Verify the rebuilt index list matches the pre-load list before declaring the load complete — a forgotten index is a silent plan regression rather than an error.
- **Use `UNLOGGED` staging tables** for import data that can be re-fetched from source, then move validated rows into the logged table.
- **Many insert-heavy tables need no surrogate key at all**; where uniqueness is required, a natural key such as `(recorded_at, device_id)` often serves. Where a surrogate is needed, prefer `BIGINT GENERATED ALWAYS AS IDENTITY` over a random UUID, whose values scatter inserts across the whole B-tree instead of appending to one end of it.
