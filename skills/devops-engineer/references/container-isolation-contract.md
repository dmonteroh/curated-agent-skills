# Container Isolation Contract for Mutating Tools

Use this when a tool under test *changes a project* — an installer, a scaffolder, a code generator, a migration runner — and the test must exercise its real behavior without the working checkout being what it changes.

The goal is not care. It is structure: configure the runtime so that mutating anything outside a scratch area is impossible, rather than merely against the rules. A test that "should not" write to the source tree writes to it the first time an argument is wrong.

## The contract

Each line is a configuration gate, and each one closes a specific way the isolation leaks.

**Identity and provenance**

- Pin the base image by immutable digest and pin the version of the tool being installed. An unpinned base means today's pass and tomorrow's failure describe different systems.
- Run as a non-root **numeric** UID/GID. Numeric, because account names differ between distributions and a name that resolves on one image silently becomes root or a missing user on another.

**Filesystem**

- Mount the repository and the source project **read-only**.
- Copy the project into a writable scratch workspace (a memory-backed `tmpfs` mount is the usual choice) before anything mutates it. The tool then operates on a disposable copy that is discarded with the container.
- Mount that workspace `noexec`, owned by the container's UID, mode `0700` — so project data cannot be executed from the workspace and cannot be read by other users in the image. (`0700` and a numeric UID are POSIX conventions, not tuned values.)
- Relocate any executable cache the toolchain needs to a separate, executable temporary mount, so `noexec` on the workspace does not break the tool it is protecting the host from. Size that mount for the toolchain in use; there is no portable default.
- Create only the writable temporary paths the tool actually needs. Every additional writable path is a place a bug can land.

**Runtime confinement**

- `read_only` root filesystem, `no-new-privileges`, all capabilities dropped, and a finite process limit so a runaway tool cannot fork the host into the ground.

**Network and credentials**

- Default the service to **no network**. A tool that cannot reach the network cannot exfiltrate the project or pull an unpinned dependency mid-test.
- Expose network only through a **separately named opt-in service**, never through an environment variable that flips the default. A named service makes the networked run visible in the command that started it; an env var makes it invisible in every log.
- Pass no host credentials by default and mount no credential directories. If a run genuinely must inherit one, make it explicit at invocation, treat the value as inspectable for the container's lifetime, and remove that container immediately afterwards.
- Prefer authenticating *inside* the disposable session over injecting a host credential into it.

**Invocation**

- Default to a **dry run**, and allowlist the specific operation modes the harness may invoke. An open command surface is not a harness.
- Build the artifact under test from the read-only checkout with dependency lifecycle scripts disabled, unpack it inside the scratch area, and verify its identity before executing it: expected package name, expected entry-point mapping, expected manifest files present. A harness that runs whatever it finds on the path is testing the host's installed copy, not the checkout.
- Invoke through argument arrays, with shell interpolation disabled. Never build a command by interpolating a project path into a shell string — a path with a space or a quote is then an injection, and this is the failure that survives every other precaution.

## Assert the refusals

The confinement is only demonstrated by the cases the harness rejects. Positive tests prove the tool runs; negative tests prove the box holds. Assert that the harness fails, visibly and with a distinguishable error, on each of:

- an empty plan (nothing to do must not be reported as success);
- a wrong or unrecognized target;
- any write attempted outside the designated workspace path;
- a dry run that creates the target directory — a dry run that touches the filesystem is not a dry run.

A harness with no failing-case tests has not been shown to confine anything; it has been shown to work when used correctly.

## Session lifecycle

When the container is a session to be reattached to rather than a one-shot run, do not start it with an auto-remove flag: leaving the terminal must not destroy the session. Start it detached under an explicit name, reattach with an interactive exec into the workspace directory, and remove the named container and its associated resources deliberately when finished. Named cleanup — the specific container and project — rather than a blanket prune, so unrelated volumes and images survive.

## The platform boundary

A container run proves something about Linux, and nothing about anything else.

- Containers share the host's Linux kernel. macOS cannot run as a container; a macOS check has to run on a macOS host.
- Windows containers require a Windows container engine and a Windows host. A Linux runner cannot stand in.
- Platform-independent logic — the tool's own decisions, its plan output, its data contracts — is legitimately proven in a container.
- Host-specific behavior is not: filesystem path semantics and case sensitivity, command shims and executable resolution, argument quoting, line endings, permission models. Those need a native runner per operating system in the test matrix.

**This is a claim rule, not just a setup rule.** Do not report that a Linux container run validates macOS or Windows behavior. When reporting a pass, name the platform the evidence covers: "verified on Linux; macOS and Windows unverified" is an honest result, and "cross-platform tests pass" over a Linux-only matrix is not.
