#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能经济学人PDF分析脚本
使用更先进的算法识别文章结构和分类
"""

import os
import re
import datetime
from pathlib import Path
import logging
import json
from collections import defaultdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 增强的文章分类配置
ENHANCED_CATEGORIES = {
    "政治": {
        "keywords": ["politics", "government", "election", "democracy", "authoritarian", "regime", "parliament", "congress", "senate", "president", "minister", "policy", "legislation", "vote", "campaign"],
        "weight": 1.2
    },
    "商业": {
        "keywords": ["business", "economy", "market", "trade", "investment", "finance", "corporate", "company", "profit", "revenue", "stock", "banking", "retail", "manufacturing", "startup"],
        "weight": 1.1
    },
    "科技": {
        "keywords": ["technology", "tech", "digital", "AI", "artificial intelligence", "innovation", "startup", "software", "algorithm", "data", "cybersecurity", "blockchain", "automation", "robotics"],
        "weight": 1.3
    },
    "美国": {
        "keywords": ["America", "American", "United States", "US", "USA", "Washington", "Congress", "Senate", "White House", "Pentagon", "Federal", "State", "California", "Texas", "New York"],
        "weight": 1.5
    },
    "中国": {
        "keywords": ["China", "Chinese", "Beijing", "Xi Jinping", "Communist Party", "CCP", "Shanghai", "Shenzhen", "Hong Kong", "Taiwan", "Belt and Road", "Made in China"],
        "weight": 1.5
    },
    "欧洲": {
        "keywords": ["Europe", "European", "EU", "European Union", "Brussels", "Berlin", "Paris", "London", "Rome", "Madrid", "Amsterdam", "Brexit", "Eurozone", "NATO"],
        "weight": 1.4
    },
    "非洲": {
        "keywords": ["Africa", "African", "Nigeria", "South Africa", "Kenya", "Ethiopia", "Egypt", "Morocco", "Ghana", "Tanzania", "sub-Saharan", "Sahel", "Horn of Africa"],
        "weight": 1.4
    },
    "亚洲": {
        "keywords": ["Asia", "Asian", "Japan", "India", "Singapore", "South Korea", "Thailand", "Vietnam", "Indonesia", "Malaysia", "Philippines", "ASEAN", "Pacific Rim"],
        "weight": 1.3
    },
    "中东": {
        "keywords": ["Middle East", "Iran", "Israel", "Saudi Arabia", "Turkey", "Syria", "Iraq", "Lebanon", "Jordan", "Palestine", "Gulf", "Persian", "Arab Spring"],
        "weight": 1.4
    },
    "拉美": {
        "keywords": ["Latin America", "Brazil", "Mexico", "Argentina", "Colombia", "Chile", "Peru", "Venezuela", "Caribbean", "Central America", "Amazon", "Andes"],
        "weight": 1.3
    },
    "国际关系": {
        "keywords": ["diplomacy", "foreign policy", "international", "global", "treaty", "alliance", "sanctions", "embassy", "ambassador", "summit", "negotiation", "conflict", "peace"],
        "weight": 1.2
    },
    "环境": {
        "keywords": ["environment", "climate", "green", "sustainability", "carbon", "renewable", "pollution", "conservation", "biodiversity", "emissions", "global warming", "clean energy"],
        "weight": 1.1
    },
    "健康": {
        "keywords": ["health", "medical", "healthcare", "pharmaceutical", "disease", "vaccine", "hospital", "doctor", "patient", "treatment", "research", "clinical trial"],
        "weight": 1.1
    },
    "教育": {
        "keywords": ["education", "university", "school", "learning", "academic", "research", "student", "teacher", "curriculum", "scholarship", "degree", "knowledge"],
        "weight": 1.0
    },
    "文化": {
        "keywords": ["culture", "arts", "literature", "film", "music", "heritage", "museum", "gallery", "theater", "festival", "tradition", "creative"],
        "weight": 1.0
    },
    "体育": {
        "keywords": ["sports", "football", "soccer", "olympics", "athletics", "competition", "team", "player", "championship", "tournament", "fitness", "exercise"],
        "weight": 1.0
    }
}

def extract_text_from_pdf(pdf_path):
    """从PDF提取文本，支持多种库"""
    text = ""
    
    # 尝试PyPDF2
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        logger.info("使用PyPDF2提取文本")
        return text
    except ImportError:
        pass
    
    # 尝试pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        logger.info("使用pdfplumber提取文本")
        return text
    except ImportError:
        pass
    
    # 尝试pymupdf
    try:
        import fitz
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        logger.info("使用PyMuPDF提取文本")
        return text
    except ImportError:
        pass
    
    logger.error("请安装以下任一库: PyPDF2, pdfplumber, 或 PyMuPDF")
    return ""

def identify_articles(text):
    """智能识别文章结构"""
    articles = []
    
    # 分割文本为段落
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    current_article = None
    
    for para in paragraphs:
        # 识别文章标题的特征
        is_title = (
            len(para) < 200 and  # 标题通常较短
            (para.isupper() or  # 全大写
             (para[0].isupper() and para.count(' ') < 15) or  # 首字母大写且词数较少
             re.match(r'^[A-Z][^.!?]*$', para)) and  # 首字母大写且无句号
            len(para) > 10  # 排除太短的段落
        )
        
        if is_title and current_article:
            # 保存前一个文章
            if current_article["content"].strip():
                articles.append(current_article)
            current_article = {"title": para, "content": para, "category": "", "confidence": 0}
        elif current_article:
            # 添加到当前文章
            current_article["content"] += "\n\n" + para
        else:
            # 开始第一个文章
            current_article = {"title": para, "content": para, "category": "", "confidence": 0}
    
    # 添加最后一个文章
    if current_article and current_article["content"].strip():
        articles.append(current_article)
    
    # 过滤太短的文章
    articles = [a for a in articles if len(a["content"]) > 100]
    
    return articles

def categorize_article_smart(article):
    """智能分类文章"""
    content = (article["title"] + " " + article["content"]).lower()
    
    category_scores = defaultdict(float)
    
    for category, config in ENHANCED_CATEGORIES.items():
        score = 0
        for keyword in config["keywords"]:
            # 计算关键词出现次数
            count = content.count(keyword.lower())
            if count > 0:
                score += count * config["weight"]
        
        if score > 0:
            category_scores[category] = score
    
    if category_scores:
        # 选择得分最高的分类
        best_category = max(category_scores.items(), key=lambda x: x[1])
        confidence = min(best_category[1] / 5.0, 1.0)  # 归一化置信度
        
        return best_category[0], confidence
    
    return "其他", 0.0

def create_organized_structure(base_dir, date_str):
    """创建有组织的目录结构"""
    economist_dir = base_dir / f"economist_{date_str}"
    economist_dir.mkdir(exist_ok=True)
    
    # 创建分类目录
    category_dirs = {}
    for category in ENHANCED_CATEGORIES.keys():
        category_dir = economist_dir / category
        category_dir.mkdir(exist_ok=True)
        category_dirs[category] = category_dir
    
    # 创建其他分类目录
    other_dir = economist_dir / "其他"
    other_dir.mkdir(exist_ok=True)
    category_dirs["其他"] = other_dir
    
    return economist_dir, category_dirs

def save_article_with_metadata(article, category_dir, index):
    """保存文章并包含元数据"""
    # 清理文件名
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', article["title"])
    safe_title = safe_title[:80]  # 限制长度
    
    filename = f"{index:03d}_{safe_title}.txt"
    filepath = category_dir / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"标题: {article['title']}\n")
            f.write(f"分类: {article['category']}\n")
            f.write(f"置信度: {article['confidence']:.2f}\n")
            f.write(f"内容长度: {len(article['content'])} 字符\n")
            f.write(f"创建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(article['content'])
        
        return True
    except Exception as e:
        logger.error(f"保存文章失败: {e}")
        return False

def generate_comprehensive_report(articles, economist_dir, date_str):
    """生成综合报告"""
    # 统计信息
    category_stats = defaultdict(lambda: {"count": 0, "total_length": 0, "avg_confidence": 0})
    
    for article in articles:
        category = article["category"]
        category_stats[category]["count"] += 1
        category_stats[category]["total_length"] += len(article["content"])
        category_stats[category]["avg_confidence"] += article["confidence"]
    
    # 计算平均值
    for category in category_stats:
        if category_stats[category]["count"] > 0:
            category_stats[category]["avg_confidence"] /= category_stats[category]["count"]
    
    # 生成报告
    report_path = economist_dir / "智能分类报告.txt"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"经济学人 {date_str} 智能分类报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"分析时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总文章数: {len(articles)}\n")
            f.write(f"总字符数: {sum(len(a['content']) for a in articles):,}\n\n")
            
            f.write("分类统计:\n")
            f.write("-" * 40 + "\n")
            f.write(f"{'分类':<15} {'数量':<8} {'平均长度':<12} {'平均置信度':<12}\n")
            f.write("-" * 40 + "\n")
            
            for category in sorted(category_stats.keys()):
                stats = category_stats[category]
                avg_length = stats["total_length"] // stats["count"] if stats["count"] > 0 else 0
                f.write(f"{category:<15} {stats['count']:<8} {avg_length:<12} {stats['avg_confidence']:<12.2f}\n")
            
            f.write("\n文章详情:\n")
            f.write("-" * 40 + "\n")
            for i, article in enumerate(articles, 1):
                f.write(f"{i:3d}. {article['title'][:50]}... -> {article['category']} (置信度: {article['confidence']:.2f})\n")
        
        logger.info(f"生成综合报告: {report_path}")
        return True
    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        return False

def analyze_pdf_intelligently(pdf_path):
    """智能分析PDF"""
    logger.info(f"开始智能分析PDF: {pdf_path}")
    
    # 提取文本
    text = extract_text_from_pdf(pdf_path)
    if not text:
        logger.error("PDF文本提取失败")
        return False
    
    logger.info(f"提取文本长度: {len(text):,} 字符")
    
    # 识别文章
    articles = identify_articles(text)
    logger.info(f"识别到 {len(articles)} 篇文章")
    
    # 提取日期
    filename = pdf_path.stem
    date_match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', filename)
    if not date_match:
        logger.error("无法提取日期")
        return False
    
    date_str = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    
    # 创建目录结构
    base_dir = Path("economist_pdfs")
    economist_dir, category_dirs = create_organized_structure(base_dir, date_str)
    
    # 分类文章
    logger.info("正在智能分类文章...")
    for i, article in enumerate(articles):
        category, confidence = categorize_article_smart(article)
        article["category"] = category
        article["confidence"] = confidence
        
        logger.info(f"文章 {i+1}: {article['title'][:50]}... -> {category} (置信度: {confidence:.2f})")
    
    # 保存文章
    logger.info("正在保存分类文章...")
    saved_count = 0
    for i, article in enumerate(articles):
        category = article["category"]
        if category in category_dirs:
            if save_article_with_metadata(article, category_dirs[category], i + 1):
                saved_count += 1
    
    logger.info(f"成功保存 {saved_count}/{len(articles)} 篇文章")
    
    # 生成报告
    generate_comprehensive_report(articles, economist_dir, date_str)
    
    # 保存JSON格式的元数据
    metadata_path = economist_dir / "文章元数据.json"
    try:
        metadata = {
            "date": date_str,
            "total_articles": len(articles),
            "categories": list(set(a["category"] for a in articles)),
            "articles": [
                {
                    "title": a["title"],
                    "category": a["category"],
                    "confidence": a["confidence"],
                    "length": len(a["content"])
                }
                for a in articles
            ]
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"保存元数据: {metadata_path}")
    except Exception as e:
        logger.error(f"保存元数据失败: {e}")
    
    logger.info("智能分析完成！")
    return True

def main():
    """主函数"""
    logger.info("开始执行智能PDF分析任务")
    
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
    
    # 执行智能分析
    success = analyze_pdf_intelligently(latest_pdf)
    
    if success:
        logger.info("智能分析任务完成")
    else:
        logger.error("智能分析任务失败")

if __name__ == "__main__":
    main()
