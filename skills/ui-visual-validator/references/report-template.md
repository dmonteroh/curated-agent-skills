# Visual Validation Report Template

Copy and fill:

```md
# Visual Validation Report: <subject>

Date: <YYYY-MM-DD>
Scope: <pages/components>

## Verdict

<pass|fail|partial|needs-evidence>

## AI-Slop Screen

<clean|flagged (<n>)> - <pattern name>: <where it appears>

Reported independently of the verdict; never averaged into it.

## Faked-Surface Check

- <region>: <live|suspect|not observable> - tell: <what raised it> - settles with: <capture>

## Surface Classification

<marketing|app|hybrid> - decided by: <observation>

## Evidence Inventory

Enumerated in scope: <n> <pages|slides|routes|states>; captured: <n>.

- <artifact> (<viewport>, <theme>, <state>, <environment>, captured <before|after> the last source change)

## Goals

- [ ] <goal 1>
- [ ] <goal 2>

## Observations (Objective)

- 

## Intended Diffs Observed

- 

## Regressions / Unintended Changes

- 

## Design Criteria Findings

- <criterion>: <met|not met|not observable> - measured: <value> (chosen default: <value>)

## Trunk Test

- What site is this: <answered|not answered>
- What page am I on: <answered|not answered>
- Major sections: <answered|not answered>
- Options at this level: <answered|not answered>
- Position in the hierarchy: <answered|not answered>
- How to search: <answered|not answered>

## Accessibility (Visual)

- Focus visibility: <ok|concerns>
- Contrast concerns: <none|list>
- Text scaling/wrapping: <ok|concerns>

## Responsive + State Coverage

- Breakpoints: Mobile <ok|issues>, Tablet <ok|issues>, Desktop <ok|issues>
- States: default <ok|missing>, hover <ok|missing>, focus (keyboard) <ok|missing>, active/pressed <ok|missing>, disabled <ok|missing>, loading <ok|missing>, error <ok|missing>, empty/no-data <ok|missing>
- Coverage gaps: <list missing states/viewport/theme>

## Issues (With Severity)

- [ ] (<blocker|major|minor|nit>) [product|evidence] <issue> - evidence: <where>

## Retest Plan

- Needed evidence: <state/viewport/theme>
- Steps to capture: <how>

## Completion Gate

- Independent (non-authoring) review returned: <pass|blocking findings>
- Evidence set judged: <complete and current|gaps>
- <Satisfied|Remaining gaps and who accepted them>
```

## Notes On Measurements

If you only have screenshots:

- Compare relative spacing using nearby known elements (e.g., icon size vs padding).
- Look for baseline alignment: text should align cleanly across rows.
- Identify clipping by checking shadows, focus rings, and borders at edges.
- Measure line length by counting characters in one full line of body copy; report the count, not an impression.
- Count unique non-gray colours by naming each distinct hue you can see (brand, accents, semantic states, tinted surfaces); report the count.
- Check nested radii by comparing a container corner against the corner of the child inside it: the child should look tighter by the padding gap, not identical.
- Before measuring anything, confirm the file is what it claims: format matching its extension, no black or missing regions, dimensions equal to the viewport in its label. A capture that fails this is a tooling defect and is reported as `[evidence]`, not as a design finding.
- For a region suspected of being a pasted image, put its two breakpoint captures side by side: real components reflow, a raster does not.

If you can run the app:

- Use browser devtools to inspect computed values for padding/font-size/line-height.
- Use responsive mode to capture standardized viewports.

## Worked example — one filled report, abridged to one line per section

The same example appears in abridged form under `Examples` in `SKILL.md`; this is the complete set of lines.

- Verdict: partial
- AI-Slop Screen: flagged (2) — three-column feature grid in "Why us"; uniform 16px radius on buttons, cards and inputs alike
- Faked-Surface Check: hero "dashboard preview" — suspect (identical internal layout at 375 and 1280 while everything around it reflowed); settles with a 768px capture of that region
- Surface Classification: hybrid — marketing hero above the fold, settings table below
- Evidence Inventory: 14 states enumerated, 12 captured; `settings-desktop-before.png` (1280x800, light, default, captured after the last source change)
- Goals: [ ] Updated button padding (needs-evidence at 768px)
- Regressions / Unintended Changes: Hover state missing from evidence
- Design Criteria Findings: measure — not met (body copy at 104 characters per line, chosen default is 45-75); palette — met (9 non-gray colours); nested radii — not met (12px card holds a 12px thumbnail inside 8px padding, expected 4px)
- Trunk Test: "where am I in the scheme of things" unanswered — no breadcrumb or active-nav marker (high impact)
- Issues: (blocker) `[evidence]` `settings-mobile-after.png` is a JPEG named `.png` and its lower third is black — re-shoot before this page can be judged; (major) `[product]` focus ring clipped by the card's overflow
- Completion Gate: not satisfied — no review by anyone other than the change's author, and two states still uncaptured
