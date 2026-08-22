# Store separation, record shape, and write-side keying

Consult when building or restructuring the store itself. The governance rules that use these shapes are in `SKILL.md`; this file carries the mechanics. Rules marked *[authored]* are this skill's generalization rather than a statement in the source designs.

## One store per question

Four persistence layers share storage mechanics and are never merged. Each has its own writers and its own readers:

| Layer | Question it answers | Typical content |
| --- | --- | --- |
| Learnings | what you know | durable institutional knowledge: patterns, pitfalls, preferences, architecture, tooling |
| Timeline | what happened | append-only event history of work done |
| Checkpoints | where you are | working-state snapshots for resuming or handing off |
| Health | how good it is | quality scores over time |

The test is one question per store. A record that answers two of them is two records. This doctrine was derived twice independently in the source corpus: once as the state-systems split above, and once when a proposed single event schema mixing declarations, overrides, verdicts, and feedback was rejected as incompatible domain objects and split into three files. Two independent derivations is the strongest evidence behind any rule in this skill.

Format follows the same split: **event streams append to a line-delimited JSON log; current state is a plain JSON document.** A question log and an event log are streams; a preferences file is state.

Nothing in the sources establishes a floor below which one file is correct. Four stores plus a version log plus tombstones plus a compactor is real machinery, and the source corpus is a large multi-project toolkit. On a small project, keep the separation of *questions* and collapse the *files* — the doctrine is that a record answers one question, not that a repository holds four files. *[authored: the sources do not address small projects.]*

## Record shape

What is required is the set of properties: a provenance class on every record, addressable keys, clear supersede semantics, and separation by question. The layout below is one implementation of them and not the only one — a store of one fact per file, superseded in place, satisfies the same properties with different mechanics and is a legitimate house choice. Adopt the properties; adopt the layout only where nothing already exists. *[authored: the sources describe their own layout as the answer and never address alternatives.]*

Each record carries:

- **The type** it belongs to — pattern, pitfall, preference, architecture, tool, or the equivalent set for the domain.
- **The provenance class** — observed, user-stated, inferred, cross-model. A first-class field, not metadata: promotion, decay, and the origin gate all key off it.
- **A stable key** plus the free-text insight, so the record is addressable rather than only searchable.
- **The context of capture** — timestamp, which process wrote it, branch, commit, files touched.
- **A confidence score** on a fixed scale.

Durability mechanics that go with it:

- **Append-only, one record per line.** No write-time mutation, so concurrent writers cannot corrupt a record.
- **Duplicates resolved at read time** — latest winner per key and type.
- **Tombstones for deletes.** A delete is a written record and stays recoverable.
- **A version log per key**, making any edit reversible; refuse a rollback when only one version exists.
- **An idle compactor** rewrites the files periodically, so append-only does not mean unbounded growth.
- **A tolerant parser that drops a partial trailing line on read**, so a crash mid-write cannot poison every subsequent read.

The last two items are what make the choice cheap: append-only plus a tolerant tail is a crash-safe store with no locking, and it is exactly why write-time mutation is worth avoiding.

Confidence decays for observed and inferred entries and does not decay for user-stated or cross-model ones. The rate is a chosen constant; the asymmetry is the transferable part (`SKILL.md`, `Chosen defaults`).

## Declared and inferred as two tracks

Store two independent values per dimension plus their gap. The declared track is what the user stated and is obeyed for user-driven work. The inferred track is derived from observed events and is displayed rather than acted on.

Keep the inferred track **event-sourced**: store the raw events and derive the dimension values on demand. A change to the derivation logic then needs no data migration, and any displayed value can be traced back to the events that produced it.

Do not clamp one track toward the other — the reasoning is in `SKILL.md`, under `Inferred preferences`.

## Write-side keying discipline

- **Store the deliverable, not a summary of it.** The body slot holds the actual artifact.
- **Keys are namespaced, kebab-case, and concrete.** Prefer a real project or feature name over an abstract category: an entry keyed for a specific rate-limit fix stays addressable, while one keyed as a general security label collides with everything and rots.
- **Tag twice**: one constant tag naming the *kind* of record, one tag naming its *subject*. One field then yields both a type index and a subject index, which is what makes traversal between related entries work.
- **Title with a constant prefix plus a human-readable subject**, for the same reason.
- **Cross-link only where the relationship is concrete.** Do not fabricate connections to make a graph look connected.
- **Check before creating an index node.** When enriching a write by extracting entities from the output, search for an existing node first and create a stub only when nothing matches. Keep extraction conservative — real person and organization names only, skipping product names, feature names, section headings, technical identifiers, and file paths. When in doubt, skip.
