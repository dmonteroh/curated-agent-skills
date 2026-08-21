---
name: frontend-design
description: "Implement distinctive, production-grade frontend UI code with high design quality. Use when asked to build or style components/pages/apps and deliver working UI code; avoid for design-only briefs without implementation."
metadata:
  category: design
---
This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. It focuses on real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Use this skill when

- Building or styling frontend UI with real code (HTML/CSS/JS, React, Vue, etc.)
- The user expects a distinct aesthetic direction and production-grade polish
- Translate a brief into a cohesive visual system and layout
- The surface is an application shell — dashboard, settings, list-detail, inbox, split pane — whose fixed regions and scrolling body have to hold real content
- A layout that looked correct against mock content breaks once content is empty, long, or unbroken
- The surface is a browser-run slide deck or another full-viewport panel sequence, where each panel has to fit one screen with nothing scrolling inside it

## Do not use this skill when

- The task is design critique or high-level UI feedback without implementation
- The request is purely backend, data, or infrastructure work
- The user only wants a neutral or default UI with minimal styling
- The deliverable is a PowerPoint or Keynote file rather than a browser surface — producing and inspecting binary office decks is a different job with different tooling

## Inputs to confirm

- Target framework or stack (plain HTML/CSS/JS, React, Vue, etc.)
- Surface type: `marketing` (hero-driven, brand-forward, visited once), `app` (workspace-driven, data-dense, returned to daily), or `hybrid`
- Constraints: accessibility, performance, browser support, design system rules
- Assets provided (logos, copy, images, brand colors, fonts)
- Interaction scope (static, subtle motion, rich motion)
- Delivery expectations (single file, component file, multiple files)

## Design Thinking

Before coding, the skill establishes context and commits to a bold aesthetic direction:
- **Purpose**: Defines the problem the interface solves and the primary audience.
- **Surface fit**: Classifies the surface by how it is used, before any tone is picked — `marketing` (visited once: launch page, portfolio, editorial, campaign), `app` (returned to daily: dashboard, admin, operations console, settings), or `hybrid` (marketing sections around a functional core). The classification constrains the tone rather than the reverse.
- **Tone**: Selects an extreme (brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian). These are inspiration points, but execution commits to one cohesive direction.
- **Constraints**: Records technical requirements (framework, performance, accessibility).
- **Differentiation**: Identifies the single unforgettable signature moment.

**CRITICAL**: Chooses a clear conceptual direction and executes it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

**Direction is chosen for fit, not for maximum boldness.** A surface someone repeats daily usually earns density, quiet, and scannability; a surface someone visits once can be expressive. A landing-page composition forced onto a tool built for repeated use is a defect even when it is executed with precision — coherence is not the same test as fit, and a direction can pass one while failing the other.

**Ships the working surface as the first screen.** Unless marketing copy was explicitly requested, the first viewport communicates the product, tool, object, or workflow itself. The primary experience is never hidden behind generic marketing sections.

Then implements working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Selects fonts that are beautiful, unique, and interesting. Avoids generic fonts like Arial and Inter; opts instead for distinctive choices that elevate the frontend's aesthetics. Pairs a distinctive display font with a refined body font.
- **Color & Theme**: Commits to a cohesive aesthetic. Uses CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Uses animations for effects and micro-interactions. Prioritizes CSS-only solutions for HTML. If a motion library already exists in the project, it may be used without adding dependencies. Focuses on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Uses scroll-triggering and hover states that surprise.
- **Spatial Composition**: Chooses unexpected layouts: asymmetry, overlap, diagonal flow, grid-breaking elements, generous negative space, or controlled density.
- **Backgrounds & Visual Details**: Creates atmosphere and depth rather than defaulting to solid colors. Adds contextual effects and textures that match the overall aesthetic. Applies creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

Avoids generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interprets creatively and makes unexpected choices that feel genuinely designed for the context. No design should be the same. Varies between light and dark themes, different fonts, and different aesthetics. Avoids converging on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Matches implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Aims for extraordinary creative work by thinking outside the box and committing fully to a distinctive vision.

## Layout mechanics

Aesthetics decide how a surface looks; these rules decide whether it holds real content. They apply to any surface with fixed regions and a scrolling body — app shells, dashboards, settings, list-detail, inbox, split panes — and to any page that looks right until content arrives.

