# Verification harness

The half that makes a portability claim fail rather than be believed. The disposition table records what is claimed per target; these checks decide whether the shipped bytes agree.

## Build the token list

One entry per literal string that either got rewritten or did not. Derived from the filled disposition table, not from memory:

- Every path root of the source agent — user-scope, project-scope, and the subdirectory prefix, in both literal and home-relative forms.
- The source agent's agent-instruction file name, which survives untouched whenever a rename was never declared.
- Every tool name in the source vocabulary, including the ones no rewrite table mentions. Absence from the table is the reason to check, not a reason to skip.
- Every canonical tool phrasing, plus the near-miss phrasings the corpus actually contains. Keyed on phrases, a rewrite covers the phrasings it knows and no others.
- The path roots of every other target the corpus mentions in prose, since cross-agent examples carry foreign paths into each target's tree.
- Any frontmatter key the corpus authors that a target does not permit.

## Run the checks

For a transformed corpus, each token becomes one check against the generated tree:

```
grep -rn "<token>" "<target-tree>"      # any hit is a failure
```

For a read-as-authored corpus the same token list is a lint over the source. There is no later step, so a hit is an authoring defect and the repair is rewording rather than rewriting.

Three checks are not token greps and belong in the same run:

- **Output exists.** A grep over an absent or empty tree passes trivially. Assert the tree exists and is non-empty before any leakage check counts.
- **Frontmatter validity per target.** Parse each item's frontmatter against that target's declared dialect: permitted keys only, description within the cap, injected keys present, and every injected key also permitted.
- **Cross-target uniqueness.** No two targets share a name, an invocation command, a subdirectory prefix, or an install root. A collision overwrites one tree with the other and produces no message; it is a single assertion over the target list.

## Parameterize over the target list

Checks iterate the target list rather than naming targets. A check written per named target is a check a new target arrives without, and the new target is precisely the one nobody has verified. The same rule applies to the token list: derive it from the table, so an axis added later is covered by construction.

## Freshness

A generated per-target tree is a build artifact: excluded from version control, regenerated before checks, and covered by a check that fails when the tree is older than the source it was built from. Without it, a stale port passes by being old — the checks run against output that predates the content they are meant to verify.

## Confirm each check can fail

Before a check counts as coverage, insert the token it hunts for into the tree, run the check, and confirm it goes red; then remove it. A leakage grep with a typo in its pattern, or one pointed at the wrong directory, reports a clean run forever and certifies exactly the gap it hides. *(Authored, not sourced: the source states the checks, not a negative-control step for them.)*

## Reporting

Each check reports the token, the target, pass or fail, and every hit with its file and line. A summary line that says "checks passed" without the token list is not a result — the token list is the claim, and a check that never ran over a token is indistinguishable in that summary from one that ran and passed.
