---
name: ui-visual-validator
description: "Verifies UI changes via rigorous, evidence-based visual validation (screenshots/video/URLs) to catch regressions, design-system drift, responsive breakage, and visual accessibility issues; judges rendered UI against explicit criteria and screens separately for generic AI-generated design patterns."
metadata:
  category: design
---
# UI Visual Validator

High-signal visual verification that is intentionally tool-agnostic and works from visual evidence.

## Use this skill when

- Confirming a UI change is actually correct (not just "different")
- Catching visual regressions before merge/release
- Needing a deterministic checklist for responsive + state coverage
- Running a visual accessibility pass (focus visibility, contrast concerns, readability)
- Judging whether a rendered page meets explicit design criteria, not only whether it changed
- Screening a rendered page for the generic patterns that mark machine-generated design

## Do not use this skill when

- Designing a UI or exploring new layouts
- Lacking visual evidence and a URL + repro steps
- Reviewing source code rather than rendered output — every criterion here is checked against what the page renders

## Required inputs

- Evidence: before/after screenshots or recordings, or a URL with repro steps
- Intended change: what should be different and why
- Scope: pages/components/states that are in scope
- Constraints: target viewports, themes, or environments (if any)
- Surface type, if known: marketing/landing page, application UI, or hybrid — this selects which criteria apply

## Workflow

1. **Inventory evidence**
   - Output: evidence table listing filename/URL, viewport, theme, state, environment.
   - If evidence is missing, stop and output `needs-evidence` with a retest plan.
2. **Classify the surface**
   - Output: `marketing`, `app`, or `hybrid`, plus the one observation that decided it.
   - Decision: `marketing` (hero-driven, brand-forward, conversion-focused) applies the landing criteria; `app` (workspace-driven, data-dense, task-focused: dashboards, admin, settings) applies the application criteria; `hybrid` applies landing criteria to the marketing sections and application criteria to the functional ones, section by section.
   - This step exists because judging a data-dense dashboard by landing-page criteria — or a landing page by application criteria — produces findings the team is right to ignore.
3. **Translate intent into goals**
   - Output: checklist of visual goals (one line per goal).
4. **Diff pass (what changed)**
   - Output: bullet list of observed diffs (objective, no judgments).
5. **Validation pass (is it correct)**
   - For each goal, mark `met`, `not met`, or `needs-evidence` and cite evidence.
6. **Responsive + state coverage**
   - Output: coverage matrix for default/hover/focus/active/disabled/loading/error/empty and breakpoints.
   - Decision: if a required state/breakpoint is missing, downgrade verdict to `partial` or `needs-evidence`.
7. **Design criteria pass**
   - Walk `Design criteria` below for the rule set the classifier selected, plus the universal checks.
   - Output: per criterion, `met` / `not met` / `not observable`, with the measured value whenever one was taken (character count, colour count, ratio).
   - `not observable` is a real result: record what evidence would make it checkable rather than guessing.
8. **Trunk test**
   - Output: which of the six questions the page answers unaided, and which it does not.
   - Decision: any unanswered question is a high-impact finding regardless of how polished the visual design is.
9. **AI-slop screen**
   - Output: `clean`, or `flagged (<n>)` naming each matched pattern and where it appears.
   - Decision: report this on its own axis. Do not merge it into the pass/partial/fail verdict and do not average it against the design criteria.
10. **Accessibility (visual) checks**
    - Output: focus visibility findings, contrast concerns, text scaling/wrapping issues.
11. **Verdict + next actions**
    - Decision rules:
      - `pass`: all goals met, no regressions, coverage complete.
      - `partial`: goals mostly met but missing coverage or minor regressions.
      - `fail`: any critical regression or goal not met.
      - `needs-evidence`: missing evidence blocks evaluation.

## Design criteria

Provenance, binding on how these are used: the WCAG ratios come from the standard. **Every other constant below is a chosen default** carried from the source rubric, not a measured finding. The falsifiable part is that the value is *measured against the evidence and reported*, not that the constant is correct. When the project states its own value — design tokens, a type scale, a brand palette — that value wins and the default is discarded.

### Universal — every surface

