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

## Do not use this skill when

- The task is design critique or high-level UI feedback without implementation
- The request is purely backend, data, or infrastructure work
- The user only wants a neutral or default UI with minimal styling

## Inputs to confirm

- Target framework or stack (plain HTML/CSS/JS, React, Vue, etc.)
- Constraints: accessibility, performance, browser support, design system rules
- Assets provided (logos, copy, images, brand colors, fonts)
- Interaction scope (static, subtle motion, rich motion)
- Delivery expectations (single file, component file, multiple files)

## Design Thinking

Before coding, the skill establishes context and commits to a bold aesthetic direction:
- **Purpose**: Defines the problem the interface solves and the primary audience.
- **Tone**: Selects an extreme (brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian). These are inspiration points, but execution commits to one cohesive direction.
- **Constraints**: Records technical requirements (framework, performance, accessibility).
- **Differentiation**: Identifies the single unforgettable signature moment.

**CRITICAL**: Chooses a clear conceptual direction and executes it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

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

## Workflow (Deterministic)

1. **Clarifies inputs and constraints.**
   - Confirms framework, assets, accessibility requirements, and output format.
   - **Output:** A short checklist of confirmed inputs and any open questions.
2. **Chooses the aesthetic direction.**
   - Picks one bold, coherent visual language aligned with purpose and audience.
   - **Output:** 3–5 design adjectives and 1–2 standout signature moments.
3. **Defines the visual system.**
   - Defines typography pairing, color palette, spacing scale, and component motifs.
   - **Decision point:** If fonts/assets are not provided, use locally available fonts and avoid external network fetches.
   - **Output:** Token list (CSS variables) and rationale for each choice.
4. **Lays out structure and hierarchy.**
   - Composes layout, grid, and content flow; introduces intentional asymmetry.
   - **Output:** A brief layout outline (sections/components and hierarchy).
5. **Implements production-grade code.**
   - Builds HTML/CSS/JS (or framework code) with accessibility and responsiveness.
   - **Output:** Working UI code, scoped to the requested format.
6. **Refines polish and motion.**
   - Adds purposeful animations, hover states, and micro-interactions.
   - **Output:** Motion list with durations/easing and where applied.
7. **Self-reviews against pitfalls.**
   - Verifies aesthetic cohesion, legibility, and performance.
   - **Output:** A quick checklist confirming adherence and any tradeoffs.

## Common pitfalls to avoid

- Reusing generic AI aesthetics (default fonts, bland palettes, predictable layouts)
- Over-animating everything instead of a few high-impact moments
- Mixing multiple aesthetic styles that dilute the visual direction
- Ignoring accessibility, responsive behavior, or content hierarchy
- Overusing external assets or fonts that require network access

## Output contract (Always)

- Confirmed inputs and constraints
- Chosen aesthetic direction and signature moments
- Visual system tokens (typography, colors, spacing)
- Implementation code with brief structure notes
- Motion/interaction summary
- Verification steps or manual checks

## Reporting format

- **Design summary:** aesthetic direction + signature moments
- **System tokens:** typography, color, spacing, effects
- **Implementation:** code blocks + file layout (if multi-file)
- **Interactions:** motion/hover behaviors and intent
- **Checks:** accessibility, responsiveness, and performance notes

## Examples

**Example input**
"Build a premium analytics dashboard hero section in React with a dark, editorial feel. Include a headline, KPI cards, and a subtle animated background."

**Example output (abbreviated)**
- Design summary: editorial dark theme with serif headline + neon data accents; signature moment is the animated data grid glow.
- System tokens: `--bg-0`, `--bg-1`, `--accent`, `--radius-lg`, typography pair.
- Implementation: React component + CSS module with layout grid.
- Interactions: cards lift on hover, background shimmer loop.
- Checks: contrast meets WCAG AA, motion reduced via prefers-reduced-motion.
