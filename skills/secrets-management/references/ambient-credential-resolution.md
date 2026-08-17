# Ambient credential resolution on a developer machine

Detail behind workflow step 7. The failure this prevents: a tool installed globally is invoked inside an unrelated project, inherits that project's exported credential from the shell, and silently spends, mutates, or logs against an account nobody meant to involve. Nothing is misconfigured, nothing errors, and the only signal is on someone else's bill.

## Resolution order

| Order | Source | Signal of intent |
| --- | --- | --- |
| 1 | The tool's own config file (a path the tool owns) | Strong — someone deliberately granted this credential to this tool |
| 2 | A generic environment variable | Weak — may be exported by a project, a shell profile, a container image, or a previous `direnv` load |
| 3 | None; the caller handles setup or fallback | Explicit absence beats an accidental value |

Check the tool-owned file first. The reason is not that files are safer than environment variables, but that a tool-specific path can only have been written for this tool, while a generic variable name is shared infrastructure.

## The disambiguation check

When resolution falls through to the environment variable, compare its value against the values defined in the current working directory's dotenv files:

1. `.env`
2. An environment-suffixed variant, e.g. `.env.<environment>` for whatever environment name the runtime reports
3. `.env.local`

First match wins; report which file matched.

### Match on value, not on name

| Case | Local file defines | Env var holds | Behavior |
| --- | --- | --- | --- |
| Coincidental collision | `SERVICE_API_KEY=abc123` | `abc123` | Warn, naming the file |
| Same name, different value | `SERVICE_API_KEY=xyz789` | `abc123` | No warning — the env credential is not this project's |
| Name absent locally | *(not defined)* | `abc123` | No warning |

Name-based matching would fire on every project that happens to use the same conventional variable name, which is most of them. A check that fires constantly is a check users learn to scroll past, and it will be scrolled past on the run that mattered.

### Parse tolerantly before comparing

Dotenv files in the wild are not uniform. Normalize before the equality test:

```
export SERVICE_API_KEY="abc123"     # leading `export`, double quotes
  SERVICE_API_KEY = 'abc123'        # surrounding whitespace, single quotes
SERVICE_API_KEY=abc123              # bare
```

All three define the same value. Strip an optional leading `export`, trim whitespace around name and value, and unwrap a single matched pair of single or double quotes. A parser that only handles the bare form silently reports "no match" on the quoted cases — a false negative in a check whose entire job is catching a collision.

## Warn, do not block

The tool cannot know whether using this project's credential was intended. Blocking breaks legitimate workflows; proceeding silently is the failure being fixed. Warn, name the matched file, state the concrete consequence in the user's terms — that this run may bill or mutate that project's account — and continue.

## Source disclosure without value disclosure

Every code path that reports where a credential came from prints a source label: a file path, a config label, or the variable name plus the dotenv file whose value it matched. No path prints the credential.

Falsifiable check: a test that captures the message, asserts it contains the expected source label, and asserts it does **not** contain the key's value. The negative assertion is the one that matters; without it, an implementation that helpfully echoes a "truncated" key still passes.

## Owner-only permissions at creation time

When the tool persists a resolved credential, create the file with owner-only permissions (`0600`) in the same call that creates it. Do not write under the ambient umask and tighten afterward: between those two operations the file exists at whatever the umask allowed, readable by group or world on a permissive umask, and any process on the machine can open it in that window (CWE-377 insecure temporary file, CWE-367 time-of-check/time-of-use).

Falsifiable check: a test that sets a deliberately permissive umask (`0o000`), saves a key, and asserts the resulting file mode is owner-only. Be honest about what that proves — a write-then-chmod implementation also ends owner-only, so a test reading only the final mode passes either way and certifies nothing. Close the gap in the implementation instead of the test: pass the mode to the call that creates the file, so no other mode is reachable and the window cannot exist.
