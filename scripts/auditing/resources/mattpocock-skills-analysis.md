# mattpocock/skills — Analysis for Our Library

Date: 2026-08-01 · Author: Claude Code (Opus 4.8) · Status: **evidence for a decision. Nothing in our library changed.**
Source: `github.com/mattpocock/skills`, branch `main`, **MIT-licensed**.
Supports **D5** of `tmp/skill-library-triage-brief.md`.

Method: the `writing-great-skills` doctrine was read directly; the architecture and per-skill mechanics were gathered against the raw repo files. Provenance rule: reimplementing a *pattern* is clean; copying *text* is not — so any criteria we adopt get written in our own words, citing mattpocock as the source pattern where relevant.

---

## Executive summary (read this if nothing else)

- Their library is a **coupled, self-orchestrating Claude Code plugin** — the deliberate inverse of our atomic, portable, agent-agnostic model. **Their architecture stays rejected** (routers, cross-skill invocation, shared setup, hard dependencies, plugin-only distribution all violate our founding constraints).
- What is worth learning is **not** their architecture but their **authoring doctrine**. It is built on one virtue our checklist never names: **predictability of *process*, not output.**
- Five of their techniques are **pure additive lift** for our checklist (Bucket A). Three collide with rules we currently enforce and need your ruling (Bucket B). The rest we keep rejected but should document *why* (Bucket C).
- **Sharpest finding:** our own mandatory "Workflow (Deterministic)" template — the thing our checklist enforces hardest — is the single biggest source of the boilerplate their pruning discipline would delete. Adopting their pruning (A-4) partly collides with our template rule (B-1). **That is the one real tension you have to resolve.**
- **Decisions needed from you** are collected at the end (§7). Nothing else is required to read.

---

## 1. What the mattpocock library actually is (its shape)

Not a set of atomic skills — a **coupled, self-orchestrating plugin**. The opposite architecture to ours, on purpose:

- **Two-tier router.** `ask-matt` is the top router ("A router over the skills in this repo") and hard-codes the whole suite into named flows (idea→ship, bug-triage on-ramp, session-crossing). `wayfinder` is a planning router that invokes siblings mid-flow: "Run a /grilling and /domain-modeling session…", "spin up a /research subagent to resolve it in parallel."
- **Hard/soft dependency policy** (ADR 0001) — *not* a no-dependency rule. Hard-dependents (`to-tickets`, `to-spec`, `triage`) must carry the sentence "…should have been provided to you — run /setup-matt-pocock-skills if not," because "without the mapping, output is wrong, not just fuzzy." Soft-dependents (`tdd`, `diagnose`) "still work" without setup, "just less sharp."
- **Shared setup skill.** `setup-matt-pocock-skills` writes a config artifact (domain glossary, tracker mapping) that other skills assume exists.
- **Invocation axis** (`.agents/invocation.md`). Every skill is **model-invoked** (rich trigger phrasing in the `description`; fires on its own) or **user-invoked** (`disable-model-invocation: true`; human-facing one-line description; triggers stripped). Rule: "A user-invoked skill may invoke model-invoked skills, but never another user-invoked skill."
- **Distribution.** Shipped as a curated, versioned, **auto-updating Claude Code plugin** (ADR 0002); Codex deferred. Buys managed central updates at the cost of single-vendor lock-in.
- **Coupling style.** Cross-skill links are runtime prose invocations ("Run the /grilling skill"), **not** filesystem `../other-skill/FILE.md` paths. Shared docs live inside the owning skill.

**Why this matters to us:** it's *why* their skills can be terse — they externalize shared context into the suite. We forbid that (atomicity/portability), so our skills must each carry their own context. Their brevity is bought with coupling we won't pay for.

---

## 2. Their doctrine (`writing-great-skills`) — the part that maps to our criteria

Root virtue: **predictability of *process*, not output.** "A skill's job is to wrangle determinism out of a stochastic system… the goal is not the same output every run but the same process." Every choice is judged against predictability, "not against how clever, complete, or exhaustive the skill reads."

