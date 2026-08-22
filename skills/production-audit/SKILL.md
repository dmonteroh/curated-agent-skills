---
name: production-audit
description: "Produces a ship-or-block readiness verdict for one repository from local, user-authorized evidence only, naming both the evidence checked and the evidence missing. Use when asked whether an application is ready to ship, what would break in production, or what must be fixed before a launch."
metadata:
  category: devops
---
# Production Audit

Two things separate it from a general code review: the audit is assembled only from evidence already on the machine or specifically authorized by the user, and a short list of named conditions puts a ceiling on the verdict no matter how good the rest of the evidence looks.

## Use this skill when

- The user asks "is this production-ready", "what would break in prod", "what did we miss", or "ready to ship?"
- A feature has merged and needs a pre-deploy or post-merge risk pass
- A public launch, demo, customer rollout, or investor walkthrough is close
- CI is green and the user wants remaining production risk rather than test status
- A release branch, pull request, current checkout, or an authorized deployed URL is available as evidence

## Do not use this skill when

- The work is line-level secure coding during active implementation — reviewing the diff as it is written is a different lens and comes first
- The repository is a library, template, scaffold, or docs-only, unless the question is packaging and release readiness rather than application readiness
- The ask is a scoped security engagement with a threat model, a findings table backed by quoted evidence, and a prioritized remediation plan. This produces one verdict over one repository, not that
- The ask is a formal compliance audit. This is engineering triage, not legal, financial, medical, or regulatory certification
- The only evidence is a product idea — no repository, deployment, CI, or runtime surface exists to read
- The question is which release gates a delivery pipeline should have: how blockers and warnings are tiered, what a gate does when its signal is missing rather than failing, how deep a canary check runs. That is pipeline design. This skill answers "is this repository ready to ship right now?", not "what gates should our pipeline have?"

## Constraints

- Build the audit from evidence already present locally or explicitly authorized by the user for this pass.
- Do not run unpinned remote code, upload repository contents to a third-party service, or invoke an external scanner unless the user approves that specific tool and that specific data flow. Reaching for a hosted scanner is the common reflex here; refusing it is what makes the audit runnable against a private repository at all.
- If a deployed URL is in scope, restrict checks to that URL and avoid credentialed actions unless the user supplies a safe test account.
- Report missing evidence as missing. Never substitute an assumption for a check that was not run.

## Workflow

1. Establish the release surface: what is shipping, to whom, and on what date or trigger.
   - Output: the artifact under audit (branch, PR, tag, or checkout) and the launch it is attached to.
2. Read branch state and recent changes before opening any file. Cheap local signals come first because they scope everything after them.
   ```text
   git status --short --branch
   git log --oneline --decorate -20
   git diff --stat origin/main...HEAD
   ```
   - Output: what changed, how far the branch has drifted, and whether the tree is clean.
3. Inspect only the boundaries this repository actually has. For each one present, the question is whether it trips a ceiling condition below — not whether it is ideal.
   - Routes, handlers, and jobs that read or write sensitive data, and where authorization is enforced for each.
   - Payment, fulfillment, and webhook handlers, and whether a repeated or out-of-order delivery is a no-op.
   - Migrations: whether they run forward on a clean database and what the recovery path is.
   - Any place a secret could reach a client bundle, a log line, example output, or a committed file.
   - Output: a list of boundaries present, boundaries absent, and which ceiling conditions each one touches.
4. Check the release machinery: CI status for this branch, whether the launch-critical path is exercised end to end, environment variables named and validated at startup, and a documented rollback path with an owner.
   - Output: CI state, end-to-end coverage of the critical path, and the rollback path or its absence.
5. Emit the verdict, applying the ceilings in Decision points, followed by the report in the output contract.
   - Output: verdict word, blockers, high-value fixes, evidence checked, evidence missing, next action.

Anything else worth fixing goes in `High-value fixes`. This skill does not enumerate those checks, because a competent general review already produces them; what it enumerates is the short set that can override an otherwise good verdict.

## Decision points

- **The verdict is a word, not a score.** Worst to best: `Blocked` — do not ship until the top risks are fixed. `Risky` — ship only behind a small rollout or internal beta. `Launchable with caveats` — ship if the owners accept the listed risks. `Strong` — no obvious launch blockers in the available evidence.
- **Ceiling of `Risky`: the verdict cannot be better than `Risky` if any of these is true.**
  - Authentication or authorization is missing on sensitive data.
  - Payment or fulfillment webhooks are not idempotent.
  - Required migrations cannot be run safely.
  - Secrets are exposed in client bundles, logs, or committed files.
  - There is no rollback path for a high-impact release.
- **Ceiling of `Launchable with caveats`: the verdict cannot be better than that if CI is not green, or the launch-critical path was not exercised end to end.**
- **A ceiling caps the verdict; it does not set it.** The verdict may land lower than the ceiling for other reasons. It may never land higher, however strong the rest of the evidence looks — that is the entire point of the mechanism, and a verdict raised past a ceiling because "everything else is solid" is the failure this skill exists to prevent.
- **A ceiling condition that could not be checked is not a ceiling condition that passed.** It goes in `Evidence missing`, and the verdict states that it is bounded by unread evidence.

## Output contract

Lead with one sentence carrying the verdict word and the one or two risks that set it. Then:

- `Blockers` — must-fix items before deploy.
- `High-value fixes` — the next fixes, if the user wants to improve the position.
- `Evidence checked` — files, commands, CI runs, deployed URLs, or PRs actually inspected.
- `Evidence missing` — what was not available and what it would change. Never omit this section and never leave it empty by default; naming the confidence bound is what separates an audit from an impression.
- `Next action` — one concrete fix or verification step.

Keep the strengths short. The user asked about readiness, so the useful answer is the remaining risk and the next step.

## Examples

**Worked case.**

User:

```text
is this ready to ship?
```

Response:

```text
Production audit: Risky — Stripe webhooks are verified but not idempotent, and the pending migration has no rollback note.

Blockers:
- Add idempotency for `checkout.session.completed` before fulfilling orders.
- Write and test the rollback path for `20260511_add_billing_state.sql`.

High-value fixes:
- Add a health check that verifies database and payment-provider reachability.
- Add one end-to-end path for upgrade, webhook fulfillment, and billing-page refresh.

Evidence checked:
- `api/stripe/webhook.ts`
- `db/migrations/20260511_add_billing_state.sql`
- CI run for the release branch

Evidence missing:
- No staging deployment was available, so the migration was never observed running against a populated database.

Next action: Want me to patch webhook idempotency first?
```

**Wrong beside right — the ceiling.**

- Wrong: "Tests pass, CI is green, observability is in place, the team is experienced — `Strong`, with a note that the fulfillment webhook is not idempotent." The one condition that can duplicate a customer's order has been averaged away against everything that is fine.
- Right: "`Risky`. Fulfillment webhooks are not idempotent, which caps this regardless of the rest; everything else on this list is genuinely in good shape."

## Common pitfalls

- Treating green CI as production readiness
