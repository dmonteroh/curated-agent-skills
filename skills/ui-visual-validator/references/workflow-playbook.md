# UI Visual Validator - Workflow Playbook

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
- Design references: design tokens or component spec (if any).

## Workflow

### Step 0 - Evidence Inventory

Start from the enumeration, not from the pile of files you were handed: write down every page, route, slide, tab, modal state, breakpoint and scroll position in scope, and its count. The inventory is then a comparison — enumerated items against artifacts present — and the gaps fall out of it instead of being noticed later.

- List each evidence artifact (filename/URL) with:
  - viewport
  - theme
  - state
  - environment (prod/stage/local)
  - capture time, against the timestamp of the last change to the rendered source

Then apply the admissibility gates from `SKILL.md` before judging anything:

- Any enumerated item with no artifact is a coverage gap, and a coverage gap caps the verdict at `partial` or `needs-evidence` — it never averages out against the pages that were captured.
- Any artifact older than the last source change goes back for re-capture. If the source's change time is unknown, ask for it; an undated capture cannot support a `pass`.
- Open each artifact before using it. Wrong format for its extension, black or missing regions, or dimensions that do not match the label mean the capture pipeline is broken. Report it as `[evidence]` and get it re-shot; do not open product findings from a broken frame, and do not spend the review round on it.
- For anything animated, expect three frames per transition and a start/mid/end sequence per reveal. One resting frame supports a finding about the resting state and nothing else — every motion criterion is `not observable` until the frames arrive.

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

### Step 3a - Criteria, Trunk Test, Slop Screen, And Faked-Surface Check

Before state coverage, classify the surface (marketing / app / hybrid), walk the design criteria for the rule set that classification selects, run the trunk test, run the AI-slop screen, and run the faked-surface check. Report each criterion as met / not met / not observable with the measured value where one was taken, and keep the slop result on its own axis — never averaged into the verdict.

If the rendering carries Korean, Japanese or Chinese text, walk `references/cjk-line-breaking.md` here, on every page's capture. Read the actual line breaks in the image; a summary of the copy will not show them.

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

### Step 5 - Accessibility (Visual) Checks (No Tools Required)

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

### Step 6 - Responsive + State Coverage Summary

- No overlapping text.
- No clipped content.
- Touch targets are not too small.
- Sticky headers/footers do not cover content.
- Modals/drawers remain usable on small screens.

Report responsive results alongside the state coverage list to match the output contract.

### Step 7 - Severity & Next Actions

Classify issues so teams can act quickly:

- `blocker`: prevents use / major a11y failure / data unreadable
- `major`: breaks design system or key flow
- `minor`: visual polish issue
- `nit`: optional

Tag each one `[product]` or `[evidence]` as it is written, not afterwards. The tag decides who acts: `[product]` goes to whoever owns the source, `[evidence]` goes to whoever owns the capture pipeline, and a mistagged finding sends a code change to fix a screenshot bug.

### Step 8 - Completion Gate

The report is not the end of the loop; the gate in `SKILL.md` is. Two operational notes:

- Run the loop per finding class. After a `[product]` fix, re-capture the pages the fix touched and take the result to a review that is starting fresh, not to the one already holding the previous findings. After an `[evidence]` fix, re-shoot the broken artifacts only and leave the source alone.
- The final approving round is different from the intermediate ones: it judges a complete, current capture set, not the delta. Partial re-captures are a round-trip optimization and never the basis of the closing verdict.
