"""Material isolation: sealed evaluation sets, leak scanning, brute-pass diff scanning.

Owns T-C from DESIGN.md §2: a skill must never absorb its own evaluation
material (holdout prompts, assertion text) or leak a sealed-file canary into
`skills/`. See DESIGN.md §3 "integrity.py" for the contract this module
implements.

Stdlib-only. No network, subprocess (outside `diff_scan`), or agent call at
import time or in unit tests.
"""
from __future__ import annotations

import argparse
import base64
import dataclasses
import json
import subprocess
import sys
import uuid
import zlib
from pathlib import Path
from typing import Iterable

from .cases import load_cases
from .common import (
    Finding,
    SEALED_DIR,
    SKILLS_DIR,
    TRIGGER_CASES_DIR,
    REPO_ROOT,
    ngrams,
    longest_common_run,
    sha256_text,
    tokenize,
    utc_now,
)

# Chosen default (DESIGN.md §3: "n (default 8, a chosen default)"). Not a
# measured threshold on its own; §6 of the T4 task packet asks for a measured
# false-positive count at n=6, 8, and 10 on the live library so an operator
# can judge it. See the task deliverable for those numbers.
DEFAULT_N = 8

# Chosen default (review finding I8). A material shorter than `n` tokens
# produced no n-grams at all under the old scheme, so it could be pasted
# verbatim and never match. Each material is now indexed at
# max(FLOOR_N, min(n, len(tokens))), so a 5-token holdout prompt matches on
# a 5-token shared run instead of needing 8. Materials shorter than FLOOR_N
# tokens still cannot be fingerprinted this way and are skipped; 3 is picked
# so a 3-token run is not so short it mostly fires on coincidence.
FLOOR_N = 3

_CANARY_PREFIX = "SKILL-EVAL-CANARY-"

_NOTICE = (
    "This file holds evaluation material (holdout cases or assertions). "
    "Decoding it into an authoring context (a skill body, a prompt an author "
    "can see) voids the evaluation. See DESIGN.md section 2, T-C."
)


# ---------------------------------------------------------------------------
# Sealing
# ---------------------------------------------------------------------------


def _validate_holdout(payload: dict) -> None:
    if not isinstance(payload, dict) or "cases" not in payload:
        raise ValueError("holdout source must be a JSON object with a 'cases' list")
    cases = payload["cases"]
    if not isinstance(cases, list) or not cases:
        raise ValueError("holdout 'cases' must be a non-empty list")
    for i, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"holdout case {i} must be an object")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise ValueError(f"holdout case {i} needs a non-empty string 'prompt'")
        if not isinstance(case.get("expect"), bool):
            raise ValueError(f"holdout case {i} needs a boolean 'expect'")
        tags = case.get("tags", [])
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            raise ValueError(f"holdout case {i} 'tags' must be a list of strings")


def _validate_assertions(payload: dict) -> None:
    if not isinstance(payload, dict) or "assertions" not in payload:
        raise ValueError("assertions source must be a JSON object with an 'assertions' list")
    assertions = payload["assertions"]
    if not isinstance(assertions, list) or not assertions:
        raise ValueError("assertions 'assertions' must be a non-empty list")
    for i, a in enumerate(assertions):
        if not isinstance(a, dict):
            raise ValueError(f"assertion {i} must be an object")
        if not isinstance(a.get("id"), str) or not a["id"].strip():
            raise ValueError(f"assertion {i} needs a non-empty string 'id'")
        if not isinstance(a.get("text"), str) or not a["text"].strip():
            raise ValueError(f"assertion {i} needs a non-empty string 'text'")


_VALIDATORS = {"holdout": _validate_holdout, "assertions": _validate_assertions}


def sealed_path(skill: str, kind: str, sealed_dir: Path = SEALED_DIR) -> Path:
    return sealed_dir / f"{skill}.{kind}.sealed"


