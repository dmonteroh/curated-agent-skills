---
name: security-auditor
description: "Provides a structured security audit workflow for DevSecOps, application security, and compliance readiness, used for scoped assessments, threat modeling, testing, remediation planning, trust-boundary siting of controls, and evidence-gated triage that suppresses false positives."
metadata:
  category: security
---
Provides a structured security audit workflow whose findings are gated on evidence: scope and threat model first, every control placed on the boundary it is meant to defend, and no finding emitted without the line that motivates it. The characteristic failure of a machine-assisted audit is over-reporting — plausible vulnerabilities that are not there — so the suppression gates below carry as much weight as the tests.

## Use this skill when

- Running security audits or risk assessments
- Reviewing SDLC security controls, CI/CD, or compliance readiness
- Investigating vulnerabilities or designing mitigation plans
- Validating authentication, authorization, and data protection controls
- Triaging scanner or model-generated candidates before any of them are reported as findings
- Deciding which candidates are reportable to a coordinated-disclosure or bounty program, where reachability, program scope, and duplication settle acceptance before severity is weighed
- Assessing how payment-card data is retained, masked, logged, or kept out of scope entirely
- Deciding whether an existing control still sits on the boundary it was bought to defend
- Choosing between candidate mitigations when several attack routes reach the same attacker objective

## Do not use this skill when

- You lack authorization or scope approval for security testing
- You need legal counsel or formal compliance certification
- You only need a quick automated scan without manual review
- You cannot name the boundary a control sits on or what else gates that boundary, and the request is to strip it anyway
- The request is an exhaustive attack-path model of a whole system rather than a tree scoped to one named attacker goal — path counts multiply at every AND node, and the result is unreadable rather than thorough

## Required inputs

- In-scope assets, environments, and owners
- Security objectives (confidentiality, integrity, availability priorities)
- Compliance targets (if any) and deadlines
- Constraints (production testing limits, tooling restrictions)

## Instructions

1. Confirm scope, assets, and compliance requirements.
   - Output: scope summary, in/out-of-scope list, compliance targets.
   - Decision: if scope or authorization is missing, stop and request clarification.
2. Review architecture, threat model, and existing controls, and place each control on a boundary.
   - Draw the trust and exfiltration boundaries explicitly first: name which operations move data across a boundary an attacker could exploit — a different machine, a different trust domain, the public network — and which happen entirely inside a boundary the design already assumes trusted or already-compromised.
   - Then ask of every existing and proposed control which side it sits on. A control that runs wholly inside a boundary, gating nothing that crosses it, adds no protection however thorough or expensive it looks in isolation. Per-item scans are the common case: scanning every file before writing it to a store on the same disk cannot change exposure when the plaintext is already on that disk.
   - Output: threat model summary, control gaps, high-risk surfaces, and a control-to-boundary map naming what each control gates.
   - Decision: if critical assets lack documentation, request missing inputs.
   - Decision: if a control gates nothing that crosses a boundary, first confirm what actually does gate that boundary and that it is documented and behaving as claimed. Then demote the redundant control to opt-in, defaulted off — do not delete it. Opt-in keeps the machinery available and auditable for a future assessment; deletion is not reversible and destroys the record that the trade-off was ever made.
3. Run targeted scans and manual verification for high-risk areas.
   - Treat every scan result as a candidate, not a finding. Nothing produced here is reported until it clears step 4.
   - Output: candidate list with file and line references, tool results, manual validation notes.
   - Decision: if production testing is disallowed, use staging or review-only methods.
