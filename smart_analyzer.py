#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能PDF分析脚本
"""

import os
import re
import datetime
from pathlib import Path
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 分类配置
CATEGORIES = {
    "政治": ["politics", "government", "election", "democracy"],
    "商业": ["business", "economy", "market", "trade"],
    "科技": ["technology", "tech", "AI", "innovation"],
    "美国": ["America", "American", "US", "USA"],
    "中国": ["China", "Chinese", "Beijing"],
    "欧洲": ["Europe", "European", "EU"],
    "非洲": ["Africa", "African"],
    "亚洲": ["Asia", "Asian", "Japan", "India"],
    "中东": ["Middle East", "Iran", "Israel"],
    "拉美": ["Latin America", "Brazil", "Mexico"],
    "国际关系": ["diplomacy", "foreign policy"],
    "环境": ["environment", "climate", "green"],
    "健康": ["health", "medical", "healthcare"],
    "教育": ["education", "university", "school"],
    "文化": ["culture", "arts", "literature"],
    "体育": ["sports", "football", "olympics"]
}

def extract_pdf_text(pdf_path):
    """提取PDF文本"""
    try:
        import PyPDF2
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except ImportError:
        logger.error("请安装PyPDF2: pip install PyPDF2")
        return ""

def categorize_article(content):
    """分类文章"""
    content_lower = content.lower()
    scores = {}
    
    for category, keywords in CATEGORIES.items():
        score = sum(1 for keyword in keywords if keyword.lower() in content_lower)
        if score > 0:
            scores[category] = score
    
    return max(scores.items(), key=lambda x: x[1])[0] if scores else "其他"

def analyze_pdf(pdf_path):
    """分析PDF"""
    logger.info(f"分析PDF: {pdf_path}")
    
    text = extract_pdf_text(pdf_path)
    if not text:
        return False
    
    # 提取日期
    filename = pdf_path.stem
    date_match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', filename)
    if not date_match:
        logger.error("无法提取日期")
        return False
    
    date_str = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    
    # 创建目录
    base_dir = Path("economist_pdfs")
    economist_dir = base_dir / f"economist_{date_str}"
    economist_dir.mkdir(exist_ok=True)
    
    # 分类文章
    paragraphs = text.split('\n\n')
    articles = []
    
    for para in paragraphs:
        para = para.strip()
        if len(para) > 50:
            category = categorize_article(para)
            articles.append({
                "content": para,
                "category": category,
                "length": len(para)
            })
    
    # 保存分类结果
    for category in CATEGORIES.keys():
        category_dir = economist_dir / category
        category_dir.mkdir(exist_ok=True)
        
        category_articles = [a for a in articles if a["category"] == category]
        
        for i, article in enumerate(category_articles):
            filename = f"{i+1:03d}_article.txt"
            filepath = category_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"分类: {category}\n")
                f.write(f"长度: {article['length']} 字符\n")
                f.write("-" * 50 + "\n")
                f.write(article['content'])
    
    # 生成报告
    report_path = economist_dir / "分类报告.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"经济学人 {date_str} 分类报告\n")
        f.write("=" * 50 + "\n\n")
        
        for category in CATEGORIES.keys():
            count = len([a for a in articles if a["category"] == category])
            f.write(f"{category}: {count} 篇\n")
    
    logger.info(f"分析完成，共处理 {len(articles)} 篇文章")
    return True

def main():
    """主函数"""
    pdf_dir = Path("economist_pdfs")
    if not pdf_dir.exists():
        logger.error("请先下载PDF文件")
        return
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logger.error("未找到PDF文件")
        return
    
    latest_pdf = max(pdf_files, key=lambda x: x.stat().st_mtime)
    analyze_pdf(latest_pdf)

if __name__ == "__main__":
    main()