def seal(src: Path, skill: str, kind: str, *, sealed_dir: Path = SEALED_DIR,
          force: bool = False) -> Path:
    """Seal `src` (a JSON holdout or assertions file) for `skill`.

    Writes `sealed_dir/<skill>.<kind>.sealed`: a one-line plain-JSON header
    (readable without decoding the payload) followed by a base64 line holding
    zlib-compressed JSON. The canary is embedded both in the header and in
    the plaintext payload, so a leak of either half is detectable.
    """
    if kind not in _VALIDATORS:
        raise ValueError(f"kind must be one of {sorted(_VALIDATORS)}, got {kind!r}")
    src = Path(src)
    payload = json.loads(src.read_text(encoding="utf-8"))
    _VALIDATORS[kind](payload)

    dest = sealed_path(skill, kind, sealed_dir)
    if dest.exists() and not force:
        raise FileExistsError(
            f"{dest} already exists; pass force=True (CLI: --force) to overwrite"
        )

    canary = f"{_CANARY_PREFIX}{uuid.uuid4()}"
    plaintext_obj = dict(payload)
    plaintext_obj["canary"] = canary
    plaintext_json = json.dumps(plaintext_obj, sort_keys=True, ensure_ascii=False)
    digest = sha256_text(plaintext_json)
    compressed = zlib.compress(plaintext_json.encode("utf-8"))
    b64 = base64.b64encode(compressed).decode("ascii")

    header = {
        "skill": skill,
        "kind": kind,
        "canary": canary,
        "sha256": digest,
        "created_at": utc_now(),
        "notice": _NOTICE,
    }

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(header, sort_keys=True, ensure_ascii=False) + "\n")
        fh.write(b64 + "\n")
    return dest


def read_header(path: Path) -> dict:
    """Read only the first line: plain JSON, no payload decoding."""
    with Path(path).open(encoding="utf-8") as fh:
        line = fh.readline()
    return json.loads(line)


def unseal(path: Path) -> dict:
    """Decode a sealed file in memory. Verifies the sha256 and the canary.

    Returns the header dict plus a `payload` key holding the decoded JSON
    object (which itself still carries the embedded `canary`).
    """
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        header_line = fh.readline()
        b64 = fh.read().strip()
    header = json.loads(header_line)
    try:
        compressed = base64.b64decode(b64)
        plaintext_json = zlib.decompress(compressed).decode("utf-8")
    except Exception as exc:  # noqa: BLE001 - re-raised as a loud, specific error
        raise ValueError(f"{path}: payload is not valid sealed data: {exc}") from exc

    computed = sha256_text(plaintext_json)
    if computed != header.get("sha256"):
        raise ValueError(
            f"{path}: sha256 mismatch (expected {header.get('sha256')}, got {computed}); "
            "the sealed file may be tampered or corrupted"
        )
    payload = json.loads(plaintext_json)
    if payload.get("canary") != header.get("canary"):
        raise ValueError(f"{path}: canary mismatch between header and payload")
    out = dict(header)
    out["payload"] = payload
    return out


def list_sealed(sealed_dir: Path = SEALED_DIR) -> list[dict]:
    out = []
    if not sealed_dir.exists():
        return out
    for p in sorted(sealed_dir.glob("*.sealed")):
        try:
            header = read_header(p)
        except Exception as exc:  # noqa: BLE001
            header = {"skill": "?", "kind": "?", "error": str(exc)}
        header["path"] = str(p)
        out.append(header)
    return out


# ---------------------------------------------------------------------------
# Trigger-case prompts: loaded through cases.load_cases -- cases.py owns the
# real parser, the only one that reliably handles single-quoted and bare
# prompts against the real corpus format.
# ---------------------------------------------------------------------------


def load_all_trigger_prompts(trigger_dir: Path = TRIGGER_CASES_DIR) -> list[dict]:
    """{skill, prompt, expect} rows for every trigger-cases/<skill>.md file."""
    out: list[dict] = []
    trigger_dir = Path(trigger_dir)
    if not trigger_dir.exists():
        return out
    for p in sorted(trigger_dir.glob("*.md")):
        if p.name.lower() == "readme.md":
            continue
        skill = p.stem
        for case in load_cases(skill, path=p):
            out.append({"skill": skill, "prompt": case.prompt, "expect": case.expect})
    return out


