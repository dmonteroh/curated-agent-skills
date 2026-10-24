# Trigger Cases: migration-observability

## Positive (should activate)

- prompt: "We kicked off the Postgres migration to add the partitioned orders table about 10 minutes ago. Please watch the logs and pg_stat_activity while it runs and flag anything that looks unsafe, like long locks or growing replica lag. Give me explicit abort criteria."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Keep an eye on the backfill job (scripts/backfill_invoices.py) as it runs. I want progress percent, ETA, error counts, and a clear go/no-go call each time you check in."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I'm running the MySQL online schema change on the 400M row events table. Babysit it: track copy progress, watch for replica delay and CPU spikes, and tell me if we should pause or throttle."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "watch the backfill and tell me when to stop"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Monitor the production database migration while it runs and keep me updated on rows processed, error rates, replication lag, and whether we should continue or roll back."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Can you supervise the schema migration in real time and give the on-call team clear go/no-go recommendations based on database load, failed writes, and migration progress?"
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Stay on the migration during the deploy and alert us with concrete proceed, pause, or abort guidance if replication delay, CPU, or write failures become unsafe."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Write a migration script that adds a nullable currency column to the payments table and backfills it from the accounts table in batches."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Review this Alembic migration file for correctness before I merge it. Don't run anything."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you monitor our API's p99 latency dashboard and alert me if it goes over 500ms during today's traffic peak?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Dry-run the migration against a copy of the database snapshot and summarize what it would change. It hasn't been run on anything live yet."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Watch the Kubernetes deployment live and tell us whether to continue based on pod health and error rates."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Keep an eye on the database’s general health during peak traffic and alert us if CPU or latency gets too high."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Investigate why yesterday’s data backfill failed and write a postmortem with recommendations."
  expect_activate: no
  tags: [generated, gen:codex]
