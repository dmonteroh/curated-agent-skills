#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys

from ooxml_extract import extract, to_markdown, to_text


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Extract content from .docx/.pptx/.xlsx (stdlib-only)")
    ap.add_argument("path", help="Path to .docx/.pptx/.xlsx")
    ap.add_argument("--format", choices=["text", "md", "json"], default="text", help="Output format")
    ap.add_argument("--max-rows", type=int, default=50, help="XLSX: max rows to extract")
    ap.add_argument("--max-cols", type=int, default=30, help="XLSX: max cols to extract")
    ap.add_argument("--sheet", default=None, help="XLSX: sheet name to extract (exact match)")
    args = ap.parse_args(argv)

    data = extract(args.path, max_rows=args.max_rows, max_cols=args.max_cols, sheet=args.sheet)

    if args.format == "json":
        sys.stdout.write(json.dumps(data, indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 0

    if args.format == "md":
        sys.stdout.write(to_markdown(data))
        return 0

    sys.stdout.write(to_text(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
