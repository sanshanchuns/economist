#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选适合上班族学习英语的文章
排除政治类，保留商业、人文、科学、历史等非政治类文章
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# 政治类关键词（排除）
POLITICS_KEYWORDS = [
    "politics", "political", "election", "vote", "campaign", "president", "prime minister",
    "government", "parliament", "congress", "senate", "democracy", "republican", "democrat",
    "trump", "biden", "ukraine", "russia", "war", "conflict", "military", "defense",
    "nato", "alliance", "diplomacy", "sanctions", "embargo", "coup", "revolution",
    "terrorism", "terrorist", "israel", "palestine", "gaza", "hizbullah", "iran",
    "china", "taiwan", "tibet", "hong kong", "communist party", "xi jinping",
    "north korea", "kim jong", "putin", "zelensky", "bolsonaro", "modi",
    "immigration", "refugee", "border", "deportation", "asylum"
]

# 商业类关键词（保留）
BUSINESS_KEYWORDS = [
    "business", "company", "corporate", "market", "economy", "economic", "finance",
    "financial", "bank", "banking", "investment", "investor", "stock", "trading",
    "consumer", "retail", "sales", "revenue", "profit", "loss", "ceo", "executive",
    "startup", "venture", "capital", "merger", "acquisition", "ipo", "share",
    "tech", "technology", "ai", "artificial intelligence", "digital", "e-commerce",
    "automation", "innovation", "product", "service", "brand", "marketing",
    "advertising", "supply chain", "logistics", "manufacturing", "industry"
]

# 人文类关键词（保留）
CULTURE_KEYWORDS = [
    "culture", "cultural", "art", "arts", "music", "film", "movie", "cinema",
    "literature", "book", "novel", "author", "writer", "poetry", "theater", "theatre",
    "drama", "entertainment", "media", "journalism", "journalist", "news", "magazine",
    "education", "school", "university", "college", "student", "teacher", "learning",
    "language", "linguistics", "society", "social", "community", "family", "marriage",
    "gender", "women", "men", "youth", "elderly", "generation", "tradition",
    "custom", "festival", "holiday", "religion", "philosophy", "history", "historical"
]

# 科学类关键词（保留）
SCIENCE_KEYWORDS = [
    "science", "scientific", "research", "study", "experiment", "discovery",
    "medicine", "medical", "health", "healthcare", "disease", "treatment", "therapy",
    "drug", "pharmaceutical", "vaccine", "cancer", "covid", "pandemic", "epidemic",
    "biology", "chemistry", "physics", "mathematics", "engineering", "computer science",
    "quantum", "genetics", "gene", "dna", "evolution", "climate", "environment",
    "energy", "renewable", "solar", "wind", "nuclear", "electricity", "battery",
    "space", "astronomy", "planet", "mars", "moon", "satellite", "rocket"
]

# 历史类关键词（保留）
HISTORY_KEYWORDS = [
    "history", "historical", "ancient", "medieval", "renaissance", "world war",
    "civilization", "empire", "kingdom", "dynasty", "archaeology", "archaeological",
    "monument", "heritage", "museum", "artifact", "antiquity"
]


def find_latest_output_dir(base_dir: Path) -> Optional[Path]:
    """找到最新的输出目录"""
    output_dir = base_dir / "output"
    if not output_dir.exists():
        return None
    
    # 获取所有 TheEconomist-* 目录
    economist_dirs = [d for d in output_dir.iterdir() 
                     if d.is_dir() and d.name.startswith("TheEconomist-")]
    
    if not economist_dirs:
        return None
    
    # 按目录名排序（日期格式：TheEconomist-YYYY-MM-DD）
    economist_dirs.sort(key=lambda x: x.name, reverse=True)
    return economist_dirs[0]


