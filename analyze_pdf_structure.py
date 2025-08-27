#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze PDF structure for The Economist issues.

Outputs:
- Basic metadata (pages, images count)
- Outline / TOC entries
- Fonts usage distribution (sizes, counts)
- Heuristic main body font size and paragraph stats
- Detection of underline usage and colored text distribution

Usage:
  python analyze_pdf_structure.py [optional_path_to_pdf]
If not provided, the script finds the most recent PDF under economist_pdfs/.
"""

import sys
import os
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional

try:
    import fitz  # PyMuPDF
except Exception as exc:  # pragma: no cover
    print("[ERROR] PyMuPDF (fitz) 未安装，请先安装: pip install PyMuPDF", file=sys.stderr)
    raise


def find_latest_pdf(base_dir: Path) -> Optional[Path]:
    pdf_dir = base_dir / "economist_pdfs"
    if not pdf_dir.exists():
        return None
    pdfs = sorted(pdf_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pdfs[0] if pdfs else None


def color_to_rgb_tuple(color_value):
    # PyMuPDF span["color"] is an int like 0xRRGGBB or a float; handle robustly
    try:
        if isinstance(color_value, int):
            r = (color_value >> 16) & 0xFF
            g = (color_value >> 8) & 0xFF
            b = color_value & 0xFF
            return (r, g, b)
        if isinstance(color_value, (list, tuple)) and len(color_value) == 3:
            # already rgb 0..1 or 0..255
            vals = list(color_value)
            if max(vals) <= 1.0:
                return tuple(int(v * 255) for v in vals)
            return tuple(int(v) for v in vals)
    except Exception:
        pass
    return (0, 0, 0)


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02X}{g:02X}{b:02X}"


def analyze_pdf(pdf_path: Path) -> Dict:
    result: Dict = {
        "file": str(pdf_path),
        "pages": 0,
        "toc": [],
        "images_per_page": [],
        "fonts": {},
        "font_sizes": {},
        "main_body_font_size": None,
        "body_paragraphs_estimate": 0,
        "underline_count": 0,
        "color_distribution": {},
        "page_level": [],
    }

    doc = fitz.open(pdf_path)
    result["pages"] = doc.page_count

    # TOC
    try:
        toc = doc.get_toc(simple=True)
        # toc rows: [level, title, page]
        for level, title, page in toc:
            result["toc"].append({"level": level, "title": title, "page": page})
    except Exception:
        pass

    font_size_counter = Counter()
    font_name_counter = Counter()
    color_counter = Counter()
    underline_count = 0
    page_summaries: List[Dict] = []

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        # images on page
        imgs = page.get_images(full=True)
        images_count = len(imgs)

        text_dict = page.get_text("dict")
        span_sizes: List[float] = []
        body_candidate_paragraphs = 0

        for block in text_dict.get("blocks", []):
            if block.get("type", 0) != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    size = float(span.get("size", 0))
                    font = span.get("font", "")
                    color_val = span.get("color", 0)
                    flags = int(span.get("flags", 0))
                    # heuristic underline bit: commonly 4
                    if flags & 4:
                        underline_count += 1
                    rgb = color_to_rgb_tuple(color_val)
                    color_counter[rgb] += 1
                    font_size_counter[round(size, 1)] += 1
                    font_name_counter[font] += 1
                    span_sizes.append(size)

        # per-page summary
        page_summaries.append({
            "page": page_index + 1,
            "images": images_count,
            "spans": len(span_sizes),
        })

    # font size stats
    result["font_sizes"] = {str(k): v for k, v in sorted(font_size_counter.items(), key=lambda kv: (-kv[1], -float(kv[0])))}
    result["fonts"] = {k: v for k, v in font_name_counter.most_common(20)}
    result["underline_count"] = underline_count
    result["images_per_page"] = [ps["images"] for ps in page_summaries]
    result["page_level"] = page_summaries

    # main body font size: mode of font sizes among spans (exclude very small sizes <6 which are often footers)
    filtered_sizes = Counter({size: cnt for size, cnt in font_size_counter.items() if float(size) >= 6.5})
    if filtered_sizes:
        main_body_size, _ = filtered_sizes.most_common(1)[0]
        result["main_body_font_size"] = float(main_body_size)

    # Color distribution (top 10)
    top_colors = color_counter.most_common(10)
    result["color_distribution"] = {
        rgb_to_hex(rgb): count for rgb, count in top_colors
    }

    # Estimate body paragraphs: number of lines whose dominant span size ~ main body
    body_paragraphs_estimate = 0
    if result["main_body_font_size"] is not None:
        body_size = result["main_body_font_size"]
        tolerance = 0.3
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            text_dict = page.get_text("dict")
            for block in text_dict.get("blocks", []):
                if block.get("type", 0) != 0:
                    continue
                for line in block.get("lines", []):
                    span_sizes = [float(s.get("size", 0)) for s in line.get("spans", [])]
                    if not span_sizes:
                        continue
                    # treat as body line if majority of spans match body size within tolerance
                    matches = sum(1 for s in span_sizes if abs(s - body_size) <= tolerance)
                    if matches >= max(1, len(span_sizes) // 2 + 1):
                        body_paragraphs_estimate += 1

    result["body_paragraphs_estimate"] = body_paragraphs_estimate

    doc.close()
    return result


def print_human_summary(stats: Dict):
    print("==== PDF 结构分析 ====")
    print(f"文件: {stats['file']}")
    print(f"总页数: {stats['pages']}")
    print("")
    if stats.get("toc"):
        print("目录 (前20条):")
        for item in stats["toc"][:20]:
            print(f"  L{item['level']} P{item['page']}: {item['title']}")
    else:
        print("未检测到内置目录 / TOC")
    print("")
    if stats.get("font_sizes"):
        print("字号分布 (前10):")
        idx = 0
        for size_str, cnt in stats["font_sizes"].items():
            print(f"  字号 {size_str}: {cnt}")
            idx += 1
            if idx >= 10:
                break
    print("")
    print(f"推测正文字号: {stats.get('main_body_font_size')}")
    print(f"估计正文行数: {stats.get('body_paragraphs_estimate')}")
    print("")
    print("颜色分布 (前10):")
    for hex_color, cnt in stats.get("color_distribution", {}).items():
        print(f"  {hex_color}: {cnt}")
    print("")
    print(f"下划线文本段计数: {stats.get('underline_count')}")
    print("")
    total_images = sum(stats.get("images_per_page", []))
    print(f"图片总数(估计): {total_images}")
    if stats.get("images_per_page"):
        non_zero_pages = sum(1 for n in stats["images_per_page"] if n)
        print(f"包含图片的页数: {non_zero_pages}")


def main():
    base_dir = Path(__file__).resolve().parent
    arg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if arg_path is None:
        pdf = find_latest_pdf(base_dir)
        if not pdf:
            print("[ERROR] 未找到 economist_pdfs/*.pdf，请先下载。", file=sys.stderr)
            sys.exit(1)
    else:
        pdf = arg_path
        if not pdf.exists():
            print(f"[ERROR] 文件不存在: {pdf}", file=sys.stderr)
            sys.exit(1)

    stats = analyze_pdf(pdf)
    print_human_summary(stats)


if __name__ == "__main__":
    main()


