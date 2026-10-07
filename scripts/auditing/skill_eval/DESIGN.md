# skill_eval: design contract

Status: implementation contract. Modules share the types and helpers in `common.py`. Task-quality evaluation extends this contract in [PERFORMANCE.md](PERFORMANCE.md).

`skill_eval` is a new, standalone evaluation toolkit under `scripts/auditing/`. It does not import from, call, or change the existing review pipeline (`run_parallel_skill_reviews.sh`, `review-result.sh`, `proposals.py`, `audit_skills.py`). `REPLACEMENT-BRIEF.md` says which existing parts each module can replace later. That call belongs to the operator.

## 1. Questions it answers

| Question | Module | Ground truth |
| --- | --- | --- |
| Does this description make the skill load for these prompts, when it is the only skill installed? (shape A, isolated) | `activation.py` | Observed in the trace: a Claude `Skill` tool call, or Codex reading `SKILL.md` |
| Which skill loads when the whole library, or a named set of neighbours, is installed? (shape B, competitive) | `activation.py` | Observed in the trace |
| Is the trigger-case corpus good enough to measure anything? | `cases.py` | Static analysis |
| Has the skill absorbed its own evaluation material? | `integrity.py` | Static analysis |
| Is an arm, a judge, or a generator running in a polluted environment? | `vendors.py` | Home, cwd, and init-event fingerprints |
| What changes in task quality with and without a skill on both vendors? | `performance.py` | Paired outputs, objective checks, and blind cross-vendor judgments |
| Which of two outputs is better, and does an output meet its assertions? | `judge.py` | Blind model judgement with mechanical evidence checks |
| Does a description generalise past the exact wording of its cases? | `activation.py` together with `judge.py` paraphrases | Observed in the trace |

## 2. Threat model: three ways an evaluation gets poisoned

Each threat names its guard and the module that owns the guard.

### T-A. The environment poisons the agent under test or the evaluator

- The repository's own `CLAUDE.md`/`AGENTS.md` bootstrap loads when an agent boots under `/workspace` (measured: 3 of 4 `claude -p` runs from the repo root answered the bootstrap instead of the prompt). A sibling `CLAUDE.md` is auto-injected whenever an agent reads a file in its directory.
- User-installed skills self-activate inside arms that should not have them. The devcontainer bind-mounts `~/.claude/skills` and `~/.codex/skills`.
- Copying `~/.codex/config.toml` into an arm home carries MCP servers (`laya-mcp`) and trusted-project entries along with it. Both are tools the arm should not have. The earlier harness did this.
- Both vendors ship built-in skills. Claude's init event listed 20 alongside one installed skill, one of them named `code-review`, the same name as a library skill. Codex ships `skills/.system/` (`skill-creator` and others). A built-in can steal an activation.
- Memory stores (`~/.codex/memories`, Claude project memory) and `settings.json` hooks carry state from the operator's own sessions.
- The process environment. An arm spawned with the orchestrator's environment inherits `CLAUDE_CODE_MESSAGING_TOKEN`, `CLAUDE_CODE_SESSION_ID`, `CODEX_HOME`, and a `HOME` that points at the operator's real home (R1 review; the first fixtures' init events listed `SendMessage` and `ListAgents`, so those arms had joined the parent session's messaging channel). A shell-capable arm can also `cat ~/.claude/...` through the real `HOME`.
- Account-level provisioning. A bare `CLAUDE_CONFIG_DIR` still receives the account's claude.ai connectors (`mcp__claude_ai_*`) and organisation skills (`anthropic-skills:*`, including `anthropic-skills:writing-style`, which shares a name with a library skill), and they did not appear in every run.

Guards, all in `vendors.py`:

