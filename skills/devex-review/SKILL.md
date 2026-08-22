---
name: devex-review
description: "Reviews a proposed developer-facing product (API, CLI, SDK, library, platform, or its docs) for developer experience before it ships, distinct from reviewing its architecture or correctness. Investigates the target developer and their actual onboarding path for evidence before scoring, then rates DX per dimension on a calibrated 0-10 scale plus a separate time-to-first-result scale whose worst tier blocks rather than merely scoring low. Use on plans, design docs, or shipped products with a developer-facing surface."
metadata:
  category: workflow
---
# Developer experience review

Provides a repeatable process for evaluating the developer experience (DX) of a developer-facing product — an API, CLI, SDK, library, platform, or the docs for one — before it ships or before its plan is finalized.

DX is UX for developers, but the bar sits higher: the audience builds products for a living and notices everything, the journey spans multiple tools and sessions, and a bad first five minutes is rarely revisited. This skill treats scoring as the output of an investigation, not a substitute for one — a score produced without the evidence steps below is a vibe wearing a number.

## Use this skill when

- Reviewing a plan, design doc, or shipped artifact that has a developer as its user, before a launch or release decision.
- The product is (or will be) an API/service, CLI tool, library/SDK, developer platform, or documentation for one of those.
- The question is "will a new developer reach a working result quickly and without pain," as distinct from "is this architecture sound" or "is this code correct" — those are separate reviews even against the same plan.
- A concrete, evidence-backed inventory of DX debt is needed before committing to a ship date.

## Do not use this skill when

- The thing under review has no developer as its consumer — a purely internal service with no exposed API, or an end-user product with no SDK/CLI/API surface of its own. Route to a design or UX review instead.
- The review needed is architectural soundness, correctness, or security. Run those separately; do not fold them into a DX pass.
- The material gives no way to classify a developer-facing surface at all (see the applicability gate below) — exit rather than force a review onto something that isn't one.
- Only a fast opinion is wanted and there's no time for the investigation step. A DX review skipped straight to scoring is not a shorter version of this process; it's a different, weaker one — say so rather than running it.

## Required inputs

- The plan, design doc, README, or product itself.
- Read access to any existing docs, examples, CLI help text, and error messages, if the product already exists in some form.
- Time for a short investigation phase before any score is produced — this is not a single-pass checklist.

## Workflow

### Step 1 — Confirm this applies (applicability gate)

Read the material and classify its developer-facing surface: API/service, CLI tool, library/SDK, platform, documentation, or an agent-facing tool (skill, plugin, MCP-style server). A product can be more than one type; work from whichever is primary.

State the inferred classification and get it confirmed rather than assuming silently — it decides which persona options and journey stages apply later.

If nothing in the material has a developer-facing surface, say so plainly and stop: "This doesn't appear to have a developer-facing surface — this review covers APIs, CLIs, SDKs, libraries, platforms, and docs. An architecture or design review fits better here." A skill that knows when it does not apply is worth more than one that forces itself onto everything.

### Step 2 — Investigate before scoring

Gather evidence and force decisions here, before any score is produced — not while scoring. Each step below produces a specific piece of evidence that a later score must be able to point at.

**a. Identify the target developer.** Read the material for "who is this for" language, package metadata, and any audience signals in existing docs. Propose two or three concrete developer archetypes grounded in that evidence — not generic "developers" — for example: a founder integrating in thirty minutes who won't read docs, versus a platform engineer evaluating security and SLAs before committing. Get a choice or a correction, then record a short persona card: who, the context they arrive in, how much friction they tolerate before giving up, and what they assume already exists. Hold here until confirmed — everything after is relative to this persona.

**b. Trace the actual onboarding path.** Write a first-person account of what the persona experiences walking through the real README, docs, or CLI help — the actual headings, the actual commands, the actual output, not a hypothetical one. Long enough to be concrete, short enough to stay readable — a couple hundred words is a reasonable default length, not a hard limit. Present it and ask whether it matches reality; correct it before continuing.

