# Atlassian MCP tool notes

Verified behaviors and parameter shapes of issue-level Atlassian MCP toolsets (observed on Atlassian Rovo; unqualified tool names — the runtime prefix varies per installation). Every Jira call requires the cloud ID from the project map; the site hostname also works in the `cloudId` argument.

## Scope of the toolset

Issue-level only: create, read, edit, transition, comment, worklog, link, plus project/user discovery. There is **no board, backlog, sprint, or agile API** — no reading board columns, no re-ranking, no sprint operations. Board placement can only be influenced indirectly via status transitions (visibility), never via rank.

## createJiraIssue

- Required: `projectKey`, `issueTypeName` (a name, e.g. "Task"), `summary`.
- Epic linking in team-managed projects: top-level `parent` param (e.g. the Epic's key). Do NOT use an Epic Link custom field — that is company-managed only, as is a required "Epic Name" field.
- `assignee_account_id` for assignment (skill default: omit; ask first).
- Everything else (priority, labels, custom fields) goes in `additional_fields` using the shapes below.
- Description accepts **Markdown** (default contentFormat); the server converts to ADF. Never hand-build ADF documents.
- Supports a create-time `transition: {id: "<transitionId>"}` — verified to create the issue directly in the target status with no follow-up call. Use this to avoid the (often board-invisible) default birth status.
- New issues always land at the bottom of the backlog regardless of parameters.

## editJiraIssue

- Custom-field value shapes by schema type: single-select `{"value": "..."}`; multi-select/checkbox/array `[{"value": "..."}]`; user `{"accountId": "..."}`; number bare; date `"YYYY-MM-DD"`. Discover shapes per type via `getJiraIssueTypeMetaWithFields`; field IDs vary per project, so cache them in the map rather than hard-coding.
- **Silent no-op warning (verified):** rank writes (the LexoRank custom field) return HTTP 200 with no error and do not persist. Treat this as proof the toolset has silent-success paths: after any write that matters, read the field back before reporting success.

## transitionJiraIssue

- Takes a **transition ID** from `getTransitionsForJiraIssue` — a separate namespace from status IDs.
- A transition's label can differ from its target status (e.g. a transition labeled "Done" targeting a status named something else). Always select by target status.
- Team-managed projects auto-manage Resolution by status category: entering any Done-category status sets Resolution and resolution date; leaving clears them. No separate resolution write is needed, and none is exposed by these tools.

## getTransitionsForJiraIssue

- Pass `includeUnavailableTransitions: true` to enumerate the full workflow from one issue. Team-managed workflows commonly use global transitions (any status → X), so one issue yields the whole table.
- Transition and status IDs can change when the project's workflow is edited in the UI — the map is a cache, not ground truth; re-discover on drift.

## searchJiraIssuesUsingJql / getJiraIssue

- **Always pass a narrow `fields` list.** `*all` on a multi-issue search overflows tool-result limits (verified: ~18 issues → 62k characters). Request only what the step needs.
- Pagination is via `nextPageToken`, not startAt offsets.
- Native JQL only: `issueFunction(...)` (linkedIssuesOf, hasSubtasks, ...) is a ScriptRunner extension and errors on vanilla Cloud. Avoid leading wildcards and `~` matches on large text fields.

## Users and links

- `lookupJiraAccountId` resolves people to account IDs — the robust path for assignment. A user's Atlassian email can differ from their git email; the map records the confirmed account ID.
- `atlassianUserInfo` identifies the authenticated account.
- `createIssueLink` needs a link type name from `getIssueLinkTypes`. Epic↔child is NOT an issue link — it is the `parent` field.

## Rate limits and errors

- Responses carry x-ratelimit-limit / x-ratelimit-remaining headers. Trust `Retry-After` and the headers over any fixed number; back off on 429 and 5xx, retry once, then report.
- On a 4xx field error during create/edit: re-check the field shape and ID via `getJiraIssueTypeMetaWithFields`, correct the map, retry once.

## Token economy

- Stable facts (IDs, mappings) come from the map file — one file read. MCP discovery calls are for bootstrap and drift repair only.
- Narrow `fields` on every read; batch questions to the user into the single pre-create confirmation instead of asking one at a time.
