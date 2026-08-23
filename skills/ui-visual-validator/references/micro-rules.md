# Micro-rules

Companion to the `Design criteria` section of `SKILL.md`, which selects the rule sets and states the provenance that binds them: apart from the WCAG ratios, every constant is a chosen default carried from the source rubric, and a value the project states for itself — design token, type scale, brand palette — wins over the default. What is falsifiable is that the value was measured against the evidence and reported.

Walk this file at workflow step 7, after the universal checks and the rule set the surface classification selected. Report each as `met` / `not met` / `not observable`, with the measured value whenever one was taken.

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
- `will-change` appears only where a first-frame stutter was actually observed, and only on compositor-friendly properties (`transform`, `opacity`, `filter`). `will-change: all` is a finding: it asks the browser to promote everything and gives back the cost the hint exists to avoid.
- Images carry a hairline neutral inset outline — an `outline` pulled inside the box with a negative `outline-offset`, black at low alpha on light surfaces and white at low alpha on dark — so an image edge does not dissolve into the surface behind it. The tell is a pale photograph on a white card with no discernible edge. Image outlines are never tinted with the brand palette. (The source rubric's 1px width and 10% alpha are chosen defaults; what is checkable is that the edge is defined and neutral.)

