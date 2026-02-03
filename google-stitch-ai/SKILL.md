---
name: google-stitch-ai
description: (Stitch) Create DESIGN.md from Stitch projects and enhance Stitch prompts. Supports MCP server retrieval or offline HTML/screenshots. Use for Stitch-compatible design system synthesis or prompt polishing.
category: ai
allowed-tools:
  - "Read"
  - "Write"
  - "web_fetch"
---

# Google Stitch AI

One combined skill for Stitch workflows:
- **Design System Synthesis**: Generate `DESIGN.md` from Stitch projects or provided assets.
- **Prompt Enhancement**: Turn vague UI ideas into structured, Stitch-optimized prompts.

## Use this skill when

- You need a `DESIGN.md` that captures a Stitch project’s design language.
- You want to enhance a prompt for Stitch or similar UI generators.

## Do not use this skill when

- You need a product or UX design brief (use `ui-design`).

## Mode A: DESIGN.md Synthesis

### Inputs (preferred)

- Stitch MCP Server access (project + screen IDs)

### Inputs (offline fallback)

- Exported HTML/CSS (or repo path)
- One or more screenshots of target screens
- Project title (and optional IDs)

### Retrieval (if MCP is available)

1. Discover tools with `list_tools` and find Stitch MCP prefix.
2. `list_projects` to find project ID.
3. `list_screens` to find screen ID.
4. `get_screen` to fetch screenshot + HTML.
5. `get_project` to fetch design theme metadata.

### Output: `DESIGN.md`

Structure:

```md
# Design System: <Project Title>
**Project ID:** <ID>

## 1. Visual Theme & Atmosphere

## 2. Color Palette & Roles

## 3. Typography Rules

## 4. Component Stylings
```

## Mode B: Prompt Enhancement

### Workflow

1. Identify missing details (platform, page type, layout, components, vibe).
2. If `DESIGN.md` exists, extract palette/typography/components.
3. Output structured prompt with:
   - Purpose + vibe (one line)
   - DESIGN SYSTEM block (if available)
   - Page structure (numbered)
   - Specific changes (for edits only)

### Output Contract

- Enhanced prompt in Markdown
- State whether `DESIGN.md` was used
- If missing, recommend creating it via Mode A

## Resources (Optional)

- UI/UX keyword palette: `references/KEYWORDS.md`
