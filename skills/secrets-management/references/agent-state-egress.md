# Egress control for agent-generated state

Detail behind workflow step 6. Applies to any local tool or agent that syncs its own generated state off the machine it runs on — a threat model distinct from CI/CD secret retrieval, because the data leaving is not a secret store but a working directory that may have accumulated one. The allowlist, exclusion, and scan sections below are specific to that sync case; the receipt sections apply to every channel that carries a payload off the machine, an outbound call to a third-party API included.

## What the allowlist covers

The allowlist names permitted content, and the default for everything else is "stays local". Two properties matter more than its contents:

- **New file types default to local.** A tool that gains a feature next quarter will write files nobody enumerated. Under a denylist those ship; under an allowlist they wait for a deliberate entry.
- **It is inspectable and extendable without reading code.** A plain text file, managed by the tool above a marker line, appendable by the user below it. A hardcoded list cannot be audited by the person whose machine it governs; an opaque one cannot be corrected by them either.

## Structural exclusions

These categories stay local regardless of what any scan concludes. They are excluded because of what they are, not because of what a scan found in them:

| Category | Examples | Why it is structural |
| --- | --- | --- |
| Credential material | key files, token caches, session stores, service-account JSON | Value is the secret itself; a scan miss is unrecoverable |
| Machine-bound state | browser profiles, model weights, build and package caches, one-time local markers | Meaningless or harmful off the originating machine; large; often carries embedded tokens |
| Per-machine preferences and logs | UX settings, command history, local telemetry, debug logs | Behavioral record of a person, not shared project knowledge |

Scanning runs behind these exclusions. Ordering matters: a scan that is asked to protect a category which should never have been eligible will eventually be the only thing standing between that category and the network.

## Credential-shaped content scan

Scan the outbound batch, not the working tree, and match a named pattern family rather than a generic secret heuristic:

- Cloud provider access-key identifiers (fixed-prefix, fixed-length key ids)
- Forge and platform tokens, including every prefix variant a provider issues — personal, OAuth, user-to-server, server-to-server, refresh, and fine-grained variants are separate prefixes and are commonly missed one at a time
- Vendor API-key prefixes for the model, payment, and messaging providers the tool actually talks to
- PEM private-key blocks (`-----BEGIN … PRIVATE KEY-----`)
- JWTs (three base64url segments, conventionally recognizable by the encoded header prefix)
- Bearer tokens and `api_key`-style fields inside JSON request or response bodies captured in logs and transcripts

**Time-sensitive.** Provider prefixes and token formats change, and providers add variants without retiring old ones. Treat the concrete prefix list as maintained configuration with an owner and a review date, verified against each provider's current token-format documentation — not as a constant compiled into the tool.

## Blocked batch: stop, preserve, remediate

On a hit the batch stops and the queue is preserved. Nothing is dropped, and the pending items retry once the block clears.

After reviewing the flagged file, exactly two remediations exist:

1. **Permanently exclude the path** when the match is a false positive on content genuinely intended to sync — a fixture, a documented example key, a redacted transcript.
2. **Remove the secret from the file** and re-run.

Discarding the queue is not among them. A tool that offers "drop it and move on" as an equal third choice makes silent data loss the fastest way past a security stop, which is exactly the path a hurried user takes.

## Second, independent gate

Run the identical scan from a second place that a bypass of the primary tool still passes through — a pre-commit hook on the synced repository is the usual one, catching a manual commit made without the tool. Two gates running the same pattern family is the point: divergent gates give the illusion of depth while each covering a different half.

## Egress receipts

Before anything is transmitted, write a receipt to an append-only, hash-chained ledger. The audit trail is a precondition for egress, not a log written after the fact: a receipt written after transmission cannot record a send that crashed mid-flight, which is the case that most needs a record. The whole point of the ordering is that an aborted, timed-out, or crashed call still registers as attempted egress — a log that only records completed calls is blind to precisely the events an incident review opens the ledger to find.

The ordering is testable rather than assertable. Stub the transport, count the ledger's entries from inside the stub, and require the count to already include this call before the transport body runs. A check that inspects the ledger after a successful call passes just as happily against an implementation that writes the receipt on the response path, and so proves nothing.

Two operations make the ledger worth keeping: `list`, to see what left and when, and `verify`, to check the hash chain and detect tampering or truncation. A ledger without a verify operation is an append-only file that anyone can rewrite.

