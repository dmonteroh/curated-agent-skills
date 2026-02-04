## Agent protocol

### 1) Skill usage (always)

- If a local skill matches the task, use it. If multiple skills apply, use the minimal set.
- Default composition order: 1) OS/workflow skills to structure the work (clarify -> decide -> plan -> execute -> verify). 2) Skills for tech-specific implementation. 3) Quality skills (testing, review, security, performance) as guardrails.
- If no skill exists for a subtask, proceed with best practices and make assumptions explicit.

### 2) Brainstorming gate (when unclear)

- If requirements are ambiguous or high-risk, pause and run a short brainstorming loop: ask one focused question at a time, offer 2-3 approaches with tradeoffs, and produce a concise design brief to confirm before implementation.

### 3) Multi-agent protocol (encouraged when feasible)

- If work can be partitioned safely, prefer parallelization using `dispatching-parallel-agents` for both partitioning and the subagent execution flow (implementer + reviewers), including verification/review gates.

### 4) Verification culture (non-negotiable)

- Do not claim “done”, “fixed”, or “tests pass” without fresh verification output.
- When reporting, include: root cause, files changed, and how it was verified.