**c. Benchmark comparable tools, best-effort.** Note how two or three comparable tools handle onboarding, where that information is actually available. If there's no way to gather it — no search, no prior knowledge of the space — say that plainly rather than presenting a guess as data. The result feeds a rough target for the time-to-first-result scale below; it is not itself a score.

**d. Design the magical moment.** Most developer tools have (or should have) a moment where "is this worth my time" flips to "this actually works" — an instant API response, a push-to-deploy that goes live in seconds. Identify the candidate moment for this product and two or three ways it could be delivered (interactive sandbox, one-command demo, guided walkthrough, a passive video walkthrough), each with a rough note on effort versus impact. Get a choice before treating it as fixed — it becomes the benchmark the first review dimension is scored against.

**e. Choose the review depth.** Offer three depths and get one chosen before proceeding, then hold it — do not silently drift to a different depth mid-review:

- **Expansion** — DX as a competitive edge; propose improvements beyond what the plan currently covers.
- **Polish** — the plan's scope is right; make every existing touchpoint as good as it can be, no scope additions.
- **Triage** — only the gaps that would block adoption; fast and surgical, for something that needs to ship soon.

A reasonable default absent other signal: a brand-new developer-facing product leans toward Expansion, an enhancement to an existing one toward Polish, an urgent fix or narrow change toward Triage — but this is a starting suggestion, not a rule to apply blindly.

**f. Walk the journey stage by stage.** For each stage a new developer passes through — discover, install, first success ("hello world"), real usage, debug, upgrade — trace the actual experience rather than guessing at it: which file, which command, which output. State every friction point with evidence, not intuition: not "installation might be hard" but "step 3 of the README requires Docker running, and nothing checks for it or tells the developer to install it." Surface each friction point as its own decision point, one at a time, rather than batching several into one question — batching is the shortcut that produces a plan nobody actually weighed in on. In Triage mode, trace only install and first-success; Polish and Expansion trace every stage.

**g. Roleplay a first attempt.** Using the persona and the journey trace, write a short timestamped log of a first attempt: what they try, what confuses them, where they succeed or give up — grounded in the actual docs and errors gathered above, not invented ones. Present it and ask which points should be addressed in the plan.

Surface findings as each investigation step produces them and get a response before moving to the next, rather than saving everything for one final report. Writing every finding into a single pass and presenting it as a fait accompli is the exact shortcut this staged process exists to prevent — the plan is the *output* of the review, not a substitute for walking through it.

### Step 3 — Score on two independent scales

This is the part that makes the two-scale design worth using: a product can score well on every quality dimension and still fail the thing that decides whether anyone gets past the front door. Score both; do not let a good quality score stand in for a good time-to-first-result, or vice versa.

**Quality scale — 0-10 per dimension, against verbal anchors** so the number means something instead of being a vibe:

| Score | Looks like |
|---|---|
| 9-10 | Best-in-class; developers rave about it unprompted |
| 7-8 | Good; usable without frustration, only minor gaps |
| 5-6 | Acceptable; it works, but developers feel the friction |
| 3-4 | Poor; developers complain and adoption suffers |
| 1-2 | Broken; developers abandon after one attempt |
| 0 | Not addressed at all |

These bands and their wording are this skill's chosen default, not a measured scale — recalibrate them against the project's own bar if one already exists, rather than treating them as fixed.

For each dimension, name what a 10 would specifically look like for *this* product, then work the plan toward that description and re-rate as changes land — a rating with no description of what a 10 looks like is not actionable.

**Time-to-first-result scale — separate, with a blocking floor.** Measure or estimate how long a new developer takes to reach a first working result — and if it's an estimate, label it one. Unlike the quality scale, the worst band here does not just score low, it blocks:

| Tier | Time (chosen default — recalibrate per product category) | Effect |
|---|---|---|
| Fast | under ~2 minutes | scores well |
| Workable | ~2-5 minutes | acceptable |
| Slow | ~5-10 minutes | flag as a real gap |
| Blocking | past ~10 minutes | do not treat this as ready to ship without addressing it |

The minute values above are a chosen default for illustration, not measured industry constants — set thresholds that fit the product category, and say so when they're being used as the bar for this review.

