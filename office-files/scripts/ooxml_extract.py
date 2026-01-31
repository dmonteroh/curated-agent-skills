#!/usr/bin/env python3
"""OOXML extraction helpers (stdlib-only).

Supports best-effort text extraction from:
- DOCX: word/document.xml
- PPTX: ppt/slides/slide*.xml
- XLSX: xl/worksheets/sheet*.xml (+ sharedStrings)

Design goal: deterministic, dependency-free extraction for agent workflows.
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple
import xml.etree.ElementTree as ET


_NS_WORD = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}

_NS_PPT = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}

_NS_XLSX = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def _read_zip_text(zf: zipfile.ZipFile, path: str) -> Optional[str]:
    try:
        with zf.open(path) as f:
            return f.read().decode("utf-8")
    except KeyError:
        return None


def _safe_xml(text: str) -> ET.Element:
    # Some OOXML parts contain leading BOM or whitespace.
    text = text.lstrip("\ufeff\n\r\t ")
    return ET.fromstring(text)


def _iter_text_nodes(root: ET.Element, tags: Iterable[str]) -> Iterable[str]:
    for el in root.iter():
        if el.tag in tags and el.text:
            yield el.text


def extract_docx(zf: zipfile.ZipFile) -> Dict:
    xml = _read_zip_text(zf, "word/document.xml")
    if not xml:
        return {"type": "docx", "error": "missing word/document.xml"}

    root = _safe_xml(xml)
    paragraphs: List[str] = []

    # Build paragraph text by walking w:p and capturing w:t, w:tab, w:br.
    for p in root.findall(".//w:p", _NS_WORD):
        parts: List[str] = []
        for node in p.iter():
            if node.tag == f"{{{_NS_WORD['w']}}}t" and node.text:
                parts.append(node.text)
            elif node.tag == f"{{{_NS_WORD['w']}}}tab":
                parts.append("\t")
            elif node.tag == f"{{{_NS_WORD['w']}}}br":
                parts.append("\n")
        text = "".join(parts).strip("\n")
        if text.strip():
            paragraphs.append(text)

    return {"type": "docx", "paragraphs": paragraphs}


def extract_pptx(zf: zipfile.ZipFile) -> Dict:
    slide_paths = sorted(
        [n for n in zf.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")],
        key=lambda s: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", s)],
    )
    if not slide_paths:
        return {"type": "pptx", "error": "no ppt/slides/slide*.xml found"}

    slides: List[Dict] = []
    for sp in slide_paths:
        xml = _read_zip_text(zf, sp)
        if not xml:
            continue
        root = _safe_xml(xml)
        # DrawingML text runs are a:t
        text_runs = list(_iter_text_nodes(root, {f"{{{_NS_PPT['a']}}}t"}))
        # Heuristic: join runs into lines by preserving existing separation where possible.
        text = " ".join(t.strip() for t in text_runs if t.strip()).strip()
        slides.append({"path": sp, "text": text})

    return {"type": "pptx", "slides": slides}


@dataclass
class Sheet:
    name: str
    path: str


def _parse_workbook_sheets(zf: zipfile.ZipFile) -> List[Sheet]:
    wb_xml = _read_zip_text(zf, "xl/workbook.xml")
    rels_xml = _read_zip_text(zf, "xl/_rels/workbook.xml.rels")
    if not wb_xml or not rels_xml:
        return []

    wb = _safe_xml(wb_xml)
    rels = _safe_xml(rels_xml)

    # Relationship Id -> Target
    relmap: Dict[str, str] = {}
    for rel in rels.findall(".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"):
        rid = rel.attrib.get("Id")
        target = rel.attrib.get("Target")
        if rid and target:
            # Targets are relative to xl/
            if target.startswith("/"):
                target = target.lstrip("/")
            relmap[rid] = "xl/" + target

    sheets: List[Sheet] = []
    for s in wb.findall(".//main:sheets/main:sheet", _NS_XLSX):
        name = s.attrib.get("name", "")
        rid = s.attrib.get(f"{{{_NS_XLSX['r']}}}id")
        path = relmap.get(rid or "", "")
        if name and path:
            sheets.append(Sheet(name=name, path=path))

    return sheets


def _load_shared_strings(zf: zipfile.ZipFile) -> List[str]:
    xml = _read_zip_text(zf, "xl/sharedStrings.xml")
    if not xml:
        return []
    root = _safe_xml(xml)
    out: List[str] = []
    # shared strings are <si> with text in <t> nodes; can have rich text runs
    for si in root.findall(".//main:si", _NS_XLSX):
        texts = [t.text or "" for t in si.findall(".//main:t", _NS_XLSX)]
        out.append("".join(texts))
    return out


def _col_to_index(col: str) -> int:
    # A -> 1, B -> 2, ..., Z -> 26, AA -> 27
    idx = 0
    for ch in col:
        if not ("A" <= ch <= "Z"):
            break
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx


def _cell_ref_to_xy(ref: str) -> Tuple[int, int]:
    m = re.match(r"^([A-Z]+)(\d+)$", ref)
    if not m:
        return (0, 0)
    col, row = m.group(1), int(m.group(2))
    return (_col_to_index(col), row)


def _sheet_to_grid(zf: zipfile.ZipFile, sheet_path: str, shared: List[str], max_rows: int, max_cols: int) -> List[List[str]]:
    xml = _read_zip_text(zf, sheet_path)
    if not xml:
        return []
    root = _safe_xml(xml)

    # Collect values by (col,row)
    cells: Dict[Tuple[int, int], str] = {}

    for c in root.findall(".//main:sheetData//main:c", _NS_XLSX):
        ref = c.attrib.get("r")
        if not ref:
            continue
        x, y = _cell_ref_to_xy(ref)
        if x <= 0 or y <= 0:
            continue
        if y > max_rows or x > max_cols:
            continue

        t = c.attrib.get("t")
        v_el = c.find("main:v", _NS_XLSX)

        if t == "s":
            # shared string index
            if v_el is not None and v_el.text and v_el.text.isdigit():
                i = int(v_el.text)
                val = shared[i] if 0 <= i < len(shared) else ""
            else:
                val = ""
        elif t == "inlineStr":
            # inline string
            texts = [t_el.text or "" for t_el in c.findall(".//main:t", _NS_XLSX)]
            val = "".join(texts)
        else:
            # number / bool / formula result (best-effort; no recalculation)
            val = (v_el.text or "") if v_el is not None else ""

        cells[(x, y)] = val

    # Build grid
    grid: List[List[str]] = []
    for row in range(1, max_rows + 1):
        r: List[str] = []
        for col in range(1, max_cols + 1):
            r.append(cells.get((col, row), ""))
        grid.append(r)

    # Trim trailing empty rows/cols
    while grid and all(not (c or "").strip() for c in grid[-1]):
        grid.pop()
    if not grid:
        return []

    # Trim trailing empty columns
    last_col = 0
    for r in grid:
        for i, c in enumerate(r, start=1):
            if (c or "").strip():
                last_col = max(last_col, i)
    last_col = max(last_col, 1)
    return [r[:last_col] for r in grid]


def extract_xlsx(zf: zipfile.ZipFile, max_rows: int = 50, max_cols: int = 30, sheet: Optional[str] = None) -> Dict:
    sheets = _parse_workbook_sheets(zf)
    if not sheets:
        # Fallback: guess worksheets
        guessed = sorted([n for n in zf.namelist() if n.startswith("xl/worksheets/") and n.endswith(".xml")])
        sheets = [Sheet(name=p.split("/")[-1], path=p) for p in guessed]

    shared = _load_shared_strings(zf)

    out_sheets: List[Dict] = []
    for s in sheets:
        if sheet and s.name != sheet:
            continue
        grid = _sheet_to_grid(zf, s.path, shared, max_rows=max_rows, max_cols=max_cols)
        out_sheets.append({"name": s.name, "path": s.path, "grid": grid})

    if sheet and not out_sheets:
        return {"type": "xlsx", "error": f"sheet not found: {sheet}", "sheets": [{"name": s.name, "path": s.path} for s in sheets]}

    return {"type": "xlsx", "sheets": out_sheets}


def extract(path: str, *, max_rows: int = 50, max_cols: int = 30, sheet: Optional[str] = None) -> Dict:
    lower = path.lower()
    with zipfile.ZipFile(path) as zf:
        if lower.endswith(".docx"):
            return extract_docx(zf)
        if lower.endswith(".pptx"):
            return extract_pptx(zf)
        if lower.endswith(".xlsx"):
            return extract_xlsx(zf, max_rows=max_rows, max_cols=max_cols, sheet=sheet)

    return {"error": "unsupported file type", "path": path}


def to_text(data: Dict) -> str:
    t = data.get("type")
    if t == "docx":
        paras = data.get("paragraphs", [])
        return "\n\n".join(paras)

    if t == "pptx":
        lines: List[str] = []
        for i, s in enumerate(data.get("slides", []), start=1):
            txt = (s.get("text") or "").strip()
            if not txt:
                continue
            lines.append(f"# Slide {i}")
            lines.append(txt)
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    if t == "xlsx":
        out: List[str] = []
        for s in data.get("sheets", []):
            out.append(f"# Sheet: {s.get('name')}")
            grid = s.get("grid", [])
            for row in grid:
                out.append("\t".join(str(c) for c in row))
            out.append("")
        return "\n".join(out).rstrip() + "\n"

    return json.dumps(data, indent=2, sort_keys=True)


def to_markdown(data: Dict) -> str:
    t = data.get("type")
    if t == "docx":
        paras = data.get("paragraphs", [])
        return "\n\n".join(paras) + ("\n" if paras else "")

    if t == "pptx":
        out: List[str] = []
        for i, s in enumerate(data.get("slides", []), start=1):
            txt = (s.get("text") or "").strip()
            out.append(f"## Slide {i}")
            out.append("")
            out.append(txt if txt else "(no text extracted)")
            out.append("")
        return "\n".join(out).rstrip() + "\n"

    if t == "xlsx":
        out: List[str] = []
        for s in data.get("sheets", []):
            out.append(f"## Sheet: {s.get('name')}")
            out.append("")
            grid = s.get("grid", [])
            if not grid:
                out.append("(empty or no cells extracted)")
                out.append("")
                continue
            # Markdown table: treat first row as header.
            header = [str(x) if str(x).strip() else "" for x in grid[0]]
            out.append("| " + " | ".join(header) + " |")
            out.append("| " + " | ".join(["---"] * len(header)) + " |")
            for row in grid[1:]:
                out.append("| " + " | ".join(str(x) for x in row) + " |")
            out.append("")
        return "\n".join(out).rstrip() + "\n"

    return "```json\n" + json.dumps(data, indent=2, sort_keys=True) + "\n```\n"


def grid_to_csv(grid: List[List[str]]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    for row in grid:
        w.writerow(row)
    return buf.getvalue()
