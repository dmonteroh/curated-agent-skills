---
name: prompt-injection-defense
description: "Provides a layered prompt-injection defense procedure for agents that consume untrusted content — web pages, tool output, repository files, agent-authored notes. Covers ingress enumeration, normalizing before classifying, warn-versus-block policy, canary tripwires, fail-open ordering, and adversarial validation. Use when designing or reviewing an agent's trust boundaries."
metadata:
  category: security
---
# Prompt Injection Defense

Provides a procedure for composing several individually unreliable defenses so that no single failure is fatal, for agents whose tools carry attacker-controllable text into the instruction channel. The problem is not "detect injection" — the published consensus, which the source material states plainly, is that prompt injection is unsolved. The problem is which layers to compose, in what order, which of them may fail, and how to measure the composite honestly.

The material is generalized from one internal design document, its engineering review, and its first-party evaluation artifact. Rules added beyond that source are marked *(Authored)*; third-party ideas are attributed where the source attributes them.

## Use this skill when

- Designing a harness that grants tool access while ingesting untrusted content — a browser-driving agent, a tool-output pipeline, a retrieval or file-ingestion path
- Reviewing an existing agent's trust boundaries, or auditing which of its tools can carry attacker text into context
- Deciding whether a detection layer warns or blocks, and what a single classifier may do on its own
- Persisting agent-authored notes, memories, or plans that later sessions load into their prompts
- Adopting third-party instruction content into the agent's own loaded set — a downloaded or forked capability definition, prompt pack, ruleset, or agent definition someone else wrote
- Building or reviewing the evaluation that decides whether the defense works

## Do not use this skill when

