---
name: agent-feedback-ui
description: "Collects a structured decision from a human out of band: generate a self-contained local page, spawn a one-shot HTTP server, block on a file result, then read typed data back. Covers transport, the handoff protocol, server state, page lifecycle after the server exits, and the degraded fallback. Use when the answer needs per-item ratings, notes, or visual comparison a prose prompt would flatten."
metadata:
  category: workflow
---

# Agent feedback UI

Provides the procedure for putting a structured question in front of a human when the harness's own ask-the-user channel cannot carry it — several artifacts to compare, a rating per item, a note per item, and a "none of these, try again" escape. The agent writes a self-contained page, serves it locally, opens the human's real browser at it, blocks on the filesystem, and reads back typed data instead of a paraphrase.

The hard part is not the page. The browser and the agent are two processes with no shared memory, no shared event bus, and no socket between them. Every rule below exists to make that gap survivable: the page fails loudly instead of silently when the server dies, the agent's wait is bounded instead of infinite, and a half-finished round is recoverable instead of lost.

Provenance: generalized from one production implementation — a design-mockup comparison board — and its two design notes, not from a survey, so these rules are attested once rather than across cases. Rules marked *(authored)* are not in that source, and its timing constants are unmeasured (see Timing).

## Use this skill when

- The answer is structured: a choice, plus a rating per item, plus a note per item, across several items.
- The artifact being judged is visual, or otherwise cannot survive being described in a chat transcript.
- The human needs several candidates side by side at full fidelity, not one at a time.
- One structured answer would otherwise be reconstructed by asking the same question three times in prose.
- A round may repeat: the human may reject everything and ask for a fresh set of candidates.

## Do not use this skill when

- The answer collapses to one sentence or a single choice. The native ask-the-user channel is correct and this is over-engineering.
- No browser on the human's own machine is reachable from where the agent runs — remote or sandboxed execution, CI, a headless server. Take the degraded path in step 1 instead.
- The runtime cannot background a process, read its stderr, or read and write files next to the artifact.
- The exchange is a conversation rather than a form: open-ended elicitation where the next question depends on the last answer.
- A result file already holds the answer. Re-asking is the exact failure this apparatus exists to prevent (item 9).
- Nothing downstream changes based on which answer comes back.

## Required inputs

- The question, as a fixed-shape result schema decided before the page is generated.
- The candidates to be judged, already produced and renderable with no network access.
- A writable directory for the page and its result files.
- A runtime that can background a process, capture its stderr, read and write files, and open a browser on the human's machine.
- The bound on the wait: how long the agent blocks before falling back.

## Workflow

### 1) Check preconditions, and route to the degraded path if any fail

If the server cannot start, or no browser on the human's machine is reachable: open the artifact by whatever means exist, ask through the native channel, accept prose, and proceed without structured data. The structured channel is a progressive enhancement, never a hard dependency — stalling when the port will not bind replaces a coarse answer with no answer.

Output: a decision, structured or degraded, stated before anything is spawned.

### 2) Produce the candidates

Generate strictly sequentially when the generator rate-limits (item 8). When the same deliverable must be judged by a human and built from by an agent, produce two artifacts rather than one — a rendering to judge, a structured form to build from — and let the human's pick gate production of the second (`references/review-page-contract.md`).

Output: N candidates, plus the artifact-split decision.

### 3) Generate the page, self-contained

Inline the CSS and JS, embed the images, make no external requests at all (item 10). Post to relative API paths (`./api/...`) with a protocol feature-detect, so one generated file works whether served at the root by a one-shot server or under a per-round base path by a long-lived one — reusable without regenerating it. The page constructs exactly the declared schema and nothing else. Everything the page must contain: `references/review-page-contract.md`.

Output: one page file, openable offline.

### 4) Start the server

