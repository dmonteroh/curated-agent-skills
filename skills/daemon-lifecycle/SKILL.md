---
name: daemon-lifecycle
description: "Adds a safe, supervisor-free singleton background daemon to a CLI tool: atomic state-file writes, an exclusive spawn lock with stale-holder reclaim, identity-verified process signaling, health-gated attach-vs-spawn decisions, and idle self-shutdown. Use when a CLI needs a persistent background process with no systemd, launchd, or container orchestrator supervising it, or when an existing one spawns duplicates, leaks processes, or has killed the wrong one."
metadata:
  category: workflow
---

# Daemon Lifecycle

Provides a language-agnostic procedure for giving a CLI tool a singleton background daemon that manages its own lifecycle without an external supervisor: state discovery, a spawn-race guard, attach-vs-spawn decisions, identity-verified process signaling, and self-directed idle shutdown. The procedure is implementable in any language with a filesystem, OS process signals, and a way to read another process's command line (Python, Go, Rust, and others all qualify).

## Use this skill when

- Adding a "server mode," "daemon mode," or persistent background process to a CLI tool that has no systemd, launchd, or container orchestrator managing it.
- The background process must be discoverable and reusable across separate, independent CLI invocations — to avoid repeated cold-start cost, hold state in memory, or serve a local UI.
- Debugging an existing background-daemon setup that spawns duplicates under concurrent use, leaks orphaned processes, or has been reported to signal or kill a process it shouldn't have.
- Implementing graceful shutdown, idle timeout, or process-signal handling for a long-running background worker a CLI starts and later needs to stop.

## Do not use this skill when

- The process is supervised externally (systemd, launchd, a container orchestrator, a process manager). Let the supervisor own restart policy, health monitoring, and shutdown; this skill's coordination primitives — lock files, state files, self-directed idle shutdown — duplicate what a real supervisor already does, and layering both creates two sources of truth for the same lifecycle.
- The task is CLI surface design with no background process involved: subcommands, flags, config precedence, interactive prompts, progress indicators, shell completions. That is a distinct problem — this skill starts where a persistent, unsupervised process enters the picture, not before.
- A single short-lived subprocess is spawned, awaited, and exits within one CLI invocation. No persistence across invocations means no discovery, attach, or lock problem exists — just run it and handle its exit code.
- The work is the application logic served over the daemon's own endpoints — business handlers, per-resource eviction policy, endpoint-specific concurrency control. That is the application riding on top of the daemon, not the daemon's own lifecycle.
- Production service orchestration at fleet or cluster scale — health checks across many replicas, load balancing, rolling deploys. This skill is scoped to one unsupervised background process on one machine, not a distributed system.

## Required inputs

- Target language/runtime and every OS platform the daemon must run on (see Platform scope — identity verification is not implementation-neutral across platforms).
- Where the state file and lock file may live: an env/config override path, a project-relative default, a cwd-relative fallback, and confirmation the filesystem backing them supports atomic rename and exclusive-create (a networked or non-POSIX filesystem can break both guarantees).
- What counts as "undrainable in-memory work" for this daemon — needed to decide the refuse-to-kill and idle-extension branches.
- What counts as a state-changing request versus passive polling — needed to decide what resets the idle timer.

## Workflow

### 1. Persist a state record atomically

Bind the daemon's listener first; only then write a small state record (PID, address, start time, version, and an identity marker — see step 4) to a well-known, discoverable path. That record is the only channel a later CLI invocation has for learning whether a daemon exists and how to reach it.

- Write atomically: write to a temp file in the same directory, then rename it over the real path. Rename is atomic on POSIX filesystems, so a concurrent reader always sees either the fully-old or fully-new record, never a torn write. Give the temp file a name that embeds the writer's own PID plus a random component so concurrent writers can't collide on the same temp path.
- Resolve the state-file path in a fixed, overridable order: an explicit environment/config override first, then a project-relative default, then a cwd-relative fallback.
- Restrict the file's permissions on write when it can carry locally-sensitive material (an address, a marker string).
- Read defensively: treat a missing or unparseable state file as "no daemon known," not an error. A read or parse failure returns null/None; it never throws.