# ---------------------------------------------------------------------------
# Materials index: one n-gram lookup built once, reused across every file
# scanned. Each material carries its own kind and owning skill so severity
# is decided per (file's skill, material) pair at query time.
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class _Material:
    kind: str          # "holdout" | "assertions" | "trigger"
    owner_skill: str
    ref_id: str        # short, human-readable label for messages (may be truncated)
    mid: str           # stable id over the FULL material text; used for dedup (finding I-minor)
    tokens: tuple      # tuple of tokens, hashable


@dataclasses.dataclass
class _Materials:
    items: list          # list[_Material]
    index: dict           # ngram tuple -> list[_Material]
    canaries: list        # list[(canary_str, sealed_path_str, sealed_skill)]
    lengths: set          # distinct n-gram lengths actually indexed (see FLOOR_N, finding I8)
    broken: list          # list[Finding] for sealed files that could not be read (finding: minor)
    skipped: list          # list[Finding] for holdout/assertions material under FLOOR_N tokens
                            # (finding I-review: silently skipped material must be visible); each
                            # Finding's `path` carries the owning skill so scan() can filter to it.


def _effective_n(token_count: int, n: int) -> int | None:
    """The n-gram length to index one material at (finding I8).

    A material with fewer than FLOOR_N tokens cannot be fingerprinted this
    way at all and is skipped (returns None). Otherwise it is indexed at
    max(FLOOR_N, min(n, token_count)), so a short material still gets a
    shorter-but-real n-gram instead of producing no n-grams at all.
    """
    if token_count < FLOOR_N:
        return None
    return max(FLOOR_N, min(n, token_count))


def _sealed_materials_for(skill: str | None, sealed_dir: Path) -> tuple[list[_Material], list[Finding]]:
    """Unseal every sealed file under sealed_dir; restrict to `skill` when given.

    Returns (materials, broken) -- `broken` holds one Finding per sealed file
    that could not be read (corrupt header, tampered payload), instead of
    raising and killing the whole scan (review finding: minor).
    """
    out: list[_Material] = []
    broken: list[Finding] = []
    sealed_dir = Path(sealed_dir)
    if not sealed_dir.exists():
        return out, broken
    for p in sorted(sealed_dir.glob("*.sealed")):
        try:
            header = read_header(p)
        except (OSError, json.JSONDecodeError) as exc:
            broken.append(Finding("error", "corrupt-sealed-file",
                                   f"{p}: unreadable sealed header: {exc}", str(p)))
            continue
        owner = header.get("skill", "")
        if skill is not None and owner != skill:
            continue
        try:
            data = unseal(p)
        except ValueError as exc:
            broken.append(Finding("error", "corrupt-sealed-file", str(exc), str(p)))
            continue
        kind = data.get("kind")
        payload = data.get("payload", {})
        if kind == "holdout":
            for case in payload.get("cases", []):
                prompt = case.get("prompt", "")
                mid = sha256_text(prompt)
                # I-review (holdout-leak label): never carry holdout prompt
                # text into a label that a `scan`/`diff-scan` finding message
                # can print. The material has no id of its own in the
                # holdout schema, so the label is the material id and a
                # sha256 prefix -- never the prompt itself.
                out.append(_Material(
                    kind="holdout", owner_skill=owner,
                    ref_id=f"sha256:{mid[:12]}", mid=mid,
                    tokens=tuple(tokenize(prompt)),
                ))
        elif kind == "assertions":
            for a in payload.get("assertions", []):
                text = a.get("text", "")
                a_id = a.get("id", "")
                mid = sha256_text(text)
                # Same guard as holdout: the label is the assertion's own id
                # (a short, non-sensitive label the evaluator chose) plus a
                # sha256 prefix, never the assertion text itself.
                ref_id = f"id={a_id} sha256:{mid[:12]}" if a_id else f"sha256:{mid[:12]}"
                out.append(_Material(
                    kind="assertions", owner_skill=owner,
                    ref_id=ref_id, mid=mid,
                    tokens=tuple(tokenize(text)),
                ))
    return out, broken


