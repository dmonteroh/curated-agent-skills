---
name: secrets-management
description: "Secure secrets handling for CI/CD, runtime, and local agent tooling: secret inventory, access boundaries, short-lived identity (OIDC/workload identity), rotation, leak response, egress control and audit receipts for data leaving a developer machine, and ambient-credential disambiguation. Works across Vault and cloud-native secret managers."
metadata:
  category: security
---
# Secrets Management

Provides guidance to prevent secret leakage and make access auditable and maintainable.

## Use this skill when

- Handling credentials, signing keys, API keys, TLS material, or connection strings
- Designing secret retrieval for CI/CD or runtime workloads
- Implementing rotation, auditing, and leak response
- Controlling what agent- or tool-generated state is allowed to leave a developer machine
- Recording what a tool or agent sends to a metered, billed, or sensitive third-party API, for cost attribution or incident forensics
- Designing how a locally invoked tool resolves, discloses, and stores a credential

## Do not use this skill when

- You only need local dev values that will never be shared and nothing on that machine syncs outward (use `.env` locally, never commit)
- You cannot secure access to any secrets backend

## Required inputs

- Target environments and workloads (CI/CD, runtime, or both)
- Current secret locations and owners (source control, env vars, secret managers)
- Access constraints (identity provider, IAM policies, compliance requirements)
- Rotation expectations and incident response requirements
- For local tooling: what state the tool generates and syncs outward, which outbound calls carry payloads to third parties, where both go, and which credential sources it is allowed to read

## Constraints

- Never request or output real secret values; use placeholders when needed
- Avoid guidance that depends on external network access or time-sensitive data

## Workflow

0) Confirm required inputs
- If any required input is missing, request it before proceeding.
- Output: list of missing inputs or a confirmation to proceed.

1) Inventory secrets
- List secret types, owners, environments, and rotation requirements.
- Identify where secrets are currently stored and where they can leak (logs, artifacts, env dumps).
- Output: inventory table with owner, location, and rotation target.

2) Choose access model (prefer short-lived)
- Prefer OIDC/workload identity over long-lived static credentials.
- Enforce least privilege and environment separation.
- If OIDC/workload identity is available, use short-lived tokens scoped to each workload.
- If only static credentials are possible, require scoped secrets, explicit expiration, and rapid rotation.
- Output: access model decision and required identity claims/scopes.

3) Choose backend (don’t overfit)
- Vault when you need centralized policy + dynamic secrets.
- Cloud secret managers when you want managed storage + IAM integration.
- If you need database credentials or just-in-time secrets, favor Vault.
- If you need simple storage with cloud IAM and KMS, favor cloud secret managers.
- Output: backend selection with rationale and constraints.

4) Integrate safely
- Fetch secrets at runtime or job runtime (not baked into images).
- Mask secrets in logs; avoid printing env.
- Add auditing and usage visibility.
- For CI/CD: use ephemeral tokens, short-lived runners, and masked variables.
- For runtime: use sidecars/agents or direct SDK calls with minimal scopes.
- Output: integration plan with retrieval flow, masking, and audit signals.

5) Rotation + incident response
- Rotation plan: cadence, automation, blast radius.
- Leak response: revoke/rotate, search logs/artifacts, postmortem follow-ups.
- If a leak is confirmed, revoke immediately, rotate dependent services, and document exposure window.
- Output: rotation runbook and leak-response checklist.

6) Gate and record what leaves the machine
- Applies when a local tool or agent sends data off the machine it runs on: a sync of its own generated state — notes, plans, transcripts, learnings, caches — to a remote store, or any call carrying a payload to a third-party API. The allowlist and scan bullets govern the sync case; the receipt bullets govern both. Skip this step when nothing leaves the machine.
- Allowlist, never denylist. Define explicitly what is permitted to leave; everything else stays local by default, including file types introduced after the list was written. A denylist ships every new unknown artifact by default, and the set of unknowns only grows.
- Exclude whole categories structurally, independent of any scan result: credential files, machine-bound state (browser profiles, model weights, caches, one-time local markers), and per-machine preferences, history, and logs. Content scanning is a second line behind these exclusions, never the boundary itself.
- Keep the allowlist as a plain text file the tool manages, with a marker line below which the user may append their own entries — readable without running the tool, extendable without editing its internals.
- Scan every outbound batch for credential-shaped content before it leaves, against a named pattern family rather than a generic "look for secrets": cloud access-key identifiers, forge and platform tokens across their prefix variants, vendor API-key prefixes, PEM private-key blocks, JWTs, and bearer or api-key fields inside JSON bodies. Pattern list and its refresh rule: `references/agent-state-egress.md`.
- On a hit, stop the batch and preserve the queue — pending items are not dropped, and they retry once the block is cleared. After reviewing the flagged file, exactly two remediations follow: permanently exclude that path when the match is a false positive on content genuinely meant to sync, or remove the secret from the file and re-run. Discarding the queue is not a third option; silent data loss is not a remediation.
- Run the identical scan from a second, independent gate so a path that bypasses the primary tool is still covered — for example a pre-commit hook on the synced repository, which catches a manual commit made without the tool.
- Write the receipt before anything is transmitted, never after. An entry written on the response path cannot record a send that timed out, aborted, or crashed mid-flight, which is the case an incident review most needs; writing it first makes an attempted egress visible whether or not the call ever completed.
- Record a hash of the payload, its byte count, the destination, and a label for the class of thing being sent — and no payload content, in any field. Compute those fields without consuming the body: where the payload is a stream or another single-pass source, record the hash as absent rather than draining it to hash it. A receipt carrying content is a second copy of whatever was sensitive enough to audit.
- Keep the ledger append-only and hash-chained, provide `list` and `verify` operations over the chain, and make it a shared service every outbound channel writes to. A sync push, an upload, a remote-access tunnel, and a call to a third-party API are one event class; a receipt mechanism wired into only one feature is bypassed by the next one.
- Choose the receipt-write's failure polarity per channel, and make the failure loud either way. Fail closed on an automatic background channel such as this step's sync: refuse to send, preserve the queue, report the refusal. Fail open only on a call the user initiated and is waiting on, where the receipt is observability layered over an already-consented action — proceed, and warn in terms that name the receipt write as what failed, say the send went ahead regardless, and point at how to inspect the trail. This polarity rule is reasoned rather than sourced; its derivation and limits are in `references/agent-state-egress.md`.
- Ask about sync scope once, persist the answer, and provide an uninstall that removes the sync machinery without touching the underlying data.
- Output: allowlist file path and contents, structurally excluded categories, scan pattern family, the second gate's location, the ledger path with its verify command, and the failure polarity chosen for each outbound channel.

