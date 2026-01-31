# Evaluations (E2E Usefulness)

The point of evals is to verify an agent can use your tools to complete realistic tasks reliably.

## Minimum eval set (recommended)

- 2x read-only tasks (search, filter, summarize)
- 2x write tasks (create/update) with a validation failure case
- 1x “large data” task (pagination/filtering, token control)

## What to capture

- Exact prompt packet used for the run
- Tool calls made by the agent (inputs/outputs)
- Pass/fail criteria per scenario
- Notes on confusion points (unclear IDs, missing filters, noisy output)

## Regression discipline

- When a tool changes, re-run the eval set.
- If a previously passing scenario fails, fix the tool or the contract before shipping more.

