# Visual Validation Report Template

Copy and fill:

```md
# Visual Validation Report: <subject>

Date: <YYYY-MM-DD>
Scope: <pages/components>
Evidence: <filenames/urls>

## Verdict

<pass|fail|partial|needs-evidence>

## Goals

- [ ] <goal 1>
- [ ] <goal 2>

## Observations (Objective)

- 

## Intended Diffs Observed

- 

## Regressions / Unintended Changes

- 

## Accessibility Visual Checks

- Focus visibility: <ok|concerns>
- Contrast concerns: <none|list>
- Text scaling/wrapping: <ok|concerns>

## Responsive Checks

- Mobile: <ok|issues>
- Tablet: <ok|issues>
- Desktop: <ok|issues>

## State Coverage

- default: <ok|missing>
- hover: <ok|missing>
- focus (keyboard): <ok|missing>
- active/pressed: <ok|missing>
- disabled: <ok|missing>
- loading: <ok|missing>
- error: <ok|missing>
- empty/no-data: <ok|missing>

## Issues (With Severity)

- [ ] (<blocker|major|minor|nit>) <issue> - evidence: <where>

## Retest Plan

- Needed evidence: <state/viewport/theme>
- Steps to capture: <how>
```

## Notes On Measurements

If you only have screenshots:

- Compare relative spacing using nearby known elements (e.g., icon size vs padding).
- Look for baseline alignment: text should align cleanly across rows.
- Identify clipping by checking shadows, focus rings, and borders at edges.

If you can run the app:

- Use browser devtools to inspect computed values for padding/font-size/line-height.
- Use responsive mode to capture standardized viewports.
