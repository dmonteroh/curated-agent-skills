#!/usr/bin/env python3

from __future__ import annotations

import argparse
import difflib
import sys

from ooxml_extract import extract, to_text


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Text diff for two OOXML files (docx/pptx/xlsx)")
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--context", type=int, default=3, help="Diff context lines")
    ap.add_argument("--max-rows", type=int, default=50)
    ap.add_argument("--max-cols", type=int, default=30)
    ap.add_argument("--sheet", default=None, help="XLSX: sheet name to diff")
    args = ap.parse_args(argv)

    old_data = extract(args.old, max_rows=args.max_rows, max_cols=args.max_cols, sheet=args.sheet)
    new_data = extract(args.new, max_rows=args.max_rows, max_cols=args.max_cols, sheet=args.sheet)

    old_text = to_text(old_data).splitlines(keepends=True)
    new_text = to_text(new_data).splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_text,
        new_text,
        fromfile=args.old,
        tofile=args.new,
        n=args.context,
    )

    sys.stdout.writelines(diff)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
