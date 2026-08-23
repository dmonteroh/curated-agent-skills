---
name: refactor-clean
description: "Provides an incremental, test-first refactoring workflow for reducing complexity or duplication while keeping behavior stable, best used during technical-debt cleanup or design improvement."
metadata:
  category: workflow
---
# Refactor Clean

## Use this skill when

- Refactoring tangled or hard-to-maintain code.
- Reducing duplication, complexity, or code smells.
- Improving testability or design consistency.
- Preparing modules for new features without regressions.
- Deciding whether recently written or generated code should exist at all, before spending effort improving it.
- Cleaning up a bounded set of recently changed files — a branch diff, a review scope — while preserving behavior.

## Do not use this skill when

- A small, targeted fix is all that is needed.
- Refactoring is blocked by policy, deadlines, or change freeze.
- The request is documentation-only or purely stylistic.
- The goal is a performance change whose equivalence needs a benchmark or a proof: that is a separate change with its own measurement, not a cleanup slice.

## Required inputs

- Target files/modules or a clear scope boundary.
- Behavior that must not change (invariants, contracts, API expectations).
- Allowed change scope and any constraints (deadlines, perf budgets, style rules).
- Available tests or how to verify changes.
- How test coverage is determined for the target — a coverage tool, or the fact that there is none and the tier will be a judgment.

## Workflow

1) Confirm intent and scope
   - If scope or invariants are unclear, ask clarifying questions before editing.
   - Output: a one-paragraph scope statement and non-goals.

2) Map the blast radius
   - Finding *where the code smells* and finding *what this change will touch* are different jobs, and a hotspot scan answers only the first. Before planning, build an impact map for the target: where it is defined, everything that imports or calls it, the analogous implementations that establish the convention it must keep following, and the tests that cover any of it.
   - Summarize the map as impact zones — core, consumers, edge — each with a risk level, the number of files affected, and **its own test coverage**. Coverage at the edge is routinely not the coverage at the core, so record it per zone rather than once for the target.
   - From the map, state the constraints the refactor inherits: patterns it must follow, dependencies it must not break, zones isolated enough to change freely, and any change that would force consumers to migrate.
   - Decision: if the pass also carries a correctness fix (only when the caller asked for one), read the callers of every shared function it touches and fix the root cause at the shared seam. A per-caller guard that leaves a sibling caller broken is a partial fix, not a cleanup.
   - Output: the impact map, the zone table with per-zone coverage, and the inherited constraints.

3) Establish a safety net, and authorize the work against the coverage the map found
   - If tests exist, run the most relevant subset.
   - If tests are missing, add minimal characterization tests for refactor seams.
   - If the refactor closes a deprecated write path (redirecting writes to a corrected owner, even if the old target stays legitimately readable during a deprecation window), add a grep-based test asserting no file outside a named allowlist still writes to it, landed in the same change as the fix — a closed path with no tripwire is one copy-paste away from reopening.
   - Decision (authorization gate), read off the coverage of the zones in scope. Strong coverage: proceed, running the existing tests after each step. Partial coverage: proceed, but add assertions around the uncovered seams first. Weak coverage: pause and propose writing tests before refactoring. **No coverage: refuse the aggressive form of the refactor** and put three options to the caller — add tests first (recommended), proceed with reduced scope and named manual verification, or abort. The gate must be able to say no; a safety-net step that always proceeds is a checklist, not a gate.
   - The tiers are a risk-tiering judgment, not a measurement. Use a coverage tool's number where the project has one; where it does not, record the tier as an estimate and label it as one. Any percentage boundary drawn between the tiers is a chosen convention — this skill states none (`references/testing-and-quality.md`).
   - Guard removal is proof-required: before deleting any validation or error handling at a trust boundary, land an **adversarial** regression test — malformed or hostile input — that fails when the guard is gone. No adversarial test, the guard stays. A guard is redundant only when it duplicates a check that already runs *inside* the boundary; a guard with no demonstrated duplicate is load-bearing.
   - Capture the pre-change diagnostic and lint output as a baseline. The bar afterwards is that the output *matches the baseline*, not that it is empty — an empty-output bar makes a pre-existing warning hide a new one.
   - Output: tests to run, any new tests added, the coverage tier with how it was determined, and the authorization decision.

4) Identify hotspots
   - Run the skill's `scripts/scan_hotspots.sh` (see Script section below) or use manual heuristics.
   - Output: 1–3 targets with a short risk/impact note each.

5) Run the deletion ladder before any smell analysis
   - For each unit in scope, walk these rungs in order and stop at the first that applies:
     1. **Delete entirely** — the behavior is not needed: speculative, YAGNI, dead on arrival.
     2. **Reuse** — an existing helper or established pattern in this repository already does it; replace the reimplementation with a call to it.
     3. **Platform** — the language standard library, the runtime, or an already-installed dependency already does it: a hand-rolled date picker becomes the native date input, a custom query parser becomes the platform's URL parser, a bespoke debounce becomes the one already imported.
     4. **Simplify in place** — it must exist; make it smaller.
   - Only units that land on rung 4 proceed to smell-level cleanup. One function replaced by a platform call is a larger and safer win than any in-place cleanup, and it needs no per-line analysis at all. The default this inverts is going straight from a hotspot to an extraction, which improves code that should not have been there.
   - Rung 1 removes behavior rather than preserving it. It stays inside the scope confirmed in step 1 and is proposed to the caller before it is executed — never folded silently into a cleanup slice.
   - Output: per unit, the rung it landed on and what replaces it.

