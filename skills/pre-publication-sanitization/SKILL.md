---
name: pre-publication-sanitization
description: "Sanitization gate for taking a private repository public: six scan categories across the working tree and the full history, internal specifics replaced by documented placeholders rather than deleted, and a blocking gate held until each finding is resolved or overridden on the record. Use before a first public push or a visibility change."
metadata:
  category: security
---
# Pre-publication sanitization

Publication is a one-way door. The moment a repository is reachable it can be cloned, forked, mirrored, indexed, and archived by parties who owe nothing to whoever published it, and nothing published can be unpublished: an exposed credential can only be rotated, an exposed internal name only apologised for. Every check here therefore runs *before* the push, and the gate blocks rather than warns — a warning is a control that costs nothing to ignore at the exact moment ignoring it is irreversible.

## Use this skill when

- A private repository is about to become public — a first push to a public remote, a visibility change, or a public mirror or fork of private work
- Private work is being extracted for public release: a sample project, an SDK carve-out, a demo, or code attached to a paper, talk, or post
- An already-public repository is about to receive its first push of code that was developed privately
- Reviewing someone else's proposed open-sourcing before approving it
- Deciding whether a specific finding blocks a release or can be accepted, and on whose authority

## Do not use this skill when

- The repository is already public. The gate has nothing left to guard and running it produces false comfort: a finding there is a live exposure, not a blocker, and it takes the incident path in step 5 rather than a decision about whether to publish.
- The move keeps the audience inside the same trust boundary — a private-to-private transfer, or a visibility change within one organization. The categories still apply if the boundary is genuinely crossed; the gate is for the crossing, not for the move.
- The task is producing public-repository boilerplate: readme, license, contribution guide, issue templates. That is packaging, it gates nothing, and treating it as part of this pass dilutes the pass.
- The question is ongoing credential lifecycle — where secrets live, how often they rotate, which backend holds them — rather than one boundary crossing.
- No one with authority over the consequences is available to accept residual risk. The sweep can run; the publication waits.

## Required inputs

- The publication boundary: which repository, which refs travel (branches and tags), and whether history travels or only a snapshot
- The owner who carries the consequence of a leak and can record an override
- What counts as internal here: hostname and domain suffixes, service and project codenames, ticket-ID shapes, customer names, employee identifiers
- Which credentials this code has ever used, and who can rotate each one
- The configuration surface the published artifact must keep working: which values a reader has to supply

## Workflow

0) Fix the boundary before touching content
- Enumerate exactly what becomes public: every ref that travels, tags included, and whether prior commits travel with them.
- Decision: if history travels, category 6 is blocking. If publication is a fresh snapshot with no prior commits, record that as the reason category 6 is not applicable — do not infer it from a repository that merely looks new.
- Output: one written statement of what becomes public, which the rest of the pass is scoped against.

1) Strip by parameterizing, not by deleting
- Replace each internal specific with a value the published artifact reads at run time: a config key, an environment variable, a documented input.
- Record every removed value in an example configuration file carrying its name, a well-formed but obviously fake sample, and one line on what it is for.
- Deleting instead of parameterizing produces an artifact that no longer runs and hides from the reviewer what was taken out — the reviewer cannot audit an absence.
- Decision: if a value cannot be parameterized because the functionality around it is itself internal, remove the functionality and name the removal in the record. Do not ship a stub that silently does nothing.
- Output: placeholder inventory — removed value class, placeholder name, where it is read, its example entry.

2) Run the sweep as a pass separate from the stripping
- The sweep reads the repository as an outsider receives it, not as the stripper left it: it does not consult the strip log and re-derives its own findings. Whoever stripped checks for what they thought to remove, which is precisely the set that is already gone.
- Run all six categories every time, over the working tree and over history as the boundary requires.
- After any fix, re-run the whole sweep rather than the failing category. Fixes move values: into a fixture, a lockfile, a snapshot test, or a fresh commit that is now itself part of history.
- Output: per-category findings, each with file and location, the class of value, and a blocking or non-blocking label.

3) Hold the gate
- Publication does not proceed while a blocking finding is unresolved. This is a stop, not a score.
- A blocking finding leaves the gate two ways: resolved, or overridden on the record. An override that is not written down is not an override — it is an unrecorded decision no one can find afterwards, on the one action that cannot be undone.
- An override entry names the finding, the exposure being accepted, why it is acceptable, and the person accepting it. Findings under a non-blocking category are listed in the record and do not stop the push.
- Decision: if a blocking finding is a credential that was ever committed, rotation is part of resolving it, not a follow-up. Removing the value from the tree does not un-expose a value that already lived in a shared history, a backup, or a colleague's clone.
- Bound the loop. Fix, then re-sweep, but after a small fixed number of consecutive blocked sweeps, stop iterating and hand every finding to a person. The source procedure fixed that bound at three attempts, a chosen constant with no derivation given; the rule is the bound, not the number.
- Output: gate verdict — blocked, cleared, or cleared with recorded overrides — plus the override entries.

4) Publish only on an explicit go
- Present the record and obtain an explicit decision to publish from the owner. Never publish as a side effect of the sweep clearing: a cleared gate is permission to ask, not permission to push.
- Output: the approval, recorded alongside the verdict it authorizes.

