---
name: jira-issue-management
description: "Create, read, transition, and link Jira issues (Epics, Tasks, Bugs) through an Atlassian MCP server, driven by a project-local Jira map file that caches cloud ID, status and transition IDs, account IDs, standing Epics, and conventions. Use when work involves creating or updating Jira tickets, turning a plan into Epics and Tasks, or bootstrapping the project's Jira map."
metadata:
  category: workflow
---
# jira-issue-management

Provides a deterministic workflow for working a project's Jira through an Atlassian MCP server (such as Atlassian Rovo): creating Epics and Tasks, reading and searching issues, transitioning status, commenting, and linking. All project-specific facts — cloud ID, issue types, statuses, transition IDs, account IDs, standing Epics, conventions — live in a project-local map file that the skill bootstraps once and keeps fresh, so routine operations cost one file read instead of repeated MCP discovery calls.

MCP tools are referred to by their unqualified names (`createJiraIssue`, `transitionJiraIssue`, ...); the runtime prefix varies per installation. If no Atlassian MCP tools are available in the session, stop and report that instead of simulating Jira operations.

## Use this skill when

- The user asks to create, update, transition, comment on, link, or search Jira issues (tickets, epics, tasks, bugs) and an Atlassian/Jira MCP server is available.
- A plan, brief, or work breakdown needs to become Jira issues — an Epic with Tasks, or a single Task.
- The project's Jira map file needs to be created or refreshed.

## Do not use this skill when

- No Atlassian MCP server is available in the session.
- The request is board, backlog-order, or sprint management (move a card onto the board, re-rank the backlog, start or close a sprint). The issue-level MCP toolset cannot do this — see "Board and backlog reality" and state the limitation rather than attempting workarounds.
- The request is Jira administration (workflow editing, permissions, board column configuration) or Confluence content work.

## The project map file

Project facts live in one committed file in the consuming project, by default at docs/jira-project-map.md (honor a different path if the project's agent instructions name one). Its format and the bootstrap discovery procedure are in `references/project-map-template.md`.

- Read the map before the first Jira operation of a session. If it is missing, offer to bootstrap it before any write.
- Prefer the map over MCP discovery calls for stable facts (cloud ID, project key, issue-type IDs, transition IDs, field IDs, account IDs, standing Epics). This is the token-cheap path.
- Live data — issue contents, current status, search results — always comes from the MCP. The map caches only stable facts.
- On drift (a transition is rejected, a status or field is unknown, an ID no longer resolves): re-discover via the MCP, update the map in the same task, and tell the user what changed.

## Board and backlog reality

These constraints are verified behavior of issue-level Atlassian MCP toolsets; encode them, do not fight them:

- Every MCP-created issue lands at the bottom of the backlog in the project's default initial status. This is not a choice — never ask "backlog or board?" on create.
- The toolset is issue-level only: there is no board, sprint, or agile API. It cannot move a card onto the board or re-rank the backlog. Rank writes through `editJiraIssue` can return HTTP 200 and silently not persist.
- Two independent axes decide where an issue shows in the board view: status controls visibility (statuses not mapped to a board column are hidden entirely, including from the backlog section), and rank controls board-versus-backlog section among visible issues. The MCP controls the first (via transitions), never the second.
- Consequence: create issues directly into a visible status (the map's default initial transition) so they appear in the backlog, and never claim an issue was placed on the board. If the user needs MCP-created issues to reach the board, the supported paths are a manual drag in the Jira UI or a Jira Automation rule set up by the user.

## Workflow

### 1) Load the map

Read the project map file. Missing → offer bootstrap per `references/project-map-template.md`. Output: project key, cloud ID, ID tables, defaults, conventions.

### 2) Gather and confirm (before any create)

- Run a dedup search first: JQL on project plus summary keywords (and parent, for Tasks under an Epic), narrow `fields`. A plausible existing issue → surface it and ask before creating.
- Collect: issue type, summary, description, parent Epic (if any), initial status, assignment.
- Ask only for missing information that changes the outcome; derive the rest from context and the map. Assignment is always such information: **never auto-assign**. If the user did not state an assignee, ask whether to assign and to whom — default is unassigned. This instruction runs against the default tendency to pick and proceed; follow it literally.
- Show a compact preview (type, summary, parent, initial status, assignee) and get confirmation before writing.

### 3) Create

`createJiraIssue` with: description in Markdown (never hand-built ADF), `parent` for Epic linking in team-managed projects, custom fields via `additional_fields` using the value shapes from the map, and a create-time `transition` to the map's default initial status so the issue is born visible.

### 4) Verify

Read the issue back with a narrow `fields` list and confirm status, parent, and assignee match the intent. Silent-success responses exist in this toolset — never report success from a bare 200. If the read-back contradicts the write, stop, report the mismatch, and do not retry blindly.

### 5) Transition

Select the transition by its **target status name** using the map (fall back to `getTransitionsForJiraIssue` on drift). Transition IDs are a separate namespace from status IDs, and a transition's label can differ from its target status — never select by label. In team-managed projects, transitioning into any Done-category status auto-sets Resolution; no separate resolution write is needed or possible. Verify by read-back.

### 6) Read and search

Always pass a narrow `fields` list; never `*all` on a multi-issue search (it overflows tool-result limits). Paginate with `nextPageToken`. Native JQL only — `issueFunction(...)` is a ScriptRunner extension and errors on vanilla Cloud.

Tool-level parameter shapes, field-format rules, and rate-limit handling are in `references/mcp-tool-notes.md`.

## Issue authoring rules

- Never write branch names or branch status into descriptions. Source-control linking is the job of Jira's development-panel integration (branches named with the issue key auto-link).
- Work-breakdown rule of thumb: one branch of work ⇒ one Task, with internal steps as short description bullets; a multi-phase plan with a branch per phase ⇒ one Epic plus one Task per phase. The Jira tracking grain can be coarser than the agent execution grain — child briefs of one branch's work stay inside one Task's description.
- Use Sub-task issue types only when the project map lists them and its conventions call for them; sub-tasks are not separate cards on team-managed boards.
- Task summary ≈ the work/phase title; description = one line of intent plus scope bullets.
- Project-specific conventions in the map file override these defaults.

## Output contract

- After any write: issue key and URL, type, summary, status (as verified by read-back), parent, assignee, plus any assumption made.
- After bootstrap or refresh: the map file path and what was added or corrected.
- When an operation is impossible through the MCP (board placement, re-ranking, sprints): a plain statement of the limitation and the supported alternative.

## Examples

**Plan → Epic + Tasks.** "Create Jira issues for the dashboard plan" → read map; dedup-search Epic summary; preview one Epic + one Task per phase (parent = the Epic, initial status = map default, assignee: asks the user); on confirmation create each with create-time transition; read each back; report keys, URLs, verified statuses.

**Status update.** "Move ABC-42 to In Progress" → map lookup: transition targeting the status named "In Progress"; `transitionJiraIssue` with that transition ID; read back; report old → new status. If the map has no such target, call `getTransitionsForJiraIssue`, update the map, then transition.

## References

- Index: `references/README.md`
- Map file format and bootstrap procedure: `references/project-map-template.md`
- MCP tool behaviors, field shapes, and pitfalls: `references/mcp-tool-notes.md`
