#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filter a bilingual Markdown to keep only Chinese lines and image lines.

Usage:
  python filter_chinese_only.py <input_md> <output_md>
If output path is omitted, appends _ChineseOnly.md next to input.
"""

import sys
import re
from pathlib import Path


def is_chinese_line(s: str) -> bool:
    # Contains any CJK Unified Ideographs or fullwidth punctuation
    return bool(re.search(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]", s))


def is_image_line(s: str) -> bool:
    st = s.strip()
    return st.startswith("![](") and st.endswith(")")


def main():
    if len(sys.argv) < 2:
        print("Usage: python filter_chinese_only.py <input_md> [output_md]", file=sys.stderr)
        sys.exit(1)
    in_path = Path(sys.argv[1])
    if not in_path.exists():
        print(f"[ERROR] Input not found: {in_path}", file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) >= 3:
        out_path = Path(sys.argv[2])
    else:
        out_path = in_path.with_name(in_path.stem + "_ChineseOnly.md")

    lines = in_path.read_text(encoding="utf-8").splitlines()
    kept = []
    in_note = False  # inside <div class="note"> ... </div>
    for line in lines:
        stripped = line.strip()

        # track note blocks
        if stripped.startswith('<div class="note"'):
            in_note = True
            continue
        if in_note:
            if stripped == "</div>":
                in_note = False
            continue  # skip all lines inside note

        # skip single-line chinese notes starting with 备注
        if stripped.startswith("备注：") or stripped.startswith("备注:"):
            continue

        # 保留空行（不再合并或裁剪），便于与原文空白一致
        if stripped == "":
            kept.append("")
            continue

        if is_chinese_line(line) or is_image_line(line):
            kept.append(line)
        else:
            # drop non-Chinese, non-image lines
            continue

    # 不再修剪首尾空行，尽量保留原始空白结构

    out_path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    print(f"[OK] Wrote: {out_path}")


if __name__ == "__main__":
    main()


