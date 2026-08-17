# Finding triage: exclusion ledger, precedents, and evidence gates

Detail behind instruction step 4. This is the apparatus for *not* reporting vulnerabilities that are not there.

A machine-assisted audit fails by over-reporting, not by missing things. Given a codebase and an instruction to find vulnerabilities, a model produces a long list of plausible ones, because plausibility is what it is generating. Every item below exists to make a candidate earn its way into the findings table, and each is a stop that can fail rather than an encouragement to be careful.

Triage order: discard by ledger, then verify without anchoring, then gate on quoted evidence, then apply the display rule for the engagement's confidence gate. A candidate that survives all four is a finding; nothing else is.

## How the rules below are marked

Each carve-back in the exclusion ledger and each standing precedent carries a mark for the basis it rests on, because a reader about to discard a real vulnerability on the strength of one deserves to know which kind it is:

- **[case]** — debugged against a real audit. The plain rule over-fired on something real, and the text after the mark is the record of that correction.
- **[judgment]** — reasoned from the shape of the rule, never tested against a case. Defensible and in force, but weaker evidence: where a **[judgment]** limit is the only thing standing between a candidate and the discard pile, read the code before discarding.

The mark ranks how well tested a rule is, not whether to apply it. Both kinds are in force.

The marks concentrate on the ledger and the precedents, where the decision being made is whether to discard. The procedures in the later sections — anti-anchoring verification, the quote gate, variant analysis, filter stats and fingerprinting — come from the same working audit; the single row extended past it is marked in place.

Every number in this file is a chosen default. None is measured, and none should be quoted as if it were.

## Confidence scale

Score every candidate on one scale, used identically at every stage:

| Band | Meaning |
| --- | --- |
| 9-10 | The path from an untrusted input to the sink is quoted end to end. |
| 7-8 | A recognized vulnerability pattern with known exploitation methods, and the motivating line is quoted. The minimum bar for a normal report. |
| 5-6 | The pattern is present, but one link in the chain was inferred rather than read. |
| 3-4 | Plausible from the shape of the code; no motivating line can be quoted. |
| 1-2 | Speculative. |

**The band boundaries are chosen defaults, not measured.** No data supports 7-8 as the reporting bar rather than 6-7. Keep them while they discriminate usefully; if a band is doing no work, change it deliberately and record the change rather than drifting.

## The gate is set by engagement mode, before triage begins

Decide the gate from how the report will be consumed, once, at the start — never per finding, where the temptation is to lower it for the finding currently in hand.

| Engagement mode | Gate |
| --- | --- |
| Recurring or unattended sweep, read in passing, running on every change | Report only 7-8 and above. Zero noise is the objective: a sweep that reports a maybe trains its reader to skip the next one, including the one that mattered. |
| Commissioned comprehensive assessment, read in full by a person | Gate low, but mark everything below 7 as tentative and route it by the display rules. |

Display rules, applied after the gate:

| Band | Recurring sweep | Comprehensive assessment |
| --- | --- | --- |
| 9-10 | Report normally | Report normally |
| 7-8 | Report normally | Report normally |
| 5-6 | Suppress | Report with an explicit caveat naming the inferred link |
| 3-4 | Suppress | Appendix only, never the findings table |
| 1-2 | Suppress | Omit, unless the severity would be top-band — then appendix, with the reason it could not be verified |

## The exclusion ledger

Classes discarded on sight, however plausible the individual candidate looks. The right-hand column is what keeps each rule from over-firing. **An exclusion without a carve-back is not ready to ship** — an unqualified exclusion is an unbounded one. But a **[judgment]** carve-back has not yet caught anything, only predicted what it would catch, and a ledger whose carve-backs are all **[judgment]** has not yet been used in anger.

| Discarded on sight | Carve-back |
| --- | --- |
| Denial of service and resource exhaustion | **[case]** Cost amplification against a metered, per-call-billed dependency is financial risk, not resource exhaustion. Never auto-discarded. |
| Memory-safety findings in a memory-safe language | **[judgment]** Explicitly unsafe regions are outside the language's guarantee: unsafe blocks, foreign-function boundaries, native extensions, and hand-written runtime bindings. |
| Log spoofing and log injection | **[judgment]** When a log stream is parsed by something that acts on it — alerting, billing reconciliation, or a model reading it as input — it is an input channel crossing a boundary, not a record. |
| Missing audit logs | **[judgment]** When the record is the only evidence that a required control ran, or a compliance target names it, its absence is the finding. |
| Missing hardening measures, as distinct from a concrete vulnerability | **[judgment]** A missing control becomes a finding the moment something concrete crosses the boundary it would have gated. Report the crossing, with the missing control as its remediation — never the absence on its own. |
| Server-side request forgery where the attacker controls only the path | **[judgment]** Path alone is sufficient against a host whose sensitive routes are path-selected; instance-metadata and admin endpoints are the standard cases. |
| Insecure randomness outside a security context | **[judgment]** Any value that gates access, resets a credential, or must be unguessable is a security context regardless of what the generating API is named: session identifiers, tokens, reset nonces, invite codes. |
| Regular-expression denial of service on inputs that are not untrusted | **[judgment]** Re-check the input's provenance before discarding. A field that is user-controlled two hops upstream is untrusted here. |
| Findings in documentation files | **[case]** Agent skill files, prompt templates, and instruction files share the documentation file extension but are executable instructions that steer an agent's behavior. A documentation exclusion does not reach them. |
| Advisories in the CVSS Low band with no known exploit | **[judgment]** Reachability changes this: an advisory whose vulnerable path is called from an entry point, or that composes with another candidate, is triaged on the composite, not on its own score. |
| Findings in test-only files | **[case]** Pipeline and continuous-integration contexts execute with real credentials. A file that runs in the pipeline is not test-only, and pipeline findings are never discarded by this rule or the development-file rule below. |
| Findings in development-only container and compose files | **[judgment]** Confirm which file the deployment actually builds from. The same construct in a production image, chart, or manifest is a finding. The root-container instance of this one is a settled call — see the precedents below. |
| Archived or disabled workflows | **[judgment]** An archived workflow a scheduler can still trigger, or that another workflow references as reusable, is live. |