Their levers:
- **Cognitive load vs context load.** Model-invoked skills spend *context* (a description sits in the window every turn); user-invoked spend *cognitive load* (the human must remember they exist). Routers are the cure for cognitive load.
- **Leading words.** Anchor behavior on one compact pretraining concept the model already thinks with (*tight*, *tracer bullet*, *seam*, *deep module*), repeated and bolded. "Consistent language is the whole point."
- **Information hierarchy / progressive disclosure / context pointer.** A ladder: in-skill step → in-skill reference → external reference behind a pointer. Disclose downward so the top stays legible.
- **Pruning.** Single source of truth, relevance, and a **no-op test** applied sentence by sentence, against named failure modes: **premature completion, duplication, sediment, sprawl, no-op.**

---

## 3. Per-skill mechanisms (what makes each behaviorally differentiated)

Concrete techniques, each reimplementable in our own voice without importing anything:

- **diagnosing-bugs** — *Forbid hypothesizing until a "red-capable command" exists.* "No red-capable command, no Phase 2… stop — jumping straight to a hypothesis is the exact failure this skill prevents." Also: 3–5 ranked falsifiable hypotheses shown before testing; tagged instrumentation `[DEBUG-a4f2]` so cleanup is one grep. Leading word: **tight** (a 2-second deterministic repro).
- **hitl-loop.template.sh** — *Structure the human as a subroutine.* A bash script drives the human via `step "<instruction>"` and `capture VAR "<question>"`, printing `KEY=VALUE` for the agent to parse. Manual observation returns through a deterministic channel.
- **tdd** — *Vertical slices; test only at pre-agreed seams.* "No test is written at an unconfirmed seam." Refactoring removed from the loop ("It belongs to the review stage"). Leading word: **tracer bullet**.
- **tdd/tests.md** — *Tautological-test anti-pattern with a mechanical tell.* Expected values must be independent literals, not recomputed; "the tell: the test breaks when you refactor but behavior hasn't changed." BAD-vs-GOOD code shown.
- **tdd/mocking.md** — *Binary mock/don't-mock list.* Mock only at system boundaries (APIs, DB, time, FS); never your own collaborators. Prefer SDK-style per-operation functions over one generic `fetch`.
- **codebase-design** — *Frozen glossary that bans synonyms.* "Use these terms exactly." Redefines depth as leverage, explicitly rejecting Ousterhout's lines-ratio ("rewards padding"). Two tests: the **deletion test** and "one adapter = hypothetical seam, two = real."
- **codebase-design/DESIGN-IT-TWICE** — *Parallel adversarial designers.* Spawn 3+ agents, each pinned to a divergent constraint (minimize interface / maximise flexibility / optimise common caller / ports-and-adapters), then compare. "Be opinionated — the user wants a strong read, not a menu."
- **code-review** — *Two independent axes, never merged.* "Standards" and "Spec" run as separate sub-agents; "Do not merge or rerank findings — the axes are intentionally independent" (standard code implementing the wrong thing passes Standards, fails Spec). Fixed-point diff; 12-smell baseline; each sub-agent under 400 words.
- **implement** — *Pure orchestration router* (~5 lines): use /tdd at pre-agreed seams, typecheck/test regularly, /code-review, commit. User-invoked.
- **research** — *Background agent + primary-source-only.* "Follow every claim back to the source that owns it"; write to one cited Markdown file.
- **grilling** — *One-question-at-a-time decision-tree interview* (full spec in §4).
- **handoff** — *Compaction by reference* (full spec in §5).
- **teach** — *Parametric knowledge treated as untrusted.* Grounds every claim in a citation; keeps a durable `MISSION.md` + learning records; leading words **storage strength** vs **fluency**.

---

## 4. The `grilling` pattern (reimplementation spec)

Mental model: **a decision tree.** "every plan branches into decisions, and decisions depend on each other. grilling descends that tree one node at a time, so an early answer can reshape which questions come next."

