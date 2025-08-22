#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济学人PDF分析脚本 - 按栏目分类
按照经济学人的实际栏目结构来分类文章
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
        logging.FileHandler('economist_sections.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 经济学人的标准栏目结构
ECONOMIST_SECTIONS = {
    "The world this week": {
        "keywords": ["The world this week"],
        "description": "本周世界要闻",
        "weight": 10
    },
    "Leaders": {
        "keywords": ["Leaders"],
        "description": "社论和领导力",
        "weight": 10
    },
    "Letters": {
        "keywords": ["Letters"],
        "description": "读者来信",
        "weight": 10
    },
    "By Invitation": {
        "keywords": ["By Invitation"],
        "description": "特邀文章",
        "weight": 10
    },
    "Briefing": {
        "keywords": ["Briefing"],
        "description": "深度简报",
        "weight": 10
    },
    "United States": {
        "keywords": ["United States"],
        "description": "美国新闻",
        "weight": 10
    },
    "The Americas": {
        "keywords": ["The Americas"],
        "description": "美洲新闻",
        "weight": 10
    },
    "Asia": {
        "keywords": ["Asia"],
        "description": "亚洲新闻",
        "weight": 10
    },
    "China": {
        "keywords": ["China"],
        "description": "中国新闻",
        "weight": 10
    },
    "Middle East & Africa": {
        "keywords": ["Middle East & Africa", "Middle East", "Africa"],
        "description": "中东和非洲新闻",
        "weight": 10
    },
    "Europe": {
        "keywords": ["Europe"],
        "description": "欧洲新闻",
        "weight": 10
    },
    "Britain": {
        "keywords": ["Britain", "British"],
        "description": "英国新闻",
        "weight": 10
    },
    "International": {
        "keywords": ["International"],
        "description": "国际新闻",
        "weight": 10
    },
    "Business": {
        "keywords": ["Business"],
        "description": "商业新闻",
        "weight": 10
    },
    "Finance & economics": {
        "keywords": ["Finance & economics", "Finance", "economics"],
        "description": "金融和经济",
        "weight": 10
    },
    "Science & technology": {
        "keywords": ["Science & technology", "Science", "technology"],
        "description": "科学和技术",
        "weight": 10
    },
    "Culture": {
        "keywords": ["Culture", "Cultural"],
        "description": "文化",
        "weight": 10
    },
    "Economic & financial indicators": {
        "keywords": ["Economic & financial indicators", "Economic indicators", "financial indicators"],
        "description": "经济和金融指标",
        "weight": 10
    },
    "Obituary": {
        "keywords": ["Obituary"],
        "description": "讣告",
        "weight": 10
    },
    "The weekly cartoon": {
        "keywords": ["The weekly cartoon", "weekly cartoon"],
        "description": "每周漫画",
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

def identify_sections(text):
    """识别经济学人的栏目结构"""
    sections = []
    
    # 按行分割文本
    lines = text.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 检查是否是栏目标题
        section_found = None
        for section_name, config in ECONOMIST_SECTIONS.items():
            for keyword in config["keywords"]:
                if keyword.lower() in line.lower():
                    section_found = section_name
                    break
            if section_found:
                break
        
        if section_found:
            # 保存前一个栏目
            if current_section and current_content:
                sections.append({
                    "name": current_section,
                    "content": "\n".join(current_content),
                    "length": len("\n".join(current_content))
                })
            
            # 开始新栏目
            current_section = section_found
            current_content = [line]
        else:
            # 添加到当前栏目
            if current_section:
                current_content.append(line)
    
    # 添加最后一个栏目
    if current_section and current_content:
        sections.append({
            "name": current_section,
            "content": "\n".join(current_content),
            "length": len("\n".join(current_content))
        })
    
    return sections

def create_section_directories(base_dir, date_str):
    """创建栏目目录结构"""
    economist_dir = base_dir / f"economist_{date_str}"
    economist_dir.mkdir(exist_ok=True)
    
    # 创建栏目目录
    section_dirs = {}
    for section_name in ECONOMIST_SECTIONS.keys():
        # 清理目录名（替换特殊字符）
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', section_name)
        section_dir = economist_dir / safe_name
        section_dir.mkdir(exist_ok=True)
        section_dirs[section_name] = section_dir
    
    return economist_dir, section_dirs

def save_section_content(section, section_dir, index):
    """保存栏目内容"""
    # 清理文件名
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', section["name"])
    filename = f"{index:03d}_{safe_name}.txt"
    filepath = section_dir / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"栏目: {section['name']}\n")
            f.write(f"描述: {ECONOMIST_SECTIONS[section['name']]['description']}\n")
            f.write(f"内容长度: {section['length']} 字符\n")
            f.write(f"创建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(section['content'])
        
        logger.info(f"保存栏目: {section['name']} -> {filepath}")
        return True
    except Exception as e:
        logger.error(f"保存栏目失败 {section['name']}: {e}")
        return False

def generate_section_report(sections, economist_dir, date_str):
    """生成栏目报告"""
    report_path = economist_dir / "栏目分类报告.txt"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"经济学人 {date_str} 栏目分类报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"分析时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总栏目数: {len(sections)}\n")
            f.write(f"总字符数: {sum(s['length'] for s in sections):,}\n\n")
            
            f.write("栏目统计:\n")
            f.write("-" * 50 + "\n")
            f.write(f"{'栏目名称':<25} {'描述':<20} {'文章数':<8} {'字符数':<10}\n")
            f.write("-" * 50 + "\n")
            
            for section in sections:
                section_info = ECONOMIST_SECTIONS.get(section["name"], {})
                description = section_info.get("description", "未知")
                f.write(f"{section['name']:<25} {description:<20} {1:<8} {section['length']:<10}\n")
            
            f.write("\n栏目详情:\n")
            f.write("-" * 50 + "\n")
            for i, section in enumerate(sections, 1):
                f.write(f"{i:2d}. {section['name']} ({section['length']} 字符)\n")
        
        logger.info(f"生成栏目报告: {report_path}")
        return True
    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        return False

def analyze_pdf_by_sections(pdf_path):
    """按栏目分析PDF"""
    logger.info(f"开始按栏目分析PDF: {pdf_path}")
    
    # 提取文本
    text = extract_text_from_pdf(pdf_path)
    if not text:
        logger.error("PDF文本提取失败")
        return False
    
    logger.info(f"提取文本长度: {len(text):,} 字符")
    
    # 识别栏目
    sections = identify_sections(text)
    logger.info(f"识别到 {len(sections)} 个栏目")
    
    # 提取日期
    filename = pdf_path.stem
    date_match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', filename)
    if not date_match:
        logger.error("无法提取日期")
        return False
    
    date_str = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    
    # 创建目录结构
    base_dir = Path("economist_pdfs")
    economist_dir, section_dirs = create_section_directories(base_dir, date_str)
    
    # 保存栏目内容
    logger.info("正在保存栏目内容...")
    saved_count = 0
    for i, section in enumerate(sections):
        if section["name"] in section_dirs:
            if save_section_content(section, section_dirs[section["name"]], i + 1):
                saved_count += 1
    
    logger.info(f"成功保存 {saved_count}/{len(sections)} 个栏目")
    
    # 生成报告
    generate_section_report(sections, economist_dir, date_str)
    
    # 显示栏目信息
    logger.info("\n识别到的栏目:")
    for i, section in enumerate(sections, 1):
        section_info = ECONOMIST_SECTIONS.get(section["name"], {})
        description = section_info.get("description", "未知")
        logger.info(f"{i:2d}. {section['name']} - {description} ({section['length']} 字符)")
    
    logger.info("按栏目分析完成！")
    return True

def main():
    """主函数"""
    logger.info("开始执行经济学人PDF栏目分析任务")
    
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
    
    # 执行栏目分析
    success = analyze_pdf_by_sections(latest_pdf)
    
    if success:
        logger.info("栏目分析任务完成")
    else:
        logger.error("栏目分析任务失败")

if __name__ == "__main__":
    main()
