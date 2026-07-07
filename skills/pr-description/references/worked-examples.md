# Worked Example Fragments

These fragments illustrate the bar for each recipe. They are intentionally short and use a fictional checklist product. Imitate the shape, not the exact wording or domain.

## Feature

```
## What & Why

The ship application exposes an on-demand checklist export. Without this surface, retrieving a completed checklist as a portable document depends on the nightly batch, which delays handover and blocks audits when the batch is late. The on-demand action returns the document within the same session.

## How

A new endpoint generates the portable document for a given checklist instance and streams the result to the caller. The ship-mode user interface adds a download action on the checklist detail view that calls the endpoint and saves the response. The endpoint reuses the existing template renderer; only the trigger surface is new.

## Manual Verification Playbook

Run against a freshly restored development database with the ship backend and frontend up via the standard local compose stack. Sign in as a ship user with the `crew` role.

1. Open a completed checklist instance in the ship application. Confirm the download action is visible on the detail header.
2. Click the download action. Confirm a portable document downloads with a filename matching the checklist title and the response status is 200.
3. Open the downloaded document. Confirm the sections, items, and signatures match the on-screen checklist state.
4. Sign in as a user without the `crew` role and open the same checklist instance. Confirm the download action is hidden and a direct call to the endpoint returns 403.
5. Trigger the download twice in succession on the same instance. Confirm both downloads succeed and produce identical content.
```

## Bugfix

```
## What & Why

The home page renders correctly when the application starts in offline mode with cached checklist rows that lack section and item arrays. The defect produced a blank page on reload for crew using the application on intermittent shipboard connectivity. The fix restores a usable home view in that state.

## How

The home page derived helpers treat cached checklist rows as untrusted historical input and guard the section and item lookups against missing arrays. Live API responses are unaffected because the same guards short-circuit when the arrays are present.

## Manual Verification Playbook

Run against the ship application built from this branch with the backend stopped, so the application falls back to cached data.

1. With the backend running, sign in as a ship user and open at least one checklist so its rows enter the offline cache. Confirm the home page renders normally.
2. Stop the backend container. Reload the home page. On the previous build this triggers a runtime error and a blank view. Confirm the reproduction on the prior build.
3. Switch to the build from this branch and reload the home page with the backend still stopped. Confirm the home page renders, the cached checklist appears in the list, and no console error is logged.
4. Restart the backend and reload. Confirm the home page still renders correctly with live data and the cached row is replaced by the live row.
```

## Migration

```
## What & Why

The checklist `started` column moves from a plain timestamp to a composite zoned timestamp so downstream reporting can keep the originating time zone alongside the instant. Existing rows are preserved and reinterpreted in coordinated universal time.

## How

A forward-only migration introduces the composite type, rewrites the column, and backfills existing rows from the old timestamp value paired with coordinated universal time. Queries that filter on the start time project the inner instant field of the composite rather than comparing the composite column directly.

## Manual Verification Playbook

Run against a development database restored from the standard fixture dump. Use a psql session against the same database for the assertions.

1. Before applying the migration, run `SELECT count(*) FROM checklist.checklist;` and record the row count. Run `SELECT id, started FROM checklist.checklist LIMIT 5;` and record the sample values.
2. Start the backend on this branch so the migration runs on startup. Confirm the startup log shows the migration applied without errors.
3. Run `SELECT count(*) FROM checklist.checklist;` and confirm the count matches the baseline.
4. Run `SELECT id, (started).timestamp, (started).timezone FROM checklist.checklist WHERE id IN (<ids from step 1>);` and confirm each instant matches the recorded value and the time zone field is `UTC`.
5. Pick a row that was not in the sample and confirm its previous value is preserved by running the same projection.
6. Stop the backend and restart it. Confirm the startup log reports the migration as already applied and the row count and sample values are unchanged.
```

## Mixed

```
## What & Why

The pull request ships two related changes for the repeatable task surface. A backend migration adjusts the persisted shape of repeatable occurrences so each clone carries the runtime identifiers generated on the client. A frontend update sends those identifiers on add and applies the optimistic patch before the network call so the user interface reflects the new occurrence immediately.

## How

The migration renames the legacy occurrence identifier columns and adds the clone-owned field and custom-input identifier columns, backfilling existing occurrences from the prior shape. The add-repeatable endpoint validates that the supplied identifiers match the schema and returns idempotent success on exact replay. The ship application generates the full runtime identifier tree on add, applies an optimistic patch to the local store, and reconciles with the server response.

## Manual Verification Playbook

Run against a freshly restored development database with the backend and ship frontend up via the standard local compose stack. Sign in as a ship user with the `crew` role. Use the Bruno collection under `api/collections/` for direct endpoint checks. Sections A and B share a dataset; run A before B so the migration has applied before the frontend exercises the new shape.

A. Migration

1. Before applying the migration, run `SELECT count(*) FROM checklist.repeatable_occurrence;` and record the count. Capture the identifier columns for five sample rows.
2. Start the backend on this branch. Confirm the migration applies cleanly in the startup log.
3. Run the same `count(*)` query and confirm the value matches the baseline. Confirm each sample row exposes the new clone-owned identifier columns with non-null values that match the prior identifiers.
4. Restart the backend and confirm the migration reports as already applied and the row state is unchanged.

B. Frontend add-repeatable flow

1. Open a checklist that contains a repeatable section. Confirm the add-repeatable action is visible.
2. Trigger the add action. Confirm a new occurrence appears in the user interface before the network response returns and the request payload in the network pane includes the clone-owned identifiers.
3. Confirm the response status is 201 with a body that echoes the supplied identifiers, and the occurrence remains visible after reconciliation.
4. Trigger the same add action again with the same identifiers via the API client request. Confirm the response is 204 and no duplicate occurrence is created.
```