### Name scroll ownership before writing layout CSS

For each region, answer three questions and record the answers alongside the layout outline:

- **What scrolls?** Name the one element that owns vertical scroll for the region.
- **What stays fixed?** List them: header, sidebar, footer, toolbar.
- **Where is height bounded?** A scroll container with no bounded-height ancestor grows instead of scrolling.

Give a region one scroll container unless every additional one has a declared job. Nested scrollbars with no stated responsibility are a defect: the user cannot predict what a wheel or trackpad gesture will move. Do not mix the two scroll models inside one region without a reason — a sticky element (`position: sticky`) follows document scroll, while a fixed-shell region (a grid area with its own `overflow: auto`) owns its scroll.

### The silent-failure contract

A grid or flex child that must scroll needs `min-height: 0` (`min-block-size: 0`). The default `min-*-size: auto` refuses to shrink the child below its content, so overflow never fires and the panel pushes the footer off-screen instead of scrolling. This is CSS-spec behaviour, not a tunable value, and it is the fix for "why won't my panel scroll". It fails silently: the layout looks correct until content is long enough to overflow.

```css
.shell {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto; /* header / body / footer */
  block-size: 100%;                             /* the shell itself must be height-bounded */
}
.shell__body {
  min-block-size: 0; /* without this the child never shrinks, so overflow never fires */
  overflow: auto;
}
```

### Choose a layout by spatial shape, not by product label

A settings page and a docs app both want a fixed side-nav shell; a support inbox and a file browser both want list-detail; a metrics view and a photo gallery both want an intrinsic grid. Do not invent a bespoke "dashboard layout" when named primitives already compose one, and do not force marketing-page structure (hero, zigzag, bento) onto a task app. `references/layout-primitives.md` holds the shared vocabulary; using those names makes a spec precise — "wrap it in a sidebar with a narrow fixed aside" beats "put it on the left, roughly".

### Content stress

Marketing pages fail on taste; app shells fail on content.

- **Empty** — no rows, no avatar, no value. Does the region collapse gracefully, or leave a broken frame?
- **Long label in a short slot** — truncation (`text-overflow: ellipsis`) or wrapping is designed, never accidental.
- **Long paragraph** — does the measure hold, or does prose run the full container width?
- **Unbroken string** — a URL or token with no spaces needs `overflow-wrap: anywhere` or `min-inline-size: 0`, or it forces horizontal scroll.
- **Reflow** — at the narrowest supported width the layout reflows to a single readable column with no horizontal scrollbar. Two-dimensional scrolling of primary content is a fail.
- **Direction** — where the product supports RTL, logical properties (`margin-inline`, `inset-inline-start`) let the layout mirror correctly.
- **Stable dimensions** — boards, grids, toolbars, tiles, and counters hold their size when labels change or a hover state appears. A layout that shifts on state change is not stable.

A layout that only holds the happy-path mock is not finished.

## Full-viewport slide surfaces

A presentation built as a web page is its own surface type: a sequence of full-viewport panels a presenter steps through, not a document a reader scrolls. The aesthetic rules above still apply and the surface is still classified before a direction is chosen — but the scroll-ownership mechanics invert, because nothing inside a panel is allowed to scroll at all.

**One slide is one viewport, and content that does not fit becomes another slide.** Each slide is height-bounded to the viewport — `100dvh`, with a `100vh` fallback for engines without dynamic viewport units — and clips its overflow. A scrollbar inside a slide means the audience is being shown content the presenter cannot see on their own screen. The only correct response to overflow is to split the slide. Shrinking type until it fits is the failure this rule exists to prevent: it trades a visible problem, a slide that is too full, for an invisible one, a slide nobody past the third row can read.

**Type and spacing are fluid, and short viewports are their own case.** Every type size and spacing value scales with the viewport rather than being fixed at one design width. Width alone does not cover it: a laptop at a squat aspect ratio and a phone held in landscape are short, not narrow, and a layout tuned only against width overflows on both. Add height-based breakpoints that tighten padding, step heading sizes down, and drop decorative chrome — position dots, keyboard hints, ornament — before touching body copy. The source's ladder of roughly 700px, 600px and 500px of viewport height is a chosen default, not a measured threshold; put the steps where this deck's own content starts to crowd.

**Density has a ceiling per slide type.**