- **Bind `127.0.0.1`, not `localhost`.** Two independent failures, both stated by the source: `localhost` can resolve to IPv6 `::1` while the listener is IPv4-only, so the browser gets connection-refused against a server that is running; and `localhost` makes the browser attach every cookie it holds for that hostname, which on a developer machine with many live sessions overflows the server's default max header size and returns HTTP 431. The exact limits belong to one runtime; the two hazards — address-family mismatch, cookie-driven header bloat — belong to every local server a real browser talks to.
- **Bind an ephemeral port** (port 0), not a fixed one.
- **Delete stale result files at startup, in code** (item 7).
- **Announce the bound port on a parseable, prefixed stderr line** — the source's form is `SERVE_STARTED: port=<port> html=<path>`, then a second line carrying the URL — **and write the same facts to a file beside the page**. The port is not optional state: without it the agent cannot push the next round to the page it opened. Stderr is a context-window artifact and a file is not. *(The port file is the source's own proposed fix for item 6; generalizing it to any agent-spawned process whose port is needed after the first turn is authored.)*

Output: the bound port, recorded on both channels.

### 5) Open the human's real browser at the served URL

Never hand over a `file://` path (item 4). Before blocking, request the URL once from the agent's own side and confirm a success status carrying the page's marker: connection-refused here is the address-family mismatch rather than a slow start, and a 431 is the cookie case. Both are invisible to an agent that skips the check and to a human who never mentions the tab that failed to load.

### 6) Block, and emit the result on every channel a caller could read

The server prints the result to stdout **and** writes it to disk, unconditionally, both always active: a foreground caller reads stdout, a backgrounded one polls the file, and the server cannot tell which it has. The general rule — when the invocation mode is not the callee's to control, emit on every channel a caller could plausibly read rather than guessing.

The agent polls for the two result filenames on a deliberately chosen interval (see Timing).

### 7) Branch on which filename appeared

| File appears | Means | The agent must |
| --- | --- | --- |
| The decided file (`feedback.json`) | Final selection | Read it, act on it, stop polling |
| The pending file (`feedback-pending.json`) | Not decided; wants another round | Read it, **delete it**, produce new candidates, post the reload, resume polling |

Deletion is not a third signal. It is the agent's consume-and-delete obligation on the pending file, so a consumed answer cannot be re-read as a fresh one on the next poll.

Where more than one page can be live at once, stamp each result with the identity of the round that produced it — round id and publish timestamp in the payload, or identity in the path. With one filename in one directory, two concurrent rounds silently overwrite each other. *(Authored generalization: the source stamps the payload and never evaluates the timestamped-filename alternative against it. The trade is "parse to disambiguate" versus "glob to find".)*

### 8) Close the round

On a decision, act on the typed fields, and do not re-ask through the native channel anything the result file already contains (item 9). On timeout, exit non-zero and fall back to step 1's degraded path rather than polling on.

Output: the decision, and what was done with it.

## Server state

Three server states, plus one transition the page infers:

- `serving` — page live and waiting; the progress endpoint returns the current value on each poll.
- Submit with the regenerate flag false → `done`: write the decided file, respond, exit zero after a short delay so the response flushes.
- Submit with the regenerate flag true → `regenerating`: write the pending file, respond, and **reset the inactivity timeout**, so the agent gets a fresh full window for the next round instead of inheriting the remainder of the human's thinking time.
- Agent posts the reload with the new page path → swap the served bytes → back to `serving`. The page's next poll sees the flip and reloads itself **in the same tab**; a new tab per round is the failure this avoids.
- Any state, on timeout expiry → exit non-zero.

"Reloading" is not a server state — it is what the page infers when its own poll flips from regenerating back to serving. The source's diagram draws four boxes; the implementation has three values and its reload handler sets `serving` directly. Four boxes describe the diagram, not the mechanism.

The reload endpoint takes a path, so validate it as one: resolve symlinks and require a regular file under an expected parent, or the endpoint reads arbitrary files. Baseline practice rather than a finding, stated because it sits on the critical path.

## Edge-case checklist

Twelve items carried from one implementation, in source order within each group. **Six are settled** — the fix is stated and shipped. **Six are hazards its authors logged and consciously did not fix**; there the fix is a proposal, verified still absent from the implementation. The second group is unfinished work to handle here, not solved problems: a checklist that presents both groups identically is worse than no checklist.