def classify_article(title: str, content: str) -> Tuple[str, float]:
    """
    分类文章
    返回: (类别, 置信度)
    类别: business, culture, science, history, politics, other
    """
    title_lower = title.lower()
    content_lower = content[:2000].lower()  # 检查前2000个字符
    
    combined_text = f"{title_lower} {content_lower}"
    
    # 检查政治类（优先排除）
    # 在标题中出现的政治关键词权重更高
    politics_title_score = sum(2 for keyword in POLITICS_KEYWORDS if keyword in title_lower)
    politics_content_score = sum(1 for keyword in POLITICS_KEYWORDS if keyword in content_lower)
    politics_score = politics_title_score + politics_content_score
    
    # 如果标题包含政治关键词，或者总得分>=3，很可能是政治类
    if politics_title_score > 0 or politics_score >= 3:
        return ("politics", 1.0)
    
    # 检查标题中的明显政治标识
    political_title_patterns = [
        r"shooting.*washington",
        r"immigration",
        r"deportation",
        r"election",
        r"vote",
        r"campaign",
        r"president",
        r"prime minister",
        r"government",
        r"parliament",
        r"ukraine",
        r"russia",
        r"war",
        r"conflict",
        r"peace.*deal",
        r"truce",
        r"israel",
        r"palestine",
        r"iran",
        r"china.*taiwan",
        r"communist party",
        r"rule.*india",  # 统治/统治印度
        r"monk.*rule",  # 僧侣统治
        r"put.*death",  # 处死
        r"death.*penalty",  # 死刑
        r"jailed",  # 监禁
        r"prison",  # 监狱
        r"coup",  # 政变
        r"take.*power",  # 夺权
    ]
    
    for pattern in political_title_patterns:
        if re.search(pattern, title_lower):
            return ("politics", 1.0)
    
    # 计算各类别的得分
    business_score = sum(1 for keyword in BUSINESS_KEYWORDS if keyword in combined_text)
    culture_score = sum(1 for keyword in CULTURE_KEYWORDS if keyword in combined_text)
    science_score = sum(1 for keyword in SCIENCE_KEYWORDS if keyword in combined_text)
    history_score = sum(1 for keyword in HISTORY_KEYWORDS if keyword in combined_text)
    
    # 检查标题中的栏目标识
    if "business" in title_lower or "finance" in title_lower or "economics" in title_lower:
        business_score += 3
    if "culture" in title_lower or "arts" in title_lower or "books" in title_lower:
        culture_score += 3
    if "science" in title_lower or "technology" in title_lower or "tech" in title_lower:
        science_score += 3
    if "history" in title_lower or "historical" in title_lower:
        history_score += 3
    
    # 检查内容开头的栏目标识
    content_start = content[:200].lower()
    if re.search(r'\b(business|finance|economics)\b', content_start):
        business_score += 2
    if re.search(r'\b(culture|arts|books)\b', content_start):
        culture_score += 2
    if re.search(r'\b(science|technology|tech)\b', content_start):
        science_score += 2
    
    # 找出得分最高的类别
    scores = {
        "business": business_score,
        "culture": culture_score,
        "science": science_score,
        "history": history_score,
    }
    
    max_category = max(scores.items(), key=lambda x: x[1])
    
    if max_category[1] == 0:
        return ("other", 0.0)
    
    # 计算置信度（基于得分）
    total_score = sum(scores.values())
    confidence = max_category[1] / max(total_score, 1)
    
    return (max_category[0], confidence)


def is_suitable_for_learning(title: str, content: str) -> Tuple[bool, str, float]:
    """
    判断文章是否适合学习
    返回: (是否适合, 类别, 置信度)
    """
    category, confidence = classify_article(title, content)
    
    # 排除政治类和其他类
    if category == "politics":
        return (False, category, confidence)
    
    # 排除明显的非学习类文章
    title_lower = title.lower()
    exclude_patterns = [
        r"^the world this week$",
        r"^politics$",
        r"^business$",  # 如果是栏目总览，排除
        r"weekly cartoon",
        r"economic data",
        r"obituary",
        r"shooting.*washington",  # 明确的政治事件
        r"immigration.*policy",  # 移民政策
        r"deportation",  # 驱逐出境
        r"put.*death",  # 处死
        r"jailed",  # 监禁
        r"rule.*india",  # 统治印度
        r"monk.*rule",  # 僧侣统治
    ]
    
    for pattern in exclude_patterns:
        if re.match(pattern, title_lower):
            return (False, "excluded", 0.0)
    
    # 如果置信度太低，可能分类不准确
    if confidence < 0.3 and category == "other":
        return (False, category, confidence)
    
    return (True, category, confidence)