6) Plan small slices
   - If the change is large or risky, propose a staged plan before editing.
   - Prefer interface-preserving steps (rename, extract, inline, encapsulate).
   - Order slices by ascending risk rather than by discovery order. Default sequence: comments → dead code → over-defensive guards → duplication → complexity → abstraction and layering → performance → tests → module splitting. This ordering is a chosen default, not a measured one; what it buys is that the blast radius of any single slice is the smallest available at that point, and a failure is attributable to the riskiest thing attempted so far.
   - If a slice deliberately keeps a bounded shortcut — a naive scan that is fine below some row count, a coarse lock, an accepted quadratic path — mark it in code with a `debt:` comment naming the ceiling it is safe under and the condition that should force the upgrade, and list it in the report's deferred section. The ceiling is whatever bound was chosen for this code, recorded as a choice; this skill supplies no default value for it. A simplification with a known ceiling and no marker is indistinguishable from a bug to the next reader, and the deferred section then works as a debt ledger rather than a disclaimer.
   - Output: ordered steps with risk notes.

7) Refactor incrementally
   - Make one small change at a time and keep diffs focused.
   - Avoid mixing behavior changes with cleanup unless explicitly required.
   - Preview any transformation applied at many sites at once — a codemod, a structural pattern rewrite, a bulk rename — in dry-run mode and review the complete match set *before* applying it, and prefer a tool-verified rename (a language server's or an IDE's rename) over a textual search-and-replace (`references/refactor-strategies.md`).
   - When verification goes red mid-pass: stop, **revert that step**, diagnose from the known-good state, then retry, drop the step, or escalate. Never carry a red suite into the next step, and never fix forward from a state nobody has verified.
   - Output: brief log of each completed slice.

8) Verify and report
   - Run tests and targeted checks after the refactor.
   - Compare diagnostics and lint against the baseline captured in step 3; new entries relative to that baseline are failures even when the file was never clean.
   - If verification cannot be run, state what should be run.
   - Output: verification results and any remaining risks.

## Abort conditions

These stop the pass mid-flight and hand it back to the caller. `Do not use this skill when` covers only what is knowable before the pass starts; these are the states that appear during it.

- The target has no test coverage at all and the caller has not chosen one of the options offered by step 3's gate.
- The change would break a public API that was not in the approved scope.
- Scope is still unclear after one round of clarifying questions.
- A constraint stated in Required inputs would have to be violated to continue.
- The same step fails verification repeatedly with no new hypothesis for why. Fix that retry ceiling before starting and treat it as a chosen budget, not a measured limit.

On abort, report what was attempted, what failed, and the current state of the tree — including which steps were reverted.

## Common pitfalls

- Broad rewrites without a safety net.
- Mixing formatting changes with structural changes.
- Letting refactors drift into new feature work.
- Deleting or weakening a test to make it pass.

## Scripts

- Purpose: quick inventory of large files and TODO/FIXME density.
- Usage: run from the target repo root, invoking the script by its path inside this skill's folder: `HOTSPOT_LIMIT=20 sh <skill-folder>/scripts/scan_hotspots.sh`
- Requirements: POSIX shell; uses `rg` if available, otherwise `find`, `wc`, `awk`, `sort`, `head`.
- Verification: output should include "Largest Files" and "TODO / FIXME Counts" sections.

## Examples

**Example 1: request for incremental refactor**

Input: "Refactor `orders.py` to remove duplication. Keep API behavior identical and tests are in pytest."

Expected output (summary):

- Scope: `orders.py` duplication cleanup, no API changes.
- Hotspots: repeated pricing logic, long validation function.
- Plan: extract pricing helpers, consolidate validation, run pytest subset.
- Verification: `pytest tests/orders`.

**Example 2: request for plan only**

Input: "Give me a plan to clean up this payment service without changing behavior."

Expected output (summary):

- Hotspots and risks identified.
- Ordered refactor slices with rationale.
- Test/verification plan.

**Example 3: the ladder changes the answer**

Input: "Clean up `date_picker.ts` — it is 200 lines and hard to follow."

Wrong: extract three helpers out of the custom picker, tidy the nesting, report a smaller file.

Right (summary):

- Blast radius: 4 call sites, all in one form module; the edge zone has no tests, so a characterization test on the form's submit payload lands first.
- Ladder: rung 3 (platform) — the component reimplements the native date input; delete it and its date-parsing dependency, and update the call sites.
- Result: the file is gone rather than tidier, and no in-place cleanup was needed.
- Verification: form tests plus the new characterization test; diagnostics match the pre-change baseline.

## Output contract

When this skill runs, report:

- Scope and invariants.
- Blast radius: impact zones, files affected, and per-zone coverage.
- Coverage tier, how it was determined (tool or judgment), and the authorization decision.
- Hotspots or target areas with brief rationale.
- Deletion-ladder outcome per unit: the rung it landed on and what replaces it.
- Plan or changes made (ordered, small slices).
- Risks or follow-up recommendations, including every `debt:` marker left in code with its ceiling and upgrade trigger.
- Verification performed or explicitly not run.

## References

- `references/README.md` for detailed playbooks and checklists.
