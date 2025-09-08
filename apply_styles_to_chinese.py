#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apply style spans from English header lines to the corresponding Chinese lines
in a bilingual Markdown (English_Chinese.md), and output a Chinese-only file
with preserved styles for title/subtitle/date and images.

Heuristic:
- If a line contains a styled span: <span style="...">EN_TEXT</span>
  and the next non-empty line is Chinese, then wrap the Chinese line using
  the same <span style="...">CH_TEXT</span> (copy style attributes, replace text).
- Preserve images and blank lines as-is.
- Skip note blocks <div class="note"> ... </div>.

Usage:
  python apply_styles_to_chinese.py <input_bilingual_md> <output_chinese_md>
"""

import sys
import re
from pathlib import Path


# Match one or more spans on a single line
SPAN_GLOBAL_RE = re.compile(r"<span\s+style=\"([^\"]+)\">(.*?)</span>")


def is_chinese_line(s: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]", s))


def is_image_line(s: str) -> bool:
    st = s.strip()
    return st.startswith("![](") and st.endswith(")")


def main():
    if len(sys.argv) < 3:
        print("Usage: python apply_styles_to_chinese.py <input_bilingual_md> <output_chinese_md>", file=sys.stderr)
        sys.exit(1)

    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    if not in_path.exists():
        print(f"[ERROR] Not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    lines = in_path.read_text(encoding="utf-8").splitlines()
    out_lines = []
    i = 0
    in_note = False
    while i < len(lines):
        line = lines[i]
        s = line.strip()

        # skip note blocks entirely
        if s.startswith('<div class="note"'):
            in_note = True
            i += 1
            continue
        if in_note:
            if s == "</div>":
                in_note = False
            i += 1
            continue

        # Preserve images and blank lines
        if is_image_line(line) or s == "":
            out_lines.append(line)
            i += 1
            continue

        # If styled English span followed by Chinese, transfer style
        spans = SPAN_GLOBAL_RE.findall(line)
        if spans:
            # Find next non-empty line index j
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                out_lines.append(lines[j])  # keep blank lines
                j += 1
            if j < len(lines) and is_chinese_line(lines[j]):
                cn_text = lines[j].strip()
                # If there are at least two spans, try to split Chinese at full-width or ASCII bar
                if len(spans) >= 2 and ("｜" in cn_text or "|" in cn_text):
                    # prefer full-width separator
                    if "｜" in cn_text:
                        left, right = cn_text.split("｜", 1)
                        sep = "｜"
                    else:
                        left, right = cn_text.split("|", 1)
                        sep = "|"
                    style0, text0 = spans[0][0], spans[0][1]
                    style1, text1 = spans[1][0], spans[1][1]
                    # Right part keeps the separator
                    right_with_sep = sep + right
                    out_lines.append(
                        f"<span style=\"{style0}\">{left}</span> "
                        f"<span style=\"{style1}\">{right_with_sep}</span>"
                    )
                else:
                    # Fallback: use first span style for the whole Chinese line
                    style_attr = spans[0][0]
                    out_lines.append(f"<span style=\"{style_attr}\">{cn_text}</span>")
                i = j + 1
                continue
            else:
                # No Chinese line after; ignore English styled line
                i += 1
                continue

        # Regular line handling: keep only Chinese text lines
        if is_chinese_line(line):
            out_lines.append(line)
        # else drop English
        i += 1

    out_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"[OK] Wrote styled Chinese: {out_path}")


if __name__ == "__main__":
    main()