| Slide type | Ceiling |
| --- | --- |
| Title | One heading, one subtitle, an optional tagline |
| Content | One heading plus 4–6 bullets, or two short paragraphs |
| Feature grid | Six cards |
| Code | 8–10 lines |
| Quote | One quotation and its attribution |
| Image | One image, held well inside the viewport |

Every figure in that table is a chosen default carried from the source, not a measured limit; what they encode is "few enough to read from the back of a room". Raise one deliberately when the audience and the room argue for it. Crossing one by accident is the signal to split the slide, not to reduce the type scale.

**Deck navigation is a contract, not a flourish.** Keyboard, pointer wheel, and touch swipe all advance and reverse the deck, and a position indicator says where the viewer is in it. Reveal animations fire on the slide entering the viewport rather than on a timer, so a presenter who moves fast is never waiting on a schedule. Under `prefers-reduced-motion: reduce`, reveals resolve to their end state and smooth scrolling becomes instant — a reduced-motion deck still navigates and still shows every slide, it simply stops animating between them.

**Discover the style by showing, not by asking.** A requester who cannot name a typeface can still pick between two rendered slides. Instead of an abstract style questionnaire, ask one question about the feeling the deck should leave, then build two or three single-slide previews in genuinely different directions — each self-contained, each small enough to take in at a glance — and ask which to keep or what to mix. Skip the previews when the requester already knows the direction. Delete them at handoff unless asked to keep them. This inverts the usual order: the visual system is chosen from evidence instead of described in advance, and the extra round trip pays for itself whenever the requester is not a designer.

**Validate against viewport shapes, not one canvas.** Check a large desktop, a laptop, a tablet in portrait, a small phone in portrait, and at least one short landscape shape. The landscape case is where viewport-fit failures actually surface and is the one routinely skipped. The source gives two different lists of specific pixel sizes and they disagree with each other; neither is measured, so the rule is coverage of those five shapes rather than a fixed set of numbers. Where browser automation is already available in the project, use it to confirm that no slide overflows and that keyboard navigation reaches every slide.

**Negated CSS functions are silently ignored.** `right: -clamp(28px, 3.5vw, 44px)` and `margin-left: -min(10vw, 100px)` are invalid: the browser drops the declaration without an error and the element sits in the wrong place. Write the negation as a multiplication instead.

```css
/* dropped silently */  right: -clamp(28px, 3.5vw, 44px);
/* applies */           right: calc(-1 * clamp(28px, 3.5vw, 44px));
```

## Motion and optical detail

- **Transitions and keyframes are not interchangeable; the choice is about interruptibility.** Use CSS transitions for interactive state changes, because a transition retargets from its current position when the user changes intent mid-motion. Reserve keyframe animations for staged one-shot entrances and loading sequences, where there is no user intent to retarget toward.
- **Enter and exit are asymmetric.** An entrance may combine opacity, a small translate, and optionally blur; the matching exit is shorter and quieter than the entrance (roughly 150ms is a chosen default, not a measured threshold). Icon and label swaps cross-fade — opacity, scale, blur — instead of toggling visibility instantly.
- **Optical alignment is not geometric alignment.** Asymmetric glyphs — icon buttons, play triangles, arrows, stars — look off-centre when they are centred geometrically, and need a small offset to look right. Fix it in the SVG where possible; otherwise nudge with padding or margin. No automated check catches this, and no reviewer catches it without knowing to look.

## Workflow

1. **Clarifies inputs and constraints.**
   - Confirms framework, assets, accessibility requirements, and output format.
   - **Output:** A short checklist of confirmed inputs and any open questions.
2. **Chooses the aesthetic direction.**
   - Picks one coherent visual language aligned with purpose, audience, and surface type.
   - **Decision point:** Classify the surface first. `app` surfaces take a direction that survives daily repetition; `marketing` surfaces can take an expressive one; `hybrid` applies each to its own sections.
   - **Output:** The surface classification with the observation that decided it, 3–5 design adjectives, and 1–2 standout signature moments.
3. **Defines the visual system.**
   - Defines typography pairing, color palette, spacing scale, and component motifs.
   - **Decision point:** If fonts/assets are not provided, use locally available fonts and avoid external network fetches.
   - **Output:** Token list (CSS variables) and rationale for each choice.
