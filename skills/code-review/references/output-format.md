# Output Format

Default output order (optimize for actionability):

1) Findings (ordered by severity)
2) Open questions / assumptions
3) Suggested follow-ups (tests, monitoring, docs)
4) Change summary (only after findings)

Sections below are added only when the corresponding step ran.

## Severity scale

- **BLOCKER**: correctness/security issue that must be fixed before merge
- **HIGH**: likely bug, vuln, or major reliability issue
- **MEDIUM**: correctness edge case, maintainability risk, perf regression risk
- **LOW**: style/nit, minor clarity improvements

## Findings format

Each finding should include:
- file path + line reference (if available)
- severity
- problem statement (1-2 sentences)
- why it matters (risk / impact)
- concrete fix suggestion (short)

Example:

```
- src/auth/session.ts:42 (HIGH): Session cookie not set with SameSite/HttpOnly.
  Risk: cookie theft / CSRF amplification in browsers.
  Fix: set HttpOnly=true, SameSite=Lax/Strict, Secure=true in prod; add a test.
```

## Advisory scan line

One line, expressed as a delta against the base ref, marked informational:

```
Scan (informational): +2 new / -3 removed vs origin/main
```

Omit the line entirely when the scanner is unavailable.

## Bot-comment triage block

```
Bot comments: 7 open — 3 valid (merged into findings), 2 already fixed (replied),
1 false positive (reply drafted, awaiting confirmation), 1 skipped by history match.
```

## Second-opinion block

Per-pass verdicts, then three lists kept separate — merging them discards the signal the second pass exists to produce:

```
Pass A: FAIL (1 BLOCKER)   Pass B: PASS   Combined: FAIL

Overlap (both passes):
- src/auth/session.ts:42 (HIGH): ...
Unique to pass A:
- src/api/limits.ts:88 (BLOCKER): ...
Unique to pass B:
- src/db/pool.ts:17 (MEDIUM): ...
```

## Applied-fix counts

Verified is a breakdown of applied, not a sibling total:

```
Fixes: 12 applied (11 verified, 1 best-effort), 4 deferred
```

## Tone rules (fast + constructive)

- Prefer "I think" + evidence over absolutes.
- Ask questions when intent is unclear rather than guessing.
- Separate "must fix" from "nice to have".
