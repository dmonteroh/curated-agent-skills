# Claim Sets

Companion to the `Claim Sets` section of `SKILL.md`. That section states the rules; this file enumerates the surfaces a task can write, gives the worked contrast behind each rule, and carries the check the controller runs over the board before any concurrent dispatch.

## Write surfaces to enumerate

Walk this list once per task and record what the task writes on each line. A dimension the task does not touch is recorded as `none`, never left blank: an unanswered dimension and an empty one look identical on the board an hour later, and only one of them is safe.

| Surface | What to name | Two tasks collide when |
| --- | --- | --- |
| Files and directories | paths the task may create or modify | they name the same path, or one names a directory containing the other's file |
| Databases and schemas | the instance and schema the task writes | both write the same instance, even through different tables |
| Tables, collections, indexes | the specific relations written | both write one relation, or one reads what the other rewrites |
| Migrations | the migration sequence the task appends to | both append to one sequence — the second one's baseline is whatever the first left |
| Long-lived services and daemons | servers, watchers, workers the task starts or restarts | both bind or restart the same service |
| Deploy targets and environments | the environment the task publishes to | both publish to one environment, in any order |
| Network ports and sockets | ports the task binds, including test harness defaults | both bind one port, usually a default neither task named |
| Caches, queues, message topics | what the task fills, invalidates, or drains | one drains or invalidates what the other depends on |
| Shared datasets and fixtures | seed data, fixtures, golden files the task regenerates | both regenerate one dataset, or one asserts against what the other rewrites |

Disjointness holds only when it holds on every line at once. Two tasks with perfectly disjoint file claims that both run a migration against the same database are not concurrency-safe, and a partition checked on paths alone will clear them.

## Rules the dimension list does not state

**The never-parallel class.** One class is not admitted to concurrency at all, whatever the disjointness check says: destructive commands, schema migrations, two tasks writing the same table, and anything customer-visible in production. For these the test is not overlap but an explicit human decision taken before the task runs. Gate them by ordering — run the gated task alone, record the decision on the board beside it, dispatch the rest around it.

**Re-deriving the partition mid-flight.** When a running task discovers something that invalidates the plan — a surface nobody claimed, a dependency nobody saw, a root cause shared with another domain — pause the tasks that depend on it and re-derive the partition before continuing. Letting the fan-out finish against a stale partition is the expensive option: those workers complete successfully against acceptance criteria that stopped being the right ones, so the loss is invisible in their reports and surfaces at integration.

**Contract artifacts are a third ownership class.** Where two tasks meet, the controller writes the boundary first — data shape, call signature, request/response or event payload, the schema of a file both sides read — owns it, and puts it in every affected packet as read-first and forbidden to modify. Changing it re-issues the affected packets and is never a worker edit; a worker that believes the contract is wrong returns `QUESTIONS` and stops. Without one, the mismatch surfaces only at the integration gate, after both sides have been written against different assumptions.

**Aggregator files leak out of any partition.** Files whose content is a list of their siblings are touched by every worker however clean the domain split is, because adding anything requires registering it. Give each a single owner, or exclude it from every claim set and put the controller's registration pass on the board as a step after integration. When a partition that looked disjoint conflicts anyway, look here first.

**Stub to unblock.** When one task is gated on another's output, hand the blocked worker a stub shaped by the contract artifact and inside its own claim set, so it proceeds against a real boundary, then replace it at integration. Record the stub on the board against what it stands in for; a stub nobody recorded ships.

## Examples

Each pair is the same partition planned badly and well. The wrong version is the one a controller reaches for by default, which is why it is written out.

**Disjoint files, one database**

- Wrong: two tasks touch entirely separate directories, so they are dispatched concurrently. Both add a migration. They apply in whichever order the runtime happens to produce, each computed against a baseline the other has already moved, and the resulting schema matches neither task's expectation. Every file claim was honored.
- Right: name the database and its migration sequence as claimed surfaces. The tasks are not disjoint, so they do not run concurrently: order them, run the migration-bearing one alone, and dispatch the rest against the schema it leaves.

**The port nobody claimed**

- Wrong: two tasks each start the project's test harness, which binds its default port. The second dispatch either fails to bind or silently attaches to the first task's process and reports the first task's results. The failure surfaces as a flaky test, which is where the controller spends the next hour.
- Right: treat bound ports as a claimed surface. Assign a distinct port per concurrent task and write it into the packet, or keep the harness runs serial.

