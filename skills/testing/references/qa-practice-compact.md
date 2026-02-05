# QA Practice (Compact, High-ROI)

This is not “manual QA theater.” Use it when automation is not enough, or when fast risk discovery is needed.

## Exploratory testing charter (60 minutes)

```md
Charter: Explore <feature> focusing on <risk area>
Mission: Find defects in <specific behavior>
Duration: 60 min

Test ideas:
- boundary values, invalid input
- interrupted flows (refresh, back/forward, offline)
- permission changes mid-session
- concurrency/conflicts (double submit, parallel edits)
- recovery after errors (retry, cancel, undo)

Findings:
1. [HIGH] <issue + impact>
2. [MED] <issue + impact>

Coverage: <what was explored> | Risks: <new risks found>
```

## Accessibility smoke checks (fast)

- Keyboard-only: can primary controls be reached and operated?
- Focus visibility: is focus clearly visible at all times?
- Labels: inputs have labels; icon-only buttons have accessible names.
- Contrast: primary text on background and text-on-action are readable.

If the project has an automated a11y runner (axe, etc.), integrate it into the E2E layer, but keep the smoke checks.

## Risk-based testing (choose depth intentionally)

Test depth should track risk:

- High impact + high likelihood: deeper tests + negative cases + monitoring gate.
- High impact + low likelihood: at least one regression test + runbook note.
- Low impact: smoke only.

## Quality gates (practical)

- Feature is not “done” without at least:
  - one happy path automated test at the right layer
  - one negative case at the boundary most likely to break
  - deterministic repro steps for any known issue