### Settled — fix shipped

- **1. Zombie form.** *What:* the page still looks interactive after the server exits; the human edits, submits, and nothing happens, silently. *Fix:* on successful submit turn the page into a read-only record — disable **all** inputs (buttons, radios, text areas, ratings, not only submit), hide the regenerate controls entirely, replace the call to action with a terminal message naming where to go next, and add a line saying how to start a fresh round.
- **2. Dead server.** *What:* the server timed out or crashed while the page was open; the POST rejects and three paragraphs of typed notes are gone. *Fix:* the POST's failure handler shows a visible error banner **and** renders the assembled payload into a selectable, copyable block, so the answer can be pasted to the agent by hand. Transport failure must never destroy human input. Highest-value item in the list: it converts total loss into a manual fallback.
- **3. Stale spinner.** *What:* the agent died mid-round, so the state the page waits on never flips and it spins forever. *Fix:* cap the page's own polling; past the cap, replace the spinner with a plain failure message plus the restart instruction, and stop polling.
- **4. `file://` handoff — the originating bug.** *What:* two failures compound. Browser-automation layers commonly refuse to navigate to `file://` on security grounds; and the OS-level "open this file" fallback opens the *human's* browser while the agent polls a *headless* browser it drives — a different process that never loaded the page, so the agent watches an empty DOM forever. *Fix:* serve the same bytes over `http://127.0.0.1:<port>/`. Both failures disappear at once.
- **8. Parallel generation against a rate-limited backend.** *What:* N concurrent generation calls return one success and N−1 aborts. *Fix:* generate strictly sequentially. Read as a sequence the lesson sharpens: the earlier document planned staggered-parallel calls with exponential backoff, the later one mandates strictly sequential after observing the aborts — the planned mitigation was tried and did not hold. Neither the stagger interval nor the rate limit it was sized against is a measurement.
- **9. Re-asking what the page answered.** *What:* the human submits a choice plus ratings plus comments as typed data, and the agent immediately asks through its native question channel which one they preferred. *Fix:* never use the native channel to re-elicit anything the result file contains; use it only to confirm the reading is correct. The doctrinal centre of the pattern — the page *is* the feedback mechanism, and a redundant question tells the human their input was not read.

### Open hazards — logged, unfixed; the fix below is a proposal

- **5. Double submit.** *What:* two POSTs can land between the state flipping to done and the process actually exiting; the handler does not check whether it is already done. Rated low risk because inputs disable on the first response, so a second click must land within about a millisecond, and both writes carry identical data. *Proposed fix:* reject a submit arriving in the done state with a 409. A sibling implementation instead serializes per-page requests behind a mutex, which prevents interleaving but still has no done-state rejection.
- **6. Lost port.** *What:* the port exists only in a stderr line, so after a context compaction the agent cannot push the next round to the page it opened and the loop cannot close. The source's #2 residual risk. *Proposed fix:* write port, pid, and page path to a file at startup — carried into step 4, because the whole regeneration loop depends on it.
- **7. Stale result files.** *What:* a pending file orphaned by a crashed prior session is found by the next session's first poll and read as this session's answer, and the agent acts on a stale decision. Unfixed because the cleanup lives in a prose instruction to the agent — "delete it after reading" — and so depends on the agent following instructions perfectly. *Proposed fix:* delete result files on server startup, in code, or timestamp the filenames. The general rule, and the sharpest one here: **a behavioral rule an agent is trained to violate must be enforced in the mechanism, not requested in prose.**
- **10. Cross-origin requests.** *What:* the server sets no CORS headers. Accepted at low risk precisely *because* the page is self-contained and makes no cross-origin requests. The rule is to avoid the case, not to configure for it: an added font, CDN script, or remote image is what breaks it — and a page with external dependencies also stops rendering once the server is gone, which is what item 1's read-only record needs it to keep doing. *Proposed fix, only if self-containment is deliberately broken:* set the headers explicitly.
- **11. Unbounded request body.** *What:* no limit on the POST body, so a multi-megabyte payload is parsed whole into memory. Theoretical while the page constructs one fixed-shape object of a few hundred bytes to a couple of kilobytes — which is what the declared schema in step 3 buys. *Proposed fix:* cap the body size.
- **12. Unguarded result write.** *What:* a full disk or read-only directory throws inside the request handler, kills the server, and leaves the page — which has no way to know — spinning forever. Rated low because the page was just written to that directory, proving it writable. *Proposed fix:* wrap the write in error handling and return a real error status, so the page falls back to item 2's copyable block. A sibling implementation ships exactly this, which confirms the hazard was real.

