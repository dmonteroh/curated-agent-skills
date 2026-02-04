# Using This Skill In Codex (Example)

This skill is still useful even if you cannot literally spawn multiple sub-agents.

## Two Modes

### Mode A: True parallelism (if your host supports it)

If your Codex environment supports parallel sub-tasks, dispatch one per domain and then merge with an integration gate.

### Mode B: "Prompt-parallel" (works everywhere)

Even without true parallelism, you can get most of the benefit by:

- partitioning the work
- writing 2-5 tight sub-task prompts
- executing them sequentially without mixing context

This avoids thrash and reduces accidental coupling.

## Practical Workflow (Recommended)

1) Partition
- Identify domains that do not share files/state.

2) Create sub-task prompts
- Use the prompt template from the main skill.

3) Execute one sub-task at a time
- Treat each sub-task as its own mini-session.
- Before moving to the next sub-task, write down:
  - root cause
  - files changed
  - verification result

4) Merge gate
- Check for file overlap and reconcile.
- Run the full verification (tests/build/smoke checks).

## Optional: Isolation via Git worktrees

If you have a git repo and want better isolation (still model-agnostic):

- Create one worktree per domain
- Do changes in each worktree
- Merge in a controlled order

(Only do this if it fits your repo workflow.)