Make it a shared service. Any channel that moves data off the machine — a state sync, a remote-access tunnel, an upload, a crash report, a call to a metered third-party API — writes to the same ledger through the same call. The same mechanism appearing in two unrelated features of one product is what shows this is a primitive rather than one feature's design choice, and a receipt facility wired into only the first feature will simply be skipped by the second.

### What a receipt records

Four fields carry the contract, and all four are computable before the send: a hash of the payload, its byte count, the destination, and a label for the class of thing being sent (`model-completion-request`, `state-sync-batch`). The payload is never among them, and neither is an excerpt, a truncation, or a preview of it. A receipt that stores content turns the audit trail into a second copy of whatever was sensitive enough to audit, so assert its absence directly rather than trusting the code path: write a receipt for a payload containing a known string, then require that string to appear nowhere in the ledger file.

Two extensions earn their place where the channel warrants them: the chain-linkage field that makes the ledger tamper-evident, and a record of what authorized the send — the user action or configuration that made this call legitimate. Together with the four core fields they are what let a reader answer, months later: what left, how much of it, where it went, on whose action, and has the record been altered.

### Do not consume the payload to instrument it

Some bodies can only be read once. Where the payload is a stream or another single-pass source, record the hash as explicitly absent and pass the source through untouched instead of draining it to hash it — a wrapper that exhausts the body before the real send reads it has broken the feature it was added to observe. The same restraint applies on the way back: the receipt is written before the send and the wrapper's job ends there, so the response is returned unbuffered and uninspected, streaming responses included.

An absent hash still makes a valid receipt, not a failed one. The byte count may be unknown alongside it, but the destination, the class label, the timestamp, and the fact of an attempt are all recorded, and those are what make the entry worth having.

### The receipt is not a content control

The scan above and the receipt are two controls on one path, and neither substitutes for the other. The scan is the active layer: it inspects content and can refuse a specific batch. The receipt is the passive layer: it records that something was attempted, without knowing or storing what. A path with only a scan stops bad sends and remembers nothing; a path with only receipts remembers every attempt faithfully and stops none of them.

### Choosing the failure polarity

What happens when the receipt itself cannot be written is the one real branch in this control, and it is decided per channel, not once per product.

**This rule is authored for this skill, not drawn from a source.** It was reasoned by contrasting two implementations that chose opposite polarities and justified only their own case, neither stating a general principle. Treat it as a starting heuristic to check against further examples rather than as an established rule, and where a channel sits ambiguously between the two columns, fail closed and record that the call was ambiguous — that failure is visible, and the other one is not.

| | Fail open | Fail closed |
| --- | --- | --- |
| Trigger | A single call the user just initiated and is waiting on | An automatic push on a schedule or a lifecycle boundary, with no per-instance user action |
| Cost of blocking | The user's foreground task dies for a reason they did not cause, cannot see, and did not ask about | A deferred retry: the queue is preserved and nothing user-facing breaks |
| What the receipt is for | Observability and cost attribution layered on an already-consented, already-configured call | A primary security control on a channel nobody watches per instance, paired with an active content scan and expected to be tamper-evident |
| Payload scope | One call of one known kind | A recurring batch drawn from whatever the tool has accumulated |

In short: fail open protects the user's foreground task from an unrelated logging failure; fail closed protects the audit trail from being silently defeated on a channel nobody is watching. Fail-closed is affordable exactly where blocking costs a deferred retry rather than a visible failure — which is why the same rule does not extend to the interactive case.

Neither polarity permits a silent failure. Fail-closed refuses the send, preserves the queue, and reports the refusal; the stall surfaces through whatever status command the channel already has. Fail-open completes the send but must warn in terms that name the receipt write as the thing that failed, state that the send proceeded anyway, and point at how to inspect or verify the trail. Without that warning, "warn and proceed" degrades into "the audit system stopped working and nobody was told" — worse than having no ledger, because a ledger people believe in is read after an incident and its gaps are read as absence of egress.

## First run and uninstall

Ask about sync scope once, persist the answer, and never re-prompt on every invocation. Provide an uninstall that removes the sync machinery while leaving the underlying data in place — an off-ramp that deletes the user's notes to remove the syncing of them is not an off-ramp.
