# Release-Readiness Gates: Staleness, Canary Depth, Config Fingerprinting, Blocker/Warning

Depth for the four gate mechanics summarized under `SKILL.md`'s Decision points. Use this when designing the specific pass/fail/warn logic for a merge-and-deploy gate, not just when naming that a gate exists.

## Review staleness

An approval is a statement about a specific diff, not a standing grant. Once new commits land on top of an approved diff, the review needs to be re-earned in proportion to how much of "what got approved" still describes "what is about to ship."

Judge staleness on two independent tests, not one:

1. **Count of intervening commits.** More commits since approval means more surface the reviewer never saw.
2. **Semantic override.** Any intervening commit that is a fix, a refactor, a rewrite, an overhaul, or that touches many files invalidates the review regardless of the count above — a single "refactor auth" commit can change more than ten typo-fix commits combined, because the review was done on different code than what is about to merge.

A commit-count banding (for example: 0 commits = current, 1-3 = recent enough to proceed, 4+ = stale) and a specific file-count cutoff for the "touches many files" leg of the override (for example: more than 5 files) are workable starting points, but neither is a measured threshold — they are **chosen defaults with no independent derivation behind them**. Tune both per repo: a repo where routine commits touch many generated files needs a higher file-count cutoff; a repo that ships hourly may want a tighter commit band. State them as defaults if you carry them into a gate design, not as an established rule.

**Worked example.** A PR was approved at commit `abc123`. Three commits landed since: two are one-line typo fixes, the third is titled "refactor validation pipeline" and touches 9 files. Commit count alone (3) would land in the "recent, proceed" band under the example bands above — but the semantic override fires on both the word "refactor" and the file count, so the review is STALE regardless of the count. Surface it as a warning naming the specific commit and why it triggered the override, not just "review is stale."

When staleness triggers, treat it as a warning (see Blocker vs. warning below) — never a silent pass, and never an automatic hard block on its own.

## Canary depth scaled to diff scope

A fixed canary-verification depth is wrong in both directions: it wastes time re-checking a docs-only change end to end, and it under-verifies a frontend change by treating it the same as a config tweak. Scale the depth of the canary check to what the diff actually touches:

| Diff scope | Canary depth |
| --- | --- |
| Docs-only | Skip verification entirely |
| Config-only | Smoke check (service responds, expected status code) |
| Backend-only | Smoke check + error-log scan + performance comparison against baseline |
| Any frontend change | Full verification, including a rendered/visual check |
| Mixed scope | Full verification (the highest depth among the scopes touched) |

Classifying a diff into one of these scopes is a repo-specific concern — a path-glob rule (`**/*.md` → docs, `**/*.yml` under a config directory → config, etc.) or a dedicated classifier both work. The scope-to-depth mapping above is the reusable part; the classifier is not.

If a canary check does run, keep the pass/fail criteria concrete and stated up front rather than judged after the fact — for example: expected HTTP status, no new critical errors in logs (matching patterns like `Error`, `Uncaught`, `Failed to load`, `TypeError`, `ReferenceError` while ignoring warnings), non-blank rendered content, and a load-time ceiling. Any numeric ceiling used here is a chosen default for the repo, not a universal constant — state it as such.

## Config-fingerprint re-validation

A passed dry run is only proof that the deployment is safe *against the configuration that was active when the dry run ran*. Earned trust does not automatically carry forward when the infrastructure description itself changes underneath it.

Mechanism:

1. After a confirmed, passing validation run, compute a fingerprint over the deploy-relevant configuration — for example, a hash of the deploy-config section of the project's documentation plus a hash of the deploy workflow/pipeline definition files.
2. Store that fingerprint alongside the pass result.
3. On each subsequent run, recompute the fingerprint from the current files and compare it to the stored one.
4. On a mismatch, do not reuse the earlier pass — re-run the full validation dry run and report the change explicitly (for example, a `CONFIG_CHANGED` flag) rather than silently trusting the new configuration.

This needs nothing beyond a hash function and the two file sets being hashed (e.g. `sha256sum` over the relevant paths) — no platform-specific tooling or private data source required.

## Blocker vs. warning

Not every gate should stop the release. Collapsing "must fix" and "should look at this" into one undifferentiated failure list either blocks releases on cosmetic issues or trains people to click through every gate without reading it. Split the gate list into two tiers:

- **Blockers** — hard failures that stop the release outright. In practice this is almost always failing tests. Keep this list short and objective; every blocker should be something nobody would argue about overriding.
- **Warnings** — signals that need a human's attention but do not, on their own, prove the release is unsafe. A stale review (see above) and a changelog or version file that was not bumped for a change that should have one are canonical examples. A skipped or missing end-to-end test run and a PR description that no longer matches what the commits actually do are related warnings worth adding to the same tier.

Warnings must be surfaced explicitly — named individually, with the specific reason each one fired — and require an affirmative, recorded override to proceed (for example, an explicit "merge anyway, I understand the warnings" confirmation rather than a default "yes"). The failure mode this guards against is symmetric: silently passing a warning as if it were a clean gate, and, just as bad, treating a warning as a hard block and stopping a release that was actually fine to ship.
