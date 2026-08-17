#!/usr/bin/env python3
"""Resolve a PPTX relationship graph and report package-integrity findings.

Slide order lives in `ppt/presentation.xml` and its relationship part, never in
member filenames: `ppt/slides/slide7.xml` can be the second slide, or can be a
part no longer referenced by the presentation at all. This script resolves the
graph and reports the parts that do not hang together.

Read-only: it opens the archive, never writes into it, and never copies parts
out of it.

Usage:
    python3 scripts/pptx_package_check.py deck.pptx [--json]

Requires: Python 3.10+ with access to the local filesystem. Standard library
only; no external packages.

Exit codes: 0 = no findings, 1 = errors or warnings reported, 2 = the file
could not be read as a PPTX package.

Verification: on a deck saved after its slides were reordered in PowerPoint,
the printed order differs from numeric filename order. A deck that opens
cleanly in PowerPoint and reports errors here means the checks are wrong;
a deck PowerPoint repairs on open should report at least one error.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import stat
import sys
import xml.etree.ElementTree as ET
import zipfile
from typing import Any, Dict, List, Optional, Tuple

PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
OFFICE_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PML = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
SLIDE_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
)

# Chosen defaults, not measured limits. They exist so a corrupt or hostile
# archive cannot exhaust memory before any XML is parsed; raise them for a
# legitimately huge deck rather than removing the guard.
MAX_MEMBERS = 5000
MAX_MEMBER_BYTES = 100 * 1024 * 1024
MAX_TOTAL_BYTES = 512 * 1024 * 1024
MAX_COMPRESSION_RATIO = 1000


def _guard_archive(zf: zipfile.ZipFile) -> None:
    members = zf.infolist()
    if len(members) > MAX_MEMBERS:
        raise ValueError(f"archive holds more than {MAX_MEMBERS} entries")
    total = 0
    for member in members:
        if stat.S_ISLNK(member.external_attr >> 16):
            raise ValueError(f"archive holds a symlink: {member.filename}")
        if member.file_size > MAX_MEMBER_BYTES:
            raise ValueError(f"archive entry is oversized: {member.filename}")
        total += member.file_size
        if total > MAX_TOTAL_BYTES:
            raise ValueError("archive uncompressed size is oversized")
        if member.compress_size and member.file_size / member.compress_size > MAX_COMPRESSION_RATIO:
            raise ValueError(f"suspicious compression ratio: {member.filename}")


def _owner_part(rels_name: str) -> Optional[str]:
    """The part a `.rels` file describes. `_rels/.rels` describes the package root."""
    if rels_name == "_rels/.rels":
        return ""
    directory, _, filename = rels_name.rpartition("/")
    if not directory.endswith("_rels") or not filename.endswith(".rels"):
        return None
    return posixpath.join(directory[: -len("_rels")].rstrip("/"), filename[: -len(".rels")])


def _resolve(rels_name: str, target: str) -> Optional[str]:
    """Resolve a relationship target against the part that owns the `.rels` file."""
    owner = _owner_part(rels_name)
    if owner is None:
        return None
    if target.startswith("/"):
        resolved = posixpath.normpath(target.lstrip("/"))
    else:
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(owner), target))
    if resolved in {"", ".", ".."} or resolved.startswith("../"):
        return None
    return resolved


def _parse(zf: zipfile.ZipFile, name: str) -> ET.Element:
    return ET.fromstring(zf.read(name).decode("utf-8-sig"))


def check(path: str) -> Dict[str, Any]:
    errors: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []
    order: List[Dict[str, Any]] = []

    with zipfile.ZipFile(path) as zf:
        _guard_archive(zf)
        names = {m.filename for m in zf.infolist() if not m.is_dir()}

        for name in sorted(n for n in names if n.endswith((".xml", ".rels"))):
            try:
                _parse(zf, name)
            except Exception as exc:  # noqa: BLE001 - any parse failure is a finding
                errors.append({"part": name, "check": "xml_well_formed", "message": str(exc)})

        overrides: Dict[str, str] = {}
        if "[Content_Types].xml" not in names:
            errors.append(
                {
                    "part": "[Content_Types].xml",
                    "check": "content_types",
                    "message": "package has no content-type registry",
                }
            )
        else:
            try:
                root = _parse(zf, "[Content_Types].xml")
                overrides = {
                    item.get("PartName", "").lstrip("/"): item.get("ContentType", "")
                    for item in root.findall(f"{CT}Override")
                }
            except Exception as exc:  # noqa: BLE001
                errors.append(
                    {"part": "[Content_Types].xml", "check": "content_types", "message": str(exc)}
                )

        # Relationship graph: every `.rels` part, resolved against its owner.
        graph: Dict[str, Dict[str, Dict[str, str]]] = {}
        referenced: set[str] = set()
        for rels_name in sorted(n for n in names if n.endswith(".rels")):
            try:
                root = _parse(zf, rels_name)
            except Exception:  # noqa: BLE001 - already reported above
                continue
            rels: Dict[str, Dict[str, str]] = {}
            for rel in root.findall(f"{PKG_REL}Relationship"):
                rel_id = rel.get("Id", "")
                target = rel.get("Target", "")
                mode = rel.get("TargetMode", "Internal")
                resolved = None if mode == "External" else _resolve(rels_name, target)
                rels[rel_id] = {
                    "type": rel.get("Type", ""),
                    "target": resolved or target,
                    "mode": mode,
                }
                if mode == "External":
                    continue
                if not resolved or resolved not in names:
                    errors.append(
                        {
                            "part": rels_name,
                            "check": "relationship_target",
                            "message": f"{rel_id} points at a missing or unsafe part: {target}",
                        }
                    )
                else:
                    referenced.add(resolved)
            graph[rels_name] = rels

        presentation = "ppt/presentation.xml"
        presentation_rels = graph.get("ppt/_rels/presentation.xml.rels", {})
        if presentation not in names:
            errors.append(
                {
                    "part": presentation,
                    "check": "presentation_part",
                    "message": "package has no presentation part, so slide order cannot be resolved",
                }
            )
        else:
            try:
                root = _parse(zf, presentation)
            except Exception:  # noqa: BLE001 - already reported above
                root = None
            if root is not None:
                seen_ids: set[str] = set()
                for index, node in enumerate(root.findall(f".//{PML}sldId"), start=1):
                    slide_id = node.get("id", "")
                    if slide_id and slide_id in seen_ids:
                        errors.append(
                            {
                                "part": presentation,
                                "check": "slide_id_unique",
                                "message": f"slide id used more than once: {slide_id}",
                            }
                        )
                    seen_ids.add(slide_id)
                    rel_id = node.get(f"{OFFICE_REL}id", "")
                    rel = presentation_rels.get(rel_id)
                    if rel is None or not rel["type"].endswith("/slide"):
                        errors.append(
                            {
                                "part": presentation,
                                "check": "slide_relationship",
                                "message": f"slide entry {index} references a missing or non-slide relationship: {rel_id}",
                            }
                        )
                        continue
                    order.append(
                        {
                            "index": index,
                            "part": rel["target"],
                            "slide_id": slide_id,
                            "hidden": node.get("show") == "0",
                        }
                    )

        ordered_parts = {entry["part"] for entry in order}
        slide_members = {n for n in names if n.startswith("ppt/slides/slide") and n.endswith(".xml")}
        for slide in sorted(ordered_parts | slide_members):
            if slide not in names:
                errors.append(
                    {
                        "part": slide,
                        "check": "slide_part_missing",
                        "message": "presentation references a slide part the package does not contain",
                    }
                )
                continue
            if overrides and overrides.get(slide) != SLIDE_CONTENT_TYPE:
                errors.append(
                    {
                        "part": slide,
                        "check": "content_type",
                        "message": "slide part has no correct content-type override",
                    }
                )
            if slide not in ordered_parts:
                warnings.append(
                    {
                        "part": slide,
                        "check": "unlisted_slide",
                        "message": "slide part exists but the presentation does not list it",
                    }
                )
            directory, _, filename = slide.rpartition("/")
            rels_name = f"{directory}/_rels/{filename}.rels"
            layouts = [
                rel
                for rel in graph.get(rels_name, {}).values()
                if rel["type"].endswith("/slideLayout")
            ]
            if len(layouts) != 1:
                errors.append(
                    {
                        "part": rels_name,
                        "check": "slide_layout_relationship",
                        "message": f"expected exactly one slideLayout relationship, found {len(layouts)}",
                    }
                )

        for name in sorted(
            n
            for n in names
            if n.startswith("ppt/media/")
            or (n.startswith("ppt/notesSlides/notesSlide") and n.endswith(".xml"))
        ):
            if name not in referenced:
                warnings.append(
                    {
                        "part": name,
                        "check": "orphaned_part",
                        "message": "part has no inbound internal relationship",
                    }
                )

    return {
        "deck": path,
        "slide_count": len(order),
        "slide_order": order,
        "errors": errors,
        "warnings": warnings,
        "ok": not errors and not warnings,
    }


def render(report: Dict[str, Any]) -> str:
    lines = [f"file: {report['deck']}", f"slides (presentation order): {report['slide_count']}"]
    for entry in report["slide_order"]:
        flag = " [hidden]" if entry["hidden"] else ""
        lines.append(f"- {entry['index']}: {entry['part']}{flag}")
    for label, key in (("errors", "errors"), ("warnings", "warnings")):
        findings = report[key]
        lines.append(f"{label}: {len(findings)}")
        for finding in findings:
            lines.append(f"- [{finding['check']}] {finding['part']}: {finding['message']}")
    return "\n".join(lines) + "\n"


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Resolve PPTX slide order through the relationship graph and check package integrity"
    )
    ap.add_argument("path", help="Path to a .pptx file")
    ap.add_argument("--json", action="store_true", help="Emit the report as JSON")
    args = ap.parse_args(argv)

    try:
        report = check(args.path)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        sys.stderr.write(f"cannot read package: {exc}\n")
        return 2

    if args.json:
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(render(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
