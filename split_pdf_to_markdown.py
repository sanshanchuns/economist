#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Split The Economist PDF by TOC sections and export Markdown per section.

Features:
- Uses PDF's built-in TOC (level==1) as sections
- Extracts text as Markdown (preserves hyperlinks from PyMuPDF)
- Extracts images for each page; saves to section-specific folder
- Appends image references after each page's text block
- Generates an index README listing sections and page ranges

Output structure:
  output/
    <issue_name>/
      README.md
      sections/
        001_<slug>.md
        002_<slug>.md
      images/
        001_<slug>/p0001_img01.png
        ...

Usage:
  python split_pdf_to_markdown.py [optional_path_to_pdf]
If not provided, the script finds the most recent PDF under economist_pdfs/.
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict

try:
    import fitz  # PyMuPDF
except Exception:
    print("[ERROR] 需要安装 PyMuPDF: pip install PyMuPDF", file=sys.stderr)
    sys.exit(1)


def find_latest_pdf(base_dir: Path) -> Optional[Path]:
    pdf_dir = base_dir / "economist_pdfs"
    if not pdf_dir.exists():
        return None
    pdfs = sorted(pdf_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pdfs[0] if pdfs else None


def slugify(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^0-9A-Za-z_\-]+", "", text)
    text = text.strip("_-")
    return text[:60] or "section"


def get_issue_name(pdf_path: Path) -> str:
    name = pdf_path.stem
    name = name.replace('.', '-')
    return name


def get_toc_level1(doc) -> List[Tuple[str, int]]:
    toc = []
    try:
        raw = doc.get_toc(simple=True)
    except Exception:
        raw = []
    for level, title, page in raw:
        if level == 1:
            # PyMuPDF pages are 1-based in TOC
            toc.append((title.strip() or "Untitled", max(1, int(page))))
    # ensure sorted by page
    toc.sort(key=lambda x: x[1])
    return toc


def ensure_dirs(base_out: Path, sections: List[Tuple[str, int]]) -> Dict[int, Dict[str, Path]]:
    paths: Dict[int, Dict[str, Path]] = {}
    (base_out / "sections").mkdir(parents=True, exist_ok=True)
    (base_out / "images").mkdir(parents=True, exist_ok=True)
    for idx, (title, _) in enumerate(sections, start=1):
        num = f"{idx:03d}"
        slug = slugify(title) or f"section_{num}"
        sec_dir = base_out / "sections"
        img_dir = base_out / "images" / f"{num}_{slug}"
        img_dir.mkdir(parents=True, exist_ok=True)
        paths[idx] = {
            "md": sec_dir / f"{num}_{slug}.md",
            "img": img_dir,
        }
    return paths


def extract_images_for_page(doc, page, target_dir: Path, page_num: int, saved_xrefs: set) -> List[str]:
    refs: List[str] = []
    images = page.get_images(full=True)
    img_index = 1
    for img in images:
        xref = img[0]
        if (xref, target_dir) in saved_xrefs:
            # avoid duplicating same xref within same section dir
            # still refer by filename
            # compute expected filename
            ext = "png"
            out_name = f"p{page_num:04d}_img{img_index:02d}.{ext}"
            refs.append(out_name)
            img_index += 1
            continue
        try:
            base = doc.extract_image(xref)
            image_bytes = base.get("image")
            ext = (base.get("ext") or "png").lower()
            if ext not in {"png", "jpg", "jpeg"}:
                ext = "png"
            out_name = f"p{page_num:04d}_img{img_index:02d}.{ext}"
            out_path = target_dir / out_name
            with open(out_path, "wb") as f:
                f.write(image_bytes)
            refs.append(out_name)
            saved_xrefs.add((xref, target_dir))
            img_index += 1
        except Exception:
            continue
    return refs


DATE_PAT = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(st|nd|rd|th)\s+\d{4}$")


def _insert_images_after_date(md_text: str, image_refs: List[str], img_dir_name: str) -> str:
    if not image_refs:
        return md_text
    lines = md_text.splitlines()
    out: List[str] = []
    inserted = False
    for i, line in enumerate(lines):
        out.append(line)
        if not inserted and DATE_PAT.match(line.strip()):
            out.append("  ")
            for name in image_refs:
                rel = Path("..") / "images" / img_dir_name / name
                out.append(f"\n![]({rel.as_posix()})")
            inserted = True
    if not inserted:
        # fallback: append to end
        for name in image_refs:
            rel = Path("..") / "images" / img_dir_name / name
            out.append(f"\n![]({rel.as_posix()})")
    return "\n".join(out)


def _style_titles_if_present(md_text: str, candidates: List[Tuple[str, float, str]]) -> str:
    # candidates: list of (text, font_size_pt, color_hex) in visual order before date
    lines = md_text.splitlines()
    if not lines or not candidates:
        return md_text
    # 仅处理前两个候选（标题与副标题）
    replace_map: Dict[str, str] = {}
    for text, size_pt, color_hex in candidates[:2]:
        styled = f'<span style="color:{color_hex}; font-size:{size_pt:.1f}pt; font-weight:bold;">{text}</span>'
        replace_map[text] = styled

    out_lines: List[str] = []
    for line in lines:
        t = line.strip()
        if t in replace_map:
            leading = line[:line.find(t)] if t in line else ""
            out_lines.append(leading + replace_map[t])
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


def _insert_paragraph_breaks(md_text: str, section_title: str) -> str:
    # 针对 Politics 章节的特定段落要求
    if section_title.lower() == "politics":
        target = "Russia has yet to respond to the proposal."
        md_text = md_text.replace(target, target + "\n ")
    return md_text


def _rgb_from_color_val(color_value) -> Tuple[int, int, int]:
    try:
        if isinstance(color_value, int):
            r = (color_value >> 16) & 0xFF
            g = (color_value >> 8) & 0xFF
            b = color_value & 0xFF
            return (r, g, b)
        if isinstance(color_value, (list, tuple)) and len(color_value) == 3:
            vals = list(color_value)
            if max(vals) <= 1.0:
                return tuple(int(v * 255) for v in vals)
            return tuple(int(v) for v in vals)
    except Exception:
        pass
    return (0, 0, 0)


def _hex(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02X}{g:02X}{b:02X}"


def _detect_header_candidates(page) -> List[Tuple[str, float, str]]:
    # 返回在日期行之前出现的非空文本行，携带平均字号与主色
    out: List[Tuple[str, float, str]] = []
    try:
        td = page.get_text("dict")
    except Exception:
        return out
    seen_date = False
    for block in td.get("blocks", []):
        if block.get("type", 0) != 0:
            continue
        for line in block.get("lines", []):
            text = "".join(span.get("text", "") for span in line.get("spans", []))
            text = text.strip()
            if not text:
                continue
            if DATE_PAT.match(text):
                seen_date = True
                break
            # 仅记录日期前的行
            if not seen_date:
                spans = line.get("spans", [])
                if not spans:
                    continue
                avg_size = sum(float(s.get("size", 0.0)) for s in spans) / max(1, len(spans))
                # 统计颜色
                color_counts: Dict[str, int] = {}
                for s in spans:
                    rgb = _rgb_from_color_val(s.get("color", 0))
                    color_counts[_hex(rgb)] = color_counts.get(_hex(rgb), 0) + 1
                dominant_hex = max(color_counts.items(), key=lambda kv: kv[1])[0] if color_counts else "#000000"
                out.append((text, avg_size, dominant_hex))
        if seen_date:
            break
    return out


def _style_date_line(md_text: str, page) -> str:
    # 用 PDF 实际颜色与字号为日期行加样式（通常灰色小字号）
    try:
        td = page.get_text("dict")
    except Exception:
        return md_text
    date_text = None
    avg_size = None
    dominant_hex = "#808080"  # 默认灰色
    for block in td.get("blocks", []):
        if block.get("type", 0) != 0:
            continue
        for line in block.get("lines", []):
            text = "".join(span.get("text", "") for span in line.get("spans", []))
            t = text.strip()
            if DATE_PAT.match(t):
                date_text = t
                spans = line.get("spans", [])
                if spans:
                    avg_size = sum(float(s.get("size", 0.0)) for s in spans) / max(1, len(spans))
                    color_counts: Dict[str, int] = {}
                    for s in spans:
                        rgb = _rgb_from_color_val(s.get("color", 0))
                        color_counts[_hex(rgb)] = color_counts.get(_hex(rgb), 0) + 1
                    if color_counts:
                        dominant_hex = max(color_counts.items(), key=lambda kv: kv[1])[0]
                break
        if date_text:
            break
    if not date_text:
        return md_text
    size_pt = avg_size if avg_size else 10.0
    styled = f'<span style="color:{dominant_hex}; font-size:{size_pt:.1f}pt;">{date_text}</span>'
    return md_text.replace(date_text, styled, 1)


def _preserve_intra_paragraph_linebreaks(md_text: str) -> str:
    # 将段内的单换行转为 Markdown 强制换行（行尾两个空格）
    lines = md_text.splitlines()
    out: List[str] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        # 跳过特殊行：HTML 注释、标题、图片、列表、HTML 标签行
        if (not stripped) or stripped.startswith("<!--") or stripped.startswith("#") \
           or stripped.startswith("!") or stripped.startswith("-") or stripped.startswith("<") \
           or stripped.startswith("**Images**"):
            out.append(line)
            continue
        # 如果下一行存在且也不是空行，则为当前行添加两个空格以强制换行
        if i + 1 < len(lines) and lines[i + 1].strip():
            if not line.endswith("  "):
                out.append(line + "  ")
            else:
                out.append(line)
        else:
            out.append(line)
    return "\n".join(out)


def _get_page_lines_with_geometry(page) -> List[Tuple[str, float, float]]:
    lines_out: List[Tuple[str, float, float]] = []
    try:
        td = page.get_text("dict")
    except Exception:
        return lines_out
    for block in td.get("blocks", []):
        if block.get("type", 0) != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            text = "".join(s.get("text", "") for s in spans).strip()
            if not text:
                continue
            bbox = line.get("bbox", None)
            if bbox and isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                top, bottom = float(bbox[1]), float(bbox[3])
            else:
                # fallback using spans
                ys = [s.get("origin", [0, 0])[1] for s in spans if isinstance(s.get("origin", None), (list, tuple)) and len(s.get("origin", [])) >= 2]
                if ys:
                    top = min(ys)
                    bottom = max(ys)
                else:
                    top = bottom = 0.0
            lines_out.append((text, top, bottom))
    return lines_out


def _apply_blank_lines_by_geometry(page, md_text: str) -> str:
    # 依据相邻行的垂直间距在需要处插入空行；其它处保留为强制换行
    page_lines = _get_page_lines_with_geometry(page)
    if not page_lines:
        return _preserve_intra_paragraph_linebreaks(md_text)
    # 计算行高与间距阈值
    heights = [max(1.0, b - t) for _, t, b in page_lines]
    heights.sort()
    mid = heights[len(heights)//2]
    gap_threshold = max(3.0, mid * 0.8)

    # 记录需要“空一行”的相邻文本对
    breaks: Dict[int, bool] = {}
    for i in range(len(page_lines) - 1):
        _, t1, b1 = page_lines[i]
        _, t2, _ = page_lines[i + 1]
        gap = t2 - b1
        if gap > gap_threshold:
            breaks[i] = True

    # 将 md_text 的行与 page_lines 顺序对齐（基于逐行匹配）
    md_lines = md_text.splitlines()
    result_lines: List[str] = []
    j = 0  # index in page_lines
    for i, line in enumerate(md_lines):
        result_lines.append(line)
        # 跳过非正文类行，不参与段落空行判断
        stripped = line.strip()
        if (not stripped) or stripped.startswith("<!--") or stripped.startswith("#") \
           or stripped.startswith("!") or stripped.startswith("-") or stripped.startswith("<") \
           or stripped.startswith("**Images**"):
            continue
        # 简单推进匹配：当 md 行文本为 page_lines[j] 的前缀/相等时，认为匹配
        while j < len(page_lines):
            page_text = page_lines[j][0]
            if page_text and (stripped == page_text or page_text.startswith(stripped) or stripped.startswith(page_text)):
                # 看看此处后是否需要空行
                if j in breaks:
                    # 只有当下一 md 行也为正文时才插入空行
                    if i + 1 < len(md_lines) and md_lines[i + 1].strip():
                        result_lines.append("")
                else:
                    # 若非空行情况，且下一行是正文，则当前行末尾添加强制换行
                    if i + 1 < len(md_lines) and md_lines[i + 1].strip() and not line.endswith("  "):
                        result_lines[-1] = line + "  "
                j += 1
                break
            else:
                j += 1
    return "\n".join(result_lines)

def _style_footer_or_source_lines(md_text: str) -> str:
    # 保留并样式化来源/水印类小字行：灰色小字号；URL 转为可点击链接
    zlib_pat = re.compile(r"^This article was downloaded by zlibrary from (https?://\S+)$", re.I)
    econ_pat = re.compile(r"^(https?://(www\.)?economist\.com/\S+)$", re.I)
    lines = md_text.splitlines()
    out: List[str] = []
    for line in lines:
        s = line.strip()
        m1 = zlib_pat.match(s)
        m2 = econ_pat.match(s)
        if m1:
            url = m1.group(1)
            styled = f'<span style="color:#808080; font-size:6.2pt;">This article was downloaded by zlibrary from [{url}]({url})</span>'
            out.append(styled)
        elif m2:
            url = m2.group(1)
            styled = f'<span style="color:#808080; font-size:6.2pt;">[{url}]({url})</span>'
            out.append(styled)
        else:
            out.append(line)
    return "\n".join(out)


def export_section_markdown(doc, start_page_1based: int, end_page_1based: int, md_path: Path, img_dir: Path, section_title: str):
    saved_xrefs = set()
    blocks: List[str] = []
    # Title will be inserted by caller
    for p in range(start_page_1based, end_page_1based + 1):
        page = doc.load_page(p - 1)
        # PyMuPDF Markdown preserves links; be compatible with multiple versions
        def page_markdown(pg):
            try:
                return pg.get_text("markdown")
            except Exception:
                try:
                    return pg.get_text("md")
                except Exception:
                    return pg.get_text("text")

        md_text = page_markdown(page) or ""

        # images for this page (先提取，便于首页插入到日期后)
        refs = extract_images_for_page(doc, page, img_dir, p, saved_xrefs)

        # 首页排版优化：样式化标题/副标题，并将图片插入到日期行之后
        if p == start_page_1based:
            # 基于实际字号/颜色样式化标题与副标题
            header_candidates = _detect_header_candidates(page)
            md_text = _style_titles_if_present(md_text, header_candidates)
            # 先在“原始日期文本”仍可匹配时插入图片，确保图片紧跟日期
            md_text = _insert_images_after_date(md_text, refs, img_dir.name)
            # 再样式化日期行（灰色小字号）
            md_text = _style_date_line(md_text, page)
            md_text = _insert_paragraph_breaks(md_text, section_title)
            # 依据几何间距插入空行，其余位置使用强制换行
            md_text = _apply_blank_lines_by_geometry(page, md_text)
            md_text = _style_footer_or_source_lines(md_text)
            # 直接追加内容，不加页面注释，跨页不强制空行
            blocks.append(md_text)
        else:
            # 直接追加内容，不加页面注释，跨页默认连续（先补一个换行，防止词黏连）
            blocks.append("\n")
            blocks.append(_style_footer_or_source_lines(_apply_blank_lines_by_geometry(page, md_text)))
            if refs:
                blocks.append("\n\n")
                for name in refs:
                    rel = Path("..") / "images" / img_dir.name / name
                    blocks.append(f"\n![]({rel.as_posix()})")
                # 图片块后补一个换行，避免与下一段落黏连
                blocks.append("\n")

    # 合并并规范多余空行（最多两连换行）
    content = "".join(blocks)
    content = re.sub(r"\n{3,}", "\n\n", content)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)


def write_readme(base_out: Path, issue_name: str, sections: List[Tuple[str, int]], page_ranges: List[Tuple[int, int]]):
    lines: List[str] = []
    lines.append(f"# {issue_name}\n\n")
    lines.append("按目录 (L1) 拆分的章节列表：\n\n")
    lines.append("| # | 标题 | 起始页 | 结束页 | 文件 |\n")
    lines.append("|---|------|--------|--------|------|\n")
    for idx, ((title, start), (sp, ep)) in enumerate(zip(sections, page_ranges), start=1):
        slug = slugify(title)
        md_rel = Path("sections") / f"{idx:03d}_{slug}.md"
        lines.append(f"| {idx} | {title} | {sp} | {ep} | {md_rel.as_posix()} |\n")
    with open(base_out / "README.md", "w", encoding="utf-8") as f:
        f.write("".join(lines))


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

    doc = fitz.open(pdf)
    issue_name = get_issue_name(pdf)
    sections = get_toc_level1(doc)
    if not sections:
        print("[ERROR] 未检测到 TOC 一级目录，无法拆分。", file=sys.stderr)
        sys.exit(2)

    # derive page ranges [start, end]
    starts = [p for _, p in sections]
    ends: List[int] = []
    for i in range(len(starts)):
        if i < len(starts) - 1:
            ends.append(starts[i + 1] - 1)
        else:
            ends.append(doc.page_count)
    page_ranges = list(zip(starts, ends))

    base_out = base_dir / "output" / issue_name
    paths = ensure_dirs(base_out, sections)

    # export sections
    for idx, ((title, _), (sp, ep)) in enumerate(zip(sections, page_ranges), start=1):
        md_path = paths[idx]["md"]
        img_dir = paths[idx]["img"]
        # Write header with section title and page range
        header = f"# {title}\n\n> Pages {sp}-{ep}\n\n"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(header)
        export_section_markdown(doc, sp, ep, md_path, img_dir, title)

    # write index
    write_readme(base_out, issue_name, sections, page_ranges)
    doc.close()

    print(f"[OK] 导出完成: {base_out}")


if __name__ == "__main__":
    main()