## Timing

Every timing constant in the source is a chosen default with no stated derivation: a page poll cap of 150 polls at 2 s (5 minutes), a 600 s server inactivity timeout, a 5 s agent poll interval, a 1 s generation stagger sized against a claimed 5–7 requests per minute. Not one is measured. Re-derive them from the round actually being run — how long the next candidate set takes to generate, how long a human takes to compare N items — or expose them as explicit inputs; do not inherit them as findings.

A backgrounded tab throttles its own timers: a browser may cut a background tab's interval to roughly once a minute, stretching a nominal five-minute cap past thirty. *(Authored fix — the source names this hazard and rates it medium, but implements nothing.)* Check a wall-clock deadline inside the tick. A tick count is not a clock.

## Decision points

| Branch | What decides it |
| --- | --- |
| Spawn a page at all, or ask in prose | Whether the answer is structured (choice + per-item ratings + per-item notes) and/or the artifact is visual (step 1). |
| Structured channel or degraded channel | Whether the server started and bound a port (step 1). |
| Sequential or parallel candidate generation | Whether the generation backend rate-limits concurrent calls; observed aborts override any planned stagger (item 8). |
| Which result file the server writes | The regenerate flag in the payload: false → decided file, true → pending file. One flag, two filenames, so the agent's next move follows from the filename alone and it never parses the payload to know what to do. |
| What the agent does after the pending file appears | The round-action field: "broaden" drives a fresh generation from the brief; "more like candidate X" drives an iteration seeded on X. |
| Reload the same page, or open a new one | Not a decision: always the same tab, driven by the page's own poll (Server state). |
| Whether to ask a follow-up at all | Whether the result file already contains the answer (item 9). |

## Output contract

- **The result file**, in the shape declared before the page was generated: a preferred selection, a ratings map, a comments map, an overall note, and the regenerate flag — plus the round-action field when regenerating.
- **What the agent reports afterwards:** which candidate was selected, which fields drove the next action, and — when the degraded path ran — that the structured channel was unavailable and the answer was taken as prose. A silent fallback leaves the human believing their ratings were read.

## Examples

**Handing over the artifact**

Wrong
```
Opened file:///home/u/.cache/rounds/42/board.html — waiting for the DOM to change.
```
The automation layer either refuses the scheme or the OS opens the human's browser while the agent watches a headless one it drives. Two processes, one of which never loaded the page; the poll never ends.

Right
```
SERVE_STARTED: port=54321 html=/home/u/.cache/rounds/42/board.html
SERVE_BROWSER_OPENED: url=http://127.0.0.1:54321
```

**The page's submit handler**

Wrong
```js
await fetch("./api/feedback", { method: "POST", body: payload });
showSpinner("Sent — return to the agent.");
```
If the server has already timed out, the request rejects, nothing visible changes, and everything the human typed is gone.

Right
```js
try {
  const res = await fetch("./api/feedback", { method: "POST", body: payload });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  showReadOnlyRecord();            // item 1: disable every input, hide regenerate, terminal message
} catch (err) {
  showErrorBanner(err);            // item 2: visible failure, never a silent one
  showCopyableBlock(payload);      // and the input survives the dead socket
}
```

## References

- `references/review-page-contract.md` — the page's own contract: artifact split by consumer, layout, the four required states, accessibility, consent.
