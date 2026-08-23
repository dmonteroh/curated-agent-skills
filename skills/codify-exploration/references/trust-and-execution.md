# Trust and execution boundaries for a codified unit

Depth behind the two rulings in the skill's Constraints section. They are separate rulings with separate reasoning and separate failure modes, and merging them produces a claim neither source makes.

## Ruling 1 — agent-authored code never runs inside the host process

The original design had the agent author code that the long-lived host process would then evaluate in place. An outside review blocked it, naming three escape routes that no amount of pre-cleaning closes:

- **Ambient globals.** Code evaluated inside the host inherits whatever the host's own global scope holds — clients, credentials in memory, open handles, module caches. Nothing was passed to it; it simply reaches.
- **Constructor gadgets.** Given any object the host hands in, the code can walk to that object's constructor and from there back to constructs the host never intended to expose. Restricting the surface that is passed in does not restrict what is reachable from it.
- **A time-of-check gap between approval and execution.** Deferred or asynchronous top-level execution lets code do something other than what a human read and approved. The text approved and the behavior executed are two different things separated by a window.

The correct in-process answer is out-of-process worker isolation with capability-passing IPC — a project expensive enough that the source records it as one that "may never ship". The cheap and complete alternative is to never be in-process at all: the unit runs as an ordinary standalone process and talks to the service over the same interface any third-party client would use. The host never imports and never evaluates unit code.

The structural benefit is larger than the isolation itself: because the unit is an ordinary client, it earns no privilege from proximity. Anything it is allowed to do, an arbitrary external client would also be allowed to do — which means the permission question has exactly one answer to maintain.

## Ruling 2 — an environment scrub is hygiene, not a sandbox

This ruling is about naming, and it applies to the out-of-process design that replaced the one above. Calling an environment scrub a sandbox was the error the "security theater" verdict named. The revised statement is the honest one: best-effort hygiene plus defense in depth, with the real boundary elsewhere.

Two axes, orthogonal, both declared in the unit's contract:

| Axis | Mechanism | Default |
| --- | --- | --- |
| Service-side capability | A scoped credential minted per spawn, bound to the non-administrative verb surface, encoding the unit name and spawn identity, and revoked when the spawn exits. Administrative verbs — arbitrary code evaluation, cookie and storage access — are excluded from the scope, so a unit that calls one is refused by the service even though the client library exposes the method. | Always scoped. Never the service's root credential. |
| Process-side environment | Trusted units receive the parent environment minus the root credential. Untrusted units — the default — receive a minimal allowlist (locale, terminal, timezone, a fixed search path) with secret-shaped keys stripped by pattern. | Untrusted. Trust is opted into, per unit, in writing. |

Two mechanics worth keeping:

- **Injection order.** Capability variables are injected last, so a parent process cannot pre-set them in the environment and have the child pick up the parent's values instead.
- **A declared field, not an implementation detail.** Because trusted-versus-untrusted is a contract field rather than a property of the spawning code, real OS-level isolation can be installed behind it later without redesigning anything above it.

What the scoped credential closes: the service refuses out-of-scope calls, and refusal happens on the side that owns the resource.

What the environment scrub does **not** close: a runtime with no filesystem sandbox lets an untrusted unit import a file-access module and read anything the operating-system user can read — private keys included. Removing secrets from the environment does not touch that.

The generalization worth carrying: **enforcement belongs to the side that owns the resource.** A check the spawned process is asked to perform on itself is advisory, because the process can decline to perform it. A check the service performs before serving is enforceable. Anything described as a boundary that lives inside the untrusted process is a name applied to a preference.

## Output protocol

A codified unit is called by programs, so it behaves like a program:

- Structured result on stdout, one document, nothing else on that stream.
- Logs and progress on stderr.
- Success or failure in the exit code.
- A per-run timeout, overridable per invocation, so a hung acquisition is distinguishable from a slow one.
- A maximum stdout size; exceeding it truncates and exits non-zero rather than emitting a partial document that parses as a smaller valid result.

The source's defaults are 60 seconds and 1 MB. Their stated justification is that they match widespread CLI conventions — they are chosen defaults, not measurements, and re-stating them as thresholds a project must adopt would be laundering. Choose values the consuming environment justifies; keep the two limits, and keep the non-zero exit on truncation.
