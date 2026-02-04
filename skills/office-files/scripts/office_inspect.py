#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
import zipfile


def _natural_key(s: str):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", s)]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Inspect OOXML package (.docx/.pptx/.xlsx)")
    ap.add_argument("path", help="Path to file")
    ap.add_argument("--list", action="store_true", help="List all zip members")
    args = ap.parse_args(argv)

    path = args.path
    lower = path.lower()

    with zipfile.ZipFile(path) as zf:
        names = sorted(zf.namelist(), key=_natural_key)
        print(f"file: {path}")
        print(f"members: {len(names)}")

        if args.list:
            for n in names:
                print(n)
            return 0

        # Quick structure summaries
        if lower.endswith(".docx"):
            print("type: docx")
            print("key parts:")
            for p in ["word/document.xml", "word/comments.xml", "word/footnotes.xml", "word/endnotes.xml"]:
                if p in names:
                    print(f"- {p}")

        elif lower.endswith(".pptx"):
            print("type: pptx")
            slides = [n for n in names if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
            slides = sorted(slides, key=_natural_key)
            print(f"slides: {len(slides)}")
            for s in slides[:10]:
                print(f"- {s}")
            if len(slides) > 10:
                print("- ...")

        elif lower.endswith(".xlsx"):
            print("type: xlsx")
            sheets = [n for n in names if n.startswith("xl/worksheets/") and n.endswith(".xml")]
            sheets = sorted(sheets, key=_natural_key)
            print(f"worksheets: {len(sheets)}")
            for s in sheets[:10]:
                print(f"- {s}")
            if len(sheets) > 10:
                print("- ...")
            if "xl/sharedStrings.xml" in names:
                print("- xl/sharedStrings.xml")

        else:
            print("type: unknown (expected .docx/.pptx/.xlsx)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
