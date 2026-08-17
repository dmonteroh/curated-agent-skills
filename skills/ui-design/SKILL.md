---
name: ui-design
description: "One canonical, framework-agnostic UI/UX design skill: turn requirements into clear UI briefs, flows, component specs, and design-system rules; review UI code against local guidelines; prioritize accessibility, consistency, and developer-hand-off clarity. Not a Google Stitch skill."
metadata:
  category: design
---
# UI Design

Provides UI design and review guidance that turns requirements into briefs, flows, component specs, and design-system rules. It is intentionally framework-agnostic and does not assume any implementation stack.

## Use this skill when

- Requirements are unclear and you need a UI brief + flow before implementation
- Defining component behaviors and states (loading/empty/error/disabled)
- Defining or enforcing design-system rules (tokens, surfaces, status hierarchy)
- Proposing a design system from scratch, where the proposal has to say where it plays safe and where it takes a deliberate risk
- Producing several distinct design directions for a human to choose between
- Reviewing UI code for accessibility and consistency using local guidelines

## Do not use this skill when

- The user explicitly wants UI code implementation only
- The task is “Google Stitch” specific
- The task is judging an already-rendered UI from screenshots rather than specifying one

## Required inputs

- Target platform(s) and form factor (web, mobile, desktop; responsive needs)
- Primary user goal and success criteria
- Constraints (density vs delight, accessibility level, branding, localization)
- If reviewing code: files/links and any local UI guidelines
- If platform-specific behavior matters: local standards or product conventions
- If proposing a design system: the product category and the conventions its users already expect, plus any direction already approved earlier in this project

## Workflow

1) Clarify intent and constraints
   - Output: concise requirements summary + explicit assumptions.

2) Produce the UI brief (design-level contract)
   - Output: goals/non-goals, primary flow, secondary flows, hierarchy + navigation notes.

3) Specify components and states
   - Output: component list with responsibilities, states, data/prop contracts, interaction rules.

4) Define design-system rules (only if needed)
   - Output: token/surface rules, status hierarchy, optional theme usage contract.
   - Decision: when the system is being *proposed* rather than applied, produce it as the labelled safe/risk split below and stop for the human's pick before anything downstream depends on it.

5) Offer distinct directions (only when more than one is wanted)
   - Output: N labelled directions, each carrying its own type, palette and layout approach.
   - Decision: two directions that fail the swap test below are one direction — replace the weaker rather than presenting both.

6) Review/verification
   - Output: checklist-based findings with remediation plan and validation steps, including the accessibility gate below.

## Decision points

- If the user only wants implementation, confirm whether a design/spec is still needed before proceeding.
- If design-system rules already exist, reference them and avoid inventing new tokens.
- If platform is unclear, ask for the primary target before drafting the brief.
- If platform standards are missing, request local guidelines instead of assuming defaults.
- If a proposed combination is internally incoherent, name the mismatch and propose the smallest change that resolves it — then accept the user's answer. Nudge, never block.

## Design-system proposals: safe choices and deliberate risks

Coherence is table stakes. Every product in a category can be internally coherent and still look identical to its competitors, so a proposal that only argues for coherence has not made the decision that matters. The decision that matters is *where this product departs from its category*, and that decision belongs to the human.

Split every design-system proposal into two labelled halves, and ship the labels with it. An unlabelled proposal hides which decisions were conventional and which were bets, which is exactly what the reader needs to know in order to overrule one.

- **Safe choices** — the decisions that match category convention, each with a one-line reason for playing safe *there* specifically. These keep the product legible to users who arrive with category expectations.
- **Deliberate risks** — the departures, where the product gets its own face. Price each one with four fields, in this order: **what it is**, **why it works**, **what you gain**, **what it costs**. A risk with no stated cost is a recommendation wearing a risk label.

Propose at least two risks. Two is a chosen floor, not a measured one, and the reason is structural: one risk gives the human an accept/reject, and two or more gives them something to choose between — which is the point of labelling them at all.

Close the proposal by handing the pen over, with three options:

- **A** — take these risks
- **B** — take some of them (name which)
- **C** — different risks: show me wilder options

Option C is load-bearing, not decoration. Without a stated route to "wilder", the human's only visible move is accept or reject, and the proposal that follows a bare rejection tends to come back *more* conservative rather than differently bold.

**On consistency.** This skill's consistency requirement is consistency *within* the system — one type scale, one spacing scale, one semantic token set, applied everywhere. It is not a requirement to match the category. Deviation from the category is what the risks are for. A system can be internally rigorous and externally distinctive at the same time; these are one rule seen from two sides, not a contradiction.

## Anti-convergence when proposing multiple directions

Asked for three design directions, the default output is three siblings: the same typographic feel, overlapping colour temperature, comparable layout rhythm. Convergence is the failure mode here, not variety.

- Each direction differs on all three axes — **type family**, **colour palette**, **layout approach**. Varying one while holding the other two is a restyle, not a direction.
- **The swap test.** If someone could swap the headline text between two directions without noticing, they are too similar. Directions should read as the work of different design teams, not one team on different days.
- A direction that fails the swap test is replaced, not shipped beside its twin. Regenerate the weaker of the pair against a different axis rather than adjusting its colours.
- Across successive rounds in the same project, vary light/dark, type, and aesthetic direction. Do not repeat a previous round's combination without saying why it is being repeated — repeating last round's answer is convergence across time.
- Prior approvals are a demonstrated preference, not a constraint. When a proposal departs from what was approved before, name the departure as deliberate so it does not read as drift.
- The "safe alternative" to an overused default is itself a default. Design tooling converges on the same escape hatch, so reaching for it is convergence with an extra step — treat a typeface or palette that is widely recommended *as the non-obvious choice* as an obvious one.