- **Measure**: count characters per line in body text. Chosen default: 45-75, 66 as target. Flag lines that run long enough to lose the reader's place at the wrap.
- **Palette bound**: count unique non-gray colours in the rendering. Chosen default: at most 12. A palette that keeps growing is drift, and the count makes it visible.
- **Nested radii**: inner radius = outer radius − gap. This is a relation, not a constant: a card at radius R with padding G holds a child at R−G. Concentric corners look machine-made when this is ignored.
- **Type scale**: sizes come from one ratio, not arbitrary values (chosen defaults: 1.25 major third, or 1.333 perfect fourth).
- **Line-height**: chosen defaults — 1.5 for body, 1.15-1.25 for headings.
- **Font count**: chosen default of at most 3 families in one rendering.
- **Contrast**: WCAG AA — 4.5:1 for body text, 3:1 for large text and UI components. From the standard, not a default.
- **Body text size**: readable without zooming on the smallest supported viewport (chosen default: at least 16px body, at least 12px captions/labels).
- **Spacing scale**: spacing values come from a scale, not arbitrary numbers (chosen default base: 4px or 8px).
- **Border-radius hierarchy**: radius varies by element role. One uniform large radius on buttons, cards, inputs and avatars alike is a finding, not a style.
- **Breakpoint ladder**: verify at the project's breakpoints; when none are stated, the chosen default ladder is 375 / 768 / 1024 / 1440.
- **Never** ship body text that is both small and low-contrast; **never** use a placeholder as an element's only label (it disappears once the field has content); **never** drop the visited/unvisited link distinction; **never** float a heading equidistant between two sections — it must sit closer to the section it introduces.

### Landing criteria — `marketing` surfaces

- First viewport reads as one composition, not a dashboard.
- Brand-first hierarchy: brand, then headline, then body, then call to action.
- Typography is expressive and chosen, not a default stack.
- Hero is full-bleed, and carries one headline, one supporting sentence, one CTA group, one image — no cards in the hero.
- One job per section: one purpose, one headline, one short supporting sentence.
- Motion is intentional and used for entrance, scroll relationship, or reveal — not decoration.
- Colour system is defined as variables with one accent by default.
- Copy is product language, not design commentary.

### Application criteria — `app` surfaces

- Calm surface hierarchy, strong typography, few colours.
- Dense but readable, with minimal chrome.
- Layout organizes into primary workspace, navigation, secondary context, one accent.
- Cards appear only where the card *is* the interaction — not as a mosaic of decorative panels.
- Section headings state what the area is or what the user can do there ("Selected KPIs", "Plan status").
- Avoid: dashboard-card mosaics, thick borders, decorative gradients, ornamental icons.

### Micro-rules

These are the checks a reviewer will not volunteer unprompted. Each is observable in the rendering, or in computed styles when the app can be run.

- `font-variant-numeric: tabular-nums` on any column of numbers. The tell is a numeric column whose digits do not align vertically between rows.
- `color-scheme` declared on the root element whenever the page has a dark theme. Without it the browser keeps form controls, scrollbars and the text caret in their light-theme rendering — a white scrollbar or checkbox against a dark surface is the visible symptom.
- The accent colour is desaturated for dark surfaces rather than reused unchanged from the light theme. (The source rubric names a 10-20% reduction; that range is unexplained there, so the rule is stated without it — check that the accent was adjusted, not by how much.)
- Dark-mode body text is off-white rather than pure white.
- `text-wrap: balance` or `text-pretty` on headings; the tell is a heading whose last line holds one orphan word.
- Real typographic characters: the ellipsis character, not three periods; curly quotes, not straight ones.
- No added letterspacing on lowercase body text.
- `env(safe-area-inset-*)` respected, so content clears notches and home indicators.
- Motion animates `transform` and `opacity` only, with properties listed explicitly rather than `transition: all`.

## Trunk test

Named for the test in Steve Krug's *Don't Make Me Think*, and used here as a check, not reproduced from it. Take one screen with no prior context and ask whether the page itself answers, unaided: what site this is, which page you are on, what the major sections are, what the options are at this level, where this page sits in the hierarchy, and how to search. Score each question answered or not.

A failure here outranks visual polish: an unanswered trunk-test question is a high-impact finding on a beautiful page.

## AI-slop screen

An independent axis. A page can satisfy every criterion above and still look like it was generated rather than designed; that outcome is exactly what this screen exists to surface, and folding it into the main verdict hides it. Slop patterns do not by themselves turn a verdict to `fail` — they are reported separately, unless a pattern is also a regression against the intended change or against the project's design system, in which case it is both.

The test for each: would a designer at a studio that signs its work ship this?

