# Reframing after failed rounds

Entered when two consecutive rounds ended without a confirmed or falsified hypothesis, or when the session's stated time budget ran out. Continuing past that point usually means the real cause sits in a category that was never imagined, and further effort inside the current mental model buys nothing.

The move is not another round. It is three **independent** analyses under three **fixed, orthogonal** framings, followed by a synthesis that reads agreement and disagreement as different signals.

## Why three, and why fixed

A single analysis returns one coherent story, and coherent stories inherit the framing of the question — which means they inherit the blind spot the investigator already has. Framings chosen fresh each time drift toward the current hypothesis set for the same reason. Fixing the three in advance is what forces divergence.

Independence is load-bearing: run the three as separate passes that do not see each other's output, and prefer a different model for at least one of them where a second is available. Three passes that read each other agree by contagion, and agreement is the whole signal being measured.

## Framing A — obvious-but-missed

Supply the failure description and every observation captured so far, verbatim, with its sources. Ask:

> What is the most embarrassing, most obvious cause that an experienced engineer would spot in thirty seconds and that has been walked past? Consider at least: a typo or off-by-one; the wrong variable, constant, or import; a stale cache or a stale build; the wrong file edited; the wrong process or the wrong instance inspected; a test harness executing different code than the application; source being edited while built output is what runs.
>
> Return exactly three candidate causes, ranked by likelihood, each with one sentence explaining how the captured evidence is consistent with it.

## Framing B — system-boundary

> Assume the bug is **not** in the code that has been read, but at a boundary. Consider at least: a dependency behaving differently from its documentation; middleware mutating the request or the response; a proxy or gateway rewriting headers or bodies; build-time versus runtime resolution of configuration; module load order; a version mismatch between a bundled library and a system one; an ABI or platform-library difference; a transport or protocol negotiation difference.
>
> Return three candidate causes, each naming the specific boundary and the specific contract assumption that may be violated there.

## Framing C — invariant-violation

> Which assumptions currently taken as true might be false? Enumerate the five assumptions most load-bearing to the current hypothesis set. For each: describe the smallest runtime query that would falsify it, and predict the observable if the assumption holds versus if it fails.
>
> At least one query must be decisive on its own.

## Synthesis

Walk the three outputs in this order. Taking the top-ranked candidate from any single output defeats the purpose of having three.

1. **Agreement scan.** Note every candidate cause that appears under two or more framings. Independent agreement across orthogonal framings is the strongest signal available here — when obvious-but-missed and system-boundary land on the same cause, that is usually the bug.
2. **Disagreement scan.** Note where the framings conflict. A conflict is genuine uncertainty that only runtime evidence can resolve, and each one becomes a candidate distinguishing query for the next round.
3. **Falsification queries.** Framing C returns queries designed to be decisive. Carry them into the next round's plan as written rather than rephrasing them.
4. **Build the new hypothesis set** under the Phase 1 rules, drawn from both scans — at least one hypothesis from the agreement scan (the likely cause) and at least one that resolves a disagreement (so one round settles it either way).
5. **Reset the failed-round counter** and return to the evidence round.

Record all of it in the journal: the three summaries, both scans, and the resulting hypothesis set. A reframe whose output is not written down cannot be checked against the round that follows it.

## If rounds keep failing after a reframe

Two further failed rounds after a reframe is the escalation threshold. Escalate with the full trace — every hypothesis tried, every observation captured, the reframe outputs — and do not guess a fix.
