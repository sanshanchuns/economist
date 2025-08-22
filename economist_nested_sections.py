#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济学人PDF分析脚本 - 支持嵌套栏目结构
正确处理The world this week等包含子主题的栏目
"""

import os
import re
import datetime
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('economist_nested.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 经济学人的标准栏目结构（包含嵌套栏目）
ECONOMIST_SECTIONS = {
    "The world this week": {
        "keywords": ["The world this week"],
        "description": "本周世界要闻",
        "subsections": ["Politics", "Business", "The weekly cartoon"],
        "weight": 10
    },
    "Leaders": {
        "keywords": ["Leaders"],
        "description": "社论和领导力",
        "subsections": [],  # 动态识别，不写死
        "weight": 10
    },
    "Letters": {
        "keywords": ["Letters"],
        "description": "读者来信",
        "subsections": [],
        "weight": 10
    },
    "By Invitation": {
        "keywords": ["By Invitation"],
        "description": "特邀文章",
        "subsections": [],
        "weight": 10
    },
    "Briefing": {
        "keywords": ["Briefing"],
        "description": "深度简报",
        "subsections": [],
        "weight": 10
    },
    "United States": {
        "keywords": ["United States"],
        "description": "美国新闻",
        "subsections": [],
        "weight": 10
    },
    "The Americas": {
        "keywords": ["The Americas"],
        "description": "美洲新闻",
        "subsections": [],
        "weight": 10
    },
    "Asia": {
        "keywords": ["Asia"],
        "description": "亚洲新闻",
        "subsections": [],
        "weight": 10
    },
    "China": {
        "keywords": ["China"],
        "description": "中国新闻",
        "subsections": [],
        "weight": 10
    },
    "Middle East & Africa": {
        "keywords": ["Middle East & Africa", "Middle East", "Africa"],
        "description": "中东和非洲新闻",
        "subsections": [],
        "weight": 10
    },
    "Europe": {
        "keywords": ["Europe"],
        "description": "欧洲新闻",
        "subsections": [],
        "weight": 10
    },
    "Britain": {
        "keywords": ["Britain", "British"],
        "description": "英国新闻",
        "subsections": [],
        "weight": 10
    },
    "International": {
        "keywords": ["International"],
        "description": "国际新闻",
        "subsections": [],
        "weight": 10
    },
    "Business": {
        "keywords": ["Business"],
        "description": "商业新闻",
        "subsections": [],
        "weight": 10
    },
    "Finance & economics": {
        "keywords": ["Finance & economics", "Finance", "economics"],
        "description": "金融和经济",
        "subsections": [],
        "weight": 10
    },
    "Science & technology": {
        "keywords": ["Science & technology", "Science", "technology"],
        "description": "科学和技术",
        "subsections": [],
        "weight": 10
    },
    "Culture": {
        "keywords": ["Culture", "Cultural"],
        "description": "文化",
        "subsections": [],
        "weight": 10
    },
    "Economic & financial indicators": {
        "keywords": ["Economic & financial indicators", "Economic indicators", "financial indicators"],
        "description": "经济和金融指标",
        "subsections": [],
        "weight": 10
    },
    "Obituary": {
        "keywords": ["Obituary"],
        "description": "讣告",
        "subsections": [],
        "weight": 10
    },
    "The weekly cartoon": {
        "keywords": ["The weekly cartoon", "weekly cartoon"],
        "description": "每周漫画",
        "subsections": [],
        "weight": 10
    }
}

def extract_text_from_pdf(pdf_path):
    """从PDF提取文本"""
    try:
        import PyPDF2
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except ImportError:
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            logger.error("请安装PyPDF2或pdfplumber: pip install PyPDF2")
            return ""

def identify_article_titles_in_leaders(text):
    """智能识别Leaders栏目中的文章标题"""
    lines = text.split('\n')
    articles = []
    in_leaders = False
    current_article = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 找到Leaders栏目开始
        if 'leaders' in line.lower() and len(line.strip()) < 20:
            in_leaders = True
            continue
            
        if in_leaders:
            # 如果遇到下一个主栏目，停止
            if any(keyword in line.lower() for keyword in ['letters', 'briefing', 'united states', 'the americas']) and len(line) < 30:
                break
                
            # 识别文章标题的模式
            # 1. 长标题行（20-200字符）
            # 2. 不包含特定关键词
            # 3. 通常包含政策、国家、地区等关键词
            if (len(line) > 20 and len(line) < 200 and
                not line.startswith('Leaders') and
                not line.startswith('August') and
                not line.startswith('This article') and
                not line.startswith('WHEN') and
                not line.startswith('brings together') and
                not line.startswith('Western leaders') and
                not line.startswith('In neither instance')):
                
                # 检查是否包含文章标题的特征
                if any(keyword in line.lower() for keyword in 
                       ['policy', 'china', 'europe', 'africa', 'trump', 'putin', 
                        'america', 'asian', 'allies', 'ocean', 'currents', 
                        'south africa', 'economic', 'empowerment', 'weaponisation',
                        'rare-earth', 'elements', 'backfire']):
                    
                    # 保存前一个文章
                    if current_article:
                        articles.append(current_article)
                    
                    # 开始新文章
                    clean_title = ' '.join(line.split())
                    current_article = {
                        'title': clean_title,
                        'content': [line],
                        'start_line': i
                    }
                    
            elif current_article:
                # 收集文章内容
                current_article['content'].append(line)
    
    # 保存最后一个文章
    if current_article:
        articles.append(current_article)
    
    return articles

def identify_nested_sections(text):
    """识别经济学人的嵌套栏目结构"""
    sections = []

    # 按行分割文本
    lines = text.split('\n')
    current_section = None
    current_subsection = None
    current_content = []

    # 用于聚合相同子栏目的内容
    section_aggregator = {}
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # 首先检查是否是当前主栏目的子栏目标题
        subsection_found = None
        if current_section and ECONOMIST_SECTIONS[current_section]["subsections"]:
            for subsection in ECONOMIST_SECTIONS[current_section]["subsections"]:
                # 处理长标题：检查当前行和下一行是否包含完整的子主题标题
                current_line_lower = line.lower()
                next_line = lines[i + 1].strip().lower() if i + 1 < len(lines) else ""
                combined_line = (current_line_lower + " " + next_line).strip()
                
                # 检查是否匹配子主题标题
                if (line.lower().strip() == subsection.lower() or 
                    subsection.lower() in current_line_lower or
                    subsection.lower() in combined_line):
                    subsection_found = subsection
                    break
        
        # 如果不是子栏目，再检查是否是主栏目标题
        main_section_found = None
        if not subsection_found:
            for section_name, config in ECONOMIST_SECTIONS.items():
                for keyword in config["keywords"]:
                    if keyword.lower() in line.lower():
                        main_section_found = section_name
                        break
                if main_section_found:
                    break
        
        if main_section_found:
            # 保存前一个栏目到聚合器
            if current_section and current_content:
                key = f"{current_section}|{current_subsection or ''}"
                if key not in section_aggregator:
                    section_aggregator[key] = []
                section_aggregator[key].extend(current_content)
            
            # 开始新栏目
            current_section = main_section_found
            current_subsection = None
            current_content = [line]
        elif subsection_found:
            # 保存前一个栏目到聚合器
            if current_section and current_content:
                key = f"{current_section}|{current_subsection or ''}"
                if key not in section_aggregator:
                    section_aggregator[key] = []
                section_aggregator[key].extend(current_content)
            
            # 开始新子栏目
            current_subsection = subsection_found
            current_content = [line]
        else:
            # 添加到当前栏目/子栏目
            if current_section:
                current_content.append(line)
    
    # 添加最后一个栏目到聚合器
    if current_section and current_content:
        key = f"{current_section}|{current_subsection or ''}"
        if key not in section_aggregator:
            section_aggregator[key] = []
        section_aggregator[key].extend(current_content)
    
    # 将聚合的内容转换为最终的sections列表
    for key, content_lines in section_aggregator.items():
        section_name, subsection = key.split('|')
        subsection = subsection if subsection else None
        
        sections.append({
            "name": section_name,
            "subsection": subsection,
            "content": "\n".join(content_lines),
            "length": len("\n".join(content_lines)),
            "is_nested": bool(subsection)
        })
    
    # 特殊处理Leaders栏目，识别其中的文章
    if any(section["name"] == "Leaders" for section in sections):
        leaders_articles = identify_article_titles_in_leaders(text)
        for article in leaders_articles:
            # 将Leaders文章作为子栏目添加
            sections.append({
                "name": "Leaders",
                "subsection": article["title"],
                "content": "\n".join(article["content"]),
                "length": len("\n".join(article["content"])),
                "is_nested": True
            })
    
    return sections

def create_nested_directory_structure(base_dir, date_str):
    """创建支持嵌套的目录结构"""
    economist_dir = base_dir / f"economist_{date_str}"
    economist_dir.mkdir(exist_ok=True)
    
    # 创建主栏目目录
    section_dirs = {}
    for section_name in ECONOMIST_SECTIONS.keys():
        # 清理目录名（替换特殊字符）
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', section_name)
        section_dir = economist_dir / safe_name
        section_dir.mkdir(exist_ok=True)
        section_dirs[section_name] = section_dir
    
    return economist_dir, section_dirs

def save_nested_section_content(section, section_dirs, index):
    """保存嵌套栏目内容"""
    section_name = section["name"]
    subsection = section.get("subsection")
    
    if section_name not in section_dirs:
        return False
    
    # 确定保存路径和文件名
    if subsection and ECONOMIST_SECTIONS[section_name]["subsections"]:
        # 保存到主栏目目录下，使用子主题作为文件名
        target_dir = section_dirs[section_name]
        filename = f"{subsection}.txt"
    else:
        # 保存到主栏目目录，使用主栏目名作为文件名
        target_dir = section_dirs[section_name]
        filename = f"{section_name}.txt"
    
    filepath = target_dir / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"主栏目: {section_name}\n")
            if subsection:
                f.write(f"子栏目: {subsection}\n")
            f.write(f"描述: {ECONOMIST_SECTIONS[section_name]['description']}\n")
            f.write(f"内容长度: {section['length']} 字符\n")
            f.write(f"创建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(section['content'])
        
        if subsection:
            logger.info(f"保存嵌套栏目: {section_name}/{subsection} -> {filepath}")
        else:
            logger.info(f"保存主栏目: {section_name} -> {filepath}")
        return True
    except Exception as e:
        logger.error(f"保存栏目失败 {section_name}: {e}")
        return False

def generate_nested_section_report(sections, economist_dir, date_str):
    """生成嵌套栏目报告"""
    report_path = economist_dir / "嵌套栏目分类报告.txt"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"经济学人 {date_str} 嵌套栏目分类报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"分析时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总栏目数: {len(sections)}\n")
            f.write(f"总字符数: {sum(s['length'] for s in sections):,}\n\n")
            
            # 统计主栏目
            main_section_stats = {}
            for section in sections:
                section_name = section["name"]
                if section_name not in main_section_stats:
                    main_section_stats[section_name] = {
                        "count": 0,
                        "total_length": 0,
                        "subsections": set()
                    }
                main_section_stats[section_name]["count"] += 1
                main_section_stats[section_name]["total_length"] += section["length"]
                if section.get("subsection"):
                    main_section_stats[section_name]["subsections"].add(section["subsection"])
            
            f.write("主栏目统计:\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'主栏目名称':<25} {'描述':<20} {'文章数':<8} {'字符数':<12} {'子栏目':<20}\n")
            f.write("-" * 60 + "\n")
            
            for section_name, stats in sorted(main_section_stats.items()):
                section_info = ECONOMIST_SECTIONS.get(section_name, {})
                description = section_info.get("description", "未知")
                subsections_str = ", ".join(sorted(stats["subsections"])) if stats["subsections"] else "无"
                f.write(f"{section_name:<25} {description:<20} {stats['count']:<8} {stats['total_length']:<12} {subsections_str:<20}\n")
            
            f.write("\n嵌套栏目详情:\n")
            f.write("-" * 60 + "\n")
            for i, section in enumerate(sections, 1):
                if section.get("subsection"):
                    f.write(f"{i:3d}. {section['name']}/{section['subsection']} ({section['length']} 字符)\n")
                else:
                    f.write(f"{i:3d}. {section['name']} ({section['length']} 字符)\n")
        
        logger.info(f"生成嵌套栏目报告: {report_path}")
        return True
    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        return False

def analyze_pdf_with_nested_sections(pdf_path):
    """分析PDF的嵌套栏目结构"""
    logger.info(f"开始分析PDF的嵌套栏目结构: {pdf_path}")
    
    # 提取文本
    text = extract_text_from_pdf(pdf_path)
    if not text:
        logger.error("PDF文本提取失败")
        return False
    
    logger.info(f"提取文本长度: {len(text):,} 字符")
    
    # 识别嵌套栏目
    sections = identify_nested_sections(text)
    logger.info(f"识别到 {len(sections)} 个栏目（包含嵌套）")
    
    # 提取日期
    filename = pdf_path.stem
    date_match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', filename)
    if not date_match:
        logger.error("无法提取日期")
        return False
    
    date_str = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    
    # 创建嵌套目录结构
    base_dir = Path("economist_pdfs")
    economist_dir, section_dirs = create_nested_directory_structure(base_dir, date_str)
    
    # 保存嵌套栏目内容
    logger.info("正在保存嵌套栏目内容...")
    saved_count = 0
    for i, section in enumerate(sections):
        if save_nested_section_content(section, section_dirs, i + 1):
            saved_count += 1
    
    logger.info(f"成功保存 {saved_count}/{len(sections)} 个栏目")
    
    # 生成报告
    generate_nested_section_report(sections, economist_dir, date_str)
    
    # 显示嵌套栏目信息
    logger.info("\n识别到的嵌套栏目:")
    for i, section in enumerate(sections, 1):
        if section.get("subsection"):
            logger.info(f"{i:3d}. {section['name']}/{section['subsection']} - {section['length']} 字符")
        else:
            logger.info(f"{i:3d}. {section['name']} - {section['length']} 字符")
    
    logger.info("嵌套栏目分析完成！")
    return True

def main():
    """主函数"""
    logger.info("开始执行经济学人PDF嵌套栏目分析任务")
    
    # 查找PDF文件
    pdf_dir = Path("economist_pdfs")
    if not pdf_dir.exists():
        logger.error("economist_pdfs目录不存在，请先下载PDF文件")
        return
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logger.error("未找到PDF文件")
        return
    
    # 选择最新的PDF
    latest_pdf = max(pdf_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"选择最新PDF: {latest_pdf}")
    
    # 执行嵌套栏目分析
    success = analyze_pdf_with_nested_sections(latest_pdf)
    
    if success:
        logger.info("嵌套栏目分析任务完成")
    else:
        logger.error("嵌套栏目分析任务失败")

if __name__ == "__main__":
    main()
