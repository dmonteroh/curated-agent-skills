# Porting an Instruction Set to Another Harness

For shipping one authored corpus — system prompts, agent instruction files, a prompt or template library — to more than one agent runtime. This is corpus portability: a different problem from adapting prompt *content* to a different model (`frontier-model-prompting.md`), and both are usually needed at once.

## The organizing rule

Express what differs per target as declarative per-target data, not as branching inside the generator. The test to hold to: adding a target is one config entry plus a registry line, with no change to the generator, the setup, or the tooling.

```
# Wrong — the rules scatter into the generator
if target == "harness-b":
    frontmatter.pop("voice_triggers")
    text = text.replace("CLAUDE.md", "AGENTS.md")

# Right — the rules stay inspectable in one place
{ name, displayName,
  frontmatter: { mode, renameFields, ... },
  extraPathRewrites: [ { from: "CLAUDE.md", to: "AGENTS.md" } ], ... }
```

Once one `if target == …` lands in the generator, every later target adds another, and no one can read the full rewrite set for a single target in one place again.

## The four rewrite classes

Nearly every per-target difference is one of these. Declare each one as data:

1. **Frontmatter transformation.** Per target: an allowlist-or-denylist mode over metadata fields (keep only the listed keys, or strip the listed keys); a description length limit with an explicit overflow policy — fail the build, truncate, or warn — chosen deliberately, since a silent truncation ships a half-sentence description; field renames where the target names the same concept differently; and conditional field injection keyed off a source value (a `sensitive: true` source field emitting the target's own opt-out flag).
2. **Path rewrites.** Literal replacements over the content, applied in a defined order — order matters, because a later rewrite can re-hit the output of an earlier one. Derive a default set from the target's own layout, then let a target either append to it or replace it wholesale, and reject a config that tries both: "append" and "replace" silently disagree about the derived set, and the failure is invisible in the output.
3. **Tool-name rewrites.** Map harness-specific tool names onto neutral capability prose — "use the Bash tool" becomes "run this command" — so the ported text never instructs the reader to reach for a tool the target does not have.
4. **Section suppression.** Name the sections whose resolver returns empty for this target, so a capability the target lacks degrades to nothing rather than to dead prose describing something unavailable. Suppression is a per-target list, not an `if` inside the section's own text.

## Per-target boundary instruction

Carry the boundary warning for cross-model invocation as a per-target field rather than one global string, so a target with weaker isolation can carry a stronger warning without changing what the others emit. What the warning should say is the same data-versus-instructions rule the prompt itself uses — see `system-prompts.md`.

## Validate the registry, then let tests self-extend

- **Collision check.** Assert no duplicate target names, output subdirectories, or install roots across all configs. A collision is not a crash; it is one target silently overwriting another's output, discovered by a user.
- **Parameterize the test suite over the registry**, so a new target inherits the suite with no new test code. The generic assertions that pay for themselves: output exists for every source item; no source-side path leaked into the output (the highest-signal one — it catches an incomplete rewrite set directly); frontmatter valid under this target's own rules; the freshness check passes, so a stale generated tree fails rather than shipping; and self-references are excluded.

## Defaults and overrides

A fully-default target should need only two fields: its name and its display name. Everything else is derived from those and from the source corpus. Overrides are additive on top of the derived defaults, except where a field explicitly declares itself a wholesale replacement — and any such field says so in its own name, so a reader can tell which of the two it is without reading the generator.