**[case]** Do not carry a trust carve-out for any particular vendor's or team's own files. The ledger this one derives from carried exactly that carve-out, for its own author's files, and it was cut: first-party code is where the audit's own blind spot lives, and an exclusion naming it is a permanent one.

## Standing precedents

The positive counterpart to the ledger: calls already settled, recorded once and cited by name afterwards rather than re-argued each audit. Each call below was settled in a real audit; two carry a later limit that was not.

- **[case]** A randomly generated UUID is unguessable and is not a weak-secret finding. **[judgment]** A sequential or time-ordered identifier is not covered by this precedent.
- **[case]** Environment variables and command-line flags are trusted input: they come from whoever ran the process. **[judgment]** The precedent lapses where a remote-triggered pipeline or a service interpolates untrusted data into them.
- **[case]** Auto-escaping template and view layers are cross-site-scripting-safe by default. Flag only the escape hatches — the raw-HTML properties, bypass-sanitization helpers, and unescaped interpolation directives — not ordinary interpolation.
- **[case]** Client-side code does not enforce authorization; a missing client-side check is not a finding, because the server is the control point. The finding, if there is one, is the server trusting the client.
- **[case]** A lockfile untracked in version control is a finding for an application repository — builds stop being reproducible and dependency pinning is lost — and is not one for a library repository, where its exclusion is deliberate.
- **[case]** A container running as root in a local-development compose file is not a finding. The same in a production image, chart, or manifest is.

## Anti-anchoring parallel verification

Every candidate that survives the ledger is verified by an independent pass with fresh context.

**What the verifier receives:** the file path, the line number, the exclusion ledger, and the precedents.

**What the verifier must not receive:** the candidate's title, description, severity, category, or any of the reasoning that produced it.

A verifier handed the claim confirms the claim; agreement then carries no information, and the second pass has cost time to manufacture false confidence. Withholding the description is the whole mechanism, not a detail of it. The verifier reads the cited lines cold, states what it finds there, and scores on the confidence scale above. Below the gate, the candidate is discarded.

Falsifiable check: read what the verifier was given. If a reader can reconstruct the suspected vulnerability from it, the pass was anchored and its result must be thrown out, not weighted.

**Verify by tracing code, never by exercising live systems.** Do not send requests to production or third-party endpoints to prove a finding — an audit that triggers the vulnerability it is documenting has caused the incident it was hired to prevent, and the outbound request is itself unauthorized traffic. Trace from entry point to sink in the source.

**Dependency findings are verified only when the vulnerable function is directly called.** Otherwise mark them unverified and state the caveat explicitly: framework internals, transitive callers, and configuration-driven code paths can all reach a function no direct call names, so "not called" is a statement about what was read, not proof of unreachability.

**A verified finding triggers variant analysis.** Search the codebase for the same pattern before moving on: one confirmed instance of a class of mistake is evidence the pattern was reused. Report each variant as its own finding, linked to the original, and put each through the same gates — inheriting a confidence score from the original defeats them.

## The pre-emit quote gate

To emit a finding at reportable confidence, quote the specific line or lines that motivate it. The standard is *the source that creates this symbol was read* — not *the name was searched for and not found*.

| Claim shape | What must be quoted |
| --- | --- |
| "Field X is not defined on model Y" | The class, struct, or schema body where it would be declared |
| "This lookup can return null" | The initialization or construction site of the container |
| "A and B race" | Both sides of the race |
| "This input reaches the sink unvalidated" | **[judgment]** The entry point and the sink |
| The symbol is generated rather than written | The generating construct itself — the metaclass, the object-relational meta class, the decorator, the migration, the code generator's input |

**If no motivating line can be quoted, the finding is unverified.** Drop its confidence into the appendix band and move it out of the findings table.

**Never raise a confidence score to clear this gate.** A score invented to pass a gate makes every other score in the report meaningless, and the gate exists precisely because inventing plausible confidence is the cheapest available action.

The classes of false positive this removes are exactly the ones a name-level search produces: attributes that exist but are generated at import or migration time; methods supplied by a mixin, base class, or plugin registry; null-return claims contradicted by the initializer three lines above; and races between operations that a lock or a single-writer design already serializes.

## Filter stats and cross-audit fingerprints

Report `N candidates → M discarded by rule → K discarded on verification → J reported` on every audit. The suppression apparatus has to be auditable itself, or it silently becomes a ceiling on what the audit can ever report, and nobody can tell an audit that found nothing from one that suppressed everything.

Fingerprint each finding on a stable hash over its category, file, and normalized title, and carry fingerprints between audits to classify findings as resolved, persistent, or new, with the trend direction stated. Fingerprinting on the title alone re-reports a renamed finding as new and loses the resolved count; including the category and file is what makes the comparison hold across edits that move a line.
