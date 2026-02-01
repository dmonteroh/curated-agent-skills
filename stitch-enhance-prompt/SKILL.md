---
name: stitch-enhance-prompt
description: (Stitch) Transform vague UI ideas into polished prompts optimized for Stitch-like generators. Enhances specificity, adds UI/UX keywords, injects DESIGN.md context when present, and structures output. Does not require the Stitch MCP server.
allowed-tools:
  - "Read"
  - "Write"
---

# Stitch Enhance Prompt

This skill improves prompt quality and consistency for Stitch (or similar UI generators). It works offline; it does not require the Stitch MCP server.

## Use this skill when

- A UI prompt is vague and needs structure, vocabulary, and constraints
- You want to inject an existing DESIGN.md so generated screens match a system
- You want a “single change only” prompt for a targeted UI edit

## Do not use this skill when

- You need a design brief/spec (use `ui-design`)
- You need to generate DESIGN.md from existing screens (use `stitch-design-md`)

## Workflow (Deterministic)

1) Assess what’s missing
- Platform (web/mobile), page type, layout structure, components, vibe, colors/tokens.

2) Check for DESIGN.md (optional but high ROI)
- If DESIGN.md exists, read it and extract:
  - palette + roles
  - typography rules
  - component stylings
- If missing, include a note recommending creating one via `stitch-design-md`.

3) Structure the output
- Start with one-line purpose + vibe.
- Add a “DESIGN SYSTEM” block (platform + theme + key colors/tokens).
- Add “Page Structure” as numbered sections.
- For edits, include a “Specific changes” block and explicitly say “make only this change”.

## Output Contract (Always)

- Enhanced prompt in Markdown
- If DESIGN.md was used: cite that it was used
- If DESIGN.md was missing: include a short tip to create it

## Resources (Optional)

- UI/UX keyword palette: `references/KEYWORDS.md`