def _canaries_in(sealed_dir: Path) -> list[tuple]:
    out = []
    sealed_dir = Path(sealed_dir)
    if not sealed_dir.exists():
        return out
    for p in sorted(sealed_dir.glob("*.sealed")):
        try:
            header = read_header(p)
        except Exception:  # noqa: BLE001
            continue
        canary = header.get("canary")
        if canary:
            out.append((canary, str(p), header.get("skill", "?")))
    return out


def _trigger_materials(trigger_dir: Path) -> list[_Material]:
    out = []
    for row in load_all_trigger_prompts(trigger_dir):
        out.append(_Material(
            kind="trigger", owner_skill=row["skill"],
            ref_id=row["prompt"][:40], mid=sha256_text(row["prompt"]),
            tokens=tuple(tokenize(row["prompt"])),
        ))
    return out


def build_materials(*, n: int, skill_for_sealed: str | None,
                     sealed_dir: Path = SEALED_DIR,
                     trigger_dir: Path = TRIGGER_CASES_DIR) -> _Materials:
    """Build the n-gram index once. Reused across every file a scan touches.

    `skill_for_sealed` is kept for callers that want to restrict sealed
    material to one owner; `scan()`/`diff_scan()` now always pass None so a
    scanned skill is checked against every sealed set in the library, not
    only its own (finding I10: another skill's sealed material pasted into
    this skill is exactly as real a leak as this skill's own).
    """
    sealed_items, broken = _sealed_materials_for(skill_for_sealed, sealed_dir)
    items = sealed_items + _trigger_materials(trigger_dir)
    index: dict = {}
    lengths: set = set()
    skipped: list[Finding] = []
    for m in items:
        eff_n = _effective_n(len(m.tokens), n)
        if eff_n is None:
            # Holdout/assertions material too short to fingerprint at all
            # (finding: this was silently dropped before). Trigger-case
            # prompts are visible by design already, so only sealed material
            # is worth flagging here. `path` carries the owning skill so
            # scan() can show it only against that skill's own findings.
            if m.kind in ("holdout", "assertions"):
                skipped.append(Finding(
                    severity="info", code="material-too-short",
                    message=(
                        f"{m.kind} material [{m.ref_id}] has fewer than {FLOOR_N} tokens "
                        "and cannot be fingerprinted for leak scanning; it is skipped, "
                        "not checked"
                    ),
                    path=m.owner_skill,
                ))
            continue
        lengths.add(eff_n)
        for gram in ngrams(list(m.tokens), eff_n):
            index.setdefault(gram, []).append(m)
    canaries = _canaries_in(sealed_dir)
    return _Materials(items=items, index=index, canaries=canaries, lengths=lengths,
                       broken=broken, skipped=skipped)


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------


def _severity_for(material: _Material, scanned_skill: str) -> tuple[str, str] | None:
    """Return (severity, code) for a material hit against `scanned_skill`.

    Sealed material (holdout or assertions) is never legitimate in any
    skill: this skill's own is an error, and so is another skill's --
    whoever tunes skill Y can read Y's holdout in plaintext once it is
    pasted into skill X, and in a competitive run X absorbing Y's holdout
    negatives lets X take Y's activations (finding I10). Plain trigger-case
    prompts stay warn for the owner (visible by design) and info for
    another skill (a useful signal, not proof of a leak).
    """
    if material.kind in ("holdout", "assertions"):
        code = "holdout-leak" if material.kind == "holdout" else "assertions-leak"
        return "error", code
    # trigger
    if material.owner_skill == scanned_skill:
        return "warn", "trigger-case-echo"
    return "info", "cross-skill-trigger-echo"