Turn-by-turn:
1. Identify the plan's open decisions and their dependency order (parents before dependents).
2. **Ask exactly one question at a time, then wait** — "never a bulk list, which is bewildering."
3. **Each question ships with the agent's own recommended answer.**
4. **Any question the codebase can settle, the agent resolves by reading**, not by asking.
5. Each answer feeds back into the tree, re-deciding the next question.
6. **Stop** when "every implicit call [is] made explicit" and shared understanding is confirmed — not when agreement comes quickly.
7. **Output: stateless — no artifacts.** The product is the sharpened understanding. (`grill-with-docs` runs the same interview but emits ADRs + glossary; `to-spec` writes the spec downstream.)

`grilling` is a **model-invocable primitive** ("single source of truth for the interview technique") that `grill-me`, `grill-with-docs`, `improve-codebase-architecture`, and `triage` all call. Directly relevant to our ux-interview + brainstorming question — but that is a **D2/consolidation** call, not a criteria call.

---

## 5. The `handoff` pattern (and overlap with our `.agent/` model)

Compacts the current conversation into a single handoff document a fresh agent can read to resume. **Compaction by reference, not copy:** "Anything captured in a spec, plan, ADR, issue, commit, or diff is referenced by path or URL, never copied." Written to the **OS temp dir, not the workspace** — deliberately ephemeral.

Overlap with our `.agent/memory.md` + `session-log.md`: **partial, and opposite in persistence.** Both distill state for a future agent, but ours is *durable, in-repo, continuously maintained*; handoff is a *one-shot, ephemeral, temp-dir* snapshot. It is session-continuity, not repo-continuity. (Their `teach` skill *does* keep a durable `.agent`-like store.) Conclusion: **no new skill needed** — our continuity model already covers this ground, better, for our use.

---

## 6. Where their technique conflicts with our rules (the tensions)

"Make ours behave similarly" is **not** "adopt their conventions." Their most effective moves violate our current checklist:
- **Voice.** They coach in imperative 2nd/1st person ("Be aggressive. Be creative. Refuse to give up."). Our rule: third-person tool voice only. Imperative is more behavior-steering.
- **Fixed template.** Their form-follows-function structure vs our mandatory "Workflow (Deterministic)" skeleton. This is the biggest tension — the template is both our consistency guarantee and our main source of no-op sediment.
- **Embedded activation cues.** Their model-invoked `description` carries triggers; ours are always externalized to trigger-case files (a portability choice — our frontmatter must work across Codex/Claude/Copilot).
- **Credited authorities.** "Seam (Michael Feathers)", Fowler's smell list. We ban personas — but crediting a named pretraining concept is a *leading-word* move, not a persona. Worth distinguishing in the rule.

---

## 7. Decisions needed from you

"Our criteria" = `scripts/auditing/SKILL_REVIEW_CHECKLIST.md` (the binding bar the audit + parallel reviews enforce). Updating it = adding/removing checklist items. **Nothing is changed yet.** The candidates:

### Bucket A — additive, no conflict (recommend: adopt all five)
1. State the north star: **predictability of *process*** over completeness/cleverness.
2. **Leading-word** criterion — each skill anchors on one concept where one exists.
3. **Teach-by-contrast** criterion — prefer BAD-vs-GOOD examples; allow a "Rejected framings / anti-patterns" section.
4. **No-op / pruning** criterion — every sentence earns its place; flag boilerplate that only restates the template.
5. **Behavioral-gate** guidance — where a skill prevents a default failure, encode a hard stop, not just an "Output:" line.

### Bucket B — requires relaxing one of *our* rules (your ruling on each; these change the library's character)
1. **Template rigidity vs pruning** — allow structural variation instead of the mandatory Workflow-Deterministic skeleton? *(This is the load-bearing one: A-4 partly requires B-1.)*
2. **Voice** — allow imperative instruction voice (while still banning personas)?
3. **Activation cues** — keep always-external, or allow description-embedded triggers for portability-safe cases?

### Bucket C — keep rejected, but document *why* in the checklist
Routers/dispatcher skills, cross-skill `/name` invocation, a shared setup skill, hard dependencies, plugin-only distribution — so future authors don't cargo-cult them from mattpocock.

**Recommended path:** adopt all of Bucket A; rule B-1 first (it gates the value of A-4); then B-2 and B-3. Only after your rulings do we touch `SKILL_REVIEW_CHECKLIST.md`.
