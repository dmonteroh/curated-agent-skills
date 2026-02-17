# Execution Mode: Single Worker

## Use This Mode When

- A single task is being delegated.
- Root cause is still uncertain or likely shared.
- Runtime isolation is unknown.

## Steps

### 1) Define One Task (`T1`)

Include:

- Outcome
- Allowed paths
- Forbidden paths
- Claim set
- Inputs/evidence
- Acceptance criteria
- Controller-run verification commands

Output: one approved task board entry (`T1`).

### 2) Build Worker Packet

Use the template in `packet-templates.md` and include all constraints.

Output: final packet for `T1`.

### 3) Dispatch Worker

- Run one worker session.
- Worker must stay inside claim set.
- Worker returns root cause, files changed, patch summary, and recommended verification.

Output: worker report for `T1`.

### 4) Barrier + Verification

- Confirm worker session has exited.
- Run controller verification commands.
- If verification fails, re-dispatch `T1` with narrowed scope and failure evidence.

Output: verified `T1` or narrowed follow-up `T1`.

### 5) Finalize

- Produce final report.
- If dot-agent files exist, run maintenance updates.

Output: final controller summary.

## Decision Points

- If packet ambiguity remains, stop and request clarification before dispatch.
- If worker edits outside claim set, mark `needs-fix` and re-dispatch with tighter constraints.
