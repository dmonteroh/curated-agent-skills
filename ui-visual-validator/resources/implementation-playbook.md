# UI Visual Validator - Implementation Playbook

Use this playbook when you need a deterministic, high-signal visual validation pass.

This skill is intentionally tool-agnostic. If your repo already uses a visual regression tool (Playwright snapshots, Chromatic, Percy, etc.), use it for evidence generation, but do not require it.

## Inputs (Ask For These)

Minimum:

- Evidence: before/after screenshots or recordings (or a URL + steps to reproduce).
- Goal: what change was intended.
- Scope: what pages/components/states are in-scope.

Strongly recommended:

- Viewports tested: e.g. `375x812`, `768x1024`, `1280x800`.
- Theme modes: light/dark/high-contrast (if relevant).
- Interaction states: hover/focus/active/disabled/loading/error/empty.
- Design references: Figma link, design tokens, or component spec (if any).

## Output Contract (Always Produce)

1) Verdict
- `pass` | `fail` | `partial` | `needs-evidence`

2) Observations (objective)
- Bullet list: what is visible.

3) Diffs & Regressions
- Intended diffs observed (mapped to goals).
- Unintended diffs/regressions.

4) Accessibility Visual Checks
- Focus visibility, contrast concerns, text sizing/line-height issues.

5) Responsive/Breakpoints
- Layout integrity across viewports.

6) Retest Plan
- What new evidence is needed and how to collect it.

## Deterministic Workflow

### Step 0 - Evidence Inventory

- List each evidence artifact (filename/URL) with:
  - viewport
  - theme
  - state
  - environment (prod/stage/local)

If evidence is incomplete, stop and output `needs-evidence` with a retest plan.

### Step 1 - Identify The Visual Goal(s)

Convert goals into a checklist. Example:

- Goal A: button has new padding and corner radius
- Goal B: focus ring matches design token and is visible

### Step 2 - Diff Pass (What Changed)

- Identify what changed at a glance.
- Then zoom into:
  - typography (font size/weight/line-height)
  - spacing (padding/margins/gaps)
  - alignment (baseline/center)
  - color (background/text/borders)
  - iconography (size/stroke/position)

### Step 3 - Validation Pass (Is It Correct)

For each goal item:

- Evidence that it is achieved (what you see).
- Evidence that it is not achieved (what contradicts the goal).
- If ambiguous: mark as `needs-evidence` and specify the missing state/viewport.

### Step 4 - State Coverage

For each relevant component/page, confirm visually:

- default
- hover
- focus (keyboard)
- active/pressed
- disabled
- loading
- error
- empty/no-data

If a state is missing from evidence, call it out.

### Step 5 - Accessibility Visual Checks (No Tools Required)

- Focus indicator is:
  - present on all interactive elements
  - not clipped by overflow
  - visible on similar-colored backgrounds
- Contrast concerns:
  - small text on tinted backgrounds
  - disabled states that become unreadable
  - link color vs surrounding text
- Text scaling:
  - truncation that hides critical info
  - line-height too tight
  - wrapping that breaks layouts

### Step 6 - Responsive Checks

- No overlapping text.
- No clipped content.
- Touch targets are not too small.
- Sticky headers/footers do not cover content.
- Modals/drawers remain usable on small screens.

### Step 7 - Severity & Next Actions

Classify issues so teams can act quickly:

- `blocker`: prevents use / major a11y failure / data unreadable
- `major`: breaks design system or key flow
- `minor`: visual polish issue
- `nit`: optional

## Visual Validation Report Template

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
