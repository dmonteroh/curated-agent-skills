# Release-Readiness Gates: Staleness, Canary Depth, Config Fingerprinting, Transformed Artifacts, Blocker/Warning

Depth for the five gate mechanics summarized under `SKILL.md`'s Decision points. Use this when designing the specific pass/fail/warn logic for a merge-and-deploy gate, not just when naming that a gate exists.

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

## Verifying an artifact the release transformed

Some releases do not ship the artifact that was built and approved. A step on the way to production rewrites it — recompressing or repackaging a bundle, minifying, stripping symbols, re-encoding media, converting a container image to another runtime's format, quantizing a model. That step introduces a failure class the rest of the pipeline cannot see: **the transform's exit status, the file's existence, and a successful load all prove nothing.** A malformed transform still produces a structurally valid artifact that opens without error. The damage is to behavior, not to structure, so every check that inspects the file rather than running it passes.

Gate the transform on replayed behavior:

1. **Keep a fixed, version-controlled set of recorded inputs**, together with the outputs the pre-transform artifact produced for them. How many is a per-artifact choice — enough to cover the behaviors the transform can plausibly damage — and any count carried in from elsewhere is a chosen default, not a measured one.
2. **Replay them through the transformed artifact in its actual target runtime**, the one that will serve it in production — not a convenient equivalent, and not the build environment. A substitute runtime supplies its own defaults for precisely the settings the transform touched, so it can only report that the artifact loads.
3. **Persist the execution settings from the pre-transform run and reuse that record** for the post-transform run, rather than configuring the second run to nominally matching values. Drift in any setting that shapes the output turns a healthy artifact into a spurious failure and, worse, can hide a real one.
4. **Pick the comparison from whether the transform is lossless or lossy.** This is the step most gates get wrong, and getting it wrong in either direction disables the gate.

**Lossless transform — byte equality is the gate.** Repackaging, a format conversion that preserves content, a rebuild that should be reproducible: output must match exactly, and any divergence is a defect to investigate rather than a tolerance to widen.

**Lossy transform — byte equality is unmeetable by design and must not gate.** A lossy step legitimately changes the output for every input; a byte-comparison gate over it fails on every run, and a gate that always fails gets switched off, which leaves the transform verified by nothing. The gate is instead **agreement between the downstream checker's verdicts before and after**: run whatever already decides that an output is acceptable — the assertion, the schema or format validator, the perceptual or structural check, the grader — against both the pre- and post-transform output, and compare verdicts. Zero exact matches with every verdict in agreement is the expected healthy result, not a warning. Keep the byte-level diff in the report for triage, because it says how far the output moved, but never let it decide.

Two conditions on the gate itself:

- **An approval of the pre-transform artifact is not evidence about the transform.** Whatever cleared the build — tests, review, a promotion decision — was earned by the artifact that went in, and says nothing about the one that comes out.
- **Re-run it on version bumps of the transform toolchain or of the target runtime**, not only on the first release that introduced the step. Both are free to change what the same transform produces.

When the gate fails, the mismatched pairs are the diagnostic, not the failure count: read the pre and post outputs side by side. Output that is garbled or structurally broken points at the transform's configuration; output that is well-formed and confidently wrong points at content the transform degraded.

## Blocker vs. warning

Not every gate should stop the release. Collapsing "must fix" and "should look at this" into one undifferentiated failure list either blocks releases on cosmetic issues or trains people to click through every gate without reading it. Split the gate list into two tiers:

- **Blockers** — hard failures that stop the release outright. In practice this is almost always failing tests. Keep this list short and objective; every blocker should be something nobody would argue about overriding.
- **Warnings** — signals that need a human's attention but do not, on their own, prove the release is unsafe. A stale review (see above) and a changelog or version file that was not bumped for a change that should have one are canonical examples. A skipped or missing end-to-end test run and a PR description that no longer matches what the commits actually do are related warnings worth adding to the same tier.

Warnings must be surfaced explicitly — named individually, with the specific reason each one fired — and require an affirmative, recorded override to proceed (for example, an explicit "merge anyway, I understand the warnings" confirmation rather than a default "yes"). The failure mode this guards against is symmetric: silently passing a warning as if it were a clean gate, and, just as bad, treating a warning as a hard block and stopping a release that was actually fine to ship.
