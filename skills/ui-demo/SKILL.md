---
name: ui-demo
description: "Produces a walkthrough recording of a running web application through a fixed discover, rehearse, record sequence, with a rehearsal gate that blocks recording until every selector resolves. Use when a demo video, screen recording, walkthrough or tutorial capture is requested; not for checking whether the UI is correct."
metadata:
  category: docs
---
# UI Demo

Provides a procedure for recording a walkthrough video of a running web application: find out what is actually on the page, prove every interaction resolves before spending a take, then record at a pace a human viewer can follow. Produces one video file at an agreed path, plus the field map and rehearsal result that make the recording reproducible.

## Use this skill when

- A demo video, screen recording, walkthrough, or tutorial capture of a web application is requested
- A feature or workflow has to be shown moving — for documentation, onboarding, a release note, or a stakeholder presentation
- An existing recording has to be re-shot because the interface changed underneath it
- A recording keeps breaking partway through and the cause has not been isolated

## Do not use this skill when

- **Judging whether a UI change is correct.** Deciding that a rendered page meets its criteria is verification against explicit criteria, from static evidence — a different job with a different input. It is also a boundary this skill must not cross in the other direction: **a demo recording is inadmissible as verification evidence**, because it carries an injected cursor, a subtitle bar and deliberate pacing pauses, every one of which contaminates the rendering that a verification pass exists to judge.
- **Exercising the application to find out whether it works** — clicking through flows to check behaviour, watching the console and network, asserting on outcomes. The rehearsal phase below resembles that and is not it: it asserts that elements resolve, never that anything behaved correctly. Functional verification is a separate job, and running it here under cover of a rehearsal is the failure this boundary exists to prevent.
- **Running an accessibility scanner, or producing accessibility findings**, over the page being recorded. Nothing in this procedure reads the accessibility tree, and a recording is not an audit.
- Static screenshots are what is wanted, for a review or a pull request. No video, no pacing, no overlays.
- Designing, specifying, or building the interface being recorded. This procedure records a build that already exists and never proposes a change to it.
- The surface is not a browser page — a terminal session, a native desktop or mobile application, a hardware device. Every step below rests on enumerating page elements and resolving selectors, and none of it degrades to those surfaces.

## Required inputs

- A URL for a running build, plus credentials if the flow starts behind a sign-in
- The flow to show, in the order it should appear; or the feature and the audience, if the order is open
- Where the video will be played — a docs page, an onboarding course, a release note, a live presentation. This sets pacing more than any other input.
- The output path and filename
- Any state the flow depends on: seeded records, a specific account, a feature flag
- A browser-automation driver with the capabilities below

## Driver capabilities

The procedure needs a driver that can do four things:

- record the session to a video file at a fixed viewport size
- move the pointer to a coordinate in visible increments, not only dispatch a click at a target
- enter text one character at a time, not only set a field's value
- evaluate script inside the page, to enumerate elements and to inject the cursor and subtitle overlays

Check all four before phase 1. If one is missing, say which, and say what the recording will lack, before recording rather than after. A driver that cannot move the pointer visibly produces a video in which effects have no visible cause; that is a limitation to disclose, not one to paper over with faster pacing.

## Workflow

Three phases in a fixed order — Discover, Rehearse, Record. Phase 2 is a gate rather than a checkpoint: a failed rehearsal stops the run. Going straight to recording is the single most reliable way to spend a take on a script that was never going to work.

### Phase 1 — Discover

Open each page in the intended flow and enumerate every visible interactive element, capturing per element: tag, input type, name attribute, placeholder, visible text, ARIA role, and whether it is contenteditable. For every native select, capture each option's value alongside its text.

Then resolve these ambiguities. Each one silently breaks a recording that assumed otherwise:

- **Native select, or a custom combobox** built from generic elements. The two need different interactions, and only one of them opens a visible dropdown.
- **Placeholder options that look real.** An option whose text starts with "Select" or whose value is `0` or empty is not a choice — it is the unset state wearing an option's clothes. Picking it submits the form with the field unset.
- **Rich text affordances.** Does a text surface support mentions, tags, markdown, or emoji? If it does, typing the trigger character opens an autocomplete that swallows the characters after it.
- **Which fields block submission.** Try submitting empty and read the validation, rather than trusting the asterisks in the labels.
- **Fields that appear only after other fields are filled.** A selector for one of these resolves on the second visit and not the first.
- **Exact button label text**, character for character. "Submit" and "Submit request" are different buttons to a selector.
- **In a table-driven form, which column header owns each numeric input.** Numeric inputs are interchangeable to a selector and are not interchangeable to the product.

Output: a field map per page. No script is written before it exists.

```text
/settings/team (page 1)
  - Role: native select, 4 options, first is "Select a role" with value 0 -> skip it
  - Start date: input type=date
  - Notes: textarea, not an input
  - Invite: button, label is "Send invite", not "Invite"

/settings/team/<id> (page 2)
  - Comment: input, placeholder "Type a message...", supports @mentions -> typing "@" opens a popup
  - Send: button, label "Send", disabled until the comment field has content
```

### Phase 2 — Rehearse

Run the whole flow with recording disabled.

- Every element lookup goes through one wrapper with a fixed contract: on success it logs the step's label; on failure it logs the label, the selector it tried, **and a dump of every visible interactive element on the page**, then marks the run failed. The dump is the load-bearing part — a rehearsal failure has to be diagnosable from its own output, without a second run to go and look.
- The run ends in one binary result. Recording does not begin on a failure. This is the check that can fail: a rehearsal that cannot report a failure is not a gate.
- On failure: read the element dump, choose the correct selector, update the script, re-run. Repeat until every step passes. Do not narrow the flow to get past a step — a skipped step is a hole in the video, not a fix.

