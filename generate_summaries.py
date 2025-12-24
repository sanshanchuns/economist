#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为12-20目录下的所有文章生成中文概要
"""

import re
from pathlib import Path
from typing import List, Dict

def extract_title_from_filename(filename: str) -> str:
    """从文件名提取标题"""
    # 移除序号和扩展名
    name = filename.replace('.md', '')
    # 移除开头的数字和下划线
    name = re.sub(r'^\d+_', '', name)
    # 将下划线替换为空格
    title = name.replace('_', ' ')
    return title

def clean_markdown_content(content: str) -> str:
    """清理markdown内容，提取纯文本"""
    # 移除HTML标签
    content = re.sub(r'<[^>]+>', '', content)
    # 移除图片引用
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    # 移除样式标签
    content = re.sub(r'<span[^>]*>', '', content)
    content = re.sub(r'</span>', '', content)
    # 移除多余空白
    content = re.sub(r'\n\s*\n', '\n\n', content)
    # 移除行首行尾空白
    lines = [line.strip() for line in content.split('\n')]
    content = '\n'.join(lines)
    return content.strip()

def extract_main_content(content: str) -> str:
    """提取文章主要内容（跳过标题、日期等）"""
    lines = content.split('\n')
    main_lines = []
    skip_patterns = [
        r'^The world this week',
        r'^Leaders',
        r'^Letters',
        r'^United States',
        r'^The Americas',
        r'^Asia',
        r'^China',
        r'^Middle East',
        r'^Europe',
        r'^December \d+th \d{4}',
        r'^This article was downloaded',
        r'^Subscribers',
        r'^Sign up',
        r'^Stay on top',
        r'^Editor\'s note',
    ]
    
    in_main_content = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 跳过匹配模式的行
        should_skip = False
        for pattern in skip_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                should_skip = True
                break
        
        if should_skip:
            continue
        
        # 如果遇到明显的正文内容，开始收集
        if len(line) > 50 or (line and not line.startswith('#')):
            in_main_content = True
        
        if in_main_content:
            main_lines.append(line)
    
    return '\n'.join(main_lines)

def generate_summary(content: str, title: str) -> str:
    """生成文章概要（100字以内）"""
    # 清理内容
    cleaned = clean_markdown_content(content)
    main_content = extract_main_content(cleaned)
    
    # 提取前几段作为基础
    paragraphs = [p.strip() for p in main_content.split('\n\n') if len(p.strip()) > 50]
    
    if not paragraphs:
        # 如果没有段落，尝试从单行提取
        sentences = [s.strip() for s in main_content.split('.') if len(s.strip()) > 20]
        if sentences:
            text = '. '.join(sentences[:3])
        else:
            text = main_content[:500]
    else:
        text = ' '.join(paragraphs[:3])
    
    # 限制长度并生成概要
    # 由于需要生成中文概要，这里先提取关键信息
    # 实际的中文概要生成需要使用AI，这里先提供一个基于规则的版本
    
    # 移除引用和特殊字符
    text = re.sub(r'["\'`]', '', text)
    text = re.sub(r'\s+', ' ', text)
    
    # 提取前300个字符作为原始文本（用于后续AI处理）
    summary_text = text[:300]
    
    return summary_text

def process_all_articles(sections_dir: Path) -> List[Dict]:
    """处理所有文章"""
    article_files = sorted(sections_dir.glob("*.md"))
    results = []
    
    for article_file in article_files:
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = extract_title_from_filename(article_file.name)
            summary_text = generate_summary(content, title)
            
            results.append({
                'filename': article_file.name,
                'title': title,
                'content': content,
                'summary_text': summary_text
            })
        except Exception as e:
            print(f"处理 {article_file.name} 时出错: {e}")
    
    return results

def generate_chinese_summaries(articles: List[Dict]) -> List[Dict]:
    """为每篇文章生成中文概要（使用AI）"""
    # 这里需要调用AI API生成中文概要
    # 由于无法直接调用API，我将提供一个基于规则的方法
    # 实际使用时应该调用AI模型
    
    summaries = []
    for article in articles:
        # 提取关键信息
        content = article['summary_text']
        title = article['title']
        
        # 生成简单的中文概要（实际应该使用AI）
        # 这里先返回英文文本，后续可以用AI转换
        summaries.append({
            'title': title,
            'filename': article['filename'],
            'summary': content[:200]  # 临时方案
        })
    
    return summaries

def main():
    base_dir = Path(__file__).resolve().parent
    sections_dir = base_dir / "output" / "TheEconomist-2025-12-20" / "sections"
    
    if not sections_dir.exists():
        print(f"[ERROR] 目录不存在: {sections_dir}")
        return
    
    print(f"[INFO] 开始处理文章...")
    articles = process_all_articles(sections_dir)
    print(f"[INFO] 找到 {len(articles)} 篇文章")
    
    # 生成中文概要
    print(f"[INFO] 生成中文概要...")
    summaries = generate_chinese_summaries(articles)
    
    # 生成markdown文件
    output_file = base_dir / "output" / "TheEconomist-2025-12-20" / "文章概要.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# The Economist 2025-12-20 文章概要\n\n")
        f.write(f"共 {len(summaries)} 篇文章\n\n")
        f.write("---\n\n")
        
        for i, summary in enumerate(summaries, 1):
            f.write(f"## {i}. {summary['title']}\n\n")
            f.write(f"**文件**: `{summary['filename']}`\n\n")
            f.write(f"**概要**: {summary['summary']}\n\n")
            f.write("---\n\n")
    
    print(f"[OK] 概要文件已生成: {output_file}")

if __name__ == "__main__":
    main()

