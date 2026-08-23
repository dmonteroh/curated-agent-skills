# Review Convergence

Companion to workflow step 6 of `SKILL.md`. That step states the loop and its cap; this file carries the reasoning behind each rule and the failure each one prevents.

## Why freshness per round is the load-bearing rule

A second-round `pass` is only evidence if the reviewer that produced it did not produce the first one.

- A reviewer re-reading a fix it asked for is grading its own instruction. It knows what it wanted, so it reads the diff for compliance with its own sentence rather than for whether the code is now correct.
- A reviewer carrying its earlier verdict into the next round is anchored on it: it finds what it found before and misses what it missed before. The second round then confirms the first round's blind spots instead of covering them.
- So each round is a fresh dispatch, never a continuation of the previous reviewer's session.

## Critique and repair are separate authorities

A reviewer that proposed a fix never evaluates that fix.

- The reviewer holds no write authority. The fixer is never asked for the verdict.
- When the same session both proposes and accepts, the acceptance carries no information: the proposal and the verdict have one author.

## Scoping the fix task

The fix dispatch is deliberately the narrowest packet in the orchestration.

- Its scope is the blocking findings and nothing else — "fix what is flagged; do not refactor and do not add unrequested changes."
- Its claim set is no wider than the files those findings name. A fix task that widens its own claim set has become a second implementation task, and its output needs a full review rather than a re-review.
- Non-blocking suggestions do not enter the loop. Recording them and moving on is the correct disposition; feeding them in is how a two-round convergence becomes a five-round one.

## The cap

- Fix the cap before the first round runs. A cap chosen after reading the findings is not a cap — it is a negotiation with the work already done.
- Three rounds is this skill's chosen default, not a measured threshold. Raise or lower it per pass on the cost of the work and the cost of shipping the defect; state the value in the packet either way.
- At the cap, stop and escalate to the human with the surviving findings, the rounds spent, and what changed between them.
- Integrating at the cap and running one more round past it are both failures of this step. The second is how a bounded loop becomes an unbounded one, and it never announces itself — each individual extra round looks locally reasonable.

## Board discipline

- Record the round count and the open findings against the task.
- A task sitting at `needs-fix` with no round count is a task nobody is converging. The status says work is outstanding; only the round count says whether it is moving.

## Decision points

- If the first round's findings and the second round's findings do not overlap at all, the reviewer axis is probably wrong for this task rather than the code being twice broken. Re-read the reviewer packet before dispatching a third round.
- If a finding survives every round unchanged, escalate it as a disagreement rather than re-dispatching it. Three workers failing to satisfy one finding usually means the finding and the acceptance criteria disagree.
- If the fix task returns `QUESTIONS`, that is not a round. Answer it, re-issue, and do not count it against the cap.