What a passing rehearsal establishes: every element the script will touch is present and visible. What it does not establish: that the application behaved correctly, that anything saved, that no error was logged. A green rehearsal is not a functional pass and must never be reported as one.

### Phase 3 — Record

Structure the take as a story. Follow the requester's order when one was given; otherwise: **entry** (sign in or land) → **context** (pan the surroundings so the viewer orients) → **action** (the main workflow) → **variation** (one secondary capability worth showing) → **result** (the outcome or new state).

Then, throughout the take:

- **Re-inject the cursor and subtitle overlays after every navigation.** Both live in the page's own DOM and both are destroyed when the page navigates. A cursor that vanishes halfway through is the most common defect in a recording, and it has exactly one cause.
- **Move the pointer to the target's centre in visible increments, pause, then click.** Never dispatch a click without the move: a cursor that teleports leaves every effect without a visible cause.
- **Type per character** at a visible rate, after clearing the field. A field that fills instantly reads as a page glitch.
- **Scroll smoothly** rather than jumping to an offset.
- **Hold after every state change** long enough for someone who has never seen the screen to read what changed.
- **Pan a dense screen** — a dashboard or overview — by moving the pointer across a handful of key elements in turn, skipping anything below the fold. Express the fold as a fraction of the viewport height, never as a pixel constant.
- **Subtitle each phase transition** with one short line in a consistent form — `Step N - Action` — and clear it during long pauses where the screen speaks for itself.
- **Copy the finished video to the agreed filename.** Drivers commonly write to a generated name; a generated name is not a deliverable.
- **Decide about popups and new tabs before recording, not after.** Most drivers record a new tab to its own separate video, so the main file shows the flow apparently stalling. Either keep the flow in one page, or plan to capture and merge the pieces.

## Pacing defaults

Every figure here is a chosen default, not a measured one, and the requester's brief overrides all of them. The rule underneath is not negotiable: a pause is long enough when a viewer seeing that screen for the first time could read the change before the next thing happens.

| After | Chosen default |
| --- | --- |
| Sign-in or first paint | 4s |
| Navigating to a new page | 3s |
| Clicking a button | 2s |
| Between major steps | 1.5-2s |
| The final action, before the recording ends | 3s |
| Each typed character | 25-40ms |

Further chosen defaults: viewport 1280x720; the pointer moved in roughly ten increments; subtitle lines under about 60 characters; at most six elements panned on a dense screen. Dense content or an unfamiliar audience raises the pauses; a narrated video where a voice track carries the explanation lowers them.

## Pre-record checklist

- [ ] A field map exists for every page in the flow
- [ ] Rehearsal ran and every step passed
- [ ] Video capture is enabled at the agreed viewport
- [ ] Cursor and subtitle overlays are re-injected after every navigation in the script, not only at the start
- [ ] Every click goes through move-then-click, with a descriptive label
- [ ] Every text entry types per character
- [ ] No silent catch anywhere — every helper reports its own failure
- [ ] Pauses match the pacing table, or the brief that overrode it
- [ ] The flow follows the requested story order
- [ ] The script reflects the interface discovered in phase 1, not the interface as assumed
- [ ] The output filename is the agreed one

## Common pitfalls

- The cursor disappears partway through: the overlay was injected once and destroyed by the first navigation.
- The video is unreadable because every pause was sized by what the script needed rather than by what a viewer needs.
- The cursor is the driver's default marker or absent entirely, so clicks appear to happen by themselves.
- The cursor teleports between targets, so the viewer never sees what is about to be clicked.
- A native select is operated by setting its value, so the dropdown never visibly opens and the choice happens off-screen.
- A modal is confirmed before the viewer has had time to read it.
- The video is delivered under the driver's generated filename.
- A selector failure is swallowed by a silent catch and the recording continues over a page that never changed.
- Field types were assumed rather than discovered: a rich-text region treated as a plain textarea, a custom combobox treated as a native select.
- A placeholder option was selected because its value looked non-empty, and the form submits with the field unset.
- A mention or tag autocomplete opens mid-typing and eats the characters that follow.
- A popup records to its own video file, and the main recording shows the flow stalling for no visible reason.

## Output contract

- The video file, at the agreed path and viewport
- The field map per page from phase 1
- The rehearsal result: each step with its pass or fail
- Deviations: any pacing default that was overridden, any driver capability that was missing, and what the recording lacks as a result
- An explicit statement of what the recording does not establish. A video of a flow completing is routinely read as proof that the flow works; it is a demonstration, and saying so on handover is part of delivering it.

## Examples

**Contrast — the same step, two ways.**

- Wrong: locate the submit button, click it, wait for the next page, keep going. When the label changed from "Submit" to "Submit request", the click missed silently, the wait expired against the same page, and the rest of the recording plays over a form nobody submitted. Nothing in the run reports a problem.
- Right: rehearsal already resolved that button by its discovered label, so a renamed button failed the run before a take was spent. During the take the pointer travels to the button's centre over several visible frames, pauses, clicks, and holds while the confirmation renders, under a subtitle reading `Step 4 - Submitting the request`.

**Field map to script.** The map records `Role: native select, first option "Select a role" with value 0`. The script therefore opens the select visibly and picks the second option by its text, rather than setting the field's value directly or taking the first option because its value was non-empty.