- Every arm, judge, and generator runs in a bare home. The home holds only credentials, a config this package generates, and the skills the run names.
- Task-quality arms extend the Claude whitelist with `Edit,Write,NotebookEdit`. Control and treatment share this role. Activation probes retain their original whitelist.
- Every agent process gets an environment built from an allowlist (`PATH`, `LANG`, `LC_*`, `TERM`, `TMPDIR`), with `HOME` set to the arm home, plus only the vendor variables this package sets on purpose (`CLAUDE_CONFIG_DIR`, `CODEX_HOME`). Nothing else is inherited.
- Claude calls pass `--strict-mcp-config` and `--settings '{"syncClaudeAiSkills":false,"syncClaudeAiPlugins":false}'`. Measured on claude 2.1.280 (R2): the claude.ai skill sync writes `<config dir>/skills/synced/` and `plugins/synced/` mid-run (3 of 6 control runs), and `--strict-mcp-config` does not stop it. The setting stopped it in 16 of 16 runs, and activation still worked. No environment variable disables the sync, and `--bare` drops authentication and the installed skills.
- Claude arms get a tool whitelist (`--tools Read,Glob,Grep,Bash,Skill`), never a denylist. The CLI prints no warning for an unknown `--disallowedTools` name, so a misspelled denial fails open. Without the whitelist, arms kept `SendMessage` and `ListAgents`, and a `ListAgents` call reported peers, so concurrent arms could reach one another.
- Every call gets a fresh home, built and destroyed around that one call. A home reused across calls carries sync downloads, `.claude.json` state, and session state from one call to the next, which is how the intermittent `anthropic-skills:*` leak happened. It also makes repeats dependent.
- `build_home` refuses any path outside `SCRATCH_ROOT`.
- A Claude arm receives the operator's access token without its refresh token, and no arm starts when that token expires within `CLAUDE_TOKEN_MIN_REMAINING_S` (a chosen default, 1200 s). Arms holding the refresh token refreshed it themselves when it expired, and refresh tokens rotate, so racing arms can invalidate the operator's own login (measured 2026-10-05: 13 arm calls failed with "OAuth session expired and could not be refreshed" in one sweep). A refused arm is a recorded vendor failure, never a scored result.
- `SCRATCH_ROOT` and its containers (`homes/`, `cwd/`, `selftest-negctrl/`) are mode `0300`, traverse-only: an arm opens its own known paths, but `ls`, globs, and `find` over the scratch root list nothing, so an agent searching for a file a prompt mentions cannot discover other arms' homes. Measured before this guard: 3 of the first 14 skills of a library selftest sweep lost their only positive-control call to such searches, on both vendors. With the guard in place, a reference that could reach other arms only by listing (the root, a container, or a glob directly under one) is recorded as an outside read, not contamination; a concrete path into another arm's home or cwd is still contamination, because a known path opens without listing.
- Shell-capable arms can still read absolute paths such as `/workspace` or the real home. The container gives no OS sandbox (bubblewrap is a settled non-goal). `parse_trace` records every path referenced outside the arm's home and cwd in `outside_reads`, including paths inside Codex's `bash -lc` wrapper and relative paths resolved against the cwd (a best-effort heuristic: bare filenames after a `cd` are not resolved), and a run that referenced the repository or the real home is marked contaminated. The body of a heredoc that only writes a file (`cat > f <<EOF`, `tee f <<EOF`) is file content and is not scanned; a heredoc fed to an interpreter still is (measured: a Terraform module's `source = "../../modules/vcn"` voided an arm before this rule).
- The post-run check treats any visible skill that is neither expected nor in the recorded built-in baseline as foreign. `anthropic-skills:*` and every other namespaced name is always foreign, and the baseline never admits one. The baseline is keyed on vendor, model, and CLI version, and is recorded only from an `ok` probe run with the sync guard. A Claude arm whose init `tools` differs from the whitelist is contaminated.
- Every agent's working directory sits under `SCRATCH_ROOT`, outside the repository. `verify_environment()` checks that no directory from the cwd up to `/` holds an instruction file.
- Every run gets a pre-flight fingerprint and a post-run check against the Claude init event's `skills` list. A mismatch between the expected skill set and the visible set is an `error` finding, and the run's records are marked invalid.
- Built-ins are measured, never hidden. The first run per vendor and model records the built-in baseline, and an activation that lands on a built-in is reported as `builtin:<name>`.

### T-B. The evaluator is poisoned by what it is shown

- A judge that knows which arm had the skill grades the label, not the output. Skill output often names the skill ("Using the writing-style skill…") or quotes its paths, and that unblinds it.
- A judge with the skill installed, or with the skill's text in its prompt, grades compliance with that skill's taste instead of task quality.
- A judge sees the first-presented option favourably (position bias).
- A judge that "quotes evidence" can invent the quote, or quote something too short to mean anything ("a").
- An activation case written by a model that has read the skill echoes the skill's vocabulary and inflates activation. The earlier corpus generator did exactly this: it wrote cases from the skill's own `Use this skill when` bullets.

Guards:

- `judge.py` gives the judge only the task prompt and the outputs, under opaque labels. Skill names, skill paths, and self-announcing sentences are redacted first, and the redaction count is recorded per output. Redaction must leave no visible trace: a `[REDACTED]` marker appears almost only in outputs that had the skill, so the marker itself would unblind the judge. Announcement sentences are deleted, and names and paths are replaced with neutral filler. Redaction runs by default over every library skill name and the built-in baseline. The judge runs through `vendors.complete()`: bare home, no skills, no tools, neutral cwd. Its trace must show zero tool calls, or the verdict is void.
- Pairwise judgements run in both orders. A verdict that flips with order counts as a tie, and the flip rate is reported as position bias.
- Every assertion verdict must carry a quotation. `judge.py` checks mechanically that the quotation is a substring of the output, after whitespace normalisation. An unsupported quotation makes the verdict `unsupported`, never `pass`. A quotation must be at least 3 content words or 15 characters (a chosen default), and `fail` needs a quotation of what the output did instead, or the literal statement that the output contains nothing relevant.
- The judge vendor is recorded and must be given explicitly. When `--source-vendor` names the vendor that produced the outputs and it equals the judge vendor, the CLI warns.
- Vendor self-references ("Claude", "Codex", "Anthropic", "OpenAI", "as an AI…") are redacted in both outputs, and file paths are normalised the same way in both. When the two outputs' redaction counts differ, the result records it as a possible tell.
- `judge.py generate` writes paraphrases and new candidate cases through an isolated agent that never sees the skill body or its description. It sees only a one-line job statement, or the existing prompts for paraphrasing. `cases.py` scores every candidate's echo against the description, and output goes to a candidates file for human review. Nothing is written into `trigger-cases/` automatically.

### T-C. The skill is tuned to brute-pass its evaluation (Goodhart)

- A description iterated against a fixed case set learns those cases' words. `skill-creator`'s improve loop feeds failing prompts back verbatim.
- A body edit can paste eval prompts, assertion wording, or rubric phrases into the skill, whether a helpful agent did it or a careless author.
- A holdout set that is measured after every change becomes a second train set.
- A holdout set kept in plaintext in the tree is read by whoever edits the skill, so it is not held out at all.

Guards:

- Three case sets, never pooled:
  - **train**: the visible `trigger-cases/` cases that `common.split_of()` assigns to train.
  - **dev**: the visible cases it assigns to its other side (the `"holdout"` key of `split_cases`, kept for compatibility). Dev protects against tuning noise, not against fitting, because it is plaintext.
  - **holdout**: only a sealed set, `SEALED_DIR/<skill>.holdout.sealed`, unsealed in memory at run time. `--split holdout` with no sealed set refuses and says how to seal one.

  The split is a per-case salted hash, so editing one case never moves another. A paraphrase inherits its parent's split through `paraphrase-of:<id>`.
- `common.HOLDOUT_LEDGER` records each distinct description measured on the sealed holdout. `activation.py` warns at the look budget and refuses past it unless given `--allow-holdout-reuse`, a flag the report records.
- Feedback for description work (`activation.py feedback`) reports train failures only, as failure classes: polarity, tags, which skill stole the activation. It never gives holdout prompts, and gives train prompts only with `--verbatim`.
- `integrity.py scan` checks each skill's text against every piece of evaluation material: trigger cases, sealed sets, assertions, and canary strings. It reports shared token runs at or above `n` (default 8, a chosen default) and any canary hit. `integrity.py diff-scan --base <ref>` runs the same checks on lines added since a git ref, which is the brute-pass check to run before accepting a skill edit.
- Sealed sets (`integrity.py seal`) keep holdout and assertion material out of plaintext in the tree, and every sealed payload embeds a canary string. A canary found anywhere in `skills/` means evaluation material leaked into a skill.
- The paraphrase gap: `activation.py` runs original cases and their paraphrases in the same run and reports the rate on each. A description that passes originals and fails paraphrases is fitted to wording, not intent.
- Self-test: `activation.py selftest` runs a skill with its description replaced by an unrelated one (the negative control) and expects its positive rate to fall. A runner that cannot show a difference is not trusted (learned rule: confirm a test can fail before trusting it).

## 3. Modules and interfaces

Stdlib-only Python 3.10+. Every module exposes `add_subparser(subparsers)`, which registers its subcommands on the single CLI `scripts/auditing/skill-eval.py` (controller-owned). Every leaf parser calls `set_defaults(func=handler)`, and `handler(args)` returns an exit code. `vendors.py` registers under the command name `env`, for example `env check` and `env builtins`. A module's pure logic is importable without side effects and without the network.

### `common.py` (controller, done)

`Case`, `TraceRecord`, `Finding`; JSONL IO; `case_id`; `split_cases`; the holdout ledger; `wilson_interval`; `tokenize`, `content_words`, `ngrams`, `longest_common_run`; `read_frontmatter`, `replace_description`; paths.

### `vendors.py` + `trace.py` (arm isolation, task T1)

```python
def build_home(vendor: str, home: Path, skills: dict[str, Path],
               description_overrides: dict[str, str] | None = None) -> dict
    # Wipes and recreates `home`. Copies credentials only:
    #   claude: ~/.claude/.credentials.json
    #   codex:  ~/.codex/auth.json plus a GENERATED config.toml (never a copy):
    #           personality="pragmatic", service_tier="default", no mcp_servers,
    #           and a trust entry only for the run's cwd root.
    # Copies each skill dir to <home>/skills/<name>, applying description_overrides
    # through common.replace_description. Returns the manifest:
    #   {vendor, home, skills: {name: sha256 of the installed SKILL.md}, created_at}

def neutral_cwd(label: str) -> Path   # fresh empty dir under SCRATCH_ROOT/cwd/

def verify_environment(vendor: str, home: Path, cwd: Path,
                       expected_skills: set[str]) -> list[Finding]
    # Pre-flight. Errors: cwd inside REPO_ROOT; an instruction file
    # (CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules, copilot-instructions.md,
    # case-insensitive) in the cwd or any ancestor; home skills != expected;
    # codex config.toml declaring mcp_servers; claude settings.json with hooks;
    # a memory store in the home. Warnings: an expected skill name that
    # collides with a known built-in.

def exec_agent(vendor: str, home: Path, cwd: Path, prompt: str, trace_out: Path, *,
               model: str | None = None, effort: str = "medium",
               timeout: int = 600, tools: str = "activation") -> dict
    # Runs one agent. The prompt always goes on stdin (codex takes `-` as its
    # prompt argument), never into argv or a shell string.
    # tools="activation": claude --permission-mode dontAsk,
    #   --tools "Read,Glob,Grep,Bash,Skill" (a whitelist) with the same
    #   --allowedTools, plus --strict-mcp-config and the sync-guard --settings;
    #   codex exec --json -s danger-full-access --skip-git-repo-check (the only
    #   working sandbox mode in this container).
    # tools="none": claude --tools "" --disable-slash-commands --strict-mcp-config;
    #   codex -s read-only (every command fails in this container, which is the
    #   point for a judge) with web search disabled. Used by complete().
    # Every call: environment from the allowlist in §2 T-A, HOME = the arm home.
    # Returns {exit_code, duration_s, trace_path, stderr_path, cmd} with
    # credentials never included in cmd.

def complete(vendor: str, prompt: str, *, model: str | None = None,
             json_schema: dict | None = None, label: str = "complete",
             timeout: int = 300, effort: str = "medium") -> tuple[str, TraceRecord]
    # One isolated single-shot call for judges and generators: fresh bare home
    # with NO skills, fresh neutral cwd, tools="none". Returns the final text
    # and the normalised record. Callers must check record.tool_calls == 0
    # (StructuredOutput is not counted; see common.TraceRecord).

def prepare_workspace(cwd: Path, kind: str = "git") -> str
    # Fills a fresh arm cwd before verify_environment runs. kind: "empty";
    # "git" (a neutral repo: main with one commit, a feature/update branch with
    # one small commit, local user.name/email, no instruction or config files);
    # or a fixture directory path copied in. Returns a sha256 over the fixture's
    # file list and contents, recorded in plan.json so A/B runs share one
    # condition. Measured (R3): the task prompt "Draft the PR description for
    # this branch against main." activated 2/2 in the git fixture, 0/1 empty.

def builtin_baseline(vendor: str, model: str | None = None) -> list[str]
    # Skills visible with nothing installed; cached per vendor and model under
    # RUNS_DIR/builtins/. Codex: list <fresh home>/skills/.system after one
    # trivial run, since the CLI seeds it.

DEFAULT_MODELS = {"claude": "sonnet", "codex": "gpt-5.6-terra"}
```

`trace.py`:

```python
def parse_trace(path: Path, vendor: str, known_skills: Iterable[str]) -> TraceRecord
    # claude stream-json: init event -> visible_skills (its "skills" list);
    #   tool_use name=="Skill" -> the input's skill field, never namespace-
    #   stripped (an unknown "org:name" reports as builtin:org:name); a Read, or
    #   a Bash read verb (cat, sed, head, ...) whose file argument is
    #   .../skills/<name>/SKILL.md -> file_read; result event -> text, cost_usd,
    #   is_error.
    # codex --json: item.completed command_execution naming
    #   skills/<name>/SKILL.md in a read-verb segment -> command_read, when the
    #   command exited 0 or its aggregated_output carries that file's
    #   `name: <name>` frontmatter line (a chain such as `sed SKILL.md && sed
    #   missing.md` exits non-zero after a successful read; measured live,
    #   4 of 35 saved codex traces were under-counted before this rule);
    #   agent_message -> text;
    #   turn.completed usage -> tokens; turn.failed / error -> ok=False.
    # script_runs: a claude Bash command or a codex command_execution (completed
    #   or failed, never declined) that executes a file under
    #   skills/<name>/scripts/, directly or through an interpreter, after a
    #   `cd` into the skill in the same command. A gate that exits non-zero
    #   still ran. Read verbs, `ls`, and `grep` naming the script do not count.
    # Activation is attributed only to skills in known_skills plus any name
    #   under a skills/ path, so a built-in reads as "builtin:<name>" when not
    #   in known_skills.
    # A trace with no result event, or an authentication error, is ok=False.
    #   Never score a failed arm as a clean non-activation: the old harness
    #   scored 73-byte auth errors as clean output.
```

### `cases.py` (corpus quality, task T2)

- `load_cases(skill) -> list[Case]` parses `trigger-cases/<skill>.md` in the existing format. It also accepts an optional `tags: [near-miss, off-register]` line under a case. The existing files stay valid unchanged.
- `lint(skill) -> list[Finding]`: fewer than the floor (chosen default: 5 positive and 5 negative, overridable); no near-miss negative, meaning a negative whose content words overlap the skill's topic (the description's content words) while the case is `expect_activate: no`, whether tagged or detected; no off-register positive (tagged, or detected as short, lowercase, and without sentence punctuation); generator template residue; duplicate or near-duplicate prompts; high echo, meaning a positive that shares a run of 4 or more content words with the description (chosen default); cross-skill collision, meaning the same normalised prompt is positive for two skills.
- `echo_score(prompt, description) -> float` and `longest_echo(prompt, description) -> int` are public, because `judge.py generate` uses them to filter candidates.
- CLI `cases lint [--skill ...|--all] [--json]` prints a table and exits 1 on any `error` finding.
- `deficits(skill) -> dict` counts what a file lacks after its template-residue cases are dropped. `apply_selection(skill, selected, allowed)` drops those cases and appends `selected`, refusing the whole selection unless every selected prompt matches an `allowed` generator row exactly, polarity included; the written case is the generator's row, with its tags. This keeps the T-B guard mechanical: a reviewer chooses among generated prompts and cannot author one. CLI: `cases deficits`, `cases apply`.
- `activation run` and `selftest` call `lint` before any spend and refuse a skill with lint errors unless `--allow-corpus-errors` is given; `plan.json` records the lint counts either way.

### `integrity.py` (material isolation, task T4)

- `seal(src_json, skill, kind) -> Path` writes `SEALED_DIR/<skill>.<kind>.sealed`: a JSON header (`skill`, `kind`, `canary`, `sha256` of the plaintext, `created_at`, and a one-line notice that the payload is evaluation material and that decoding it into an authoring context voids the evaluation), plus a base64 zlib payload. `kind` is `holdout` or `assertions`. The canary is `SKILL-EVAL-CANARY-<uuid4>` and is also embedded inside the plaintext.
- `unseal(path) -> dict` works in memory. It returns `{"header": {...}, "payload": {...}}`. Callers that must pass material to an agent write it under `SCRATCH_ROOT`, never into the repository.
- `scan(skill) -> list[Finding]` checks every text file under `skills/<skill>/`. Errors: any canary from any sealed file; a shared token run of `n` or more (default 8) with any holdout prompt or assertion. Warnings: the same against the plain `trigger-cases/` prompts, because those are visible by design, so an overlap there is a smell and not proof.
- `diff_scan(skill, base_ref) -> list[Finding]` runs the same checks restricted to lines added since `base_ref` (`git diff --unified=0`).
- `scan-all` runs across the whole library. It is cheap and deterministic, which makes it suitable for CI later.

### `activation.py` (runner, task T3)

- `run --skill S [--shape isolated|competitive] [--neighbors a,b|--library] [--vendors claude,codex] [--models claude=sonnet,codex=gpt-5.6-terra] [--repeats 3] [--split train|dev|holdout|visible] [--workspace git|empty|DIR] [--include-paraphrases FILE] [--description-file F] [--concurrency 4] [--max-calls N] [--max-cost-usd X] [--max-codex-tokens N] [--limit N] [--case ID ...] [--timeout S] [--effort E] [--keep-homes] [--allow-holdout-reuse] [--dry-run]`. `python3 scripts/auditing/skill-eval.py activation run -h` is authoritative.
- Before any agent runs, it calls `verify_environment` for every arm home and cwd and aborts on any `error`. After each run it checks the init-event skill list against the expected set and the built-in baseline. It prints the planned call count and asks for nothing: `--dry-run` shows the plan and exits.
- Records land in `RUNS_DIR/<run_id>/`: `plan.json` (config, skill hashes, split salt, and the description sha per skill), `records.jsonl` (one row per call: case id, split, tags, vendor, model, repeat, `TraceRecord`), `summary.json` and `summary.md` (per vendor and case: activation rate over repeats with a Wilson interval; per polarity and split: sensitivity and specificity; for competitive runs, a confusion list of which skill fired instead).
- `--workspace empty|git|<dir>` (default `git`) prepares each fresh cwd through `vendors.prepare_workspace`. `selftest` takes the same flag.
- `selftest` returns `inconclusive` (exit 3) when the positive control is below its threshold: that pattern means "the environment does not let the skill activate", not "detection is broken", and the negative control is judged only after the positive control passes. It also returns `inconclusive`, never `fail`, when an arm has no valid call (capped, failed, or contaminated); the reason names the arm and the cause. `selftest` supports `--dry-run`, `--max-calls`, `--max-cost-usd`, and `--max-codex-tokens` like `run`, with two differences: `--max-calls` is split evenly per vendor and shrinks the number of train positives used so each vendor gets a complete comparison (a cap too small for one is refused before any call), and real and negative calls are reserved in pairs so a cost or token cap leaves the arms balanced. `selftest.json` is rewritten after each vendor, and an exception in one vendor becomes that vendor's `inconclusive` result.
- Contamination also covers reads under `SCRATCH_ROOT` outside the arm's own home and cwd: other arms' cwds, homes, and anything else there.
- Codex reports no visible-skill list, so the post-run visible-skill check is Claude-only. Codex contamination rests on the pre-flight home check and on `outside_reads`.
- `--split holdout` checks and records ledger looks as §2 T-C describes. The ledger path is fixed. Tests override it only through the `SKILL_EVAL_HOLDOUT_LEDGER` environment variable, never through a CLI flag.
- Holdout results are aggregate only in every output (`summary`, `report`, `compare`, `feedback`): rates per vendor and polarity, never per-case ids or prompts. Holdout records and traces keep no prompt text.
- `report RUN_DIR` re-renders the summary from `records.jsonl`, never from memory.
- `selftest-all` runs `selftest` per skill as parallel child processes and aggregates their `selftest.json` files into one sweep table; a child that writes none is listed as `error`, never dropped.
- `compare RUN_A RUN_B` gives per-case rate deltas for a description A/B run on the same cases.
- `feedback RUN_DIR` produces class-level train-only failure feedback (§2 T-C).
- `selftest --skill S` runs the negative control (§2 T-C) and fails loudly when positive activation does not drop.
- Default repeats: 3 (a chosen default; the writing-style campaign measured 3 as too few to rank close variants, where 4 trials across 5 probes was the floor). `compare` warns when either side has fewer than 4 repeats.
- Cost is carried per vendor in the vendor's own unit and never converted.

### `judge.py` (blind judging and isolated generation, task T5)

- `redact(text, skill_names) -> (text, n_redactions)`: skill names, `skills/<name>` paths, and sentences announcing skill use ("using the X skill", "per the X skill", "I'll load/invoke/activate …").
- `pairwise --prompt F --a OUT_A --b OUT_B [--repeats 2] [--judge-vendor V]` shuffles labels, runs both orders, and reports `a|b|tie` with the flip count. The arm map lives only in the run directory. The judge prompt never mentions skills or arms.
- `grade --prompt F --output OUT --assertions A.json [--judge-vendor V]` gives per-assertion `pass|fail|unsupported` with the quotation. The quote check is mechanical. Assertions may come from a sealed file.
- `generate paraphrases --skill S --k 2` and `generate cases --job "one line" --skill S` (or `--jobs F.json` for a batch, one candidates file per skill) go through `complete()`. `--gen-vendor` may list several vendors; each row carries `gen:<vendor>`, because a prompt one vendor wrote may suit that vendor's phrasing and the corpus keeps the provenance. `--n-off-register` adds terse lowercase positives tagged `off-register`, echo-checked like any positive. The generator never receives the SKILL.md body or the description. Output: `RUNS_DIR/<run_id>/candidates.md` in trigger-case format with `tags: [generated]` or `[paraphrase-of:<id>]`, each annotated with its echo score. Candidates above the echo threshold are listed separately as rejected.
- `compare_and_grade(prompt, out_a, out_b, requirements)` grades every requirement for both outputs and gives the preference in one call per presentation order, two in total. A grade counts only when both orders agree after the quote check. Disagreement makes it `unsupported`, and a winner that flips with order is a tie. It returns the comparison in `pairwise`'s shape. `performance run` uses it by default.
- `pairwise.json` and `grading.json` record the judge vendor, model, and effort. Rejected generator candidates are written in a form the trigger-case parser cannot load.
- Every judge or generator call checks `record.tool_calls == 0`. A call that used tools is void. JSON schemas set `"additionalProperties": false` at every object level, because the Codex API rejects any schema without it.

## 4. Output and file layout

```
scripts/auditing/skill-eval.py          CLI entry (controller)
scripts/auditing/skill_eval/
  __init__.py  common.py  DESIGN.md  README.md  REPLACEMENT-BRIEF.md   (controller)
  vendors.py  trace.py                  T1
  cases.py                              T2
  activation.py                         T3
  performance.py                        paired task-quality runner
  PERFORMANCE.md                        suite format and quality-evaluation contract
  integrity.py                          T4
  judge.py                              T5
  fixtures/<module>/…                   per-task test fixtures
scripts/auditing/sealed/                sealed sets + holdout ledger (tracked)
$SKILL_EVAL_RUNS_DIR (default ~/.cache/skill-eval/runs)   runs, outside the repository and outside SCRATCH_ROOT
scripts/tests/test_skill_eval_<module>.py
```

## 5. Rules for every module

- No network, subprocess, or agent call at import time or in unit tests. Tests use fixture traces and a stubbed `exec_agent` or `complete`.
- Never interpolate a prompt into a shell string. Use `subprocess.run([...], input=...)`.
- Never print or record credentials. Never copy anything from a real home except the credential file named above.
- Every number that looks like a threshold is either measured, with its source named, or labelled a chosen default where it is defined.
- A vendor that cannot run, whether from a missing binary, auth, or quota, gives a failed arm with the reason recorded. It is never dropped silently from the vendor list (learned rule: never narrow arms mid-effort).