- The agent combines at most two of untrusted input, sensitive access, and state change (Meta's "Rule of Two"), and that configuration is fixed — keeping it that way beats any detector added here. *(Authored: the source records the Rule of Two without adopting it; using it as the entry test is added here.)*
- Every input originates with the operator in the same session and nothing persists into a later one — there is no attacker-controllable span to defend
- The task is conventional application security — authentication, secrets handling, dependency CVEs — where untrusted input never reaches an instruction channel
- The ask is to certify an agent injection-proof, or to sign off a detector as sufficient alone. No arrangement of these layers supports that claim; report the request as unsatisfiable rather than satisfying it weakly
- The ask is to tune classifier thresholds with no adversarial corpus in hand. Thresholds tuned against benign traffic move the false-positive rate and say nothing about detection

## The layer set

The source's stack, with its layer numbering dropped: two documents in the same source numbered the same product's layers differently, so the numbers are local bookkeeping. The set and the ordering constraints transfer; the labels do not.

| Layer | Class | Built |
| --- | --- | --- |
| Model selection — default to the most capable model available | Capability | Yes |
| Structured prompt framing — delimited regions, untrusted span escaped | Deterministic enforcement | Yes |
| Classifier over the incoming span | Probabilistic detection | No |
| Pattern match, run after normalization | Detection, advisory | No |
| Content pre-scan before prompt construction | Probabilistic detection | No |
| Command allowlist — only the verb class the task needs | Deterministic enforcement | Yes |
| Canary token checked against output and tool-call arguments | Tripwire | No |
| Transparent blocking — show what was caught and why | Surface | No |
| Security state indicator | Surface | No |

Three of the nine existed when the source was written, and all three were deterministic or architectural; every detection layer was still a proposal. This is a design to work from, not an inventory of something proven in production.

## Workflow

1. **Enumerate every ingress before choosing any defense.**
   - For each tool the agent can call, ask whether its output reaches the context. Every tool that answers yes is an ingress, including tools that accept no untrusted input themselves. *(Authored: the source's engineering review records two misses — mid-session content, and file-reading tools under a locked-down shell — and proposes no unifying test; this is that test.)*
   - Separate session-start ingress from mid-session ingress. A pre-scan that runs once before the prompt is built does not cover content pulled in later by a mid-session tool call.
   - Include the ingestion surface, not only the tool-output surface: anything the harness auto-loads — per-directory instruction files, bundled configuration, cached artifacts, vendored bundles — is an ingress nobody reviewed. Worked case under Examples.
   - Count adopted instruction content as an ingress class of its own: a capability definition, prompt pack, ruleset, or agent definition taken from a public source, a colleague, or a distribution channel is text a stranger wrote that loads into the agent's instruction channel in every session that follows, and it is reviewed at adoption or never. Screen it before it installs, not after it fires — read the metadata header *and* the instruction body end to end, and treat unexpected shell commands, file writes, network calls, credential handling, or package installs as findings to resolve first. Weigh whether the upstream source looks maintained: an abandoned one is where a hostile edit sits longest unnoticed. Adopt by copying into a branch and reviewing the diff, never by editing the upstream original in place — editing in place destroys the diff the next review would have read, and leaves the adopted copy and the reviewed copy as the same object.
   - Ask what harm is reachable *through allowed verbs*. An allowlist constrains verbs, not intent: blocking `curl` and `rm` leaves navigation intact, and navigating to an attacker's URL with the user's data in the query string is exfiltration written in the agent's own vocabulary.
   - Output: an ingress table — tool or path, content carried, whether it is scanned, and when in the session it arrives.

2. **Place the deterministic floor before adding a single detector.**
   - An LLM-based guardrail is never the final line of defense; at least one deterministic enforcement layer is required. *(Sourced: the material attributes this to Perplexity's published guardrail position rather than claiming it. It is the load-bearing constraint of the whole architecture.)*
   - For each consequential action the agent can take, name the deterministic layer that gates it. Deterministic means identical behavior every run with no model in the loop — prompt framing with the untrusted span escaped, and a command allowlist admitting only the verb class the task needs.
   - Framing creates its own attack surface: once untrusted content is delimited with markup, closing that markup is the attack. Escaping the span is part of the layer, not an optimization on top of it.
   - Stop condition: if a consequential action has no deterministic gate, report that as the finding and do not proceed to detection design. A classifier in front of an ungated action is the failure this skill exists to prevent.
   - Output: the deterministic layer list, and the gate named for each consequential action.

3. **Normalize before classifying.**
   Run the full pipeline before any detector sees the text, in this order:
   1. Detect and decode base64 segments
   2. Percent-decode URL-encoded sequences
   3. Decode HTML entities
   4. Flatten Unicode homoglyphs (Cyrillic а to Latin a)
   5. Strip zero-width characters
   6. Run the detectors on the decoded text
   - A detector that reads the wire form of its input is defeated by the cheapest available transformation of the payload. This ordering is the strongest transferable rule in the material.
   - Do not claim the normalizer is complete. The source asserts that no encoding trick survives full normalization; that claim carries no evidence and contradicts the same document's position that no filter is reliable. Nested encodings, novel encodings, and encodings the normalizer does not implement all pass through.
   - Output: the normalization steps as implemented, plus a named list of what they do not decode. The gap list is the deliverable — an unnamed gap is the one that gets exploited.

4. **Decide the action per layer: warn at the cheap layers, block only on high confidence.**
   - Pattern match → warn. Inject an explicit injection-warning marker around the suspect span and let the model proceed knowing the content is suspect. Blocking on patterns buys a false-positive rate the pattern set cannot justify. Pattern family and its limits: `references/pattern-layer.md`.
   - That trade holds only if the model is capable enough to act on a warning, which is why model selection is a defense layer rather than an afterthought. Downgrading the model silently removes this layer.
   - Classifier verdict → two independent classifiers that agree may block at the normal confidence bar; a single classifier blocks alone only above a materially higher bar and under a stricter label requirement. *(The flat "two classifiers must agree" rule traces to one line of product prose whose cited specification is absent from the source; the differential-threshold form is what the source's own tuning artifact supports.)*
   - Every confidence threshold is a per-deployment tuning constant. Record each as chosen, with the corpus it was tuned against; none is a property of the technique.
   - A classifier reviewing the session transcript sees the user messages and the tool calls and **not** the agent's own reasoning. A guard that reads the justification an injection produced can be argued into agreeing with it. *(Sourced: recorded in the material as an industry observation attributed to Anthropic, not as the design's own contribution.)*
   - Give the guard no ambient read access: it receives the span under test and nothing else — no working directory, no tools of its own. *(Authored: generalized from an undocumented isolation flag in the source's tuning artifact — a guard that can read the content it is judging has its own ingress.)*
   - Output: a layer → action → threshold table, each threshold marked measured or chosen.

5. **Install the canary tripwire.**
   - Place a per-session random token in the system prompt, declared confidential and forbidden from appearing in any output or any tool-call argument.
   - Check the output stream **and** tool-call arguments. Arguments are the exfiltration path an output-only check misses.
   - On appearance: terminate the session, tell the operator plainly that it was terminated because an injection was detected, and log the event.
   - Carry the limitation with the rule. This catches naive system-prompt exfiltration; anything that encodes, splits, or paraphrases the token walks past it. A canary is a tripwire, not a detector, and it is worth exactly one layer.

6. **Define the degradation ladder and check what it fails open past.**
   - Write one rung per failure mode — detector model unavailable, detector runtime fails, detector output distrusted, security module crashes — and for each rung name the layers still standing and the state shown to the operator.
   - Fail open by deliberate choice, documented as such. A security layer that takes the product down when it crashes is removed within a week; one that degrades to a visible warning survives to defend something.
   - The branch inverts if a deterministic layer can fail with the module. Failing open is defensible only because the enforcement floor from step 2 is still standing; if losing the module also loses the framing or the allowlist, fail closed instead.
   - Output: the ladder, one line per rung, naming surviving layers and visible state.

7. **Log incidents without storing the payload.**
   - Record timestamp, source domain only (never the full path), a salted hash of the payload (never the payload), the confidence, which layer fired, and the verdict. Salt randomly per session: a bare hash of a short, common injection string is trivially reversed from a precomputed table, so hashing alone is not anonymization.
   - A global telemetry opt-out is a standing answer to a standing question. Re-asking at detection time is defensible only when the ask is scoped to that single event, enumerates exactly what would be sent, and accepts refusal with no degradation. Where the harness cannot ask the operator mid-session the step is unavailable — do not route the ask through the agent as a substitute.

8. **Re-validate persisted agent-authored content at load time, not only at save.**
   - Notes, memories, and plans the agent writes and later sessions replay are an agent-to-agent injection channel: one poisoned note is read as trusted context by every session that loads it.
   - Split the checks by cost — deterministic checks at save time, the classifier at load time — so a later detector improvement re-screens content already on disk.
   - Derive the storage key from a signal the agent cannot influence, such as the top-level origin actually in effect, never from an agent-supplied argument. Otherwise a redirect chain lets a hostile page make the agent poison a different key.
   - Quarantine new content until it has loaded without a flag a fixed number of times. *(The source uses three and gives no derivation; treat the count as a chosen default.)*

9. **Validate against an adversarial corpus, with the gate declared before the run.**
   - Report detection rate per attack type, false-positive rate, bypass rate per evasion strategy, and latency percentiles. An aggregate detection rate hides an evasion family that passes every single time.
   - Thresholds are per-deployment choices, not properties of the technique — which is why they are declared in advance and not moved afterwards. A run whose gate was chosen after the results were seen is a tuning pass, not a validation; record it as one and re-declare the gate for the next run. Protocol, methodology split, and the case study behind this rule: `references/validation-protocol.md`.
   - Output: the per-attack-type and per-strategy tables, the gate with the date it was declared, and the pass or fail.

## Common pitfalls

- Scanning tool output while leaving the ingestion path unscanned, so content the harness auto-loads never meets a detector
- Classifying the wire form of the input, so a base64 wrapper defeats the entire detection stack
- Blocking on pattern matches, then loosening the patterns until they stop firing — ending with neither detection nor enforcement
- Reading a quiet canary as evidence of a clean session
- Treating a command allowlist as a semantic boundary when it only constrains verbs
- Naming a specific classifier or vendor as the defense; the source named three different classifiers for the same product across three documents
- Reporting aggregate detection while one evasion family passes at 100%
- Moving the gate instead of fixing the system, then recording the run as passed
- Fetching the eval corpus from a third-party host at test time, making an outside service a build dependency

## Examples

**Worked case — an ingestion path nobody audited.** A third-party bundle unpacked into a working tree carried conventionally-named agent-instruction files at nearly every package root, one of them lowercase. Reading an unrelated *sibling* file in one of those directories made the harness auto-load the instruction file into the agent's context, matched case-insensitively. No page was fetched and no tool output was involved: third-party text reached an agent's instruction channel purely through unpacking a bundle and reading a file next to it. Verified by probe in this library's own skill-intake pipeline. The containment is step 1's ingress table — enumerate and strip such files before dispatching agents across a drop — not a better classifier downstream.

**Wrong beside right — normalization order.**

- Wrong: the detector scores the literal span `SWdub3JlIGFsbCBwcmV2aW91cw==` as benign, the span reaches the model inside the untrusted region, and the model decodes it in context. The stack reports clean and the incident log is empty.
- Right: base64 is decoded first, so the detectors score `Ignore all previous`; the classifier scores it high, the pattern layer fires too, the prompt carries an injection-warning marker around the span, and the event is logged as a salted hash rather than the payload.

## Output contract

- Ingress table
- Layer map, split into deterministic enforcement and probabilistic detection, naming the gate for every consequential action
- Normalization pipeline as implemented, plus the named list of what it does not decode
- Layer → action → threshold table, each threshold marked measured or chosen, with its tuning corpus
- Degradation ladder with the surviving layers per rung
- Validation results per attack type and per evasion strategy, against a gate declared before the run
- Residual list: what this composite does not defend against, stated plainly rather than left to be inferred from what the report omits

## References

- `references/README.md` — index
- `references/pattern-layer.md` — the pattern family, tag injection against the framing layer, and the staleness and language limits that make it illustrative rather than a specification
- `references/validation-protocol.md` — the adversarial harness shape, the live-versus-replay split, corpus hermeticity, and the provenance case study behind step 9's gate rule