5) Treat any later finding as an incident, not as cleanup
- Rotate and revoke exposed credentials first, notify the owners of exposed personal data or third-party names, and only then consider rewriting or deleting.
- Rewriting history after publication does nothing for the exposure window and does not recall what was already fetched. Ordering matters because rotation is the only step that actually ends the exposure.
- Output: incident record with rotation status per credential, notification status, and the exposure window.

## Scan categories

Six categories, run as a set. The severity column is the source procedure's; the membership of each category is expanded in `references/sweep-categories.md`.

| # | Category | Severity | Covers |
| --- | --- | --- | --- |
| 1 | Credentials | Blocking | API keys and tokens, passwords, private keys and certificates, connection strings, signed URLs, session material in fixtures |
| 2 | Personal data | Blocking | Names, addresses, contact details and identifiers in code, seed data, fixtures, screenshots, and commit metadata |
| 3 | Internal references | Blocking | Internal hostnames and URLs, service and project codenames, ticket identifiers, employee and team names, customer names, internal document links, organization-specific paths |
| 4 | Unintended files | Blocking | Key material, environment and credential files, database dumps, backups, archives, build outputs, editor and OS metadata, notebook outputs carrying data |
| 5 | Configuration completeness | Non-blocking | Whether the artifact still runs on placeholders alone: example config present, every stripped value documented, no dangling reference to a removed internal service |
| 6 | History | Blocking where history travels | Every commit reachable from every published ref: deleted files, superseded values, commit messages, author identities, tags |

Categories 3 and 6 are the two the source procedure singles out as most often missed, for different reasons. An internal reference is not a secret, so no credential scanner matches it, and it leaks the organization rather than an account. History is the irreversible one: sanitizing the working tree leaves every earlier value intact in the commits, and the commits are what a clone takes.

## What a cleared gate does and does not mean

It means no configured pattern matched the surfaces that were actually scanned, by the people or tools that scanned them. It is a floor, not a proof, and no coverage or detection rate is claimed here — the source procedure claimed none either, and none of these categories has a measured hit rate to cite. The blind spots below are reasoned rather than sourced, and they are stated because a sweep that implies completeness it cannot deliver is worse than one that states its limits:

- Encoded and compiled content: base64 blobs, minified bundles, binary assets, embedded metadata in images and documents, compiled artifacts
- Values with no distinguishing shape: a password that reads as a word, an internal hostname that reads as a product name
- Leaks that are not strings: a diagram, a roadmap in a comment, a test that encodes an unreleased customer's behaviour
- Surfaces outside the scan: submodules, vendored dependencies pulled from internal registries, platform-held configuration that is not in the repository, release assets
- Pattern decay: a category is only as good as its current pattern list, and credential formats keep being added

Report per category what was scanned and what was not, so a reader can see where the claim stops.

## Constraints

- Never copy a real value into a finding, a record, an override entry, or a commit message. Name the file, the location, and the class of value.
- Placeholders are well-formed but unmistakably fake, so nothing shipped can be mistaken for a live value or tried against a live system.
- Findings, records, and override entries are written where they survive the publication and stay findable by someone who was not in the room, not left in a chat thread or a terminal scrollback.

## Common pitfalls

- Reading one tool's empty output as the verdict for a whole category

## Examples

**Parameterize, don't delete — wrong beside right**

- Wrong: delete the block that reads the internal endpoint. The project builds, the feature silently does nothing, and the reviewer cannot tell what was removed or whether anything else depended on it.
- Right: read the endpoint from a documented setting, ship an example configuration entry with a fake value, and list it in the placeholder inventory. The published project runs against the reader's own endpoint.

```
# example configuration entry
SERVICE_BASE_URL=https://api.example.invalid   # base URL of the backing service
SERVICE_API_KEY=replace-me                     # issued per deployment; never commit a real key
```

**Resolving a credential finding — wrong beside right**

- Wrong: remove the key from the file, commit, re-sweep, publish. The value is still valid and still sits in every earlier commit that travels.
- Right: rotate the key at its issuer, confirm the old value is dead, then remove it from the tree and from history if history travels, then re-sweep. The published copy cannot be recalled, so the durable fix is that the value no longer works.

**Override entry for a blocking finding**

```
FINDING  H-03 | category 6 (history) | blocking
         Author identities across the published history use an internal mail domain.
OVERRIDE accepted by <name, role> on <date>
         Exposure accepted: the domain is already public in package metadata.
         Rejected alternative: rewriting every commit, which invalidates the signed tags.
         Scope: this finding only. No credential or personal-data finding is covered.
```

## Output contract

The record handed to whoever authorizes the push contains:

- What becomes public: repository, refs, and whether history travels
- Per category: the surface scanned, the surface not scanned, and each finding as file, location, and class of value — never the value itself
- Unresolved blocking findings: none, or one override entry each
- Placeholder inventory: every removed value, its placeholder, where it is read, its example entry
- Rotation status per credential finding, tracked separately from removal status
- Verdict — blocked, cleared, or cleared with recorded overrides — and, when the push proceeds, the explicit approval that authorized it

## References

- `references/README.md` — index
- `references/sweep-categories.md` — what each of the six categories covers, where each hides, and what each misses
- `references/history-and-remediation.md` — the history surface in depth, and the rotate-before-rewrite remediation order