def _scan_text(*, label: str, text: str, scanned_skill: str,
               materials: _Materials, n: int) -> list[Finding]:
    findings: list[Finding] = []

    # Canary check: cheap substring search, independent of n-gram matching.
    lowered = text.lower()
    for canary, sealed_file, sealed_skill in materials.canaries:
        if canary.lower() in lowered:
            findings.append(Finding(
                severity="error", code="canary-leak",
                message=(
                    f"canary from sealed file {sealed_file} (skill={sealed_skill}) "
                    f"found in {label}"
                ),
                path=label,
            ))

    tokens = tokenize(text)
    if not tokens or not materials.index:
        return findings

    # Each material is indexed at its own effective n-gram length (finding
    # I8), so the file must be n-grammed at every length actually in use,
    # not just the caller's `n`.
    file_grams: set = set()
    for length in materials.lengths:
        file_grams |= ngrams(tokens, length)
    hit_grams = file_grams & materials.index.keys()
    if not hit_grams:
        return findings

    # Dedup key uses the material's full-text id (mid), not a 40-char ref_id
    # prefix, so two distinct materials that share the same 40-character
    # prefix are reported as separate findings rather than collapsed into one.
    seen: set[tuple[str, str, str]] = set()
    for gram in hit_grams:
        for material in materials.index[gram]:
            key = (material.kind, material.owner_skill, material.mid)
            if key in seen:
                continue
            sev = _severity_for(material, scanned_skill)
            if sev is None:
                continue
            seen.add(key)
            severity, code = sev
            run_len = longest_common_run(list(material.tokens), tokens)
            snippet = " ".join(gram)
            owner_note = (
                "" if material.owner_skill == scanned_skill
                else " (belongs to another skill, not this one)"
            )
            findings.append(Finding(
                severity=severity, code=code,
                message=(
                    f"shared token run (len={run_len}, min-n={len(gram)}) with {material.kind} "
                    f"material owned by '{material.owner_skill}'{owner_note} "
                    f"[{material.ref_id!r}]: …{snippet}…"
                ),
                path=label,
            ))
    return findings


def _skill_files(skill: str, skills_dir: Path) -> list[Path]:
    """Every file under skills/<skill>/, regardless of extension.

    `vendors.build_home` copies the whole skill directory into an arm, so a
    suffix allowlist (the old `_TEXT_SUFFIXES`) let material in
    `references/`, `cases.csv`, `.js`, `.toml`, suffix-less files, or
    gitignored files reach the arm unscanned (finding I9). `_read_text`
    decides text-vs-binary by content instead.
    """
    root = Path(skills_dir) / skill
    if not root.exists():
        return []
    return [p for p in sorted(root.rglob("*")) if p.is_file()]


def _read_text(path: Path) -> str | None:
    """Read a file as text, or None when it is not decodable UTF-8 text.

    A NUL byte anywhere in the file is treated as a binary marker (the same
    heuristic `git`, `grep -I`, and `file` use) so a binary asset shipped
    with a skill is skipped without needing an extension allowlist.
    """
    try:
        data = Path(path).read_bytes()
    except OSError:
        return None
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def scan(skill: str, *, n: int = DEFAULT_N, skills_dir: Path = SKILLS_DIR,
          sealed_dir: Path = SEALED_DIR, trigger_dir: Path = TRIGGER_CASES_DIR,
          materials: _Materials | None = None) -> list[Finding]:
    """Scan every file under skills/<skill>/ against evaluation material.

    Errors: any canary from any sealed file; a shared token run with any
    sealed holdout or assertions in the library, this skill's own or
    another skill's (finding I10). Warnings: a shared token run with this
    skill's own plain trigger-case prompts. Info: the same against another
    skill's trigger-case prompts (useful, not proof of a leak); also, for
    this skill's own holdout/assertions material, a material too short to
    fingerprint (fewer than FLOOR_N tokens) that was silently skipped, so
    the gap is visible instead of hidden. A sealed file that cannot be
    decoded is reported as a `corrupt-sealed-file` error instead of raising
    (finding: minor).
    """
    if materials is None:
        materials = build_materials(n=n, skill_for_sealed=None,
                                     sealed_dir=sealed_dir, trigger_dir=trigger_dir)
    findings: list[Finding] = list(materials.broken)
    findings.extend(f for f in materials.skipped if f.path == skill)
    root = Path(skills_dir) / skill
    for path in _skill_files(skill, skills_dir):
        text = _read_text(path)
        if text is None:
            continue
        try:
            rel = str(path.relative_to(root.parent))
        except ValueError:
            rel = str(path)
        findings.extend(_scan_text(label=rel, text=text, scanned_skill=skill,
                                    materials=materials, n=n))
    return findings