**The never-parallel class**

- Wrong: a fan-out of four code tasks plus "apply the migration to the shared environment", admitted because its file claim is disjoint from all four. Disjointness was the wrong test: the task is irreversible and visible to everyone using that environment.
- Right: hold it out of the concurrent set, run it alone behind an explicit human decision, and record that decision on the board beside the task. Whether it runs before or after the fan-out is itself part of the decision.

**Contract artifact — the boundary written last**

- Wrong: one task produces a record and another consumes it. Each is given a clean, disjoint claim set and left to define the shape it needs. Both finish, both pass their own checks, and integration finds one side emitting a field the other never reads. The claim sets were never violated; the outputs simply do not compose.
- Right: the controller writes the boundary first — the record's shape, the call signature, the event payload, the schema of the file both sides read — owns it, and hands it to both packets as read-first and forbidden to modify. Each worker implements against it. If a worker believes the contract is wrong, it returns `QUESTIONS`; changing the contract re-issues the affected packets.

**Aggregator file — the leak in a clean partition**

- Wrong: three tasks own three separate modules, and each registers its new module in the shared index that enumerates them. The partition is disjoint by domain and conflicting by line, and the conflict appears at integration in the one file nobody assigned.
- Right: either give the index a single owner, or exclude it from every claim set and put "controller applies the registrations" on the board as a step after integration. The same holds for route tables, dependency-injection containers, migration indexes, plugin registries, test-suite manifests, package init files, and lockfiles — anything whose content is a list of its siblings.

**Stub to unblock**

- Wrong: task B cannot finish until task A's component exists, so the controller either serializes the whole fan-out behind A or lets B invent the interface it wants.
- Right: hand B a stub of the missing dependency, shaped by the contract artifact and inside B's own claim set, so B proceeds against a real boundary. Record the stub on the board with the implementation it stands in for, and replace it at integration. A stub that nobody recorded ships.

**The partition that went stale**

- Wrong: a running task discovers the failure it was given is actually in a shared client two other tasks also depend on. The controller notes it and lets the fan-out finish, because the other workers are already running. Two of them complete against acceptance criteria that stopped being the right ones when the discovery landed.
- Right: pause the tasks that depend on the discovery, re-derive the partition, and re-issue the packets whose scope changed. Re-deriving costs the work already done on those tasks; not re-deriving costs it too, later, plus the integration that has to be unpicked.

## Pre-dispatch claim-set check

Run over the board before any concurrent dispatch. Each line has an artifact behind it — an enumeration, an owner, a recorded decision — and a board that cannot produce one is not ready.

- [ ] Every task's write surfaces enumerated across all dimensions above, with `none` written where the task writes nothing.
- [ ] Pairwise disjointness confirmed over that enumeration, not over file paths alone, for every pair that will run concurrently.
- [ ] Any task in the never-parallel class held out of the concurrent set, with its human gate recorded on the board.
- [ ] A contract artifact exists for every boundary two tasks meet at, written by the controller before dispatch, and listed read-first and forbidden in each affected packet.
- [ ] Aggregator files either assigned a single owner or excluded from all claim sets, with the controller's post-integration registration step on the board.
- [ ] Every stub handed out to unblock a task recorded on the board against the implementation it stands in for.
- [ ] `depends_on` recorded for every task that cannot integrate before another, and a rollback plan for every task whose integration is not trivially revertible.
- [ ] Long-running processes a task is authorised to start named in its packet, with who stops them before the barrier.

## Decision points

- If two tasks cannot be made disjoint on every surface, collapse them into one task or run them in sequence. Do not run them concurrently and reconcile afterwards: the surfaces that collide are the ones a merge cannot arbitrate.
- If the contract at a boundary cannot be written before dispatch because the boundary is genuinely unknown, the domains are not independent yet. Run a single-worker investigation first and partition after it.
- If the only way to keep a task in the concurrent set is to let it write an aggregator file, take it out of the set.
- If a running task invalidates the partition, a re-derived partition is a new board: packets whose scope changed are re-issued, not amended by a message to a worker that is already running.
- If a gated task in the never-parallel class has no human available to gate it, the orchestration stops there rather than proceeding with the ungated tasks and leaving it for later.