1. Purple/violet/indigo gradient backgrounds, or blue-to-purple colour schemes.
2. The three-column feature grid — icon in a coloured circle, bold title, two-line description, repeated three times symmetrically. The single most recognizable machine-generated layout.
3. Icons in coloured circles used as section decoration.
4. Centred everything: headings, descriptions and cards all centre-aligned.
5. One uniform, large border-radius on every element regardless of role.
6. Decorative blobs, floating circles, wavy dividers — decoration standing in for content in a section that is actually empty.
7. Emoji used as design elements: in headings, as bullets, as substitute icons.
8. A coloured left border on cards as the only differentiator between them.
9. Generic hero copy — "Welcome to [X]", "Unlock the power of…", "Your all-in-one solution for…".
10. Cookie-cutter section rhythm: hero, three features, testimonials, pricing, CTA, every section the same height.
11. `system-ui` or `-apple-system` as the primary display or body font — the "gave up on typography" signal.

**Count note:** the source rubric labels this list "10 patterns" and then enumerates 11. Eleven is correct — re-counted against the source, with no duplicate entries; the eleventh (the system font stack) is a distinct pattern, not a restatement.

**Provenance:** the pattern list is adapted from a third-party design-review rubric, which credits an OpenAI developer-blog post on frontend design (dated March 2026 there) plus its own in-house methodology. That upstream citation could not be verified from this repository: treat it as reported, not confirmed.

## Common pitfalls

- Calling a change "correct" without listing visible evidence.
- Skipping focus/contrast checks because the change seems minor.
- Ignoring states that are in scope (loading/error/empty) for the component.
- Mixing subjective language with objective observations.
- Averaging the AI-slop result into the design verdict, which conceals a page that is technically correct and entirely generic.
- Applying landing criteria to an application surface, or the reverse, because the classifier step was skipped.
- Quoting a chosen default back as a requirement when the project's own design system states a different value.
- Reporting a criterion as met when the evidence cannot show it; `not observable` plus a retest note is the honest result.

## Output contract

Use this exact section order:

1. **Verdict**: pass/fail/partial/needs-evidence
2. **AI-Slop Screen**: `clean` or `flagged (<n>)` with the patterns named — reported independently of the verdict
3. **Surface Classification**: marketing/app/hybrid + the observation that decided it
4. **Evidence Inventory**: list of artifacts with viewport/theme/state
5. **Goals**: checklist with status per goal
6. **Observations (Objective)**: what is visible
7. **Intended Diffs Observed**: which goals are satisfied
8. **Regressions / Unintended Changes**: anything unexpected
9. **Design Criteria Findings**: per criterion — met/not met/not observable, with measured values
10. **Trunk Test**: which questions the page answers unaided
11. **Accessibility (Visual)**: focus visibility, contrast concerns, readability
12. **Responsive + State Coverage**: breakpoints and states covered + gaps
13. **Issues (With Severity)**: blocker/major/minor/nit
14. **Retest Plan**: missing evidence + how to capture it

## Examples

**Output snippet**

- Verdict: partial
- AI-Slop Screen: flagged (2) — three-column feature grid in "Why us"; uniform 16px radius on buttons, cards and inputs alike
- Surface Classification: hybrid — marketing hero above the fold, settings table below
- Evidence Inventory: `settings-desktop-before.png` (1280x800, light, default)
- Goals: [ ] Updated button padding (needs-evidence at 768px)
- Design Criteria Findings: measure — not met (body copy at 104 characters per line, chosen default is 45-75); palette — met (9 non-gray colours); nested radii — not met (12px card holds a 12px thumbnail inside 8px padding, expected 4px)
- Trunk Test: "where am I in the scheme of things" unanswered — no breadcrumb or active-nav marker (high impact)
- Regressions / Unintended Changes: Hover state missing from evidence

**Contrast — the same page, two ways of reporting it**

- Wrong: "Design score B−; looks a bit generic but broadly fine." One blended judgment, no measurement, nothing anyone can act on or dispute.
- Right: "Verdict `pass` (no regressions, coverage complete). AI-Slop Screen `flagged (3)`: gradient hero, three-column icon grid, centred everything." The change shipped correctly *and* the page is generic — two findings that must not cancel each other out.

## Optional automation

- Report scaffold script: `scripts/visual_report.sh`
- Usage: `./scripts/visual_report.sh "<subject>" <output-path>`
- Requirements: bash, standard coreutils (`date`, `mkdir`, `dirname`).
- Verification: confirm the report file exists and open it to fill in findings.
- Template reference: `references/report-template.md` (matches output contract order).

## References

- Index: `references/README.md`
