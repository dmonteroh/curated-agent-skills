# Project Jira map — format and bootstrap

The map file is a committed markdown document in the consuming project (default: docs/jira-project-map.md) that caches every stable Jira fact the agent would otherwise re-discover via MCP calls. One project per file. The consuming project owns and versions it; this skill defines the format, fills it, and keeps it fresh.

## Principles

- **Stable facts only.** IDs, mappings, conventions, verified toolset behavior. Never cache live state (issue status, assignees of existing issues, search results).
- **Every entry names its source** — the MCP call that produced it — so a future refresh can re-derive it.
- **Drift handling:** when a cached ID fails (rejected transition, unknown field), re-run the source call, correct the map in the same task, and report the correction.
- **No secrets.** Account IDs and cloud IDs are fine; never store tokens or credentials.

## Bootstrap procedure

Run these discovery calls once and write the file. Ask the user for anything marked *(ask)*.

1. `getAccessibleAtlassianResources` → cloud ID and site hostname.
2. `getVisibleJiraProjects` → project key, project ID, project type, `simplified` flag (true = team-managed).
3. `getJiraProjectIssueTypesMetadata` → issue types with IDs and hierarchy levels.
4. `getJiraIssueTypeMetaWithFields` per creatable type → required fields and custom field IDs.
5. `getTransitionsForJiraIssue` on any existing issue (with `includeUnavailableTransitions: true`) → the status table and the transition table, including each transition's target status.
6. `atlassianUserInfo` and `lookupJiraAccountId` → the operator's account ID and frequent teammates *(ask which accounts matter)*.
7. A narrow JQL search for hierarchy-level-1 issues → standing Epics *(ask which are long-lived)*.
8. *(ask)* Conventions: default initial status for new issues, work-breakdown grain, description format rules, board-visibility notes the user knows from the UI (column-to-status mapping is board config and not readable through the MCP).

Verify the bootstrap by creating nothing: the map is complete when a dry-run preview of a hypothetical create can be filled entirely from the file.

## Template

```markdown
# Jira project map — <PROJECT KEY>

Maintained by the jira-issue-management skill. Stable facts only; refresh entries via the named source calls when they drift. Last verified: <YYYY-MM-DD>.

## Site

- Cloud ID: `<uuid>` (source: getAccessibleAtlassianResources; the site hostname also works in cloudId args)
- Site: <name>.atlassian.net
- Project: <KEY> "<name>", id <id>, <team-managed|company-managed> (simplified: <true|false>)

## Accounts

| Person | Atlassian account ID | Notes |
|--------|----------------------|-------|
| <name> | <accountId>          | <e.g. operator; Atlassian email may differ from git email> |

Assignment default: unassigned; always ask before assigning.

## Issue types

(source: getJiraProjectIssueTypesMetadata)

| Name | ID | Hierarchy level | Notes |
|------|----|-----------------|-------|
| Epic | <id> | 1 | |
| Task | <id> | 0 | |

Types that do NOT exist here (do not assume): <e.g. Story, Sub-task>.

## Fields

(source: getJiraIssueTypeMetaWithFields per type)

- Required on create — <Type>: <fields>
- Custom field IDs: <name> = customfield_<n> (value shape: <shape>)
- Epic linking: top-level parent param (team-managed) | Epic Link customfield_<n> (company-managed)

## Statuses

(source: getTransitionsForJiraIssue target statuses)

| Status | Status ID | Category | Board-visible? |
|--------|-----------|----------|----------------|
| <name> | <id>      | <To Do|In Progress|Done> | <yes|no|unknown — board config, confirm in UI> |

## Transitions

(source: getTransitionsForJiraIssue, includeUnavailableTransitions: true. transitionJiraIssue takes the TRANSITION ID — a separate namespace from status IDs. Select by target status, never by label.)

| Transition ID | Label | → Target status (ID) |
|---------------|-------|----------------------|
| <id> | <label> | <status> (<id>) |

- Create transition (birth status of every new issue): <label> → <status>
- Label ≠ target traps: <list any transitions whose label differs from their target status>

## Create defaults

- Default initial transition on create: <id> → <status> (chosen so new issues are board-visible)
- New issues land at the bottom of the backlog; the MCP cannot rank or move them to the board.

## Standing Epics

| Key | Summary | Use for |
|-----|---------|---------|
| <KEY-n> | <summary> | <what belongs under it> |

## Conventions

- <work-breakdown grain, description format, dedup query patterns, lifecycle mirrors, anything project-specific that overrides the skill's defaults>

## Open items

- <unverified entries, pending discoveries>
```