## Accessibility rules

The rules below are DOM and WAI-ARIA facts, not framework facts, and are stated in plain HTML terms. `references/web-interface-guidelines.md` carries the wider review checklist; this section carries the two discriminators and the failure modes that reviews catch late.

**Two decision rules**

- **`aria-label` vs `aria-labelledby`.** Use `aria-label` when no visible label text exists — an icon-only close button. Use `aria-labelledby`, pointing at the `id` of the visible text, when one does exist — a `<section>` named by the `<h2>` inside it. The discriminator is whether the label is already on screen. Copying on-screen text into `aria-label` creates two names that drift apart on the next copy edit.
- **`aria-live` urgency.** `polite` waits for the user to finish what they are doing. `assertive` interrupts immediately and is reserved for urgent errors; on routine status updates it talks over the user's own typing.

**Six anti-patterns**

- A click handler on a `<div>` or `<span>` with no keyboard path. Use `<button>`. If the element must stay generic it needs `role`, `tabindex="0"`, *and* a `keydown` handler for Enter and Space — any one or two of the three is still not a button.
- `role="button"` without `tabindex="0"` and Enter/Space handling. The role announces a button that cannot be reached or activated from a keyboard, which is worse than announcing nothing.
- `aria-label` on a `<div>` with no `role`. A generic element exposes no accessible name, so the label is silently discarded.
- A positive `tabindex` such as `tabindex="3"`. Positive values jump ahead of document order and make the tab sequence unpredictable across the whole page, not just the component. Only `0` and `-1` are safe.
- `aria-hidden="true"` on a focusable element. It disappears from assistive technology while staying in the tab order, so keyboard users land on something the screen reader will not announce.
- A placeholder standing in for a label. It vanishes as soon as the field has content — the field loses its name exactly when the user is re-checking their answer.

**Pre-review gate.** Before an interactive component is handed off or reviewed:

- [ ] Every `<input>`, `<select>` and `<textarea>` has a `<label>` connected by `for`/`id`
- [ ] Error messages are tied to their field with `aria-describedby` and announced with `role="alert"`
- [ ] No click handler on a `<div>` or `<span>` without `role`, `tabindex` and a keyboard handler
- [ ] Icon-only controls carry an accessible name
- [ ] Decorative images use `alt=""` and `aria-hidden="true"`
- [ ] Dialogs record the element that opened them, keep Tab/Shift+Tab inside while open, and return focus to that element on close
- [ ] Content that updates without a page load is announced through a live region
- [ ] `prefers-reduced-motion` is honored for animation

## Common pitfalls

- Skipping empty/error/permission states in the flow
- Overloading the UI with multiple status colors or competing emphasis
- Missing keyboard/focus/label requirements in interactive components
- Providing pixel-perfect visuals when the user asked for structural guidance only
- Assuming platform conventions without local confirmation
- Presenting one coherent recommendation, or an undifferentiated menu, instead of a labelled safe/risk split — both hide which decisions were bets
- Listing a risk's upside without its cost, which converts the choice back into a recommendation
- Blocking on a coherence objection after the user has chosen
- Shipping design directions that differ only in accent colour

## Examples

**Input**: “We need a billing settings screen, but requirements are fuzzy.”

**Output (summary)**:
- UI brief: goals/non-goals, primary + secondary flows, hierarchy notes
- Component list: tables, forms, confirmation dialog, loading/empty states
- A11y notes: focus order, labels, error summary

**Contrast — proposing a design system, two ways**

- Wrong: "A calm, professional system: neutral greys, a blue accent, generous whitespace, a modular type scale. Coherent and appropriate for a finance product." One undifferentiated recommendation. Nothing is labelled as conventional, nothing is labelled as a bet, and the only reply available is yes or no.
- Right:
  - *Safe* — neutral greys and a single blue accent (finance users read blue as trustworthy; not the place to argue); tabular figures throughout (numeric comparison is the product's core job).
  - *Risk 1* — a serif for headings against the sans body. **Why it works:** the category is uniformly geometric sans, so a serif reads as institutional rather than start-up. **Gain:** immediate recognition in a screenshot. **Cost:** one more font to load, and it will look wrong if the marketing site stays all-sans.
  - *Risk 2* — no card borders anywhere; separation by spacing and background level only. **Why it works:** removes the dashboard-mosaic look. **Gain:** dense screens stay calm. **Cost:** weaker grouping cues at narrow widths, and it needs a disciplined surface stack to survive.
  - Which risks appeal? (A) take both, (B) take some — say which, (C) different risks: show me wilder options.

## Output contract

Use this reporting format, in this order:

```md
# UI Brief
- Goals:
- Non-goals:
- Primary flow:
- Secondary flows:
- Hierarchy/navigation notes:

# Component + State Specs
- <Component>: responsibilities, states, data/props, interactions, acceptance criteria

# Accessibility Notes
- Focus/keyboard:
- Labels/ARIA:
- Motion/contrast:
- Pre-review gate: <items passed / items failed>

# Design System Proposal (if proposing a system)
- Safe choices:
  - <decision> - why safe here:
- Risks (at least two):
  - <name>: what it is / why it works / what you gain / what it costs
- Your pick: (A) take these risks (B) take some - name which (C) different risks - show me wilder options

# Directions (if more than one was requested)
- <Direction name>: type / palette / layout approach
- Swap test: <pass|fail per pair, and which direction was replaced>

# Review Findings (if reviewing code)
- blocker: `file:line` issue -> fix + verify step
- should-fix: `file:line` issue -> fix + verify step
- nice-to-have: `file:line` issue -> fix + verify step
```

## Resources

- `resources/implementation-playbook.md`
- `references/README.md`