def scan_all(*, n: int = DEFAULT_N, skills_dir: Path = SKILLS_DIR,
              sealed_dir: Path = SEALED_DIR,
              trigger_dir: Path = TRIGGER_CASES_DIR) -> dict[str, list[Finding]]:
    """Scan every skill in the library. Builds the materials index once."""
    materials = build_materials(n=n, skill_for_sealed=None,
                                 sealed_dir=sealed_dir, trigger_dir=trigger_dir)
    skills_dir = Path(skills_dir)
    skills = sorted(p.parent.name for p in skills_dir.glob("*/SKILL.md"))
    out: dict[str, list[Finding]] = {}
    for skill in skills:
        # build_materials(skill_for_sealed=None) already includes every
        # sealed skill's items; _severity_for now treats any sealed hit as
        # an error regardless of owner (I10), so reuse is correct as-is.
        out[skill] = scan(skill, n=n, skills_dir=skills_dir, sealed_dir=sealed_dir,
                          trigger_dir=trigger_dir, materials=materials)
    return out


def canary_search(*, skills_dir: Path = SKILLS_DIR,
                   sealed_dir: Path = SEALED_DIR) -> list[Finding]:
    """Search the whole skills/ tree for any sealed-file canary."""
    canaries = _canaries_in(sealed_dir)
    findings: list[Finding] = []
    if not canaries:
        return findings
    skills_dir = Path(skills_dir)
    for path in sorted(skills_dir.rglob("*")):
        if not path.is_file():
            continue
        text = _read_text(path)
        if text is None:
            continue
        lowered = text.lower()
        rel = str(path.relative_to(skills_dir.parent))
        for canary, sealed_file, sealed_skill in canaries:
            if canary.lower() in lowered:
                findings.append(Finding(
                    severity="error", code="canary-leak",
                    message=(
                        f"canary from sealed file {sealed_file} (skill={sealed_skill}) "
                        f"found in {rel}"
                    ),
                    path=rel,
                ))
    return findings


# ---------------------------------------------------------------------------
# Diff scanning: the brute-pass check on lines added since a git ref.
# ---------------------------------------------------------------------------


def parse_added_lines(diff_text: str) -> list[str]:
    """Pure function: pull added-line content out of a unified=0 git diff.

    A `+++ b/...` file header line is skipped only when it appears before
    that file section's first `@@` hunk marker, which is the only place a
    real diff ever emits one. Without that guard, an added line whose
    *content* begins with `++` (rendered as `+++...` once the diff's own
    leading `+` is added) was indistinguishable from the header and got
    silently dropped (review finding I-minor). `diff --git` resets the
    per-file state so a multi-file diff parses each section independently.
    """
    out: list[str] = []
    seen_hunk = False
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            seen_hunk = False
            continue
        if line.startswith("@@"):
            seen_hunk = True
            continue
        if line.startswith("+++") and not seen_hunk:
            continue
        if line.startswith("+"):
            out.append(line[1:])
    return out


class GitError(RuntimeError):
    """A git call needed by diff_scan failed (e.g. an unknown ref)."""


