#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标注风格视觉优化脚本

功能：
1. 恢复标题样式（参考76风格）
2. 给单词解析部分加上统一的头部"备注"
3. 每个单词加粗（确保格式正确）
4. 音标弱化，使用更淡的灰色
5. 每个单词解析末尾统一加上网页换行符<br>
6. 每个单词在原文段落中加粗、加下划线，字体颜色使用莫兰迪红色（#A24C4A）
7. 合并备注（词汇解析和句子成分解析在一个备注下）
8. 自动将句子成分解析中的"第一句"、"第二句"等替换为直接引用原英文句子
"""

import re
import sys
import os
from pathlib import Path


def extract_vocabulary_words(div_content):
    """从div内容中提取所有词汇"""
    words = []
    # 匹配格式：- **word** 或 - <strong>word</strong> 或 - <strong><em>word</em></strong>
    pattern1 = r'- \*\*([^*]+)\*\*'
    pattern2 = r'- <strong><em>([^<]+)</em></strong>'
    pattern3 = r'- <strong>([^<]+)</strong>'
    matches1 = re.findall(pattern1, div_content)
    matches2 = re.findall(pattern2, div_content)
    matches3 = re.findall(pattern3, div_content)
    return matches1 + matches2 + matches3


def highlight_word_in_text(text, word):
    """在文本中高亮单词（加粗、下划线、莫兰迪红色），避免在HTML标签内替换"""
    # 转义特殊字符
    escaped_word = re.escape(word)
    
    # 处理短语（包含空格的词汇）
    if ' ' in word:
        # 短语需要匹配整个短语（不使用单词边界，因为短语中间有空格）
        pattern = r'(' + escaped_word + r')'
    else:
        # 单词匹配（使用单词边界）
        pattern = r'\b(' + escaped_word + r')\b'
    
    def replace_func(match):
        matched_word = match.group(1)
        start_pos = match.start()
        
        # 检查是否已经在HTML标签内（避免重复高亮）
        before_text = text[:start_pos]
        # 找到最后一个未闭合的标签
        last_open_tag = before_text.rfind('<span')
        last_close_tag = before_text.rfind('</span>')
        
        # 如果最后一个未闭合的标签是<span>，说明当前单词在标签内
        if last_open_tag > last_close_tag:
            return matched_word
        
        return f'<span style="color:#A24C4A; font-weight:bold; text-decoration:underline;">{matched_word}</span>'
    
    # 替换所有匹配的单词（不区分大小写）
    text = re.sub(pattern, replace_func, text, flags=re.IGNORECASE)
    return text


def format_phonetic(phonetic_text):
    """格式化音标，使用更淡的灰色"""
    # 音标格式：/[音标]/
    return f'<span style="color:#999999;">{phonetic_text}</span>'


def add_annotation_header(div_content):
    """给单词解析部分添加头部'备注'"""
    header = '<p style="font-weight:bold; margin-bottom:8px; color:#666;">备注</p>'
    return header + '\n' + div_content


def process_vocabulary_entry(line):
    """处理单个词汇条目"""
    # 清理已有的灰色span标签和多余的闭合标签
    line = re.sub(r'<span style="color:#999999;">(.*?)</span>', r'\1', line, flags=re.DOTALL)
    # 清理多余的</span>标签
    line = re.sub(r'</span></span>', r'</span>', line)
    line = re.sub(r'</span>', '', line)  # 先清理所有</span>
    line = re.sub(r'<span[^>]*>', '', line)  # 清理所有<span>
    # 清理已有的strong、em或b标签
    line = re.sub(r'<strong><em>(.*?)</em></strong>', r'\1', line)
    line = re.sub(r'<strong>(.*?)</strong>', r'\1', line)
    line = re.sub(r'<em>(.*?)</em>', r'\1', line)
    line = re.sub(r'<b>(.*?)</b>', r'\1', line)
    
    # 匹配格式：- **word** 或 - <strong>word</strong> 或 - <strong><em>word</em></strong>
    # 找到单词后面的所有内容（从冒号开始到行尾，排除<br>）
    # 先尝试匹配已存在的<strong><em>格式
    pattern1 = r'(- <strong><em>([^<]+)</em></strong>)(.*?)(<br/>|$)'
    # 再匹配<strong>格式
    pattern2 = r'(- <strong>([^<]+)</strong>)(.*?)(<br/>|$)'
    # 最后匹配**格式
    pattern3 = r'(- \*\*([^*]+)\*\*)(.*?)(<br/>|$)'
    # 匹配纯文本格式（单词后直接跟冒号、斜杠或其他符号）
    # 匹配：- word/ 或 - word： 或 - word: 格式（支持包含空格的短语）
    # 匹配从- 开始到第一个冒号、斜杠或中文冒号之间的所有内容（包括空格）作为单词
    pattern4 = r'(- (.+?)[：:/])(.*?)(<br/>|$)'
    # 匹配：- word" 格式（单词后直接跟引号）
    pattern5 = r'(- (.+?)")(.*?)(<br/>|$)'
    
    def replace_entry(match):
        prefix = match.group(1)  # - **word** 或 - <strong>word</strong>
        word = match.group(2)  # word（不包含标记）
        content_part = match.group(3)  # 后面的所有内容
        br_part = match.group(4) if match.group(4) else ''  # <br/>或行尾
        
        # 将单词改为HTML加粗斜体标签：- <strong><em>word</em></strong>
        word_part = f'- <strong><em>{word}</em></strong>'
        
        # 将后面的所有内容用灰色span包裹，在单词和内容之间添加中文冒号
        if content_part.strip():
            # 移除可能存在的多余空格
            content_part = content_part.strip()
            # 如果内容不是以中文冒号开头，则添加中文冒号
            if not content_part.startswith('：'):
                content_part = '：' + content_part
            return f'{word_part}<span style="color:#999999;">{content_part}</span>{br_part}'
        else:
            return match.group(0)
    
    # 按顺序尝试匹配
    if re.search(pattern1, line):
        line = re.sub(pattern1, replace_entry, line)
    elif re.search(pattern2, line):
        line = re.sub(pattern2, replace_entry, line)
    elif re.search(pattern3, line):
        line = re.sub(pattern3, replace_entry, line)
    elif re.search(pattern4, line):
        line = re.sub(pattern4, replace_entry, line)
    elif re.search(pattern5, line):
        # 对于pattern5，需要在引号前添加中文冒号
        def replace_entry_with_quote(match):
            prefix = match.group(1)  # - word"
            word = match.group(2)  # word
            content_part = match.group(3)  # 后面的内容（包括引号）
            br_part = match.group(4) if match.group(4) else ''  # <br/>或行尾
            
            word_part = f'- <strong><em>{word}</em></strong>'
            if content_part.strip():
                content_part = content_part.strip()
                # 确保引号前有中文冒号
                if content_part.startswith('"'):
                    content_part = '："' + content_part[1:]
                elif '配对、结合"' in content_part:
                    # 特殊情况：配对、结合" 应该改为 "配对、结合"
                    content_part = content_part.replace('配对、结合"', '"配对、结合"')
                    if not content_part.startswith('：'):
                        content_part = '：' + content_part
                elif not content_part.startswith('：'):
                    content_part = '：' + content_part
                return f'{word_part}<span style="color:#999999;">{content_part}</span>{br_part}'
            else:
                return match.group(0)
        line = re.sub(pattern5, replace_entry_with_quote, line)
    
    # 修复已处理过的行：如果音标被包含在<strong><em>标签内，需要移出
    # 匹配格式：<strong><em>word[音标]</em></strong>
    def fix_phonetic_in_tag(match):
        full_content = match.group(0)
        word_with_phonetic = match.group(1)
        # 检查是否包含音标格式 [音标]
        phonetic_pattern = r'\[([^\]]+)\]'
        if re.search(phonetic_pattern, word_with_phonetic):
            # 分离单词和音标
            word_only = re.sub(r'\[[^\]]+\]', '', word_with_phonetic).strip()
            phonetic_match = re.search(phonetic_pattern, word_with_phonetic)
            phonetic = phonetic_match.group(1) if phonetic_match else ''
            # 重新构建：<strong><em>word</em></strong>，音标会在后续处理中添加到灰色span内
            return f'<strong><em>{word_only}</em></strong>'
        return full_content
    
    # 修复音标在标签内的问题
    line = re.sub(r'<strong><em>([^<]+\[[^\]]+\][^<]*)</em></strong>', fix_phonetic_in_tag, line)
    
    # 修复音标在标签外但不在灰色span内的问题
    # 匹配格式：<strong><em>word</em></strong>：[音标]<span style="color:#999999;">...
    def fix_phonetic_outside_span(match):
        word_tag = match.group(1)  # <strong><em>word</em></strong>
        phonetic = match.group(2)  # 音标内容
        span_content = match.group(3)  # span内的内容
        
        # 将音标移到span内，并在音标前添加中文冒号（如果还没有）
        if span_content.strip():
            # 检查span内容是否以中文冒号开头
            if not span_content.strip().startswith('：'):
                span_content = '：' + span_content.strip()
            # 将音标添加到span内容开头，确保音标后有斜杠
            if not span_content.strip().startswith('：'):
                span_content = '：' + span_content.strip()
            # 检查音标后是否有斜杠，如果没有则添加
            phonetic_part = f'[{phonetic}]'
            if not span_content.strip().startswith('：' + phonetic_part + '/'):
                # 移除开头的冒号（如果有），然后添加音标和斜杠
                span_content = span_content.strip().lstrip('：')
                span_content = f'：{phonetic_part}/ ' + span_content
            return f'{word_tag}<span style="color:#999999;">{span_content}</span>'
        else:
            return match.group(0)
    
    # 匹配：<strong><em>word</em></strong>：[音标]<span style="color:#999999;">...
    line = re.sub(r'(<strong><em>[^<]+</em></strong>)：\[([^\]]+)\](<span style="color:#999999;">.*?</span>)', fix_phonetic_outside_span, line)
    
    # 确保末尾有<br/>标签（如果还没有）
    line = line.rstrip()
    if not line.endswith('<br/>'):
        line = line + '<br/>'
    
    # 后处理：修复引号位置问题
    # 匹配：<span style="color:#999999;">：配对、结合"；...
    line = re.sub(r'(<span style="color:#999999;">：)配对、结合"', r'\1"配对、结合"', line)
    
    # 后处理：修复音标后缺少斜杠的问题
    # 匹配：<span style="color:#999999;">：[音标]："...
    line = re.sub(r'(<span style="color:#999999;">：\[[^\]]+\])："', r'\1/ "', line)
    # 匹配：<span style="color:#999999;">：[音标]"...
    line = re.sub(r'(<span style="color:#999999;">：\[[^\]]+\])"', r'\1/ "', line)
    # 匹配：<span style="color:#999999;">：[音标] "...
    line = re.sub(r'(<span style="color:#999999;">：\[[^\]]+\])\s+"', r'\1/ "', line)
    
    return line


def split_paragraph_into_sentences(paragraph):
    """将段落分割成句子"""
    # 移除HTML标签
    clean_para = re.sub(r'<[^>]+>', '', paragraph)
    # 按句号、问号、感叹号分割句子
    sentences = re.split(r'([.!?]+)', clean_para)
    # 合并句子和标点
    merged = []
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            merged.append((sentences[i] + sentences[i + 1]).strip())
    return [s for s in merged if s]


def restore_title_styles(content):
    """恢复标题样式（参考76风格）"""
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    # 检查前几行是否已经有完整的标题（最多检查10行）
    has_complete_title = False
    title_count = 0
    for j in range(min(10, len(lines))):
        line = lines[j].strip()
        if '<span style="color:#E3120B' in line or '<span style="color:#000000; font-size:29.1pt' in line or '<span style="color:#000000; font-size:21.0pt' in line:
            title_count += 1
        if title_count >= 4:  # 如果有4行标题格式，说明标题已经完整
            has_complete_title = True
            break
    
    # 如果已经有完整的标题，直接返回原内容（只确保格式正确）
    if has_complete_title:
        return content
    
    # 检查前几行是否是标题（最多检查10行，因为可能有空行）
    while i < len(lines) and i < 10:
        line = lines[i]
        stripped = line.strip()
        
        # 检查是否已经有正确的HTML格式
        if '<span style="color:#E3120B' in stripped or '<span style="color:#000000; font-size:21.0pt' in stripped or '<span style="color:#000000; font-size:29.1pt' in stripped:
            # 已经有格式，保持原样
            result_lines.append(line)
            i += 1
            continue
        
        # 跳过空行
        if not stripped:
            result_lines.append(line)
            i += 1
            continue
        
        # 跳过图片行
        if stripped.startswith('![') or stripped.startswith('<img'):
            result_lines.append(line)
            i += 1
            continue
        
        # 检测标题行（第一行非空非图片行）
        # 移除已有的HTML标签和<br/>标签
        clean_line = re.sub(r'<[^>]+>', '', stripped)
        clean_line = clean_line.replace('<br/>', '').strip()
        
        # 检查是否是栏目+子栏目格式（包含|）
        if '|' in clean_line and len(clean_line.split('|')) == 2:
            parts = clean_line.split('|', 1)
            section = parts[0].strip()
            subsection = parts[1].strip()
            # 移除subsection中的高亮标签（如果有）
            subsection = re.sub(r'<[^>]+>', '', subsection).strip()
            result_lines.append(f'<span style="color:#E3120B; font-size:14.5pt; font-weight:bold;">{section}</span> <span style="color:#000000; font-size:14.5pt; font-weight:bold;">| {subsection}</span>')
            i += 1
            # 继续读取下一行（主标题）
            if i < len(lines):
                next_line = lines[i].strip()
                clean_next = re.sub(r'<[^>]+>', '', next_line).replace('<br/>', '').strip()
                # 跳过空行和图片
                while i < len(lines) and (not clean_next or clean_next.startswith('![') or clean_next.startswith('<img')):
                    if not clean_next:
                        result_lines.append(lines[i])
                    else:
                        result_lines.append(lines[i])
                    i += 1
                    if i < len(lines):
                        next_line = lines[i].strip()
                        clean_next = re.sub(r'<[^>]+>', '', next_line).replace('<br/>', '').strip()
                
                if i < len(lines) and clean_next and clean_next[0].isupper():
                    result_lines.append(f'<span style="color:#000000; font-size:29.1pt; font-weight:bold;">{clean_next}</span>')
                    i += 1
                    # 继续读取副标题和日期
                    if i < len(lines):
                        next_line = lines[i].strip()
                        clean_next = re.sub(r'<[^>]+>', '', next_line).replace('<br/>', '').strip()
                        # 跳过空行和图片
                        while i < len(lines) and (not clean_next or clean_next.startswith('![') or clean_next.startswith('<img')):
                            if not clean_next:
                                result_lines.append(lines[i])
                            else:
                                result_lines.append(lines[i])
                            i += 1
                            if i < len(lines):
                                next_line = lines[i].strip()
                                clean_next = re.sub(r'<[^>]+>', '', next_line).replace('<br/>', '').strip()
                        
                        # 检查是否是副标题（通常比较短，且不是日期）
                        if clean_next and len(clean_next) < 100 and not re.match(r'^\d+', clean_next) and ('December' in clean_next or 'November' in clean_next or 'October' in clean_next or clean_next[0].isupper()):
                            # 如果是日期
                            if any(month in clean_next for month in ['December', 'November', 'October', 'September', 'August', 'July', 'June', 'May', 'April', 'March', 'February', 'January']):
                                result_lines.append(f'<span style="color:#808080; font-size:10.9pt;">{clean_next}</span>')
                                i += 1
                            # 如果是副标题
                            elif clean_next[0].isupper() and len(clean_next.split()) < 15:
                                result_lines.append(f'<span style="color:#808080; font-size:14.5pt; font-weight:bold; font-style:italic;">{clean_next}</span>')
                                i += 1
                                # 再读取日期
                                if i < len(lines):
                                    next_line = lines[i].strip()
                                    clean_next = re.sub(r'<[^>]+>', '', next_line).replace('<br/>', '').strip()
                                    if any(month in clean_next for month in ['December', 'November', 'October', 'September', 'August', 'July', 'June', 'May', 'April', 'March', 'February', 'January']):
                                        result_lines.append(f'<span style="color:#808080; font-size:10.9pt;">{clean_next}</span>')
                                        i += 1
            continue
        
        result_lines.append(line)
        i += 1
    
    # 添加剩余的行
    while i < len(lines):
        result_lines.append(lines[i])
        i += 1
    
    return '\n'.join(result_lines)


def process_file(file_path):
    """处理整个文件"""
    import os
    
    # 转换为绝对路径
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 如果文件开头是图片，尝试从sections文件中读取标题
    lines = content.split('\n')
    first_non_empty = None
    for line in lines[:5]:
        if line.strip() and not line.strip().startswith('<p'):
            first_non_empty = line.strip()
            break
    
    # 检查文件开头是否有标题（检查前10行是否有HTML格式的标题）
    has_title = False
    for line in lines[:10]:
        if '<span style="color:#E3120B' in line or '<span style="color:#000000; font-size:29.1pt' in line or '<span style="color:#000000; font-size:21.0pt' in line:
            has_title = True
            break
    
    if not has_title and first_non_empty and (first_non_empty.startswith('![') or first_non_empty.startswith('<img')):
        # 尝试从sections文件中读取标题
        dir_path = os.path.dirname(file_path)
        sections_dir = os.path.join(os.path.dirname(dir_path), 'sections')
        filename = os.path.basename(file_path)
        # 移除_Chinese后缀
        if filename.endswith('_Chinese.md'):
            base_name = filename[:-11] + '.md'
        else:
            base_name = filename
        sections_file = os.path.join(sections_dir, base_name)
        
        if os.path.exists(sections_file):
            with open(sections_file, 'r', encoding='utf-8') as sf:
                sections_content = sf.read()
                sections_lines = sections_content.split('\n')
                # 提取前4行作为标题
                title_lines = []
                for i in range(min(4, len(sections_lines))):
                    line = sections_lines[i].strip()
                    if line and not line.startswith('!['):
                        title_lines.append(line)
                    elif line.startswith('!['):
                        break
                
                # 如果有标题，添加到内容开头
                if title_lines:
                    title_content = '\n'.join(title_lines) + '\n<br/>\n'
                    content = title_content + content
    
    # 恢复标题样式
    content = restore_title_styles(content)
    
    # 先清理已经存在的灰色span标签（在词汇条目中的）
    # 递归清理所有嵌套的灰色span标签
    def clean_gray_spans(text):
        # 清理格式：- **word**<span style="color:#999999;">内容</span> -> - **word**内容
        # 先清理最外层的（匹配词汇条目中的灰色span）
        text = re.sub(r'(- \*\*[^*]+\*\*)<span style="color:#999999;">(.*?)</span>', r'\1\2', text, flags=re.DOTALL)
        
        # 清理所有嵌套的灰色span标签（多次清理直到没有嵌套）
        max_iterations = 20
        for _ in range(max_iterations):
            new_text = re.sub(r'<span style="color:#999999;"><span style="color:#999999;">(.*?)</span></span>', r'<span style="color:#999999;">\1</span>', text, flags=re.DOTALL)
            # 清理格式错误的嵌套：<span style=<span style="color:#999999;">"color:#999999;">...</span>
            new_text = re.sub(r'<span style=<span style="color:#999999;">"[^"]*">(.*?)</span>', r'<span style="color:#999999;">\1</span>', new_text, flags=re.DOTALL)
            if new_text == text:
                break
            text = new_text
        
        # 清理所有单独的灰色span（在词汇条目中的，但保留"标注"标题）
        # 只清理词汇条目行中的灰色span
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip().startswith('- **'):
                # 这是词汇条目，清理其中的灰色span
                line = re.sub(r'<span style="color:#999999;">(.*?)</span>', r'\1', line, flags=re.DOTALL)
            cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)
    
    # 只清理div内的灰色span
    div_pattern_temp = r'(<div[^>]*style="background-color:#f5f5f5[^"]*"[^>]*>)(.*?)(</div>)'
    def clean_div_spans(match):
        div_open = match.group(1)
        div_content = match.group(2)
        div_close = match.group(3)
        cleaned_content = clean_gray_spans(div_content)
        return div_open + cleaned_content + div_close
    
    content = re.sub(div_pattern_temp, clean_div_spans, content, flags=re.DOTALL)
    
    # 清理可能存在的span包裹（移除之前添加的span包裹）
    # 匹配：<span style="font-size:0.8em;">...</span> 在div内
    content = re.sub(
        r'(<div[^>]*>)\s*<span style="font-size:0\.8em;">(.*?)</span>\s*(</div>)',
        r'\1\2\3',
        content,
        flags=re.DOTALL
    )
    
    # 提取所有词汇（从div中）
    div_pattern = r'(<div[^>]*style="background-color:#f5f5f5[^"]*"[^>]*>)(.*?)(</div>)'
    
    def process_div(match):
        div_open = match.group(1)
        div_content = match.group(2)
        div_close = match.group(3)
        
        # 提取词汇列表
        words = extract_vocabulary_words(div_content)
        
        # 处理div内容：添加头部、格式化条目
        lines = div_content.split('\n')
        processed_lines = []
        has_header = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 如果是词汇条目（匹配多种格式）
            # 匹配：- **word** 或 - <strong>word</strong> 或 - word/ 或 - word： 或 - word: 或 - word" 格式
            if (line.startswith('- **') or line.startswith('- <strong>') or 
                (line.startswith('- ') and ('：' in line or ':' in line or '/' in line or '"' in line))):
                if not has_header:
                    # 备注标题：字号减小，使用0.8em
                    processed_lines.append('<p style="font-weight:bold; margin-bottom:8px; color:#666; font-size:0.8em;">备注</p>')
                    has_header = True
                
                # 处理词汇条目
                processed_line = process_vocabulary_entry(line)
                processed_lines.append(processed_line)
        
        if processed_lines:
            # 处理内容，移除div标签，只保留内容
            processed_content = '\n'.join(processed_lines)
            
            # 直接返回内容，不包含div标签
            # 如果需要保留样式，可以在每个元素上添加，但这里直接移除div
            return processed_content
        else:
            return match.group(0)  # 如果没有处理，返回原内容
    
    # 处理所有div块
    content = re.sub(div_pattern, process_div, content, flags=re.DOTALL)
    
    # 处理直接使用Markdown格式的词汇条目（不在div标签内）
    # 使用逐行处理的方式，合并词汇和句子成分解析到一个备注中
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    # 找到前一个英文段落，用于句子成分解析时引用原英文
    def find_previous_english_paragraph(lines, current_index):
        """找到当前索引之前的最后一个英文段落"""
        for j in range(current_index - 1, -1, -1):
            line = lines[j].strip()
            # 跳过空行、备注、图片等
            if not line or \
               line.startswith('<p style') or \
               line.startswith('**') or \
               line.startswith('- ') or \
               line.startswith('![') or \
               line.startswith('<span') or \
               line.startswith('</span>') or \
               any(tag in line for tag in ['<div', '</div>', '<strong', '<em']):
                continue
            # 如果是英文段落（以大写字母开头）
            if line and line[0].isupper():
                return line
        return None
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 跳过Markdown格式的备注标题
        if stripped.startswith('**备注**') or stripped.startswith('**备注**：'):
            i += 1
            continue
        
        # 检测词汇条目块的开始（- **word**格式，且不在div标签内）
        if (stripped.startswith('- **') and
            not any(tag in line for tag in ['<div', '</div>', '<span', '</span>']) and
            ('/' in stripped or '"' in stripped or '：' in stripped)):
            # 收集词汇条目
            vocab_block_lines = []
            vocab_block_lines.append(line)
            i += 1
            
            # 继续收集词汇条目，直到遇到非词汇条目或句子成分解析
            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()
                
                # 如果遇到句子成分解析，结束词汇块收集
                if next_stripped.startswith('**句子成分解析**'):
                    break
                # 如果是词汇条目（包含音标标记/或中文引号"），继续收集
                elif (next_stripped.startswith('- **') and ('/' in next_stripped or '"' in next_stripped or '：' in next_stripped)) or \
                     (next_stripped.startswith('- ') and ('/' in next_stripped or '"' in next_stripped or '：' in next_stripped)):
                    vocab_block_lines.append(next_line)
                    i += 1
                # 如果遇到空行或非词汇条目，结束词汇块
                elif not next_stripped or not next_stripped.startswith('- '):
                    break
                else:
                    break
            
            # 收集句子成分解析部分
            sentence_analysis_lines = []
            if i < len(lines) and lines[i].strip().startswith('**句子成分解析**'):
                # 跳过句子成分解析标题
                i += 1
                # 收集句子成分解析内容，直到遇到新的段落或备注
                while i < len(lines):
                    next_line = lines[i]
                    next_stripped = next_line.strip()
                    
                    # 如果遇到新的备注标题或新的段落，结束收集
                    if (next_stripped.startswith('<p style') and '备注</p>' in next_stripped) or \
                       (next_stripped.startswith('**句子成分解析**')) or \
                       (next_stripped and next_stripped[0].isupper() and not next_stripped.startswith('-') and not next_stripped.startswith('**')):
                        break
                    # 如果遇到新的词汇条目块，结束收集
                    if (next_stripped.startswith('- **') and 
                        ('/' in next_stripped or '"' in next_stripped or '：' in next_stripped)):
                        break
                    
                    sentence_analysis_lines.append(next_line)
                    i += 1
            
            # 处理词汇块和句子成分解析，合并到一个备注中
            processed_content = []
            has_header = False
            
            # 处理词汇条目
            for vocab_line in vocab_block_lines:
                vocab_stripped = vocab_line.strip()
                if not vocab_stripped:
                    continue
                
                if (vocab_stripped.startswith('- **') or vocab_stripped.startswith('- <strong>') or 
                    (vocab_stripped.startswith('- ') and ('：' in vocab_stripped or ':' in vocab_stripped or '/' in vocab_stripped or '"' in vocab_stripped))):
                    if not has_header:
                        processed_content.append('<p style="font-weight:bold; margin-bottom:8px; color:#666; font-size:0.8em;">备注</p>')
                        has_header = True
                    
                    processed_line = process_vocabulary_entry(vocab_line)
                    processed_content.append(processed_line)
            
            # 处理句子成分解析，将"第一句"、"第二句"等改为直接引用原英文
            if sentence_analysis_lines:
                # 找到前一个英文段落
                prev_paragraph = find_previous_english_paragraph(lines, i - len(sentence_analysis_lines) - 1)
                
                # 将段落分割成句子
                sentences = []
                if prev_paragraph:
                    sentences = split_paragraph_into_sentences(prev_paragraph)
                
                # 处理句子成分解析，替换"第一句"、"第二句"等为原英文
                for sent_line in sentence_analysis_lines:
                    sent_stripped = sent_line.strip()
                    if not sent_stripped:
                        continue
                    
                    # 匹配格式：- <strong><em>第二句</em></strong><span style="color:#999999;">：...</span>
                    def replace_sentence_ref(match):
                        full_match = match.group(0)
                        sentence_num = match.group(1)  # "第一句"、"第二句"等
                        # 获取span标签内的内容（如果有）
                        if len(match.groups()) > 1:
                            span_tag = match.group(2) if match.group(2) else ''
                            # 提取span标签内的文本内容
                            span_content_match = re.search(r'<span[^>]*>(.*?)</span>', span_tag, re.DOTALL)
                            if span_content_match:
                                rest_content = span_content_match.group(1)
                            else:
                                rest_content = span_tag
                        else:
                            rest_content = ''
                        
                        # 从原英文段落中提取对应的句子
                        if sentences:
                            # 提取数字（第一句=1，第二句=2，等等）
                            num_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                                      '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15}
                            
                            # 尝试匹配中文数字
                            for num_str, num_val in num_map.items():
                                if num_str in sentence_num:
                                    idx = num_val - 1
                                    if 0 <= idx < len(sentences):
                                        original_sentence = sentences[idx].strip()
                                        # 移除可能的高亮标签
                                        original_sentence = re.sub(r'<span[^>]*>', '', original_sentence)
                                        original_sentence = re.sub(r'</span>', '', original_sentence)
                                        # 如果句子太长，截取前150个字符
                                        if len(original_sentence) > 150:
                                            original_sentence = original_sentence[:150] + '...'
                                        return f'- <strong><em>{original_sentence}</em></strong><span style="color:#999999;">：{rest_content}</span><br/>'
                            
                            # 如果无法解析数字，使用第一个句子
                            if len(sentences) > 0:
                                original_sentence = sentences[0].strip()
                                original_sentence = re.sub(r'<span[^>]*>', '', original_sentence)
                                original_sentence = re.sub(r'</span>', '', original_sentence)
                                if len(original_sentence) > 150:
                                    original_sentence = original_sentence[:150] + '...'
                                return f'- <strong><em>{original_sentence}</em></strong><span style="color:#999999;">：{rest_content}</span><br/>'
                        
                        # 如果找不到原英文，保持原样
                        return full_match
                    
                    # 匹配并替换（处理已处理的HTML格式）
                    sent_line = re.sub(
                        r'- <strong><em>([^<]+?句)</em></strong>(<span style="color:#999999;">.*?</span>)(<br/>|$)',
                        replace_sentence_ref,
                        sent_line,
                        flags=re.DOTALL
                    )
                    # 匹配Markdown格式（未处理的格式）
                    sent_line = re.sub(
                        r'- \*\*([^*]+?句)\*\*(.*?)(<br/>|$)',
                        replace_sentence_ref,
                        sent_line,
                        flags=re.DOTALL
                    )
                    
                    processed_content.append(sent_line)
            
            if processed_content:
                # 用span包裹所有内容（不包括备注标题）
                if len(processed_content) > 1:
                    result_lines.append(processed_content[0])  # 备注标题
                    result_lines.append('<span style="font-size:0.8em;">')
                    result_lines.extend(processed_content[1:])
                    result_lines.append('</span>')
                else:
                    result_lines.extend(processed_content)
        else:
            # 非词汇条目，直接添加
            result_lines.append(line)
            i += 1
    
    content = '\n'.join(result_lines)
    
    # 后处理：为备注部分添加字体大小设置
    # 匹配备注标题和后续的词汇条目，用span包裹并设置字体大小
    def add_font_size_to_notes(match):
        note_title = match.group(1)  # <p>备注</p>
        note_content = match.group(2)  # 后续的词汇条目内容
        
        # 在备注标题后添加一个span包裹所有内容，设置字体大小
        return f'{note_title}\n<span style="font-size:0.8em;">{note_content}</span>'
    
    # 匹配：<p>备注</p> 后面跟着的词汇条目（直到下一个段落或文件结束）
    # 使用非贪婪匹配，匹配到下一个空行或下一个段落开始
    # 更新匹配模式以支持新的样式（包含font-size:0.8em）
    content = re.sub(
        r'(<p style="[^"]*font-size:0\.8em[^"]*">备注</p>)\n((?:- .*?<br/>\n?)+)',
        add_font_size_to_notes,
        content,
        flags=re.DOTALL
    )
    
    # 后处理：更新所有备注标题，添加font-size:0.8em
    # 匹配旧的备注标题格式，更新为包含font-size的格式
    content = re.sub(
        r'(<p style="font-weight:bold; margin-bottom:8px; color:#666;">备注</p>)',
        r'<p style="font-weight:bold; margin-bottom:8px; color:#666; font-size:0.8em;">备注</p>',
        content
    )
    
    # 后处理：移除备注标题前的空行（<br/>标签）
    # 匹配：<br/><br/>后紧跟备注标题，移除一个<br/>（在同一行）
    content = re.sub(
        r'(<br/>)<br/>\n(<p style="[^"]*font-size:0\.8em[^"]*">备注</p>)',
        r'\1\n\2',
        content
    )
    # 匹配：段落结束（以句号、问号、感叹号等结尾，后面有<br/><br/>）后紧跟备注标题，移除一个<br/>
    content = re.sub(
        r'([.!?])<br/><br/>\n(<p style="[^"]*font-size:0\.8em[^"]*">备注</p>)',
        r'\1<br/>\n\2',
        content
    )
    # 匹配：</span><br/>后紧跟备注标题，移除<br/>
    content = re.sub(
        r'(</span>)<br/>\n(<p style="[^"]*font-size:0\.8em[^"]*">备注</p>)',
        r'\1\n\2',
        content
    )
    
    # 后处理：在备注段落（</span>）和后面的英文原文段落之间添加空行（使用<br/>标签）
    # 匹配：</span>后面紧跟英文段落（以大写字母开头）
    content = re.sub(
        r'(</span>)\n([A-Z])',
        r'\1<br/>\n\2',
        content
    )
    
    # 后处理：将所有连续的空行（两个或更多换行符）替换为<br/>标签
    # 匹配：两个或更多连续的换行符（不包括已经处理过的）
    content = re.sub(
        r'\n{2,}',
        lambda m: '<br/>\n' if len(m.group(0)) > 1 else m.group(0),
        content
    )
    
    # 后处理：将所有<br>标签替换为<br/>
    content = re.sub(r'<br>', r'<br/>', content)
    
    # 后处理：确保图片引用的上一行和当前行末尾都有<br/>标签
    def fix_image_br_tags(text):
        """确保图片引用的上一行和当前行末尾都有<br/>标签"""
        lines = text.split('\n')
        result_lines = []
        
        for i, line in enumerate(lines):
            # 检查是否是图片引用行（markdown格式或HTML格式）
            is_image_line = bool(re.search(r'!\[[^\]]*\]\([^\)]+\)', line) or re.search(r'<img[^>]*>', line))
            
            if is_image_line:
                # 检查上一行是否有<br/>标签
                if i > 0:
                    prev_line = result_lines[-1] if result_lines else ''
                    # 如果上一行存在且不以<br/>结尾，则添加
                    if prev_line and not prev_line.rstrip().endswith('<br/>'):
                        # 移除上一行末尾的换行符（如果有），然后添加<br/>
                        result_lines[-1] = prev_line.rstrip() + '<br/>'
                
                # 检查当前行末尾是否有<br/>标签
                if not line.rstrip().endswith('<br/>'):
                    # 移除行尾空白，添加<br/>
                    line = line.rstrip() + '<br/>'
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    # 应用图片<br/>标签修复
    content = fix_image_br_tags(content)
    
    # 后处理：在markdown格式的图片后的<br/>标签后添加<p>标签（缩小空行间距）
    # 使用逐行处理的方式，确保所有图片都能被正确处理
    def fix_all_images(text):
        """处理所有markdown格式的图片，确保每个图片后都有正确的<p>标签
        
        规则：
        1. 如果图片前一行是</span>或</span><br/>，在图片前添加空行，帮助Markdown转换器正确识别图片
        2. 确保每个图片后都有<p style="margin:0; padding:0; line-height:0;"></p>标签
        """
        lines = text.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 检查是否是markdown格式的图片行
            img_match = re.match(r'^(!\[[^\]]*\]\([^\)]+\))(<br/>)?$', line.strip())
            
            if img_match:
                img_markdown = img_match.group(1)
                br_tag = img_match.group(2) if img_match.group(2) else '<br/>'
                
                # 规则：如果上一行是</span>或包含</span>，在图片前添加空行，帮助转换器识别图片
                # 这样可以确保第二、第三及后续图片都能被正确转换
                # 注意：由于空行处理在fix_all_images之前，我们需要添加真正的空行（\n），
                # 这样在后续处理中会被转换为<br/>，形成</span><br/>\n<br/>的格式，帮助转换器识别
                if result_lines:
                    prev_line = result_lines[-1].strip()
                    # 检查上一行是否是</span>或</span><br/>（可能有空格）
                    if prev_line == '</span>' or re.match(r'^</span>(<br/>)?\s*$', prev_line):
                        # 如果上一行不是空行，且上一行不是已经有两个<br/>，才添加空行
                        if prev_line and not prev_line.endswith('<br/><br/>'):
                            result_lines.append('')
                
                # 检查下一行是否已经有<p>标签
                has_p_tag = False
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if re.match(r'^<p[^>]*style="margin:0[^"]*"></p>$', next_line):
                        has_p_tag = True
                
                # 添加图片行
                result_lines.append(img_markdown + br_tag)
                
                # 如果没有<p>标签，添加一个
                if not has_p_tag:
                    result_lines.append('<p style="margin:0; padding:0; line-height:0;"></p>')
                
                i += 1
            else:
                # 非图片行，直接添加
                result_lines.append(line)
                i += 1
        
        return '\n'.join(result_lines)
    
    # 先清理可能已经存在的错误格式的<p>标签
    content = re.sub(
        r'(!\[[^\]]*\]\([^\)]+\))<p[^>]*></p>(<br/>)',
        r'\1\2',
        content
    )
    
    # 处理所有图片
    content = fix_all_images(content)
    
    # 后处理：在HTML的<img>标签后添加<p>标签，确保第一个段落的空格正常显示
    # 匹配：<img>标签（包括data:image格式）后紧跟段落内容
    # 解决方案：在<img>标签后添加一个空的<p>标签，并确保段落格式正确
    def fix_img_tag(match):
        img_tag = match.group(0)  # 完整的<img>标签
        # 在<img>标签后添加一个空的<p>标签，确保段落空格正常显示
        # 如果后面已经有<p></p>，则不重复添加
        return img_tag + '<p></p>'
    
    # 匹配<img>标签（包括自闭合标签和带data:image的标签）
    # 先检查是否已经有<p></p>，避免重复添加
    content = re.sub(
        r'<img[^>]*>(?!<p></p>)',
        fix_img_tag,
        content
    )
    
    # 确保<img>标签后的第一个段落有正确的格式
    # 匹配：<img>标签后紧跟段落（以大写字母开头），确保段落被<p>标签包裹
    # 如果段落还没有被<p>标签包裹，则添加
    def wrap_first_paragraph(match):
        img_and_p = match.group(1)  # <img>标签和<p></p>
        paragraph = match.group(2)  # 段落内容
        
        # 检查段落是否已经被<p>标签包裹
        if paragraph.strip().startswith('<p>') and paragraph.strip().endswith('</p>'):
            return match.group(0)  # 已经包裹，不需要修改
        else:
            # 确保段落被<p>标签包裹
            return f'{img_and_p}<p>{paragraph}</p>'
    
    content = re.sub(
        r'(<img[^>]*><p></p>)\s*([A-Z][^<]*(?:<span[^>]*>[^<]*</span>[^<]*)*[.!?][^<]*)',
        wrap_first_paragraph,
        content,
        flags=re.DOTALL
    )
    
    # 在原文段落中高亮所有词汇
    # 先提取所有词汇（从所有词汇条目中，不仅仅是div中的）
    all_words = []
    
    # 从已处理的内容中提取词汇（匹配格式：- <strong><em>word</em></strong> 或 - **word**）
    vocab_pattern1 = r'- <strong><em>([^<]+)</em></strong>'
    vocab_pattern2 = r'- \*\*([^*]+)\*\*'
    vocab_pattern3 = r'- <strong>([^<]+)</strong>'
    
    matches1 = re.findall(vocab_pattern1, content)
    matches2 = re.findall(vocab_pattern2, content)
    matches3 = re.findall(vocab_pattern3, content)
    all_words = matches1 + matches2 + matches3
    
    # 过滤掉句子成分解析中引用的原英文句子（这些是长句子，不是单词）
    # 真正的词汇通常不超过50个字符，且不包含句号、问号、感叹号
    filtered_words = []
    for word in all_words:
        # 移除HTML标签和空格
        clean_word = re.sub(r'<[^>]+>', '', word).strip()
        # 如果包含句号、问号、感叹号，说明是句子引用，跳过
        if '.' in clean_word or '?' in clean_word or '!' in clean_word:
            continue
        # 如果长度超过50个字符，可能是句子引用，跳过
        if len(clean_word) > 50:
            continue
        # 如果包含"句"字，说明是句子引用标记，跳过
        if '句' in clean_word:
            continue
        filtered_words.append(word)
    
    all_words = filtered_words
    
    # 去重并排序（长的先匹配，避免部分匹配问题）
    all_words = sorted(set(all_words), key=len, reverse=True)
    
    # 在原文段落中高亮词汇（排除备注部分和HTML标签内的内容）
    def highlight_in_paragraphs(text):
        """在所有英文段落中高亮词汇，排除备注部分"""
        # 先找到所有需要高亮的区域（英文段落）
        # 排除备注部分、图片、HTML标签等
        
        # 使用更智能的方法：识别英文段落（即使被HTML标签包裹）
        # 匹配英文段落：以大写字母开头，包含英文单词和标点，可能被HTML标签包裹
        
        # 先处理整个文本，找到所有英文段落
        # 英文段落特征：
        # 1. 包含英文单词（至少3个字母）
        # 2. 以大写字母开头（在HTML标签之后）
        # 3. 不是备注部分、不是图片、不是列表项
        
        lines = text.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # 跳过备注部分（包括备注标题和词汇条目）
            if (stripped.startswith('<p style="') and '备注</p>' in stripped) or \
               (stripped.startswith('**句子成分解析**')) or \
               (stripped.startswith('- <strong><em>') or stripped.startswith('- <strong>') or 
                (stripped.startswith('- ') and ('：' in stripped or ':' in stripped or '/' in stripped or '"' in stripped))) or \
               (stripped.startswith('<span style="font-size:0.8em;">')) or \
               (stripped.startswith('</span>') and i > 0 and '备注' in lines[i-1]) or \
               stripped.startswith('![') or \
               stripped.startswith('<img'):
                result_lines.append(line)
                i += 1
                continue
            
            # 跳过句子成分解析中引用的原英文句子（这些是长句子，不是单词）
            # 检查是否是句子成分解析中的原英文引用（以- <strong><em>开头，且包含句号、问号或感叹号）
            if stripped.startswith('- <strong><em>') and ('.' in stripped or '?' in stripped or '!' in stripped):
                # 这是句子成分解析中的原英文引用，不应该被高亮
                result_lines.append(line)
                i += 1
                continue
            
            # 检查是否是英文段落
            # 移除HTML标签后检查
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_stripped = clean_line.strip()
            
            # 检查是否是英文段落：
            # 1. 以大写字母开头
            # 2. 包含至少一个英文单词（3个或更多字母）
            # 3. 不是空行
            # 4. 不是列表项（不以-开头）
            is_english_paragraph = False
            if clean_stripped and \
               clean_stripped[0].isupper() and \
               not clean_stripped.startswith('-') and \
               re.search(r'\b[A-Za-z]{3,}\b', clean_stripped) and \
               not any(tag in stripped for tag in ['<p style="', '<span style="font-size:0.8em']):
                is_english_paragraph = True
            
            if is_english_paragraph:
                # 这是英文段落，需要高亮其中的词汇
                # 但需要避免在已有的高亮标签内再次高亮
                highlighted_line = line
                for word in all_words:
                    highlighted_line = highlight_word_in_text(highlighted_line, word)
                result_lines.append(highlighted_line)
            else:
                # 其他行直接添加
                result_lines.append(line)
            
            i += 1
        
        return '\n'.join(result_lines)
    
    content = highlight_in_paragraphs(content)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已处理文件: {file_path}")
    print(f"共处理 {len(set(all_words))} 个词汇")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python 标注风格视觉优化.py <文件路径>")
        print("示例: python 标注风格视觉优化.py output/TheEconomist-2025-11-08/translate_sections/004_xxx_Chinese.md")
        print("支持的文件格式: .md 和 .html")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)
    
    # 检查文件扩展名
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in ['.md', '.html']:
        print(f"警告: 文件扩展名 {file_ext} 可能不被支持，将继续处理...")
    
    process_file(file_path)
    print("处理完成！")


if __name__ == '__main__':
    main()

