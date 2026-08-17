# History as a scan surface, and the remediation order

Category 6 of the sweep in `SKILL.md`. The source procedure names the history audit as a scan category and nothing more; the surface inventory, the coverage checks, and the remediation ordering below are authored — reasoned from how history-borne exposure behaves, not carried from a verified source. Names here are the ones commit-graph version-control systems use; adapt the terms for another system, but the reasoning holds wherever a publication copies a graph rather than a snapshot.

## Why the working tree is the wrong surface

Sanitizing the working tree makes a claim about one snapshot. A clone takes the graph. A value deleted in the most recent commit is present in every earlier commit that still travels, and the earlier value is usually the interesting one — it is the version that was live long enough to be used.

## What travels

- Every commit reachable from every published ref, not just the tip of the default branch
- Branches other than the default, wherever the publication copies more than one
- Tags, including annotated tag messages
- Commit messages, which routinely carry ticket identifiers, incident summaries, internal hostnames, and occasionally a pasted value
- Commit metadata: author and committer names, mail addresses, and timestamps
- Files deleted in a later commit, in full, at their earlier revision
- Every superseded value of a file that was edited to remove something
- Merge commits, which can reintroduce content that a branch had removed
- Submodule or sub-repository pointers, including the location they point at
- Large-file pointers, whose backing store may not travel with the publication and may not be reachable by the reader

One asymmetry is worth stating explicitly: publishing by pushing refs carries what those refs reach, while publishing by copying a repository directory carries the whole object store, including objects no ref reaches. The two are not equivalent, and a directory copy is the wider exposure.

## Auditing it

- Scan content across every reachable commit, not the checked-out tree. Falsifiable check: compare the number of objects the scan examined against the number the repository holds; a scan whose count matches the working tree's file count only scanned the tip.
- Scan commit messages and author metadata as a separate pass from file content. Content scanners generally do not read them, and this is where internal identifiers concentrate.
- Verify the audit's own coverage before reading its verdict. A tool that skipped binary objects, skipped large files, or stopped at a depth limit produces an empty result that looks identical to a clean one.
- Where publication is meant to be a fresh snapshot, verify that it actually is: a repository re-created by copying a directory keeps the original graph, and the intent to publish a snapshot is not the same as having one.

## Remediation order

1. Rotate or revoke anything that is a live credential first, before deciding whether to rewrite. Rewriting takes time and does not shorten the exposure window; rotation ends it.
2. Decide rewrite-or-snapshot before the first publication. A rewrite beforehand costs nothing downstream. The same rewrite afterwards costs everyone holding a copy, and recalls nothing.
3. Weigh what a rewrite breaks before running one: every downstream commit identifier changes, so signatures, tags, references from issue trackers, and any external link into the history stop resolving.
4. Where a value can neither be removed nor rotated, it is not a technical problem any more — it is an override decision, recorded with the finding, the accepted exposure, the rationale, and the accepting owner, per the gate.
5. After publication, treat a finding as an incident: rotate, notify the owners of any exposed personal data or third-party name, and rewrite only where it reduces *future* exposure. Report the exposure window as running from first publication to rotation, not from discovery.

## The snapshot trade

Publishing a single fresh commit with no prior history is the cheapest way past this category, and it is legitimate whenever the private history has no public value. Record it as a decision rather than letting it happen quietly: the published repository starts at one commit, the private history stays private, and contribution history and authorship attribution are lost. The trade is real in both directions — a project whose value includes its provenance pays for the snapshot, and a project carrying five years of internal commits pays for the history.
