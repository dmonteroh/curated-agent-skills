# Changes needed in this skill

Source: the `writing-style` measurement campaign, 1,645 agent runs across four models on two vendors — the largest run of the method this skill teaches. Lessons: `tmp/writing-style-skill/LEARNINGS.md`. Numbers: `tmp/writing-style-skill/measure/RESULTS.md`. This file proposes edits and does not make them. The skill already carries blind grading, frozen eval sets, recorded run configuration, defined control arms, and joinable records — nothing below re-proposes those.

## Additions to the workflow

1. **A trial floor for ranking close variants: four trials across five probes.** Three-trial screens pointed the wrong way three separate times in one campaign. One variant that screened strong on a vendor died at forty runs per variant. The rule a screen may follow: nominate, never ship. Belongs beside step 5 (run both arms) or step 7 (the discrimination split).
2. **Re-establish after ANY change to the artifact under test.** A section added to one part of the artifact, "measured" against the surface it targeted, silently regressed a different surface by half. Per-surface invalidation tables understate blast radius: after any edit, the whole standing set reruns or the numbers carry a stale label.
3. **Two vendors by default, and narrowing is a finding stated before the run.** Seven of nine runners in the source harness were authored single-vendor. Every decision after day one rested on one vendor until the gap was forced closed. A vendor difference in kind is invisible to any single-vendor design: one vendor loads skills on chat turns, the other never does.
4. **Multi-model legs need a label discipline.** When runner labels are vendor names and the model varies underneath, write a marker file naming what actually ran into every output directory. The campaign's small-tier leg would otherwise read as frontier data to any later reader of the filenames.

## Additions to the constraints

5. **The scorer must encode the artifact's own contracts.** Scoring replies with deliverable rules invented a 29-violation residue that never existed. Capturing final messages as "the deliverable" charged clean file deliverables for their chat wrapper. A grader that does not know the artifact's carve-outs measures a different artifact.
6. **Isolation from installed skills is mandatory for without-arms.** Skills installed in real agent homes self-activate in dispatched arms — all four control arms of one earlier eval silently ran the treatment. Bare credential-only homes, plus a fingerprint sweep of every control output for treatment markers, with a hit voiding the arm.
7. **Copy credentials into isolated homes unconditionally.** A guarded copy keeps an expired token forever, and each failed arm writes a short auth error the grader counts as clean output. The failure mode is worse than a lost run: it is a fabricated clean cell.
8. **Traces and filenames are the ground truth. Prose summaries are not.** A rename collapsed two identities in a results file and silently disabled the arm isolating the name. A later ad-hoc scorer contradicted a 360-run result until the raw trace showed the tool firing. Before believing any surprising number, read the trace it came from.
9. **Generate variant and baseline artifacts from the live source at run time.** Two stored mirrors drifted in one harness, each invalidating every arm that used it. Store nothing that mirrors something.
10. **Report cost in each vendor's native unit and never convert.** And report the treatment's cost next to its effect — the measured enforcement mechanism roughly doubled cost per deliverable, and that number belongs in the verdict.

## Additions to `references/threats-to-validity.md`

11. **A saturated design cannot rank.** A 360-run matrix answered "identity is irrelevant" precisely because every cell hit the ceiling — which is a strong answer, and also proof the design had no headroom to rank anything. Say which of the two a saturated result is being used as.
12. **Activation is read from the tool stream, never inferred from output prose.** The two vendors' signals differ in kind: a tool-use event on one, a shell read of the skill file on the other. The trace layer must normalise them into one record shape.
13. **Rule-based graders calibrate on two legs and a range.** Fire-rate on accepted material sets severity. The spread across several pre-treatment corpora says how much of a rate is register and how much is residue — a single baseline misled by six-fold in this campaign.

## Sequencing

Items 1-3 are the load-bearing workflow changes and belong in `SKILL.md`. Items 4-10 fit the Constraints section or `references/behavioral-compliance.md`, whichever the operator prefers. Items 11-13 extend `references/threats-to-validity.md` in its existing one-threat-per-heading shape.
