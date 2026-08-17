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