### 2. Never trust the state file alone — confirm liveness over the network

A state file is a claim, not proof: the daemon may have crashed without cleanup, or its PID may since have been reused by an unrelated process. Before treating a state file as evidence of a live, usable daemon, call the daemon's own health endpoint, with a short, bounded timeout so an unreachable daemon fails fast rather than hanging the calling invocation.

The health response must carry what the caller needs for its next decision: a version identifier, to detect drift between the caller and the running daemon, and a signal for whether the daemon currently holds undrainable in-memory work, needed for the refuse-to-kill and idle-extension decisions below.

### 3. Exclusive spawn lock: stale-holder reclaim, then re-read under the lock

Before spawning, acquire an exclusive, filesystem-based lock so two concurrent invocations cannot both decide to spawn.

- Acquire via an atomic create-exclusive open (`O_CREAT | O_EXCL`, or your language's equivalent exclusive-create call) — a single atomic filesystem operation, so exactly one of any number of racing callers succeeds. The winner writes its own PID into the lock file.
- On failure to acquire, first ask if the holder is still alive: read the PID recorded in the lock file and liveness-check it (step 4's liveness check). If dead, the lock is stale — unlink it and retry acquisition once. If alive, the lock is genuinely held; wait, don't force through.
- A caller that loses the race polls, it does not fail: re-read the state file and re-run the health check on a fixed interval up to a bounded timeout, attaching as soon as the winner's daemon becomes healthy. Only past the timeout does it give up with an error.
- **Re-read the state file after acquiring the lock, before spawning.** Between a caller's first, unlocked state check and its lock acquisition, another process may already have finished spawning. Re-checking state and health from inside the lock closes this window — only spawn if the re-read still shows no usable daemon. This is the step that makes the lock race-safe rather than merely race-reduced.
- Release the lock in a `finally`/`defer`-equivalent block regardless of whether spawning succeeded, so a spawn failure never leaves the lock permanently held.

### 4. Verify identity before ever signaling a PID recovered from a state file

This is the load-bearing safety property, and the order is fixed: **liveness check → identity check → signal.** Never signal-then-check — a signal delivered to the wrong process cannot be undone.

1. Reject an obviously invalid PID (`<= 0`) outright.
2. Check liveness with a zero/no-op signal — an existence probe with no side effect on the target. Permission-denied still counts as "alive": the process exists, the caller just can't touch it. No-such-process means it's already gone; there is nothing left to protect against.
3. Read the live process's own command line and check it for a distinctive marker string embedded in the daemon's spawn arguments at launch time. Absence of the marker means the PID exists but is not the process the state file thinks it is — almost certainly the original daemon exited and the OS reassigned its PID to something unrelated. Log the mismatch and return without signaling anything.
4. Only once identity is confirmed does the first signal (graceful terminate) go out.
5. Wait a bounded grace period, polling liveness.
6. If still alive at the deadline, **re-verify identity a second time** before escalating to a forceful kill. A second PID-reuse window can open during the wait itself, if the original process happened to exit and something else claimed the PID while the caller was waiting.

**Why:** a PID recovered from a state file is a claim about the past, not evidence about the present. Skip the identity check and signal on liveness alone, and a daemon that already exited cleanly — with its PID since reused by an unrelated process — gets that unrelated process killed instead. This is the rule this skill treats as non-negotiable, and it should be verified the same way: by a test that plants a state file whose PID field points at a real, currently-alive, unrelated process, then runs the full attach/spawn flow against it and asserts that process is still alive afterward while a fresh daemon spawned on a different PID. That is an authored testing recommendation, not something to skip — a mocked identity check proves the function returns the right boolean; only a real, live, unrelated PID proves the property that matters, which is that nothing gets signaled.

How the marker gets there: pass it as a literal argument in the daemon's own spawn command at launch. No IPC or shared secret is needed — a process's command-line arguments are visible to anything with permission to inspect that process, which is exactly the visibility this check requires and nothing more.

A residual risk remains even with this check: a race window still exists in principle between "identity confirmed" and "signal delivered," where the verified process could exit and its PID be reassigned inside that (very small) window. Treat this as an accepted residual risk unless the target platform offers a stronger primitive that binds the signal to the exact process instance rather than to its PID.

### 5. Attach-vs-spawn decision

Given a state file, in order:

- No state file → go straight to the locked spawn path (step 3).
- State present, health check succeeds, versions match → attach; done, no signaling of any kind.
- State present, health check succeeds, versions differ, daemon reports undrainable work → **refuse.** Do not attempt any shutdown or signal. Surface what's blocking and how to override, and exit with a distinct non-zero code so a wrapping script can tell "refused, action needed" apart from a bare crash.
- State present, health check succeeds, versions differ, daemon reports no undrainable work → attempt a graceful shutdown over the daemon's own control channel first (bounded timeout; failure here is expected and non-fatal, it just means the process wasn't reachable that way — fall through to the next step); then run the identity-verified kill from step 4; then the locked spawn path.
- State present, health check fails (unresponsive) → the daemon crashed without cleanup, or the record is stale for some other reason. Skip the graceful-shutdown attempt, since it would just time out again, and go straight to the identity-verified kill, then the locked spawn path.

Refuse to evict a running singleton whenever it holds undrainable state, regardless of what triggered the eviction attempt — version drift, an operator's restart request, or anything else. The check protects the state, not the reason eviction was requested. This is stated here as the general rule the pattern implies; the case actually built and exercised is version-drift-on-attach specifically, so treat other triggers as covered by the same rule, not as independently proven.

### 6. Idle self-shutdown that ignores passive observation

Nothing external supervises the daemon, so it must decide on its own when to exit — but it must not confuse "someone is watching it" with "someone is using it."

- Track one "last meaningful activity" timestamp, separate from any per-resource bookkeeping. Only state-changing requests reset it. Read-only or status-polling requests must not reset it — this is a deliberate guard against idle-immortality, not an oversight to fix later.
- On a fixed check interval, if idle time exceeds the idle threshold: shut down if the daemon holds no undrainable work; if it does, extend the idle deadline by a fixed increment rather than killing immediately or running forever, up to a bounded number of extensions, after which it force-shuts-down regardless of in-progress work.
- Make shutdown idempotent — a termination signal and an idle-timeout can race, so guard against double-running. Stop accepting new work, remove the state file, and only then exit. Removing the state file before exit matters: a caller polling "is it gone yet" via the state file should never see a ghost record outlive the process it described.
- Route termination signals and uncaught exceptions through this same graceful path, rather than letting default runtime handling skip state-file cleanup.

### 7. Surface spawn failures, don't swallow them

Redirect the newly spawned process's output to a log file truncated at the start of this spawn attempt, so a later read reflects only the current attempt, not a stale prior one. Poll for a definite "started" signal — state file present and health check passing — up to a timeout. On timeout, read the log back and include its contents directly in the failure the caller sees, rather than reporting a bare "failed to start." A daemon that fails to start for a real reason (bad config, port conflict, an init-time crash) should never look identical, from the caller's side, to one that simply took too long.

## Decision points

| Point | Branches on |
|---|---|
| Attach vs. spawn | Does a state file exist, and does its target pass a health check? |
| Respawn vs. refuse on version drift | Does the running instance report undrainable work? |
| Graceful shutdown attempt vs. skip to signal | Is the daemon reachable (health check passed) or already unresponsive? |
| Wait-and-poll vs. spawn | Did this caller win the exclusive lock? |
| Attach vs. still spawn, post-lock | Does the re-read under the lock show a racing winner already finished? |
| Signal vs. refuse to signal | Does the live process's command line contain the expected identity marker? |
| Escalate to forceful kill vs. stop | Is the process still alive *and* still identity-verified after the grace wait? |
| Idle: shut down vs. extend vs. force-shutdown | Idle past threshold? Undrainable work present? Extensions already exhausted? |
| Lock: fail vs. reclaim | Is the recorded lock-holder PID still alive? |

## Platform scope

The identity check in step 4 depends on reading a live process's own command line, and that operation has no universal cross-platform implementation:

- Linux and macOS both expose a process's command-line arguments to anything with permission to inspect the process (for example, the `/proc/<pid>/cmdline` file on Linux, or a process-information API on macOS).
- On a platform with no real implementation of that read, the identity check always returns "no match," which fails closed, not open: it will never signal an unverified PID. That is safe, but it is not equivalent to support — it also means the daemon's stale-PID reclaim and crash-recovery paths silently stop working on that platform, because nothing there can ever be positively identified and reclaimed by signal.

Do not ship silent degradation as though it were parity with the supported platforms. Before targeting a platform outside Linux and macOS, either implement a real per-platform command-line or process-image query for step 4, or state explicitly in the implementation and its documentation that signal-based reclaim is unavailable there, and define the operator-facing fallback (a documented manual-cleanup procedure, a different eviction mechanism, or an explicit unsupported-platform error at startup). This platform-gap response is authored guidance to close a gap, not a pattern the source material itself implements for non-Linux/macOS targets.

## Common pitfalls

- Signaling an unrelated process because a stale state file's PID was reused by the OS — prevented only by the identity check (step 4); treat any implementation that signals on liveness alone as unsafe by construction.
- Duplicate daemons from a concurrent-launch race — prevented by the exclusive spawn lock (step 3).
- A daemon spawned between a caller's first check and its lock acquisition getting spawned over again — prevented specifically by the re-read-under-lock step, not by the lock alone.
- Permanent deadlock from a crashed lock-holder that never releases its lock — prevented by the stale-lock liveness check and reclaim (step 3).
- Silent loss of in-memory session state from auto-restarting or auto-killing a busy instance without checking — prevented by the refuse-to-kill branch (step 5).
- A daemon that never exits because status polling looks like use — prevented by the meaningful-activity/passive-polling distinction (step 6).
- A daemon that exits mid-task because a naive idle timer doesn't know work is in flight — prevented by the extension-with-hard-ceiling mechanism (step 6).
- A reader observing a half-written state file during a crash or a concurrent write — prevented by write-temp-then-rename (step 1).
- A spawn failure that looks identical to "still starting" from the caller's side — prevented by surfacing the startup log on timeout (step 7).

## Examples

**Wrong: signal on liveness alone**

```
pid = read_state_file().pid
if is_alive(pid):
    send_signal(pid, SIGTERM)   # no identity check
```

If the daemon at `pid` already exited and the OS reassigned that PID to an unrelated process, this sends `SIGTERM` to whatever now holds the PID — not to the daemon.

**Right: identity-verified signal**

```
pid = read_state_file().pid
if pid <= 0:
    return
if not is_alive(pid):
    return                          # nothing to protect against
if not cmdline_contains_marker(pid, DAEMON_MARKER):
    log("pid reused, not signaling"); return
send_signal(pid, SIGTERM)
wait_for_exit(timeout)
if still_alive(pid) and cmdline_contains_marker(pid, DAEMON_MARKER):
    send_signal(pid, SIGKILL)
```

The only difference is the marker check gating every signal call — but it is the difference between a daemon manager and a process manager that occasionally kills the wrong thing.

## Output contract

When this procedure is applied to a concrete implementation task, report:

- State-file and lock-file layout: fields carried, path-resolution order, permission mode.
- The spawn-lock mechanism and its stale-holder reclaim condition.
- The attach-vs-spawn decision table as implemented, mirroring step 5.
- The identity-verification mechanism chosen per target platform, and which platforms it does not cover.
- The shutdown escalation sequence and the exact refuse-to-kill condition.
- The idle-shutdown activity classification (what counts as state-changing vs. passive) and the extension/hard-ceiling policy.
- Test coverage confirming: concurrent spawn attempts converge on exactly one daemon; a state file pointing at a live, unrelated PID is never signaled; idle timeout fires under passive-only polling and does not fire while state-changing activity continues.
