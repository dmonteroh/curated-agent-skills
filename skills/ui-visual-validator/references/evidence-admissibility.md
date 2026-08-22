# Evidence admissibility

Companion to the `Evidence admissibility` section of `SKILL.md`. That section states the four gates; this file carries what each one rejects and why a review that skips it produces a verdict nobody should trust.

The gates run at workflow step 1, before any design criterion is applied. Failing one is never a reason to `pass` the parts that happen to be present.

## 1. Complete coverage, never a sample

Enumerate the full set of pages, routes, slides, tabs, modal states, breakpoints and scroll positions in scope, record the count, and require one capture per item.

- A forty-slide deck needs forty captures, not five. The defect is always on the page nobody opened.
- The verdict is per page, and one failing page fails the surface. "Most pages look fine" is not a `pass`; it is an unfinished review reported as a finished one.
- Sampling is the failure mode that hides best: the report looks complete, the coverage number is never stated, and the reader has no way to tell a five-of-forty review from a forty-of-forty one.

## 2. Freshness

A capture is admissible only if it postdates the last change to the source it claims to verify.

- An older artifact is stale and says nothing about the current build, however good it looks.
- Between rounds, re-capturing only the pages a fix touched is enough. The round that finally approves the work judges a complete, current set.
- When capture time or source-change time cannot be established, that is `needs-evidence`, not the benefit of the doubt.

## 3. Capture hygiene

Inspect the artifact before judging the product.

- The file's actual format matches its extension. A JPEG named `.png` is a broken capture, not a design finding.
- The frame is fully composited, with no black bands or missing regions.
- Its dimensions match the viewport it claims to show.
- A defective capture burns a whole review round on the pipeline. Send it back to be re-shot and record it as a tooling defect, never as a product issue — a compression artifact reported as a visual defect sends someone to fix code that was always correct.

## 4. Motion frames

A single resting frame is not evidence for anything that moves.

- Each transition needs three frames: rest, in-flight, and settled. The in-flight frame is taken while the motion is running, which is what proves it runs at all.
- Each scroll or entrance reveal needs a start/mid/end sequence.
- The source protocol names a specific in-flight millisecond timing. That figure is unmeasured, so the requirement is that the frame catches the motion mid-flight, not that it lands on a particular millisecond.

## Decision points

- If the enumeration cannot be produced because the surface's own page list is unknown, that is the first finding, and it blocks the review rather than shrinking it.
- If a capture set mixes fresh and stale artifacts, judge nothing until the stale ones are re-shot: a per-page verdict over a mixed set produces findings nobody can attribute to a build.
- If capture hygiene fails on more than an occasional frame, report the pipeline as the defect and stop. Re-shooting one frame at a time across several rounds costs more than fixing the capture step once.
