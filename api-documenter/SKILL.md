---
name: api-documenter
description: Create or improve API documentation (OpenAPI, AsyncAPI, GraphQL) for
  developer-facing APIs, including interactive docs, code examples, and portal content.
category: docs
---
Provides API documentation guidance focused on accurate, developer-friendly docs that reduce integration time.

## Use this skill when

- You need to create or update API documentation for public or internal users
- You must author or refine OpenAPI, AsyncAPI, or GraphQL docs
- You need interactive docs, SDK snippets, or onboarding materials
- You want to audit documentation for completeness and accuracy

## Do not use this skill when

- The task is only backend implementation with no documentation work
- You only need an informal note or meeting summary
- There is no API surface or interface to document

## Trigger phrases

- "document this API"
- "write OpenAPI" or "update the spec"
- "build a developer portal" or "improve API docs"
- "add SDK examples" or "add code snippets"

## Inputs to collect

- API surface: endpoints/events, request/response shapes, error formats
- Auth and security: schemes, scopes, rate limits, headers
- Examples: real or representative payloads and status codes
- Audience: primary personas and their success criteria
- Tooling constraints: doc site, templates, CI requirements

## Constraints and assumptions

- Use only the provided API details; flag missing or conflicting inputs
- Label synthetic examples as representative if real payloads are unavailable
- Follow the existing documentation style guide or template if provided
- Avoid time-sensitive claims unless explicitly supplied

## Workflow

1. **Scope the documentation**
   - Confirm target users, API boundaries, and success criteria.
   - Output: a documentation plan with required sections.
2. **Validate or author the spec**
   - If a spec exists, review for accuracy, examples, and auth coverage.
   - If no spec exists, draft a minimal spec aligned to the API surface.
   - Output: updated or draft spec outline and gaps list.
3. **Write documentation content**
   - Document auth, endpoints, errors, pagination, and versioning.
   - Include at least one working request/response example per endpoint.
   - Output: documentation pages or markdown sections with examples.
4. **Add interactive and SDK materials**
   - Provide SDK snippets or language-specific examples when needed.
   - Note any required setup steps for testing or sandbox environments.
   - Output: code examples and integration steps.
5. **Quality check and maintenance**
   - Verify consistency between spec and docs.
   - Define a lightweight update cadence and ownership.
   - Output: QA checklist and maintenance notes.

## Decision points

- If documentation targets external users, include onboarding and auth setup guides.
- If multiple APIs exist, add a navigation map and versioning policy.
- If examples are missing, request or synthesize representative payloads and label them.

## Common pitfalls

- Missing auth prerequisites or unclear token scope requirements
- Examples that do not match schemas or real responses
- No error catalog or troubleshooting guidance
- Versioning information buried or inconsistent across pages

## Output contract

Report results in this format:

- Summary: what was documented or updated
- Spec updates: files or sections created/changed
- Docs output: pages/sections and example coverage
- Open questions: any missing inputs or blockers
- Verification: checks performed or not run

## Examples

**Input**: "Document the Payments API and add OpenAPI examples."
**Output**: Documentation plan, updated OpenAPI outline, example request/response snippets, and a QA checklist.

**Trigger test prompts**

- "Create OpenAPI docs for these endpoints"
- "Improve our developer portal onboarding for API keys"

## References

See `references/README.md` for detailed checklists, standards, and tooling guidance.