7) Disambiguate ambient credentials in locally invoked tools
- Applies when a tool can be invoked from any directory and can read a credential from the environment.
- Resolve in a fixed, documented order: the tool's own config file first, then a generic environment variable, then none (the caller handles setup). A dedicated config file is a deliberate grant to this tool; an inherited environment variable is a weaker signal of intent and may belong to whatever project the shell was last used in.
- When falling back to the environment variable, compare its value against the values defined in the working directory's dotenv files — `.env`, an environment-suffixed variant such as `.env.<environment>`, then `.env.local` — in that order, first match wins.
- Compare values, not variable names. A local file defining the same name with a different value is not a collision and must not warn; a check that fires on unrelated projects trains users to ignore it.
- Parse those files tolerantly before comparing: strip an optional leading `export`, trim whitespace, and unwrap single or double quotes around the value.
- On a match, warn and proceed — do not block. Name the file that matched and the concrete consequence (this run may bill or mutate that project's account), because only the user can say whether that was the intended credential.
- Disclose the source of a credential, never its value. Every path that reports where a key came from prints a file path, a config label, or the variable name plus the dotenv file it matched, and no path prints the key. Verify with a test asserting the message contains the source label and does not contain the value.
- Create any credential file the tool persists with owner-only permissions at creation time, rather than writing under the ambient umask and tightening afterward. The chmod-after-write window leaves the file briefly group- or world-readable (CWE-377, CWE-367); a test that sets a permissive umask, saves a key, and asserts the resulting mode fails against the tighten-afterward implementation.
- Output: documented resolution order, the disambiguation warning text, and the permission mode applied at file creation. Detail and worked cases: `references/ambient-credential-resolution.md`.

## Common pitfalls

- Reusing the same secret across environments or teams

## Examples

**Example request**
"We need to move GitHub Actions secrets to OIDC and choose a backend."

**Example response (condensed)**
- Secret inventory: GitHub deploy key (prod), DB password (staging/prod)
- Access model: OIDC with repository + environment claims
- Backend: cloud secret manager (managed storage + IAM)
- Integration: job-level token exchange, masked outputs, audit logs enabled
- Rotation: policy-based cadence, automated rotation + alerting

**Example — ambient credential disclosure, wrong beside right**

- Wrong: `Using API key sk-live-1a2b3c4d… from the environment.` The value is printed, and the message still does not say why this key was the one selected.
- Right: `Using API key from $SERVICE_API_KEY, whose value matches ./.env in this directory. This run may bill that project's account.` The source and the consequence are named; nothing about the key is disclosed.

## Output contract

- Secret inventory (what/where/owner/rotation)
- Recommended backend + access model with rationale
- Integration plan (CI/CD and/or runtime) with least-privilege boundaries
- Egress policy where data leaves the machine: allowlist, structural exclusions, scan family, receipt ledger, per-channel failure polarity
- Rotation + incident response plan
- Verification steps (how to prove masking, rotation, access policies, the receipt's pre-send ordering and chosen failure polarity, and source-only disclosure work)

## Resources

- References index: `references/README.md`
- Implementation playbook (patterns + examples): `resources/implementation-playbook.md`
- Vault setup notes: `references/vault-setup.md`
- GitHub secrets hygiene: `references/github-secrets.md`
- Egress control and audit receipts for data leaving the machine: `references/agent-state-egress.md`
- Ambient credential resolution on a developer machine: `references/ambient-credential-resolution.md`