def _git(args: list[str], cwd: Path) -> str:
    """Run git and return stdout, or raise GitError with a clean message.

    `--no-color` and `--no-ext-diff` keep the output plain and independent
    of the caller's git config (review finding I-minor), which matters
    because `parse_added_lines` parses that output structurally.
    """
    try:
        result = subprocess.run(
            ["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise GitError(f"git {' '.join(args)} failed: {stderr or exc}") from exc
    except OSError as exc:
        raise GitError(f"git {' '.join(args)} could not run: {exc}") from exc
    return result.stdout


def diff_scan(skill: str, base_ref: str, *, n: int = DEFAULT_N,
               skills_dir: Path = SKILLS_DIR, sealed_dir: Path = SEALED_DIR,
               trigger_dir: Path = TRIGGER_CASES_DIR,
               repo_root: Path = REPO_ROOT) -> list[Finding]:
    """Scan lines added to skills/<skill>/ since base_ref for evaluation-material leaks.

    Covers tracked changes (`git diff --unified=0`) and every untracked file
    in the skill directory, tracked-ignore status or not (`git ls-files
    --others` with no `--exclude-standard`, so a `.gitignore`'d file still
    gets scanned -- finding I9), whose whole content counts as "added". A
    bad `base_ref` is reported as a `bad-git-ref` error Finding instead of
    raising a traceback (review finding: minor).
    """
    rel_dir = f"skills/{skill}/"
    try:
        diff_text = _git(["diff", "--no-color", "--no-ext-diff", "--unified=0",
                           base_ref, "--", rel_dir], repo_root)
    except GitError as exc:
        return [Finding("error", "bad-git-ref", str(exc), rel_dir)]
    added_lines = parse_added_lines(diff_text)

    try:
        untracked = _git(["ls-files", "--others", "--", rel_dir], repo_root)
    except GitError as exc:
        return [Finding("error", "bad-git-ref", str(exc), rel_dir)]
    for rel_path in untracked.splitlines():
        if not rel_path.strip():
            continue
        full = Path(repo_root) / rel_path
        text = _read_text(full)
        if text is not None:
            added_lines.extend(text.splitlines())

    materials = build_materials(n=n, skill_for_sealed=None,
                                 sealed_dir=sealed_dir, trigger_dir=trigger_dir)
    combined = "\n".join(added_lines)
    findings = list(materials.broken)
    findings.extend(_scan_text(label=f"skills/{skill}/<added-lines vs {base_ref}>",
                                text=combined, scanned_skill=skill, materials=materials, n=n))
    return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _finding_to_dict(f: Finding) -> dict:
    return dataclasses.asdict(f)


def _print_findings(findings: Iterable[Finding], *, as_json: bool) -> None:
    findings = list(findings)
    if as_json:
        print(json.dumps([_finding_to_dict(f) for f in findings], indent=2, sort_keys=True))
        return
    if not findings:
        print("no findings")
        return
    for f in findings:
        print(f"[{f.severity:5}] {f.code:26} {f.path}: {f.message}")


def _cmd_seal(args: argparse.Namespace) -> int:
    try:
        dest = seal(Path(args.src), args.skill, args.kind, force=args.force)
    except (ValueError, FileExistsError) as exc:
        print(f"integrity seal: {exc}", file=sys.stderr)
        return 1
    print(f"sealed {args.skill}.{args.kind} -> {dest}")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    rows = list_sealed()
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0
    if not rows:
        print("no sealed files")
        return 0
    for r in rows:
        if "error" in r:
            print(f"{r.get('path')}: UNREADABLE ({r['error']})")
            continue
        print(f"{r['skill']:30} {r['kind']:12} created={r['created_at']} sha256={r['sha256'][:12]}…")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    try:
        data = unseal(Path(args.file))
    except ValueError as exc:
        print(f"integrity show: {exc}", file=sys.stderr)
        return 1
    print("=" * 70)
    print("EVALUATION MATERIAL — do not paste this into a skill, a prompt an")
    print("author can see, or any other authoring context. Doing so voids the")
    print("evaluation (DESIGN.md section 2, T-C).")
    print("=" * 70)
    print(json.dumps(data["payload"], indent=2, sort_keys=True))
    return 0


def _has_error(findings: Iterable[Finding]) -> bool:
    return any(f.severity == "error" for f in findings)


# Codes for an operational failure (a bad ref, an unreadable sealed file)
# rather than a genuine content finding. The CLI reports these as a clean
# one-line message on stderr and exits 2, distinct from the normal "findings
# present" exit 1 (review finding: minor).
_OPERATIONAL_CODES = {"bad-git-ref", "corrupt-sealed-file"}


def _operational_failure(findings: Iterable[Finding], *, command: str) -> int | None:
    for f in findings:
        if f.code in _OPERATIONAL_CODES:
            print(f"integrity {command}: {f.message}", file=sys.stderr)
            return 2
    return None


def _cmd_scan(args: argparse.Namespace) -> int:
    findings = scan(args.skill, n=args.n)
    failed = _operational_failure(findings, command="scan")
    if failed is not None:
        return failed
    _print_findings(findings, as_json=args.json)
    return 1 if _has_error(findings) else 0


def _cmd_scan_all(args: argparse.Namespace) -> int:
    by_skill = scan_all(n=args.n)
    all_findings = [f for fs in by_skill.values() for f in fs]
    failed = _operational_failure(all_findings, command="scan-all")
    if failed is not None:
        return failed
    if args.json:
        print(json.dumps(
            {skill: [_finding_to_dict(f) for f in fs] for skill, fs in by_skill.items()},
            indent=2, sort_keys=True,
        ))
    else:
        for skill, fs in by_skill.items():
            if fs:
                print(f"== {skill} ==")
                _print_findings(fs, as_json=False)
        if not all_findings:
            print("no findings across the library")
    return 1 if _has_error(all_findings) else 0


def _cmd_diff_scan(args: argparse.Namespace) -> int:
    findings = diff_scan(args.skill, args.base, n=args.n)
    failed = _operational_failure(findings, command="diff-scan")
    if failed is not None:
        return failed
    _print_findings(findings, as_json=args.json)
    return 1 if _has_error(findings) else 0


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "integrity",
        help="seal evaluation material, scan skills for leaked material, brute-pass diff scan",
    )
    sub = p.add_subparsers(dest="integrity_command", required=True)

    p_seal = sub.add_parser("seal", help="seal a holdout or assertions JSON source file")
    p_seal.add_argument("--skill", required=True)
    p_seal.add_argument("--kind", required=True, choices=sorted(_VALIDATORS))
    p_seal.add_argument("--src", required=True, help="path to the plaintext JSON source")
    p_seal.add_argument("--force", action="store_true")
    p_seal.set_defaults(func=_cmd_seal)

    p_list = sub.add_parser("list", help="list sealed files (header only, no decoding)")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=_cmd_list)

    p_show = sub.add_parser("show", help="decode and print a sealed file's plaintext")
    p_show.add_argument("file")
    p_show.set_defaults(func=_cmd_show)

    p_scan = sub.add_parser("scan", help="scan one skill for leaked evaluation material")
    p_scan.add_argument("--skill", required=True)
    p_scan.add_argument("-n", "--n", type=int, default=DEFAULT_N)
    p_scan.add_argument("--json", action="store_true")
    p_scan.set_defaults(func=_cmd_scan)

    p_scan_all = sub.add_parser("scan-all", help="scan every skill in the library")
    p_scan_all.add_argument("-n", "--n", type=int, default=DEFAULT_N)
    p_scan_all.add_argument("--json", action="store_true")
    p_scan_all.set_defaults(func=_cmd_scan_all)

    p_diff = sub.add_parser("diff-scan", help="scan lines added to a skill since a git ref")
    p_diff.add_argument("--skill", required=True)
    p_diff.add_argument("--base", required=True)
    p_diff.add_argument("-n", "--n", type=int, default=DEFAULT_N)
    p_diff.add_argument("--json", action="store_true")
    p_diff.set_defaults(func=_cmd_diff_scan)
