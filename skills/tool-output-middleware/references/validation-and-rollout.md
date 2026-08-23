# Validating a transformation layer

How to prove a middleware layer is safe to enable, and how to keep it safe as the tools it wraps drift. Everything here is design-stage material from a source that was never implemented: the structures are sound, the numbers in the original were chosen, and no measurement exists behind any of them.

## Test tiers, priced

Make the economics of each tier explicit instead of implicit. One row per tier, with four columns: **tier, cost, frequency, blocks merge**. Filling that table is the exercise — a tier whose cost and blocking power are not both written down will either be skipped or will block a release nobody expected it to block.

The source's allocation, as a worked shape:

| Tier | Cost | Frequency | Blocks merge |
| --- | --- | --- | --- |
| Unit, golden-file, schema validation | Free | Every change | Yes |
| Pathological gate subset | Free | Every change | Yes |
| End-to-end with the model stage mocked | Free | Every change | Yes |
| Adversarial regression | Free | Every change | Yes |
| Cross-host end-to-end | Free | Every change | Yes |
| Real-model verifier tests | Paid | Only on changes touching verifier code | Yes |
| Synthetic evaluation suite | Expensive | Periodic | **No — informational by design** |
| Real-corpus benchmark | Expensive | Pre-release | Yes — the hard gate |
| Fixture version-drift check | Free | Every change | No — warning only |

Two of those rows carry the actual opinion. The synthetic eval is demoted to informational *on purpose*, so that the real-corpus benchmark is the only expensive thing that can block; and the drift check warns rather than fails, because an upstream tool changing its output format is news, not a defect in this layer.

## The test series that fill the tiers

- **Good cases.** One named scenario per transformation rule, each with a stated expected reduction. The scenarios themselves are specific to whichever tools you wrap and do not transfer; the obligation does — every rule owes a named case with a number attached to it.
- **Pathological cases.** The thirty-item checklist in `pathological-inputs.md`, with a subset gating merge and the rest as backlog.
- **Cross-host end-to-end.** The same fixture through every supported harness, asserting byte-identical output modulo the host identifier. Also covers install and uninstall idempotency, coexistence with the user's other hooks or wrappers, config precedence, the bypass switch, and "an error inside the layer does not crash the session."
- **Verifier tests.** Mock the model to return each adversarial shape — injection, timeout, server error, the no-op sentinel — so the contract is tested without paying per run. Reserve real-model calls for the small tier above.
- **Adversarial regression.** *"Starts empty; grows with scars."* Every post-ship bug becomes a permanent test, recorded on a fixed template so the series stays greppable: an ID, the commit that introduced the bug, a one-line summary, the reproducer, and a link to the fix.

## Fixture freshness by version stamp, not by calendar

Every golden fixture carries the version of the tool that produced it in its frontmatter. CI **warns**, never fails, when the installed version differs, and the drift list is reviewed before a release. The source records this as a correction of its own earlier calendar-based rotation, which expires fixtures that are still correct and keeps fixtures that silently went stale.

This generalizes to any fixture captured from an external tool whose output format drifts, well beyond this kind of middleware.

## The real-corpus benchmark

The premise, stated by the source: every competing transformer ships with hand-picked fixture numbers. A benchmark built from the user's own logged sessions proves the layer works on their actual workload before they enable it, and doubles as the only honest performance claim the project can make.

Six stages:

1. **Scan** the local transcript corpus, pairing each tool-invocation record with its result record.
2. **Rank** by estimated token cost and cluster by tool and command pattern, to find the heavy tail — which small fraction of calls produced most of the tokens.
3. **Emit** one fixture per high-leverage cluster, capped at a scenario count you choose. (The source's cap is openly flagged as unresolved in its own open questions.)
4. **Replay** the transformer over each fixture; measure reduction and produce a diff of exactly which lines were dropped.
5. **Plant** synthetic critical lines into those *real* scenarios and confirm they survive. Real data plus real threats is what makes the result proof; planting hazards only into synthetic inputs proves the layer handles inputs it will never see.
6. **Report** per-scenario before and after, not just an aggregate.

Stage five is the one most implementations skip, and the one the gate depends on.

## Privacy rules for a corpus of real transcripts

Marked non-negotiable in the source, and correctly so — it rates corpus leakage as one of only two High-severity risks in the whole design.

- Local read only. The corpus is never uploaded, never logged to telemetry, never shared.
- The local-only setting is hard-coded rather than configurable; where a config key exists at all, it is documentary and cannot be changed.
- Benchmark output is written with a restrictive owner-only file mode.
- The command prints a banner naming the exact path it is reading and stating that nothing leaves the machine. The banner is a control, not decoration: it is what lets a user notice the day the path changes.
- A *shared* corpus is a separate workstream, built from hand-contributed and secret-scanned fixtures. It is never the user's own transcripts with a scrubber applied.

## The ship gate

Three floors, all three set and recorded before anything is measured:

1. A total token-reduction floor across the corpus.
2. A zero-loss criterion on planted critical lines — no scenario may lose one.
3. A per-scenario floor, so a strong average cannot hide a scenario that got worse.

**The values are yours to choose, and choosing them is the point.** The source's three figures were selected in advance and never measured against any corpus, because the benchmark component that would have produced them was never built. A different figure for the same threshold appears elsewhere in the same document, described as the level below which the premise itself would be weaker than claimed — which confirms these were negotiable targets rather than findings. Third-party reduction percentages quoted in the source come from blog posts, and the source itself instructs the reader to verify them independently.

Record the floors, the date, and the corpus they were measured against, so a later run can tell a regression from a different workload.

## Latency budgets

Enforce median and tail latency in CI, with separate budgets per platform, a separate budget for the path where the model stage fires, and separate budgets for config deserialization and the staleness check. The one figure in the source with real provenance is a latency correction of exactly this kind — a runtime's cold-start cost on one platform was measured, and an earlier target was revised because the measurement made it unreachable. That is the only shape in which a number in this design earned its place: measured on the machine, then written down.