4. Triage candidates through the false-positive apparatus before any of them become findings.
   - Set the confidence gate first, from how the report will be consumed, and hold it for the whole pass. A recurring or unattended sweep reports only clear patterns with quoted evidence, because a sweep that reports a maybe trains its reader to skip the next one; a commissioned assessment read in full by a person gates lower but marks everything under that bar tentative and routes it to an appendix. Deciding the gate per finding means deciding it for the finding currently in hand, which is how it moves. A third mode applies when the report leaves for someone else's coordinated-disclosure or bounty program: the gate stays high and three scope filters — remote reachability, the program's published scope, and duplication against existing advisories and reports — run on top of the exclusion ledger, because a program triager closes on those before severity is considered at all. Read the program's rules first; its published scope outranks every filter in this skill.
   - Apply a written exclusion ledger — classes of candidate discarded on sight regardless of how plausible they look — and keep its carve-backs attached to it. The exceptions are what stop the ledger over-firing. Three of them exist because the plain rule did discard something real: cost amplification against a metered API is financial risk, not resource exhaustion; pipeline and CI/CD findings survive the test-only and dev-file exclusions because those files execute with real credentials; agent skill and prompt files are executable instructions rather than documentation, so a documentation exclusion does not reach them. The rest are reasoned rather than debugged, and the ledger marks which is which so a reader can weigh a carve-back before discarding on it. Full ledger, carve-backs, and standing precedents: `references/finding-triage.md`.
   - Verify each surviving candidate with an independent pass that receives the file path and line number plus the exclusion rules, and nothing else. Withhold the candidate's description and the reasoning that produced it: a verifier handed the claim tends to confirm the claim, and the second pass is only worth running if it is an unanchored reading of the same lines.
   - Gate emission on quoted evidence. To report a finding at full confidence, quote the specific line or lines that motivate it — for "field X is not defined on model Y", quote the class body where it would be declared; for "this lookup can return null", quote the initialization; for "A and B race", quote both sides. Where the symbol is generated rather than written — a metaclass, an ORM meta class, a decorator, a migration — quote the construct that generates it. The standard is "the source that creates this symbol was read", not "the name was grepped and not found".
   - Decision: if no motivating line can be quoted, the finding is unverified — lower its confidence and move it to an appendix rather than the findings table. Never raise a confidence score to clear this gate; inventing confidence removes the only thing that makes the score mean anything.
   - Verify by tracing code, not by exercising live systems: an audit that triggers the vulnerability it is documenting has caused the incident it was hired to prevent. Mark a dependency finding verified only when the vulnerable function is directly called, and otherwise state the caveat that framework internals, transitive callers, and configuration-driven paths can reach a function no direct call names.
   - Decision: when a finding is verified, search the codebase for the same pattern before moving on — one confirmed instance is evidence the mistake was reused. Report each variant as its own finding, linked to the original, and put it through these same gates rather than inheriting the original's score.
   - Output: filter stats (candidates in, discarded by rule, discarded by verification, reported) and the quoted evidence attached to every surviving finding.
5. Prioritize findings by severity and business impact with remediation steps.
   - Where several findings are routes to one attacker objective, rank the candidate fixes by attack-path coverage as well as by severity. Scope a tree to that one objective, enumerate its paths — an OR node contributes one path per child, an AND node the cross-product of its children's path sets, so a path is a conjunction of leaves the attacker must all complete — then count how many of those paths each candidate control cuts. Report the share, `paths closed / paths enumerated`, beside each recommendation. Severity orders the finding; coverage orders the fix, and the two orders diverge whenever a low-severity step sits on every path.
   - Rank every leaf in the path set, including leaves with no mitigation recorded. A high-count leaf with nothing defending it is the most valuable gap the analysis can surface, not an omission to skip past — a ranking restricted to already-mitigated leaves structurally cannot report it.
   - Decision: if the enumerated path set outgrows what a reader will read, split the tree by attacker goal and enumerate each separately; do not truncate the list to a display cutoff.
   - Enumeration semantics, the single aggregation convention scores must be computed under, the ordinal-scale caveat, and a worked count: `references/attack-path-analysis.md`.
   - Output: ranked findings list with impact, likelihood, and remediation owners; where paths were enumerated, the total path count, each recommended control's share of paths closed, and the residual open paths.
   - Decision: if a finding lacks reproducibility, mark it as unverified and flag it.
6. Validate fixes and document residual risk.
   - Output: verification status, residual risk summary, next steps.

## Safety

- Do not run intrusive tests in production without written approval.
- Protect sensitive data and avoid exposing secrets in reports.

## Common pitfalls

