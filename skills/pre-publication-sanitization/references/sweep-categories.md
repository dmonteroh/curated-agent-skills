# The six scan categories

Expansion of the category table in `SKILL.md`. The categories and their severities come from the rescued source procedure; the membership, hiding places, and limits below are authored — reasoned from how these leaks are found, not carried from a verified source. Treat them as a starting pattern list to extend per organization, never as a complete one.

Run order that shrinks work: category 4 first, because removing a whole file removes its contents from every other category's surface; then 1–3 over what remains; then 5; then 6 once the tree has stopped changing.

Every category result states three things: the surface it scanned, the surface it did not, and each finding as file, location, and class of value. A category with no findings and no stated surface is not a result.

## 1. Credentials — blocking

Covers API keys and tokens, passwords, private keys and certificate material, connection strings with embedded credentials, pre-signed URLs, webhook signing secrets, and session or cookie material captured in fixtures.

Hiding places that are not the obvious config file:

- Recorded HTTP fixtures and cassettes captured against a live system, which keep the authorization header
- Notebook output cells, which persist whatever the cell printed
- Minified or bundled frontend assets and mobile resource files with a key compiled in
- Infrastructure state files and generated manifests
- Quickstart snippets in documentation, pasted with a working value so the example ran
- Comments explaining a value that was later moved but not removed
- Dependency lockfiles and package manifests pointing at an authenticated registry with inline credentials
- Test setup files and sample scripts, where a real value is often used because the test needed to pass

Misses: values with no distinguishing prefix or shape; credentials assembled at run time from parts; encrypted blobs published alongside the key that opens them.

Resolution is rotation first, removal second — a value removed from the tree but never rotated is still a live credential in every copy that already exists.

## 2. Personal data — blocking

Covers names, contact details, addresses, government or account identifiers, photographs, device and network identifiers, and free-text content authored by users.

Hiding places:

- Seed, demo, and fixture data copied from a production system rather than generated
- Database dumps and sample exports committed for convenience
- Screenshots, recordings, and documentation images
- Analytics or event schemas carrying example payloads taken from real traffic
- Captured exception traces and log samples
- Commit metadata: author and committer identities, trailers, and any identity map committed to the tree

Misses: pseudonymous identifiers that re-identify when joined with something public; data that is personal only in context, such as a fixture whose row count reveals a named customer's size.

Two different questions live in this category and are decided separately: contributor identity, which publication normally exposes by design, and user data, which it never should.

## 3. Internal references — blocking

Covers internal hostnames, domains, and dashboard URLs; service, project, and release codenames; ticket and incident identifiers; team, employee, and manager names; customer and partner names; organization-specific directory layouts; internal package registries and mirrors; internal address ranges; account, tenant, and cost-centre identifiers.

This category exists separately because none of it is a secret, so no credential scanner matches it, and the loss is organizational rather than account-level: an unreleased product name, a customer list inferable from fixture names, an internal topology reconstructed from hostnames in test configuration, a delivery timeline reconstructed from ticket identifiers in commit messages.

Hiding places: comments and TODO markers, changelog entries, decision records, test hostnames, job and pipeline names, dependency manifests pointing at an internal mirror, sample environment files, error and log message text, generated documentation, default configuration values, links and badges in the readme, ownership and reviewer files, and runbook links.

Misses: internal knowledge carried structurally rather than as a string — a directory layout that mirrors an internal org chart, a module split that discloses an unannounced product boundary.

Three different resolutions apply, and choosing the wrong one is how functionality is lost: parameterize what is real and still needed, rename what is incidental, delete what is purely an artifact of internal process such as a ticket identifier.

## 4. Unintended files — blocking

Covers key and certificate material, environment and credential files, local tool and credential caches, database dumps and backups, archives, build outputs, coverage and profiling artifacts, editor and operating-system metadata, vendored downloads, notebooks with retained outputs, and large binaries carrying embedded metadata.

Decide membership by allowlist, not denylist: enumerate the file categories that belong in the published artifact and treat everything else as excluded until reviewed. A denylist publishes every artifact type invented after the list was written.

Misses: files that legitimately belong but carry embedded metadata — document properties, image capture metadata, producer strings, and revision history inside office documents.

## 5. Configuration completeness — non-blocking

Covers whether the published artifact still works for a stranger holding none of the removed values: an example configuration listing every stripped value, documentation of how to obtain each one, and no code path that references a removed internal service without failing clearly.

Falsifiable check: from a clean copy carrying only the example configuration, the documented first step either succeeds or fails with a message naming the missing setting. Failure looks like a stack trace against an unreachable internal host, or a silent success that does nothing.

This is the one category whose failure is repairable after publication, which is exactly why it does not block: a broken published artifact is embarrassing, a published credential is not recoverable. Keep the severity split for that reason and no other.

## 6. History — blocking where history travels

Covered in `references/history-and-remediation.md`, because the surface is unlike the other five: it is not a set of files, it does not change when the working tree is fixed, and it is the category whose failure cannot be repaired after the fact.
