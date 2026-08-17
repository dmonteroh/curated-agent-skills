# DX reference material

Supporting detail for `../SKILL.md`. Read the section relevant to the step in progress rather than the whole file — it exists to be looked up, not memorized.

## Persona archetype examples (Step 2a)

Starting points for proposing concrete archetypes — adapt to the actual product rather than picking one verbatim. Each is deliberately specific about tolerance and context, because "developers" as an audience is too broad to score against.

- **Founder building an MVP** — roughly a thirty-minute integration budget, won't read documentation beyond a README, copies working code directly from the getting-started page.
- **Platform engineer evaluating for adoption** — thorough, reads the security model and SLA before committing, cares about CI integration and operational visibility more than raw feature count.
- **Frontend developer adding one feature** — cares about type definitions, bundle size, and framework-specific examples (React/Vue/Svelte) over a generic quick start.
- **Backend developer integrating an API** — wants a working curl example, a clear auth flow, and rate-limit documentation before writing any code.
- **Open-source contributor arriving from a repository** — expects `git clone && <one command> test` to work, a contributing guide, and issue templates that make the first PR low-friction.
- **Developer new to the domain** — needs explicit hand-holding, error messages that teach rather than assume, and more worked examples than an experienced user would want.
- **Infrastructure engineer setting up automation** — expects infrastructure-as-code support, a non-interactive mode, and environment-variable configuration over an interactive wizard.

## Error-message quality tiers (Step 4, dimension 3)

Three shapes of error message, in increasing structure, useful as a reference bar rather than a template to copy verbatim:

**Conversational.** First person, complete sentences, points at the exact location, suggests the fix in place. Example shape (paraphrased from the Elm compiler's error style):

```
-- TYPE MISMATCH ---- src/Main.elm
I cannot do addition with a value of this type here:
42|   "hello" + 1
     ^^^^^^^
Hint: to put strings together, use the (++) operator instead.
```

**Annotated source.** A stable error identifier, source shown inline with the exact span marked, and a suggested edit rather than just a description of the problem. Example shape (paraphrased from Rust's compiler diagnostics):

```
error[E0308]: mismatched types
 --> src/main.rs:4:20
help: consider borrowing here
  |
4 |     let name: &str = &get_name();
  |                       +
```

**Structured, machine- and human-readable.** A small fixed set of fields — error type, a stable code, a human message, which parameter caused it, and a link to documentation for that specific error. Example shape (paraphrased from Stripe's API error format):

```json
{"error":{"type":"invalid_request_error","code":"resource_missing","message":"No such customer: 'cus_nonexistent'","param":"customer","doc_url":"https://example.com/docs/error-codes/resource-missing"}}
```

The common formula across all three: what happened, why, how to fix it, where to learn more, and the actual value that caused it. A message lacking any of these five is a concrete, citable finding, not a stylistic preference.

**Anti-pattern worth naming:** an error chain that buries the actionable "did you mean…" suggestion at the bottom of a long trace. The most actionable line should appear first, not last.

## Gold-standard shapes, by dimension (qualitative only)

Illustrative, not exhaustive — use to calibrate what a 9-10 looks like, not as a checklist to match feature-for-feature. Numbers describing adoption impact or conversion lift are deliberately omitted here: none in the material this reference was drawn from carried a verifiable source, and an unsourced percentage is worse than no number at all.

- **Getting started:** a working call in a handful of lines, with the developer's own test credentials already filled into the example when they're logged in; a shell that runs API calls from inside the docs page itself, with nothing to install locally first.
- **API/CLI/SDK design:** identifiers prefixed by type (so passing the wrong kind of ID to the wrong field is visibly wrong at a glance); mutation endpoints that accept an idempotency key so retries are safe by default; a CLI that detects terminal vs. piped output and adjusts formatting accordingly.
- **Documentation:** a persistent code-language switcher that holds its selection across every page; example code that is the literal code run to produce the shown output, not a hand-written paraphrase of it.
- **Upgrade path:** a single command that runs every relevant codemod for a major upgrade in one pass, rather than requiring the developer to find and run each one manually.
- **Environment fit:** sub-second local dev loops; installation and first-run that work identically across the operating systems the persona actually uses, without a platform-specific caveat buried in the docs.

## Named measurement frameworks (Step 4, dimension 8)

Borrow dimensions from published frameworks rather than inventing new ones when a plan needs to state how DX will be measured after shipping:

- **SPACE** (Microsoft Research) — Satisfaction, Performance, Activity, Communication, Efficiency. Recommends measuring across at least a few of these dimensions rather than any single one.
- **DevEx** (ACM Queue) — organizes around feedback loops, cognitive load, and flow state; combines perceptual (survey) data with workflow (instrumented) data.
- **Fagerholm & Munch** (IEEE) — a cognition / affect / conation framing for developer experience, i.e. what a developer thinks, feels, and is motivated to do.

These are cited as starting points for a measurement plan, not as a mandatory rubric — pick whichever dimensions the specific product can actually instrument.

## Output templates (optional convenience)

Journey map, filled in during Step 2f and finalized in the output contract:

```
STAGE          | WHAT THE DEVELOPER DOES  | FRICTION POINTS      | STATUS
---------------|---------------------------|----------------------|--------
Discover       |                           |                      |
Install        |                           |                      |
Hello world    |                           |                      |
Real usage     |                           |                      |
Debug          |                           |                      |
Upgrade        |                           |                      |
```

Scorecard, filled in after Step 4:

```
Dimension               Score
Getting started         __/10
API/CLI/SDK design      __/10
Error messages          __/10
Documentation           __/10
Upgrade path            __/10
Environment fit         __/10
Community               __/10
DX measurement          __/10
Time-to-first-result    __ (tier: Fast / Workable / Slow / Blocking)
```