4. **Lays out structure and hierarchy.**
   - Composes layout, grid, and content flow; introduces intentional asymmetry.
   - **Decision point:** Before writing layout CSS, name scroll ownership per region. If a region ends up with more than one scroll container, state each one's job or remove it.
   - **Output:** A brief layout outline (sections/components and hierarchy), naming the primitive and the scroll owner for each region.
5. **Implements production-grade code.**
   - Builds HTML/CSS/JS (or framework code) with accessibility and responsiveness.
   - **Output:** Working UI code, scoped to the requested format.
6. **Refines polish and motion.**
   - Adds purposeful animations, hover states, and micro-interactions; checks optical centring on asymmetric glyphs.
   - **Decision point:** Interactive state changes get transitions; staged one-shot entrances and loading sequences get keyframes.
   - **Output:** Motion list with durations/easing and where applied, exits noted as shorter than their entrances.
7. **Self-reviews against pitfalls.**
   - Verifies aesthetic cohesion, legibility, and performance.
   - Drives every layout region through the content-stress list; a region that has only been seen with happy-path mock content is not verified.
   - **Output:** A quick checklist confirming adherence, the content-stress result per region, and any tradeoffs.

## Common pitfalls

- Reusing generic AI aesthetics (default fonts, bland palettes, predictable layouts)
- Over-animating everything instead of a few high-impact moments
- Mixing multiple aesthetic styles that dilute the visual direction
- Ignoring accessibility, responsive behavior, or content hierarchy
- Overusing external assets or fonts that require network access
- Forcing a landing-page composition onto a tool built for repeated daily use, or putting marketing sections in front of the working surface
- Declaring a layout done against happy-path mock content, before empty, long, and unbroken content have been tried
- Leaving nested scroll containers with no declared job, so nobody can predict what a scroll gesture will move
- Answering an overfull slide by shrinking type or letting the slide scroll, instead of splitting it in two
- Fixed-height content boxes that look right on a large monitor and clip on a laptop or on a phone held in landscape

## Output contract

- Confirmed inputs and constraints
- Surface classification (`marketing`, `app`, or `hybrid`) and the observation that decided it
- Chosen aesthetic direction and signature moments
- Visual system tokens (typography, colors, spacing)
- Implementation code with brief structure notes
- Motion/interaction summary
- Content-stress result per layout region
- Verification steps or manual checks

## Reporting format

- **Design summary:** surface classification + aesthetic direction + signature moments
- **System tokens:** typography, color, spacing, effects
- **Implementation:** code blocks + file layout (if multi-file), with the scroll owner named per region
- **Interactions:** motion/hover behaviors and intent
- **Checks:** accessibility, responsiveness, content stress, and performance notes

## Examples

**Example input**
"Build a premium analytics dashboard hero section in React with a dark, editorial feel. Include a headline, KPI cards, and a subtle animated background."

**Example output (abbreviated)**
- Design summary: editorial dark theme with serif headline + neon data accents; signature moment is the animated data grid glow.
- System tokens: `--bg-0`, `--bg-1`, `--accent`, `--radius-lg`, typography pair.
- Implementation: React component + CSS module with layout grid.
- Interactions: cards lift on hover, background shimmer loop.
- Checks: contrast meets WCAG AA, motion reduced via prefers-reduced-motion.

**Example input (application shell)**
"Build an on-call incident console: fixed left nav, an incident list, and a detail pane. Operators live in it all day."

**Example output (abbreviated)**
- Design summary: surface classified `app` — operators return to it daily and the primary object is the incident queue, so the direction is industrial/utilitarian, dense and quiet; signature moment is the severity rail colouring the list edge.
- System tokens: `--surface-0`, `--surface-1`, severity ramp, spacing scale, one display/body pair.
- Implementation: `fixed-sidenav-shell` composed with `list-detail`. Scroll owners are the incident list and the detail pane; nav, header, and status bar are fixed; the shell is height-bounded and both panes carry `min-block-size: 0`.
- Interactions: row selection and pane swaps use transitions, so an operator moving fast retargets mid-motion; the initial list reveal is the one keyframed sequence, and its exit is shorter than its entrance.
- Checks: content stress per region — empty queue, long service names truncating by design, an unbroken trace ID wrapping via `overflow-wrap: anywhere`, single-column reflow at the narrowest supported width with no horizontal scrollbar, toolbar dimensions stable across hover.
