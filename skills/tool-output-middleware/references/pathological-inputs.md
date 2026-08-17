# Pathological-input checklist

Thirty scenarios a transformation layer between a tool and an agent's context must survive. Introduced in the source as the cases that *"turn a nice feature into a catastrophic regression if we get any of them wrong."*

Two provenance notes before using it:

- **Nothing here has been run.** The source document was tabled before implementation; the checklist is design-time analysis, not a suite that ever went green. Its value does not depend on that — a hazard enumeration is useful before any code exists — but it is not a certificate.
- **Every threshold below is a chosen constant.** Sizes, timeouts, and caps (1KB, 5s, 64MB, 1M lines, 50 calls/sec) were picked by the author and never measured against a workload. Read each as a slot for your own value, not as a validated bound. The exceptions are facts rather than choices: exit code 137 is what an OOM kill produces, and a JWT does have three base64 segments.

## The checklist

| ID | Scenario | Required behavior |
| --- | --- | --- |
| P1 | Binary garbage in output (non-UTF8 bytes) | Pass through unchanged; do not crash |
| P2 | ANSI escape explosion (10K+ codes) | Strip cleanly; do not choke the regex engine |
| P3 | Empty output (`""`) | Pass through empty; do NOT inject a header |
| P4 | Stdout and stderr interleaved | Rule matches across both streams |
| P5 | Truncated output (broken pipe mid-stream) | Do not mis-transform partial output |
| P6 | **Failed test, critical stack frame at line 4 of 200** | Must NOT filter the frame |
| P7 | Exit 0 but `ERROR:` present in output | Rule must not trust the exit code alone |
| P8 | Output contains a cloud key, bearer token, or password | Sidecar file must not be world-readable; redact in the transformed output |
| P9 | Single-line minified error (40KB on one line) | Truncate to a fixed head budget (1KB); append an explicit truncation marker |
| P10 | Unicode: emoji, RTL, combining characters, CJK | Byte-safe truncation; do not split codepoints |
| P11 | Two rules match the same call | Deterministic priority: longest command-match prefix wins; tie broken by rule ID alphabetically |
| P12 | A rule's output matches another rule's pattern | No recursive application; the layer runs once per tool call |
| P13 | Command contains embedded newlines in a quoted argument | Rule does not misparse arguments |
| P14 | Concurrent tool calls (parallel invocations) | No shared mutable state; each call is isolated |
| P15 | Layer execution exceeds its budget (5s) | Pass through raw; emit a timed-out flag in metadata |
| P16 | Model-verifier endpoint offline or rate-limited | Skip the verifier silently; use pure rule output |
| P17 | Model verifier returns a malformed response | Skip the verifier; do NOT feed the raw model response to the agent |
| P18 | Verifier response contains prompt injection (`"Ignore all prior instructions..."`) | Sanitize: append only lines present verbatim in the original raw output |
| P19 | 1M-line output | Stream-process; cap memory (64MB); truncate with a clear marker |
| P20 | Rapid-fire: 50 tool calls per second | Layer latency stays within its tail budget |
| P21 | Command with shell redirects (`cmd >file 2>&1`) | Match on the underlying command name, not the redirect wrapper |
| P22 | Deeply nested quotes and escapes in the command string | Robust argument parser; no shell injection possible |
| P23 | NULL bytes in output | Strip safely; do not truncate at the NULL |
| P24 | Process exits, then writes more to stderr | Layer receives the final combined output and handles it gracefully |
| P25 | Read-only filesystem or no sidecar write permission | Degrade gracefully; still emit transformed output; record a tee-failed flag |
| P26 | The user's rule config is malformed | Skip that rule; warn to the error stream; do not break the layer |
| P27 | Rule references a non-existent field | Ignore the unknown field; apply the rest of the rule |
| P28 | Rule regex has catastrophic backtracking | Backtracking-free engine OR a per-rule timeout |
| P29 | Exit code 137 (OOM kill) | Treat as a generic failure; preserve full output |
| P30 | Verifier returns lines NOT present in the raw output (hallucination) | Drop hallucinated lines; keep only verbatim matches |

## Rows that encode a design decision

Four rows are not edge cases at all — they are decisions that stay invisible until they bite, and they are the rows to read twice.

- **P6** is the canonical case the entire design exists to prevent, and the only correctness hazard the source rates High severity. Everything else in the layer is in service of it.
- **P7** forbids trusting the exit code as the failure signal. A zero exit with `ERROR:` in the body is common enough that a rule keyed on exit status alone will filter real diagnostics.
- **P11** forces a deterministic, documented tie-break when two rules match. Arbitrary-order matching is a reproducibility bug that surfaces only under load, and it produces defects nobody can reproduce.
- **P12** forbids recursive re-application, making the layer idempotent by construction rather than by luck. Without it, transformed output that re-matches another rule compounds the loss.

## Where the source resolved an either/or

- **P28** is stated as a choice. The source resolves it toward a per-rule abort budget (50ms, chosen) rather than a backtracking-free engine, on the grounds that it avoids a heavyweight dependency and leaves rule-author syntax unconstrained.
- **P19 and P9** are resolved together by a line-oriented streaming pipeline — read, filter, group, dedupe, ring-buffered tail truncation, write — with any single line over a size threshold truncated to a head budget with a marker. Memory is then capped regardless of total input size.

## Gating a subset

Do not gate merges on all thirty. Gate on the hazards that are both likely and catastrophic, and keep the rest as a written backlog that becomes a regression suite as real bugs arrive — a stated deferral, not an oversight.

The source's initial gate is nine rows: **P1** binary, **P3** empty, **P6** critical frame, **P8** secrets, **P15** timeout, **P18** injection, **P26** malformed config, **P28** regex DoS, **P30** hallucination. The remaining twenty-one are deferred to grow the regression series *"as real bugs hit."*

The specific nine are a judgment call for one product's risk profile. The transferable part is the shape: a small gate chosen by likelihood times severity, plus a recorded backlog, beats either gating on everything (nobody merges) or gating on nothing.

## Gap: non-line-oriented payloads

*(authored — the source never addresses this.)* Every row assumes line-oriented text. For structured payloads the analogues need restating before this checklist is usable:

- **P10 (unicode truncation)** becomes: never truncate inside an escape sequence or a multi-byte value; truncate at a structural boundary.
- **P11 (rule collision)** is unchanged, but "longest command-match prefix" needs a different tie-break for content-keyed rules.
- **P19 (huge input)** requires a streaming parser rather than a line reader; the memory cap argument survives, the mechanism does not.
- **P23 (NULL bytes)** generalizes to any byte the container format cannot represent.
- **P18 and P30 (injection, hallucination)** are the rows that transfer *worst*: whole-line set membership has no direct analogue for a tree-shaped payload. Define the unit of membership — a leaf value, a fully-qualified path plus value — before letting a model near a structured payload, or keep the model on the text rendering only.
