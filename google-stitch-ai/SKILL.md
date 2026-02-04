---
name: google-stitch-ai
description: Create DESIGN.md summaries from Google Stitch projects or offline assets, and refine Stitch-ready UI prompts using extracted design tokens.
category: ai
allowed-tools:
  - "Read"
  - "Write"
---

# Google Stitch AI

One combined skill for Stitch workflows:
- **Design System Synthesis**: Generate `DESIGN.md` from Stitch projects or provided assets.
- **Prompt Enhancement**: Turn vague UI ideas into structured, Stitch-optimized prompts.

## Use this skill when

- You need a `DESIGN.md` that captures a Stitch project’s design language.
- You want to enhance a prompt for Stitch or similar UI generators.
- You have Stitch-exported HTML/CSS and screenshots and need a structured summary.

## Do not use this skill when

- You need user research, product strategy, or a full UX design brief.
- You must invent a brand identity without any assets or inputs.
- You require cross-skill dependencies or multi-agent orchestration.

## Activation cues (trigger phrases)

- "Create a DESIGN.md from this Stitch project"
- "Summarize the Stitch design system"
- "Polish this Stitch prompt"
- "Turn this UI idea into a Stitch-ready prompt"

## Required inputs

- **Mode A (DESIGN.md)**: Stitch MCP access *or* offline assets (HTML/CSS export plus screenshots).
- **Mode B (Prompt Enhancement)**: Draft prompt plus target platform (web/mobile) and optional `DESIGN.md`.

## Decision points

- If Stitch MCP access is available, use it for accurate theme data.
- If MCP is unavailable, rely on offline HTML/CSS and screenshots.
- If key inputs are missing (palette, typography, layout), ask for them before final output.

## Mode A: DESIGN.md Synthesis

### Step-by-step

1. **Choose retrieval path.**
   - If MCP is available, collect project metadata + screen HTML/screenshot.
   - If offline, collect HTML/CSS export + screenshots + project title.
   - **Output:** asset bundle summary.
2. **Extract visual theme details.**
   - Identify primary/secondary colors, background/surface colors, text colors.
   - Capture typography (font family, weights, sizes, line heights).
   - **Output:** theme notes list.
3. **Catalog components and states.**
   - Buttons, inputs, cards, nav, modals, tables, etc.
   - Note states (hover, active, disabled) if visible.
   - **Output:** component inventory.
4. **Draft `DESIGN.md`.**
   - Use the template below; fill with extracted tokens and observations.
   - **Output:** `DESIGN.md` file.
5. **Validate gaps.**
   - If missing critical details, list follow-up questions.
   - **Output:** question list (if needed).

### Output: `DESIGN.md` structure

```md
# Design System: <Project Title>
**Project ID:** <ID>

## 1. Visual Theme & Atmosphere

## 2. Color Palette & Roles

## 3. Typography Rules

## 4. Component Stylings
```

## Mode B: Prompt Enhancement

### Step-by-step

1. **Clarify intent and platform.**
   - Identify page type, user goal, and platform (web/mobile).
   - **Output:** clarified intent line.
2. **Pull design tokens (if available).**
   - Use `DESIGN.md` to populate colors, typography, spacing, and components.
   - **Output:** token summary block.
3. **Structure the prompt.**
   - Purpose + vibe (one line).
   - DESIGN SYSTEM block (if available).
   - Page structure (numbered layout sections).
   - Specific changes (only if editing an existing design).
   - **Output:** enhanced prompt in Markdown.
4. **Check for missing details.**
   - Ask for missing platform or target audience info.
   - **Output:** question list (if needed).

## Output contract

- **Mode A:** Provide `DESIGN.md`, plus any open questions for missing tokens.
- **Mode B:** Provide enhanced prompt in Markdown and state whether `DESIGN.md` was used.
- If `DESIGN.md` is missing, recommend creating it via Mode A.

## Common pitfalls to avoid

- Inventing brand colors or typography without evidence
- Mixing web and mobile patterns in one prompt
- Overloading the prompt with unrelated features
- Ignoring accessibility contrast or text hierarchy

## Examples

### Trigger test

- "Generate a DESIGN.md for my Stitch project export."
- "Polish this Stitch prompt for a mobile onboarding screen."

### Example input → output (prompt enhancement)

**Input:** "Make a clean dashboard for sales KPIs."

**Output (excerpt):**

```md
Purpose/Vibe: Clean, professional sales KPI dashboard for executives.

DESIGN SYSTEM
- Primary: #1F4ED8, Secondary: #93B5FF
- Typography: Inter (H1 32/40, H2 24/32, Body 16/24)

Page Structure
1. Top nav with logo, account, date range filter
2. KPI summary cards (Revenue, ARR, Churn)
3. Line chart for revenue trend
4. Table of top accounts
```

## Reporting format

Provide results in this structure:

```
## Output
- Mode: DESIGN.md | Prompt
- Inputs used: MCP | Offline (list assets)
- Files created/updated: <paths or none>
- Open questions: <list or none>
```

## Resources (Optional)

- UI/UX keyword palette: `references/KEYWORDS.md`
- Reference index: `references/README.md`
