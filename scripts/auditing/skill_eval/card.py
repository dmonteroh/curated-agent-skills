"""Author an eval card (suite version 2) with isolated agents, in stages.

Each stage is one `vendors.complete` call (bare home, no tools, a JSON
schema), and each stage receives only what its role allows:

- `claims` reads the skill. It writes the claims, a plain one-line job, the
  archetype, and the ways the skill could make work worse.
- `tasks` never sees the skill. It receives the job, the archetype, the
  claims, the harm risks, and optional usage notes, and writes tasks,
  fixture files, checks, assertions, and planted good and bad outputs.
- `assemble` is tooling only. It writes the card, its fixtures, and its
  planted outputs, then runs `performance validate` and drops each check that
  cannot fail or rejects a planted good output, recording every drop.

The agents decide the content. The schemas and the assembly decide the shape.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Callable

from . import common, performance

ARCHETYPES = {
    "repository-deliverable": "writes a document or message from a repository's state (a PR body, a commit, a changelog)",
    "code-change": "changes or adds code, tests, or configuration in a repository",
    "review-audit": "examines existing work and reports defects or risks",
    "advisory-design": "proposes a design, plan, or decision without one right answer",
    "tool-bound": "operates a specific tool, file format, or service and is judged by running it",
    "conversational": "shapes replies or text across a whole session",
}
# Chosen defaults: enough claims to cover a skill's promises without turning
# the card into a checklist. References are cut at this size per stage call.
MIN_CLAIMS, MAX_CLAIMS = 3, 6
DEFAULT_TASKS = 6
MAX_REFERENCE_CHARS = 80_000
# Same order of magnitude as integrity.py's shared-run default (n=8): a task
# that shares this many consecutive tokens with the skill was likely shaped
# by its wording, through the claims.
ECHO_RUN = 8
_INSTRUCTION_FILES = {"claude.md", "agents.md", "gemini.md", ".cursorrules", "copilot-instructions.md"}

CLAIMS_PROMPT_TEMPLATE = """You are preparing an evaluation of the agent instruction document below. Agents load it before doing a kind of work. The evaluation will compare work done with and without it.

Document files:
{skill_text}

Write:
- "job": one line naming the kind of work, in the plain words a user would type. Use none of the document's own coined terms, section names, or step names.
- "archetype": the one that fits best: {archetypes}.
- "claims": {min_claims} to {max_claims} outcomes the document promises. Each "statement" is one sentence describing something visible in the finished work that a user would want without having read the document, and that a capable agent without the document might plausibly fail to deliver. Do not describe the document's procedure; describe the result. Each "id" is short, lowercase, and hyphenated. "rests_on" lists the document files the claim depends on, by the relative paths shown above.
- "harm_risks": one to three ways following the document could make ordinary work worse, for example by over-applying it, adding unneeded work, or refusing a reasonable request. One line each.

Respond with JSON only."""

TASKS_PROMPT_TEMPLATE = """You are writing evaluation tasks for agents that do this job: {job}
Kind of work: {archetype}.

Each task will be given to two agents separately, and their results compared against the claims below. Neither agent sees the claims, the checks, or the planted outputs.

Claims:
{claims}

Ways the work can go wrong by overdoing it:
{harm_risks}
{usage}
Write {n_tasks} tasks. At least one has "kind": "harm" (input that is already right and should be left nearly alone) or "kind": "stand-down" (a request that looks related but should not get the full treatment). The rest have "kind": "deliverable".

