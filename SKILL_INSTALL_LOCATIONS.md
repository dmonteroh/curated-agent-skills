# Skill Install Locations

This repo is agent‑agnostic. Different tools scan different folders for skills. Below are the **two scopes you asked for** (project and user), plus the common Codex locations for completeness.

## Project‑Level (Repo) Skills

**Codex**

- Repo‑local skill locations are under `.codex/skills` relative to the current working directory or repository root.

**GitHub Copilot Agent Skills**

- Project skills live under `.github/skills` or `.claude/skills` in the repository.

## User‑Level (Home) Skills

**Codex**

- User skills live under `$CODEX_HOME/skills` (default `~/.codex/skills`).

**GitHub Copilot Agent Skills**

- Personal skills live under `~/.copilot/skills` or `~/.claude/skills`. citeturn0search0

## Other Agents

Agents beyond Codex/Copilot each define their own skill paths (for example, separate locations per tool). This is one reason shared skill repositories are useful across tools.

## References (for path conventions and scope)

```
https://developers.openai.com/codex/skills/
https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
https://medium.com/@richardhightower/agent-skills-the-universal-standard-transforming-how-ai-agents-work-fc7397406e2e
```
