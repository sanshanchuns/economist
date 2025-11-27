#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将HTML格式的标注文件还原为Markdown格式
并合并备注，将句子成分解析改为直接引用原英文
"""

import re
import sys
import os


def extract_english_paragraphs(content):
    """提取所有英文段落"""
    paragraphs = []
    lines = content.split('\n')
    
    for line in lines:
        stripped = line.strip()
        # 移除HTML标签
        clean_line = re.sub(r'<[^>]+>', '', line)
        clean_stripped = clean_line.strip()
        
        # 检查是否是英文段落
        if clean_stripped and \
           clean_stripped[0].isupper() and \
           not clean_stripped.startswith('-') and \
           not clean_stripped.startswith('**') and \
           not clean_stripped.startswith('![') and \
           re.search(r'\b[A-Za-z]{3,}\b', clean_stripped):
            paragraphs.append(clean_stripped)
    
    return paragraphs


def html_to_markdown(content):
    """将HTML格式还原为Markdown格式"""
    # 提取英文段落
    english_paragraphs = extract_english_paragraphs(content)
    
    # 移除所有HTML标签，保留文本内容
    # 但保留图片引用
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    # 找到前一个英文段落，用于句子成分解析
    def find_previous_paragraph(current_index):
        """找到当前索引之前的最后一个英文段落"""
        for j in range(current_index - 1, -1, -1):
            line = lines[j]
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_stripped = clean_line.strip()
            if clean_stripped and clean_stripped[0].isupper() and \
               not clean_stripped.startswith('-') and \
               not clean_stripped.startswith('**') and \
               not clean_stripped.startswith('![') and \
               re.search(r'\b[A-Za-z]{3,}\b', clean_stripped):
                return clean_stripped
        return None
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 处理标题行（保留原样，但清理HTML）
        # 检查是否是标题行（前5行）
        if i < 5 and ('Leaders' in line or 'The rise of singlehood' in line or 'November 6th' in line or 'In good ways' in line):
            # 移除HTML标签，保留文本
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_line = clean_line.replace('<br/>', '').strip()
            if clean_line:
                result_lines.append(clean_line)
            i += 1
            continue
        
        # 处理图片
        if stripped.startswith('![') or '<img' in stripped:
            # 移除HTML标签，保留markdown格式
            clean_line = re.sub(r'<[^>]+>', '', line)
            if clean_line.strip():
                result_lines.append(clean_line.strip())
            i += 1
            continue
        
        # 处理空行和HTML标签行
        if not stripped or stripped.startswith('<p') or stripped.startswith('<span') or stripped.startswith('</span>') or stripped.startswith('<br'):
            # 如果是空行，保留一个空行
            if not stripped and (not result_lines or result_lines[-1].strip()):
                i += 1
                continue
            elif not stripped:
                result_lines.append('')
            i += 1
            continue
        
        # 处理备注标题
        if '备注</p>' in stripped or (stripped.startswith('**句子成分解析**') and '备注' not in result_lines[-5:]):
            # 跳过备注标题，稍后会统一添加
            i += 1
            continue
        
        # 处理词汇条目（HTML格式转换为Markdown）
        if stripped.startswith('- <strong><em>') or stripped.startswith('- <strong>'):
            # 提取词汇和内容
            # 格式：- <strong><em>word</em></strong><span style="color:#999999;">：内容</span><br/>
            vocab_match = re.search(r'- <strong><em>([^<]+)</em></strong>', stripped)
            if not vocab_match:
                vocab_match = re.search(r'- <strong>([^<]+)</strong>', stripped)
            
            if vocab_match:
                word = vocab_match.group(1)
                # 提取span内的内容
                content_match = re.search(r'<span[^>]*>(.*?)</span>', stripped, re.DOTALL)
                if content_match:
                    content_text = content_match.group(1)
                    # 移除可能存在的HTML标签
                    content_text = re.sub(r'<[^>]+>', '', content_text)
                    # 转换为Markdown格式
                    result_lines.append(f'- **{word}**{content_text}')
                else:
                    result_lines.append(f'- **{word}**')
            i += 1
            continue
        
        # 处理句子成分解析
        if stripped.startswith('**句子成分解析**'):
            # 收集句子成分解析内容
            sentence_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()
                
                # 如果遇到新的段落或备注，结束收集
                if (next_stripped and next_stripped[0].isupper() and 
                    not next_stripped.startswith('-') and 
                    not next_stripped.startswith('**') and
                    not next_stripped.startswith('![')) or \
                   (next_stripped.startswith('<p') and '备注</p>' in next_stripped):
                    break
                
                # 如果遇到新的词汇条目，结束收集
                if next_stripped.startswith('- <strong>') or next_stripped.startswith('- **'):
                    break
                
                # 处理句子成分解析行
                if next_stripped.startswith('- <strong><em>') or next_stripped.startswith('- <strong>'):
                    # 提取句子引用（第一句、第二句等）和内容
                    sent_match = re.search(r'- <strong><em>([^<]+)</em></strong>', next_stripped)
                    if not sent_match:
                        sent_match = re.search(r'- <strong>([^<]+)</strong>', next_stripped)
                    
                    if sent_match:
                        sent_ref = sent_match.group(1)
                        # 提取内容
                        content_match = re.search(r'<span[^>]*>(.*?)</span>', next_stripped, re.DOTALL)
                        content_text = content_match.group(1) if content_match else ''
                        content_text = re.sub(r'<[^>]+>', '', content_text)
                        
                        # 如果是"第一句"、"第二句"等，需要替换为原英文
                        if '句' in sent_ref:
                            # 找到前一个英文段落
                            prev_para = find_previous_paragraph(i)
                            if prev_para:
                                # 分割句子
                                sentences = re.split(r'([.!?]+)', prev_para)
                                merged = []
                                for j in range(0, len(sentences) - 1, 2):
                                    if j + 1 < len(sentences):
                                        merged.append((sentences[j] + sentences[j + 1]).strip())
                                sentences = [s for s in merged if s]
                                
                                # 提取数字
                                num_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, 
                                          '七': 7, '八': 8, '九': 9, '十': 10}
                                for num_str, num_val in num_map.items():
                                    if num_str in sent_ref:
                                        idx = num_val - 1
                                        if 0 <= idx < len(sentences):
                                            original = sentences[idx]
                                            if len(original) > 150:
                                                original = original[:150] + '...'
                                            sentence_lines.append(f'- **{original}**{content_text}')
                                            break
                                else:
                                    # 无法解析，保持原样
                                    sentence_lines.append(f'- **{sent_ref}**{content_text}')
                            else:
                                sentence_lines.append(f'- **{sent_ref}**{content_text}')
                        else:
                            # 不是句子引用，直接转换
                            sentence_lines.append(f'- **{sent_ref}**{content_text}')
                    else:
                        # 处理子项（二级列表）
                        if next_stripped.startswith('  -'):
                            clean_sub = re.sub(r'<[^>]+>', '', next_stripped)
                            sentence_lines.append(clean_sub)
                        else:
                            clean_line = re.sub(r'<[^>]+>', '', next_stripped)
                            if clean_line.strip():
                                sentence_lines.append(clean_line)
                elif next_stripped.startswith('  -'):
                    # 子项
                    clean_sub = re.sub(r'<[^>]+>', '', next_stripped)
                    sentence_lines.append(clean_sub)
                elif not next_stripped or next_stripped.startswith('</span>'):
                    # 空行或结束标签，跳过
                    pass
                else:
                    clean_line = re.sub(r'<[^>]+>', '', next_stripped)
                    if clean_line.strip():
                        sentence_lines.append(clean_line)
                
                i += 1
            
            # 添加句子成分解析
            if sentence_lines:
                result_lines.append('**句子成分解析**：')
                result_lines.extend(sentence_lines)
            continue
        
        # 处理英文段落（移除HTML标签，保留文本）
        clean_line = re.sub(r'<[^>]+>', '', line)
        if clean_line.strip():
            result_lines.append(clean_line.strip())
        
        i += 1
    
    return '\n'.join(result_lines)


def merge_notes(content):
    """合并备注：将词汇解析和句子成分解析合并到一个备注下"""
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 检测词汇条目块
        if stripped.startswith('- **') and ('/' in stripped or '"' in stripped or '：' in stripped):
            # 收集词汇条目
            vocab_lines = []
            vocab_lines.append(line)
            i += 1
            
            # 继续收集词汇条目
            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()
                
                # 如果遇到句子成分解析，结束词汇收集
                if next_stripped.startswith('**句子成分解析**'):
                    break
                # 如果是词汇条目，继续收集
                elif next_stripped.startswith('- **') and ('/' in next_stripped or '"' in next_stripped or '：' in next_stripped):
                    vocab_lines.append(next_line)
                    i += 1
                # 如果遇到空行或非词汇条目，结束收集
                elif not next_stripped or not next_stripped.startswith('- '):
                    break
                else:
                    break
            
            # 添加备注标题和词汇条目
            result_lines.append('')
            result_lines.append('**备注**：')
            result_lines.extend(vocab_lines)
            
            # 收集句子成分解析
            if i < len(lines) and lines[i].strip().startswith('**句子成分解析**'):
                # 跳过标题
                i += 1
                # 收集句子成分解析内容
                while i < len(lines):
                    next_line = lines[i]
                    next_stripped = next_line.strip()
                    
                    # 如果遇到新的段落或词汇条目，结束收集
                    if (next_stripped and next_stripped[0].isupper() and 
                        not next_stripped.startswith('-') and 
                        not next_stripped.startswith('**')) or \
                       (next_stripped.startswith('- **') and ('/' in next_stripped or '"' in next_stripped)):
                        break
                    
                    if next_stripped:
                        result_lines.append(next_line)
                    i += 1
            continue
        
        # 其他行直接添加
        result_lines.append(line)
        i += 1
    
    return '\n'.join(result_lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python 还原为markdown.py <文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 还原为Markdown格式
    markdown_content = html_to_markdown(content)
    
    # 合并备注
    merged_content = merge_notes(markdown_content)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(merged_content)
    
    print(f"已还原文件: {file_path}")


if __name__ == '__main__':
    main()