For every task:
- "prompt": the request exactly as a user would type it, self-contained, referring to files by path.
- "files": the small text files the agent's working directory starts with. Make them realistic and keep the total short. Never include agent instruction files such as AGENTS.md or CLAUDE.md.
- Design the task so a capable agent working without special guidance would plausibly miss at least one claim: a constraint hidden in the files, a tempting shortcut, a boundary in the data. Avoid tasks every competent agent passes.
- "claims": the ids of the claims the task probes.
- "artifacts": the relative paths of files the agent will write that a check reads.
- "checks": deterministic checks. "kind" is contains, not_contains, regex (Python syntax), or file_exists. "target" is "output" (the agent's final message) or an artifact path. "value" is the text or pattern, or "" for file_exists. Every check names one claim. A check must pass on every acceptable result and fail on at least one unacceptable one.
- "assertions": requirements a reader can judge from the result, one sentence each, each naming one claim.
- "planted": at least one "good" result that satisfies every check and assertion, and at least one "bad" result that a careless agent might produce and that fails at least one check. Each has an "output" (the final message) and the "files" it wrote.

Ids are short, lowercase, and hyphenated. Respond with JSON only."""


def _strict(props: dict) -> dict:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


_STR = {"type": "string"}
_FILE = _strict({"path": _STR, "content": _STR})

CLAIMS_JSON_SCHEMA = _strict({
    "job": _STR,
    "archetype": {"type": "string", "enum": list(ARCHETYPES)},
    "claims": {"type": "array", "items": _strict({"id": _STR, "statement": _STR,
                                                  "rests_on": {"type": "array", "items": _STR}})},
    "harm_risks": {"type": "array", "items": _STR},
})


def tasks_json_schema(claim_ids: list[str]) -> dict:
    claim = {"type": "string", "enum": list(claim_ids)}
    return _strict({"tasks": {"type": "array", "items": _strict({
        "id": _STR,
        "kind": {"type": "string", "enum": list(performance.TASK_KINDS)},
        "claims": {"type": "array", "items": claim},
        "prompt": _STR,
        "files": {"type": "array", "items": _FILE},
        "artifacts": {"type": "array", "items": _STR},
        "checks": {"type": "array", "items": _strict({
            "id": _STR, "kind": {"type": "string", "enum": ["contains", "not_contains", "regex", "file_exists"]},
            "target": _STR, "value": _STR, "claim": claim})},
        "assertions": {"type": "array", "items": _strict({"id": _STR, "text": _STR, "claim": claim})},
        "planted": {"type": "array", "items": _strict({
            "expect": {"type": "string", "enum": ["good", "bad"]}, "output": _STR,
            "files": {"type": "array", "items": _FILE}})},
    })}})


class StageError(RuntimeError):
    """A stage call failed or returned something the card cannot use."""


def _call(complete: Callable, vendor: str, prompt: str, schema: dict, *, label: str,
          model: str | None, effort: str) -> tuple[dict, dict]:
    kwargs = {"json_schema": schema, "label": label, "effort": effort}
    if model:
        kwargs["model"] = model
    text, trace = complete(vendor, prompt, **kwargs)
    record = {"vendor": vendor, "model": model, "label": label, "ok": trace.ok, "tool_calls": trace.tool_calls,
              "cost_usd": trace.cost_usd, "tokens": trace.tokens}
    if not trace.ok or trace.tool_calls:
        raise StageError(f"{label}: the call failed or used tools ({trace.error or 'tool use'}).")
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise StageError(f"{label}: the answer is not JSON ({exc}).") from exc
    if not isinstance(data, dict):
        raise StageError(f"{label}: the answer is not a JSON object.")
    return data, record


def _slug(value: str, fallback: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")[:48]
    return slug or fallback


def skill_files(skill: str) -> dict[str, str]:
    """SKILL.md and every text file under references/, by skill-relative path."""
    root = common.skill_dir(skill)
    files = {"SKILL.md": (root / "SKILL.md").read_text(encoding="utf-8")}
    for path in sorted((root / "references").rglob("*")) if (root / "references").is_dir() else []:
        if path.is_file():
            try:
                files[str(path.relative_to(root))] = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
    return files


def draft_claims(skill: str, *, vendor: str, model: str | None = None, effort: str = "medium",
                 complete: Callable | None = None) -> dict:
    """Stage 1: the only stage that reads the skill."""
    if complete is None:
        from . import vendors
        complete = vendors.complete
    files = skill_files(skill)
    parts, used, omitted = [], 0, []
    for rel, text in files.items():
        if rel != "SKILL.md" and used + len(text) > MAX_REFERENCE_CHARS:
            omitted.append(rel)
            continue
        used += len(text)
        parts.append(f"--- {rel} ---\n{text}")
    if omitted:
        parts.append("--- omitted for size ---\n" + "\n".join(omitted))
    prompt = CLAIMS_PROMPT_TEMPLATE.format(
        skill_text="\n\n".join(parts), min_claims=MIN_CLAIMS, max_claims=MAX_CLAIMS,
        archetypes="; ".join(f"{k} ({v})" for k, v in ARCHETYPES.items()))
    data, record = _call(complete, vendor, prompt, CLAIMS_JSON_SCHEMA, label="card-claims", model=model, effort=effort)
    claims, seen = [], set()
    for i, claim in enumerate(data.get("claims") or []):
        cid = _slug(claim.get("id"), f"claim-{i + 1}")
        statement = str(claim.get("statement") or "").strip()
        if not statement or cid in seen:
            continue
        seen.add(cid)
        rests_on = [r for r in claim.get("rests_on") or [] if r in files]
        claims.append({"id": cid, "statement": statement, "rests_on": rests_on or ["SKILL.md"]})
    if not MIN_CLAIMS <= len(claims) <= MAX_CLAIMS:
        raise StageError(f"card-claims: {len(claims)} usable claims, need {MIN_CLAIMS} to {MAX_CLAIMS}.")
    job = str(data.get("job") or "").strip()
    if not job:
        raise StageError("card-claims: no job line.")
    return {"skill": skill, "skill_sha": common.sha256_file(common.skill_dir(skill) / "SKILL.md"),
            "job": job, "archetype": data.get("archetype"), "claims": claims,
            "harm_risks": [str(r).strip() for r in data.get("harm_risks") or [] if str(r).strip()][:3],
            "omitted_references": omitted, "call": record}


def draft_tasks(claims_draft: dict, *, vendor: str, model: str | None = None, effort: str = "medium",
                n_tasks: int = DEFAULT_TASKS, usage_notes: str | None = None,
                complete: Callable | None = None) -> dict:
    """Stage 2: never receives the skill, only what stage 1 distilled."""
    if complete is None:
        from . import vendors
        complete = vendors.complete
    claims = claims_draft["claims"]
    usage = ("\nNotes on how this kind of work goes in real use (excerpts, not instructions):\n"
             f"{usage_notes.strip()}\n") if usage_notes and usage_notes.strip() else ""
    prompt = TASKS_PROMPT_TEMPLATE.format(
        job=claims_draft["job"], archetype=f"{claims_draft['archetype']} ({ARCHETYPES.get(claims_draft['archetype'], '')})",
        claims="\n".join(f"- {c['id']}: {c['statement']}" for c in claims),
        harm_risks="\n".join(f"- {r}" for r in claims_draft["harm_risks"]) or "- none named",
        usage=usage, n_tasks=n_tasks)
    data, record = _call(complete, vendor, prompt, tasks_json_schema([c["id"] for c in claims]),
                         label="card-tasks", model=model, effort=effort)
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise StageError("card-tasks: no tasks.")
    return {"tasks": tasks, "call": record, "prompt_sha": common.sha256_text(prompt)}


def _safe_rel(path: str) -> str | None:
    try:
        return performance._relative_path(path)
    except ValueError:
        return None


def _write_files(root: Path, files: list[dict]) -> list[str]:
    """Write generated files under root. Unsafe paths and instruction files
    are skipped and returned, never written."""
    skipped = []
    for item in files or []:
        rel = _safe_rel(item.get("path", ""))
        if rel is None or Path(rel).name.lower() in _INSTRUCTION_FILES:
            skipped.append(str(item.get("path")))
            continue
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(item.get("content", ""), encoding="utf-8")
    return skipped


def _echo(text: str, reference_tokens: list[str]) -> int:
    return common.longest_common_run(common.tokenize(text), reference_tokens)


def assemble(skill: str, claims_draft: dict, tasks_draft: dict, out: Path) -> dict:
    """Stage 3, tooling only: write the card, then validate it and drop each
    check that cannot fail or rejects a planted good output. Returns the
    authoring record, also written to `authoring.json` beside the card."""
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    claim_ids = [c["id"] for c in claims_draft["claims"]]
    notes, tasks, seen = [], [], set()
    for i, raw in enumerate(tasks_draft["tasks"]):
        tid = _slug(raw.get("id"), f"task-{i + 1}")
        while tid in seen:
            tid += "-x"
        seen.add(tid)
        claims = [c for c in dict.fromkeys(raw.get("claims") or []) if c in claim_ids]
        if not claims:
            notes.append(f"{tid}: dropped, it probes no known claim")
            continue
        skipped = _write_files(out / "fixtures" / tid, raw.get("files"))
        notes += [f"{tid}: fixture file skipped: {p}" for p in skipped]
        artifacts = [a for a in dict.fromkeys(_safe_rel(a) for a in raw.get("artifacts") or []) if a]
        checks, check_ids = [], set()
        for j, c in enumerate(raw.get("checks") or []):
            target = c.get("target") or "output"
            if target != "output":
                target = _safe_rel(target)
                if target is None:
                    notes.append(f"{tid}: check with an unsafe target dropped")
                    continue
                if target not in artifacts:
                    artifacts.append(target)
            cid = _slug(c.get("id"), f"check-{j + 1}")
            while cid in check_ids:
                cid += "-x"
            check_ids.add(cid)
            check = {"id": cid, "kind": c.get("kind"), "target": target, "claim": c.get("claim")}
            if check["kind"] != "file_exists":
                check["value"] = c.get("value", "")
                if check["kind"] == "regex":
                    try:
                        re.compile(check["value"])
                    except re.error:
                        notes.append(f"{tid}: check {cid} dropped, invalid regex")
                        continue
                if not check["value"]:
                    notes.append(f"{tid}: check {cid} dropped, empty value")
                    continue
            elif target == "output":
                notes.append(f"{tid}: check {cid} dropped, file_exists needs an artifact")
                continue
            if check["claim"] not in claims:
                notes.append(f"{tid}: check {cid} dropped, its claim is not one the task probes")
                continue
            checks.append(check)
        assertions, assertion_ids = [], set()
        for j, a in enumerate(raw.get("assertions") or []):
            aid = _slug(a.get("id"), f"assertion-{j + 1}")
            while aid in assertion_ids:
                aid += "-x"
            assertion_ids.add(aid)
            if a.get("claim") in claims and str(a.get("text") or "").strip():
                assertions.append({"id": aid, "text": a["text"].strip(), "claim": a["claim"]})
        planted, counts = [], {"good": 0, "bad": 0}
        for sample in raw.get("planted") or []:
            expect = sample.get("expect")
            if expect not in counts:
                continue
            counts[expect] += 1
            rel = f"planted/{tid}/{expect}-{counts[expect]}"
            (out / rel / "artifacts").mkdir(parents=True)
            (out / rel / "output.txt").write_text(sample.get("output", ""), encoding="utf-8")
            _write_files(out / rel / "artifacts", sample.get("files"))
            planted.append({"path": rel, "expect": expect})
        task = {"id": tid, "kind": raw.get("kind") if raw.get("kind") in performance.TASK_KINDS else "deliverable",
                "claims": claims, "prompt": str(raw.get("prompt") or "").strip(),
                "workspace": f"fixtures/{tid}" if (out / "fixtures" / tid).is_dir() else "empty",
                "artifacts": artifacts, "checks": checks, "assertions": assertions, "planted": planted}
        if not task["prompt"] or not (checks or assertions):
            notes.append(f"{tid}: dropped, no prompt or no evidence")
            continue
        tasks.append(task)
    invalidation = {"SKILL.md": "all"}
    for claim in claims_draft["claims"]:
        for rel in claim["rests_on"]:
            if rel != "SKILL.md":
                invalidation.setdefault(rel, [])
                if isinstance(invalidation[rel], list) and claim["id"] not in invalidation[rel]:
                    invalidation[rel].append(claim["id"])
    card = {"version": 2, "claims": claims_draft["claims"], "invalidation": invalidation, "tasks": tasks}
    card_path = out / "card.json"

    def write():
        card_path.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")

    write()

    def validate():
        try:
            return performance.validate_card(card_path)
        except ValueError as exc:
            notes.append(f"card invalid: {exc}")
            return None

    # One pruning pass is enough: validate judges each check on its own, so
    # dropping one check never changes another's verdict. Dropping can still
    # leave a claim without evidence, which the final validation reports.
    dropped_checks = []
    findings = validate()
    bad = {}
    for f in findings or []:
        m = re.match(r"Check (\S+) ", f["message"])
        if f["severity"] == "error" and m and f["task"]:
            bad.setdefault(f["task"], set()).add(m.group(1))
    if bad:
        for task in tasks:
            dropped_checks += [f"{task['id']}/{cid}" for cid in sorted(bad.get(task["id"], ()))]
            task["checks"] = [c for c in task["checks"] if c["id"] not in bad.get(task["id"], ())]
        write()
        findings = validate()
    reference = common.tokenize(" ".join(skill_files(skill).values()))
    echoes = []
    for task in tasks:
        text = task["prompt"] + " " + " ".join(p.read_text(encoding="utf-8")
                                              for p in (out / "fixtures" / task["id"]).rglob("*") if p.is_file()) \
            if (out / "fixtures" / task["id"]).is_dir() else task["prompt"]
        run = _echo(text, reference)
        if run >= ECHO_RUN:
            echoes.append({"task": task["id"], "longest_shared_run": run})
    record = {"skill": skill, "skill_sha": claims_draft["skill_sha"], "assembled_at": common.utc_now(),
              "job": claims_draft["job"], "archetype": claims_draft["archetype"],
              "harm_risks": claims_draft["harm_risks"], "omitted_references": claims_draft.get("omitted_references", []),
              "calls": [claims_draft.get("call"), tasks_draft.get("call")], "notes": notes,
              "dropped_checks": dropped_checks, "skill_echo": echoes,
              "validation": findings if findings is not None else "card invalid"}
    (out / "authoring.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def _default_out(skill: str) -> Path:
    return common.AUDITING_DIR / "suites" / "cards" / skill


def _read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _cmd_claims(args) -> int:
    try:
        draft = draft_claims(args.skill, vendor=args.vendor, model=args.model, effort=args.effort)
    except (StageError, OSError, ValueError) as exc:
        print(f"card claims: {exc}", file=sys.stderr)
        return 3 if isinstance(exc, StageError) else 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(draft, indent=2) + "\n", encoding="utf-8")
    print(args.out)
    return 0


def _cmd_tasks(args) -> int:
    try:
        notes = Path(args.usage_notes).read_text(encoding="utf-8") if args.usage_notes else None
        draft = draft_tasks(_read_json(args.claims), vendor=args.vendor, model=args.model, effort=args.effort,
                            n_tasks=args.n_tasks, usage_notes=notes)
    except (StageError, OSError, ValueError, KeyError) as exc:
        print(f"card tasks: {exc}", file=sys.stderr)
        return 3 if isinstance(exc, StageError) else 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(draft, indent=2) + "\n", encoding="utf-8")
    print(args.out)
    return 0


def _report(record: dict, out: Path) -> int:
    validation = record["validation"]
    errors = [f for f in validation if f["severity"] == "error"] if isinstance(validation, list) else None
    print(f"Card: {out / 'card.json'}")
    print(f"Dropped checks: {', '.join(record['dropped_checks']) or 'none'}")
    for note in record["notes"]:
        print(f"note: {note}")
    for echo in record["skill_echo"]:
        print(f"warning: task {echo['task']} shares {echo['longest_shared_run']} consecutive tokens with the skill")
    if errors is None:
        print("The card is invalid. Regenerate the tasks stage.", file=sys.stderr)
        return 1
    for f in errors:
        print(f"error\t{f['task'] or '-'}\t{f['message']}")
    return 1 if errors else 0


def _cmd_assemble(args) -> int:
    out = args.out or _default_out(args.skill)
    try:
        record = assemble(args.skill, _read_json(args.claims), _read_json(args.tasks), out)
    except (OSError, ValueError, KeyError) as exc:
        print(f"card assemble: {exc}", file=sys.stderr)
        return 2
    return _report(record, out)


def _cmd_draft(args) -> int:
    out = args.out or _default_out(args.skill)
    if args.dry_run:
        print(json.dumps({"skill": args.skill, "calls": 2, "claims_vendor": args.vendor,
                          "tasks_vendor": args.tasks_vendor or args.vendor, "n_tasks": args.n_tasks,
                          "out": str(out)}, indent=2))
        return 0
    try:
        notes = Path(args.usage_notes).read_text(encoding="utf-8") if args.usage_notes else None
        claims = draft_claims(args.skill, vendor=args.vendor, model=args.model, effort=args.effort)
        tasks = draft_tasks(claims, vendor=args.tasks_vendor or args.vendor,
                            model=args.tasks_model or args.model, effort=args.effort,
                            n_tasks=args.n_tasks, usage_notes=notes)
        draft_dir = common.RUNS_DIR / common.run_id(f"card-{args.skill}")
        draft_dir.mkdir(parents=True)
        (draft_dir / "claims.json").write_text(json.dumps(claims, indent=2) + "\n", encoding="utf-8")
        (draft_dir / "tasks.json").write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
        record = assemble(args.skill, claims, tasks, out)
    except (StageError, OSError, ValueError, KeyError) as exc:
        print(f"card draft: {exc}", file=sys.stderr)
        return 3 if isinstance(exc, StageError) else 2
    print(f"Stage outputs: {draft_dir}")
    return _report(record, out)


def _skill_arg(raw: str) -> str:
    if raw not in common.library_skills():
        raise argparse.ArgumentTypeError(f"unknown library skill: {raw}")
    return raw


def add_subparser(subparsers) -> None:
    parser = subparsers.add_parser("card", help="Author an eval card with isolated agents, in stages.")
    sub = parser.add_subparsers(dest="subcommand", required=True)

    def common_args(cmd, tasks_stage=False):
        cmd.add_argument("--vendor", choices=common.VENDORS, default="claude")
        cmd.add_argument("--model")
        cmd.add_argument("--effort", default="medium")
        if tasks_stage:
            cmd.add_argument("--n-tasks", type=performance._positive_int, default=DEFAULT_TASKS)
            cmd.add_argument("--usage-notes", help="a text file of real-use excerpts for the tasks author")

    cmd = sub.add_parser("draft", help="Run claims, tasks, and assemble. Two calls.")
    cmd.add_argument("--skill", type=_skill_arg, required=True)
    common_args(cmd, tasks_stage=True)
    cmd.add_argument("--tasks-vendor", choices=common.VENDORS, help="tasks author vendor (default: --vendor)")
    cmd.add_argument("--tasks-model")
    cmd.add_argument("--out", type=Path, help="card directory (default scripts/auditing/suites/cards/<skill>)")
    cmd.add_argument("--dry-run", action="store_true")
    cmd.set_defaults(func=_cmd_draft)

    cmd = sub.add_parser("claims", help="Stage 1: the claims author reads the skill. One call.")
    cmd.add_argument("--skill", type=_skill_arg, required=True)
    common_args(cmd)
    cmd.add_argument("--out", type=Path, required=True)
    cmd.set_defaults(func=_cmd_claims)

    cmd = sub.add_parser("tasks", help="Stage 2: the tasks author never sees the skill. One call.")
    cmd.add_argument("--claims", type=Path, required=True)
    common_args(cmd, tasks_stage=True)
    cmd.add_argument("--out", type=Path, required=True)
    cmd.set_defaults(func=_cmd_tasks)

    cmd = sub.add_parser("assemble", help="Stage 3: write and validate the card. Free.")
    cmd.add_argument("--skill", type=_skill_arg, required=True)
    cmd.add_argument("--claims", type=Path, required=True)
    cmd.add_argument("--tasks", type=Path, required=True)
    cmd.add_argument("--out", type=Path)
    cmd.set_defaults(func=_cmd_assemble)
