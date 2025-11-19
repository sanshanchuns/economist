#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标注风格视觉优化脚本

功能：
1. 给单词解析部分加上统一的头部"标注"
2. 每个单词加粗（确保格式正确）
3. 音标弱化，使用更淡的灰色
4. 每个单词解析末尾统一加上网页换行符<br>
5. 每个单词在原文段落中加粗、加下划线，字体颜色使用莫兰迪红色（#A24C4A）
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


def process_file(file_path):
    """处理整个文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
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
    
    # 后处理：在markdown格式的图片后的<br/>标签后添加<p>标签（缩小空行间距）
    # 先清理可能已经存在的<p>标签（在图片和<br/>之间的，或在<br/>之后的，包括多个<p>标签）
    content = re.sub(
        r'(!\[[^\]]*\]\([^\)]+\))<p[^>]*></p>(<br/>)',
        r'\1\2',
        content
    )
    # 清理<br/>后面可能已经存在的<p>标签（包括多个连续的<p>标签和换行）
    content = re.sub(
        r'(!\[[^\]]*\]\([^\)]+\))(<br/>)\n?(<p[^>]*></p>\n?)+',
        r'\1\2',
        content
    )
    
    # 匹配：markdown格式的图片 ![](路径)<br/>
    def fix_markdown_img(match):
        img_markdown = match.group(1)  # markdown图片格式
        br_tag = match.group(2)  # <br/>标签
        # 在<br/>标签后先换行，再添加带样式的<p>标签，缩小空行间距
        # 使用margin:0; padding:0; line-height:0; 来缩小空行
        # <p>标签后也要换行，然后才开始正文
        return img_markdown + br_tag + '\n<p style="margin:0; padding:0; line-height:0;"></p>\n'
    
    # 匹配markdown格式的图片：![](路径)<br/>
    # 先检查是否已经有<p>标签，避免重复添加
    content = re.sub(
        r'(!\[[^\]]*\]\([^\)]+\))(<br/>)(?!\n<p[^>]*></p>)',
        fix_markdown_img,
        content
    )
    
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
    # 先提取所有词汇
    all_words = []
    div_matches = re.finditer(div_pattern, content, flags=re.DOTALL)
    for match in div_matches:
        div_content = match.group(2)
        words = extract_vocabulary_words(div_content)
        all_words.extend(words)
    
    # 去重并排序（长的先匹配，避免部分匹配问题）
    all_words = sorted(set(all_words), key=len, reverse=True)
    
    # 在原文段落中高亮词汇（排除div内的内容和HTML标签内的内容）
    def highlight_in_paragraphs(text):
        # 分割文本，分别处理div内和div外的内容
        parts = []
        last_pos = 0
        
        # 找到所有div的位置
        div_matches = list(re.finditer(div_pattern, text, flags=re.DOTALL))
        
        for i, match in enumerate(div_matches):
            # 处理div之前的内容
            before = text[last_pos:match.start()]
            
            # 只处理不在HTML标签内的文本
            # 使用更智能的方法：先标记所有HTML标签，然后只替换标签外的文本
            for word in all_words:
                before = highlight_word_in_text(before, word)
            
            parts.append(before)
            
            # 保留div内容不变
            parts.append(match.group(0))
            last_pos = match.end()
        
        # 处理最后一部分
        if last_pos < len(text):
            after = text[last_pos:]
            for word in all_words:
                after = highlight_word_in_text(after, word)
            parts.append(after)
        
        return ''.join(parts)
    
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