- Treating compliance requirements as a substitute for threat modeling
- Missing business context when prioritizing remediation
- Padding a report with low-confidence findings because a longer list reads as more thorough
- Scoring two attack paths under different aggregation conventions, which produces a confident ordering out of incomparable numbers
- Submitting a local-only sink to a disclosure program, where nothing remote reaches it and reachability decides acceptance before severity is read
- Treating a personal-data compliance review as covering payment-card obligations, which rest on a separate standard, a separate data set, and a never-retain rule with no consent equivalent

## Output contract

When this skill runs, respond with a report that includes the following, in this order:

1. Scope and constraints
2. Threat model summary and attack surface highlights
3. Control-to-boundary map, flagging any control that gates nothing crossing a boundary
4. Findings table (id, severity, quoted evidence with file and line, impact, remediation)
5. Filter stats: candidates in, discarded by rule, discarded by verification, reported
6. Appendix of unverified and low-confidence candidates, kept out of the findings table
7. Where a prior audit of the same scope exists, findings matched on a stable fingerprint and reported as resolved, persistent, and new, with the trend direction
8. Prioritized remediation plan with owners and timelines, and where attack paths were enumerated, the total path count, each control's share of paths closed, and the residual open paths
9. Verification status and residual risk
10. Open questions, where inputs are missing

## References
See `references/README.md` for detailed capabilities, behavioral traits, and knowledge areas. The confidence scale and its mode-bound gate, the exclusion ledger with its carve-backs, the standing precedents, the anti-anchoring verification protocol, the quote-the-line gate, and the filter-stat and fingerprint reporting are in `references/finding-triage.md`. Attack-path enumeration, choke-point counting, and the aggregation convention behind step 5's coverage ranking are in `references/attack-path-analysis.md`. The coordinated-disclosure engagement mode and its three reportability filters are in `references/finding-triage.md`, with the submission gate, the classes that carry impact, and the report structure in `references/devsecops-and-testing.md`. The payment-card rules — the never-retained set, the PAN masking cap, and scope reduction through tokenization — are in `references/compliance-checklist.md`.

## Examples

**Worked case — a control sitting on the wrong side of the boundary**

An ingest pipeline ran a secret scanner over every source file before writing those files into a store on the same disk, spawning one scanner process per file; that scan dominated the run's wall-clock time. The audit drew the boundary and found the scan entirely inside it: the plaintext secret already sat on that disk, so scanning a file on its way to a local store could not change exposure. The control that actually gates exfiltration was the scan at the sync step, where content leaves the machine — documented and confirmed independently before anything was touched. Remediation was to make the per-file scan opt-in and default it off, not to delete it: the cost disappeared, the machinery stayed available for a future assessment, and exposure was unchanged. Report the improvement as scoped to the phase that was fixed; an unrelated bottleneck elsewhere in the same pipeline was untouched by it, and quoting an end-to-end speedup would have claimed a result the change did not produce.

## Example Output

1. Scope & Constraints: Production tests excluded; staging-only validation.
2. Threat Model Highlights & Control-to-Boundary Map: Token theft, privilege escalation, data exfiltration. Egress gated at the API gateway; the per-request payload scan in the internal worker gates nothing crossing a boundary — flagged for demotion to opt-in.
3. Findings (table):
   - SA-01 | High | `auth/token.py:114` — `TOKEN_TTL = None` with no rotation path | Account takeover | Implement rotation
   - SA-02 | Medium | `auth/scopes.py:27` — client granted `admin:*` | Data exposure | Scope minimization
4. Filter Stats & Suppressed Candidates: 41 candidates → 33 discarded by rule → 6 discarded on verification → 2 reported. Appendix: SA-A1 (no line quotable for the claimed missing field), SA-A2 (dependency CVE, vulnerable function not called).
5. Remediation Plan: Address SA-01 short-term, SA-02 medium-term. Path coverage for the account-takeover tree (3 paths enumerated): token rotation closes 3 of 3, scope minimization closes 1 of 3; residual open paths after both, 0 within the enumerated tree.
6. Verification & Residual Risk: SA-01 pending validation; SA-02 not started.
7. Open Questions: Confirm token TTL requirements.
