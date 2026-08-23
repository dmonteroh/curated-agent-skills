# When the real operation cannot be run

Read this when the requirement for observed runtime values collides with an operation that cannot be executed: a paid call with no quota, hardware that is absent, a network path that is blocked, a credential that exists only in production, a dataset that cannot be copied.

Partial runtime evidence is still runtime evidence. This page says which partial signals to harvest, and how many of them a conclusion needs before it may be stated without a caveat.

## When it applies

All three must hold:

1. The question genuinely requires runtime confirmation rather than code reading.
2. The direct attempt failed for a reason unrelated to the bug — quota, access, hardware, isolation.
3. Mocking the whole system would defeat the point, because what is needed is evidence about how the *real* code behaves.

If the third does not hold, mock cleanly and proceed. This page is for the case where a mock would invalidate the answer.

## Evidence tiers

Ordered by how much inference sits between the signal and the fact. Higher tiers are closer to ground truth; lower tiers carry more reasoning.

| Tier | Signal | What it gives, and what it misses |
| --- | --- | --- |
| 1 | Logs emitted around the operation — the assembled request before it is sent, the parsed response after it returns | The system's own view of what it built or received. Misses whatever the transport layer adds or transforms below that point. |
| 2 | Local interception: run the real code against a local proxy or a shim that records what crosses the boundary | What actually crossed the wire. Requires the target to honor the interception path. |
| 3 | Static reading cross-checked against a runtime fingerprint the system emits without the blocked operation — a written state file, a version or capability listing, a cache it maintains | Two disjoint sources agreeing on the same fact. |
| 4 | Contrastive runs: execute a variant that *is* permitted and reason about the blocked one across the code path they share | Confirms the shared path. The remaining gap is exactly the difference between the two variants. |
| 5 | Records kept on the far side — audit logs or dashboards from the service that received the call | Real observed behavior, usually summarized: statuses and counts, rarely payloads. |
| 6 | Careful code reading with a skeptical second opinion | The weakest tier. Conclusions from it are marked unverified. |

## Combining signals

A defensible conclusion prefers **two independent signals from different tiers**. Independence is the actual requirement: two readings of the same log are one signal, and two tiers that both derive from the same emitting code path are closer to one than to two.

| Available evidence | Defensibility |
| --- | --- |
| Two readings from the same source | Weak — a single signal counted twice |
| Tier 1 with tier 2 | Strong — independent confirmation |
| Tier 1 with tier 3 | Strong — disjoint sources |
| Tier 2 alone, a complete capture | Strong **for claims about what was sent**, which is what the capture directly shows. Claims about what the system then did with the response need a second signal |
| Tier 3 with tier 4 | Medium — both partial |
| Tier 6 alone | Insufficient — escalate, or state the conclusion as unverified |

Record the assessment in the journal: the specific claim, each signal with its tier and source, an explicit statement of why the signals are independent, and the resulting verdict.

## Labelling the deliverable

If neither a complete tier-2 capture nor two independent non-tier-6 signals could be obtained, the conclusion still ships — but it ships labelled, in the deliverable itself rather than only in the journal:

> Partial-evidence finding. The full observation could not be captured because *(reason)*. The conclusion rests on *(signal A, tier and source)* and *(signal B, tier and source)*. A later verification should attempt *(the missing tier)* once *(condition)*.

## Anti-patterns

| Anti-pattern | Why it fails | Replacement |
| --- | --- | --- |
| "It reads correctly, so it works" | Tier 6 alone, unverified | Add at least one signal from tiers 1 to 3 |
| "It ran once without erroring, so it is correct" | Absence of an error is not presence of the right result | Capture the actual output and check its content |
| "The mock returned the expected value, so the code is fine" | The mock returns the assumption being tested | Intercept the real path, or cross-check against a fingerprint |
| "The far-side dashboard shows the call succeeded" | Usually a status code, not behavior | Combine with a tier-1 signal |
| "A published answer says this is how the library behaves" | Written against a different version or context | Verify against the artifact actually installed |

Every artifact created for partial-evidence work — proxies, shims, trace files, exported overrides — is journalled before creation and reverted in the scrub, exactly like any other debug artifact.
