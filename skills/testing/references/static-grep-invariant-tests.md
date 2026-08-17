# Static-grep invariant tests

A **static-grep invariant test** encodes a known-bad textual signature — a value, or a combination of values, that must never appear in the source tree — as a filesystem-level check that runs inside the ordinary test suite. It targets regressions with a cheap, textual precondition: something a future contributor could reintroduce by copy-pasting working code into a sibling file, without ever running the code that would actually fail.

It is not a substitute for behavioral tests. It stands alongside them because it is cheaper and faster than re-triggering the original failure through a live call or an integration run — no network, no process spin-up, no live credentials.

## Recipe

1. Name the forbidden textual signature exactly as it appears in source: an exact literal, or a specific value in a specific field — not a loose pattern that also matches legitimate code.
2. Enumerate the relevant files at test-run time (`readdir`/glob over the directory), not a hardcoded file list, so new files are covered automatically.
3. Generate one test case per file, not one test for the whole tree, so a failure names the specific offending file in the test runner's output.
4. Assert on the signature itself, not on behavior: a literal, a pairing of two literals in one file, or a write to a specific path. Each half of a forbidden pairing may be fine alone; only the combination (or the write) is forbidden.
5. Fail with a message that states the concrete fix, not "invariant violated" — name the remediation path(s) so a future contributor does not have to re-derive them from the regression's history.
6. Record why the test exists: the commit or version that introduced the fix, the date, what broke, its real blast radius, and how long it went undetected, if known. That is what justifies a cheap always-on test over relying on code review to catch the same drift again, and it lets a future reader judge whether the test is still earning its place before deleting it.
7. If the forbidden signature has a legitimate way to reappear (an intentional migration, a documented exception), state it in the test or its message. A tripwire that can never legitimately fire again is a permanent block on a future intentional change, not a regression guard.

## Worked example: forbidden literal pairing

Two configuration values are each valid alone but invalid in combination — for example, an orchestrator setting that only one specific downstream mode supports, paired with a downstream mode that doesn't support it. The failure mode: a working file gets duplicated into a sibling module, and only one of the two paired values gets updated to match the new context, silently reintroducing the bad pairing.

```javascript
const FORBIDDEN_A = 'mode: "legacy-batch"';
const FORBIDDEN_B = 'engine: "streaming-only"';

for (const file of fs.readdirSync(SRC_DIR).filter(f => f.endsWith(".ts"))) {
  test(`${file} does not pair legacy-batch mode with the streaming-only engine`, () => {
    const text = fs.readFileSync(path.join(SRC_DIR, file), "utf8");
    const hasBoth = text.includes(FORBIDDEN_A) && text.includes(FORBIDDEN_B);
    // fix: drop `engine: "streaming-only"` (a default exists) or move this file off legacy-batch mode
    expect(hasBoth).toBe(false);
  });
}
```

Each test case's name carries the file, so a failure points straight at the offending module instead of requiring a second search across the tree.

## A second situation this same technique covers

The identical mechanism guards a structurally different case: after closing a specific deprecated write path — not necessarily removing the whole resource; a legacy target can stay legitimately readable during a deprecation window — assert that no file outside an explicit, named allowlist writes to it. The allowlist is what lets the test separate a legitimate remaining reference (a reader, a migration shim, documentation) from the write-path regression it exists to catch. Land the test in the same change as the fix that closes the path, not a follow-up: a closed path with no tripwire is one accidental copy-paste away from reopening.