**Every score, on either scale, must cite a specific piece of Step 2 evidence.** Not "Getting Started: 4/10" but "Getting Started: 4/10 because [the persona from step a] hits [the friction point from step f] at step 3, and [the comparable tool from step c] reaches this point in under a minute." A score that cannot point at something gathered in Step 2 is not assertable — go back and gather the evidence instead of asserting the number.

### Step 4 — Review dimensions

Score each of the following against the two scales above. This is this skill's default grouping of dimensions, not a sacred count — drop a dimension that genuinely doesn't apply (a brand-new library has no upgrade story yet) rather than forcing a score onto it, and say why it was skipped.

1. **Getting started** — one command or one click to install; a first run that produces visible, meaningful output; a sandbox to try before installing; no credit card or sales call standing between "want to try" and "it worked." Score this against the magical-moment delivery chosen in step d and the benchmark tier from step c.
2. **API/CLI/SDK design** — names guessable without docs; every parameter has a sensible default; consistent patterns across the whole surface; full coverage instead of dropping to raw HTTP for edge cases; does the interface match how the persona from step a actually thinks about the problem?
3. **Error messages and debugging** — trace two or three real error paths. For each, does the message state what happened, why, how to fix it, and where to learn more, with the actual values that caused it? A useful contrast when judging quality: a message that reads like a person explaining the problem in place (what/why/fix, with the offending value shown) versus one that dumps an internal stack trace and leaves the developer to reverse-engineer the cause.
4. **Documentation and learning** — can the persona find what they need in under a couple of minutes; do code examples run as copy-pasted, in real context, not just toy snippets; does structure separate a beginner path from a reference path?
5. **Upgrade and migration path** — what breaks on an upgrade, and how contained is the blast radius; are deprecations announced with an actionable alternative; do breaking changes ship with a migration guide or an automated codemod?
6. **Environment and tooling fit** — does it work inside the developer's existing toolchain (editor, CI, package manager) without special-casing; are there fast local-dev loops (hot reload, dry-run, verbose mode); does it work across the platforms the persona actually uses?
7. **Community and ecosystem** — is there a place developers actually get answered; are examples real and runnable rather than hello-world only; is pricing (if any) transparent enough that nobody is surprised?
8. **DX measurement and feedback** — does the plan include any way to find out whether the DX promises held after shipping (time-to-first-result tracking, drop-off visibility, a feedback channel)? This dimension is about whether the plan can tell reality from intention later, not about getting it perfect now.

Depth mode changes how far each dimension goes: Triage only flags gaps scoring below the midpoint of the quality scale (and, per step f, narrows journey tracing to install and first-success only); Polish works every gap toward a 10; Expansion also asks, for each dimension already at a good score, what would make it best-in-class.

## Output contract

- The persona card from step a.
- The onboarding narrative from step b, corrected against user feedback.
- The competitive benchmark from step c, or an explicit note that none was available.
- The magical-moment specification chosen in step d.
- The journey map from step f, with every friction point marked resolved or explicitly deferred.
- The first-attempt log from step g.
- A score per dimension from Step 4, each carrying its cited evidence and its "what a 10 looks like" description.
- The time-to-first-result assessment, its tier, and whether it blocks.
- Any DX debt explicitly deferred rather than fixed, each with a one-line reason — never silently dropped.

## Examples

**Weak (no cited evidence):** "Getting Started: 4/10. The onboarding could be smoother."

**Strong (cites Step 2 evidence, per the rule in Step 3):** "Getting Started: 4/10 — the founder persona from step a hits the friction point recorded in step f at install (README step 3 requires Docker running, with no check or prompt), and the comparable CLI benchmarked in step c reaches a working state in under a minute. A 10 here means the docker requirement is either removed or checked-and-explained inline, cutting time-to-first-result from the current ~12 minutes (Blocking tier) toward the Workable tier."

## References

- `references/dx-reference.md` — persona archetype examples, the error-message quality-tier breakdown with worked examples, and named external measurement frameworks to borrow metrics from.