def analyze_article(file_path: Path) -> Optional[Dict]:
    """分析单篇文章"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题（从文件名）
        title = file_path.stem
        # 移除编号前缀（如 "001_"）
        title = re.sub(r'^\d+_', '', title)
        title = title.replace('_', ' ')
        
        # 检查是否适合学习
        suitable, category, confidence = is_suitable_for_learning(title, content)
        
        if not suitable:
            return None
        
        # 提取文章的前几行作为摘要
        lines = content.split('\n')
        preview_lines = []
        for line in lines[:10]:
            line = line.strip()
            # 移除HTML标签
            line = re.sub(r'<[^>]+>', '', line)
            if line and not line.startswith('![') and len(line) > 20:
                preview_lines.append(line)
                if len(preview_lines) >= 3:
                    break
        
        preview = ' '.join(preview_lines[:3])[:200] + "..." if preview_lines else ""
        
        return {
            "file": file_path.name,
            "title": title,
            "category": category,
            "confidence": confidence,
            "preview": preview,
            "path": str(file_path.relative_to(file_path.parent.parent.parent))
        }
    except Exception as e:
        print(f"分析文章失败 {file_path}: {e}")
        return None


def generate_report(articles: List[Dict], output_dir: Path) -> str:
    """生成筛选报告"""
    # 按类别分组
    by_category = {}
    for article in articles:
        category = article["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(article)
    
    # 按置信度排序
    for category in by_category:
        by_category[category].sort(key=lambda x: x["confidence"], reverse=True)
    
    # 生成报告
    lines = []
    issue_name = output_dir.name
    
    lines.append(f"# {issue_name} 适合英文学习的文章列表\n")
    lines.append("## 筛选标准\n")
    lines.append("- **主题**：商业、人文、科学、历史等适合学习的主题\n")
    lines.append("- **排除**：政治类、时事新闻类\n")
    lines.append("- **词汇难度**：适合普通上班族（词汇量约2000-3000）\n")
    lines.append("- **内容趣味性**：话题有趣，易于理解\n")
    lines.append("- **实用性**：与日常生活、工作相关\n")
    lines.append("\n---\n\n")
    
    # 类别图标映射
    category_icons = {
        "business": "📊",
        "culture": "🎭",
        "science": "🔬",
        "history": "📚",
    }
    
    category_names = {
        "business": "商业类（Business）",
        "culture": "人文类（Culture/Humanities）",
        "science": "科学类（Science）",
        "history": "历史类（History）",
    }
    
    # 按类别输出
    total_count = 0
    for category in ["business", "culture", "science", "history"]:
        if category not in by_category:
            continue
        
        articles_list = by_category[category]
        if not articles_list:
            continue
        
        icon = category_icons.get(category, "📄")
        name = category_names.get(category, category)
        
        lines.append(f"## {icon} {name} - {len(articles_list)}篇\n\n")
        
        for idx, article in enumerate(articles_list, start=1):
            confidence_stars = "⭐" * min(5, int(article["confidence"] * 5) + 1)
            lines.append(f"### {idx}. {article['file']}\n")
            lines.append(f"- **标题**：{article['title']}\n")
            lines.append(f"- **适合度**：{confidence_stars}\n")
            lines.append(f"- **类别**：{category}\n")
            lines.append(f"- **路径**：{article['path']}\n")
            if article['preview']:
                lines.append(f"- **预览**：{article['preview']}\n")
            lines.append("\n")
        
        total_count += len(articles_list)
        lines.append("---\n\n")
    
    # 统计信息
    lines.append("## 📝 总结\n\n")
    lines.append(f"### 总计：{total_count}篇适合英文学习的文章\n\n")
    
    for category in ["business", "culture", "science", "history"]:
        if category in by_category:
            count = len(by_category[category])
            icon = category_icons.get(category, "📄")
            name = category_names.get(category, category)
            lines.append(f"- **{icon} {name}**：{count}篇\n")
    
    lines.append("\n---\n\n")
    
    # 推荐列表
    lines.append("## 💡 推荐阅读顺序\n\n")
    lines.append("### 最推荐（高置信度）\n\n")
    
    high_confidence = [a for a in articles if a["confidence"] >= 0.6]
    high_confidence.sort(key=lambda x: x["confidence"], reverse=True)
    
    for idx, article in enumerate(high_confidence[:10], start=1):
        lines.append(f"{idx}. {article['title']} ({article['category']})\n")
    
    lines.append("\n---\n\n")
    
    lines.append("## 💡 建议\n\n")
    lines.append("这些文章适合：\n")
    lines.append("- 普通上班族（词汇量约2000-3000）\n")
    lines.append("- 希望提高商务英语的读者\n")
    lines.append("- 对现代科技、社会话题感兴趣的读者\n")
    lines.append("- 需要实用英语表达的读者\n")
    lines.append("\n")
    lines.append("翻译时建议：\n")
    lines.append("- 使用\"标注风格\"进行翻译\n")
    lines.append("- 识别超纲词汇（超出2000词汇量的单词）\n")
    lines.append("- 提供IPA音标和中文解释\n")
    lines.append("- 说明词汇在文中的具体用法\n")
    
    return "".join(lines)


def main():
    """主函数"""
    base_dir = Path(__file__).resolve().parent
    
    # 找到最新的输出目录
    latest_dir = find_latest_output_dir(base_dir)
    if not latest_dir:
        print("[ERROR] 未找到输出目录", file=__import__('sys').stderr)
        return
    
    print(f"[INFO] 找到最新目录: {latest_dir.name}")
    
    # 获取所有文章文件
    sections_dir = latest_dir / "sections"
    if not sections_dir.exists():
        print(f"[ERROR] 未找到 sections 目录: {sections_dir}", file=__import__('sys').stderr)
        return
    
    article_files = sorted(sections_dir.glob("*.md"))
    print(f"[INFO] 找到 {len(article_files)} 篇文章")
    
    # 分析每篇文章
    suitable_articles = []
    for article_file in article_files:
        result = analyze_article(article_file)
        if result:
            suitable_articles.append(result)
    
    print(f"[INFO] 筛选出 {len(suitable_articles)} 篇适合学习的文章")
    
    # 生成报告
    report = generate_report(suitable_articles, latest_dir)
    
    # 保存报告
    output_file = latest_dir / "适合英文学习的文章列表.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[OK] 报告已保存: {output_file}")
    
    # 打印统计信息
    by_category = {}
    for article in suitable_articles:
        category = article["category"]
        by_category[category] = by_category.get(category, 0) + 1
    
    print("\n[统计]")
    for category, count in sorted(by_category.items()):
        print(f"  {category}: {count}篇")


if __name__ == "__main__":
    main()

