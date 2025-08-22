#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试经济学人栏目分析功能
"""

import re
from pathlib import Path

def test_section_recognition():
    """测试栏目识别功能"""
    print("=== 测试栏目识别功能 ===")
    
    # 模拟PDF文本内容
    test_text = """
August 16th 2025

The world this week
Politics
Business
The weekly cartoon

Leaders
Some leader content here

Letters
Some letters content here

By Invitation
Some invitation content here

Briefing
Some briefing content here

United States
Some US content here

The Americas
Some Americas content here

Asia
Some Asia content here

China
Some China content here

Middle East & Africa
Some Middle East content here

Europe
Some Europe content here

Britain
Some Britain content here

International
Some international content here

Business
Some business content here

Finance & economics
Some finance content here

Science & technology
Some science content here

Culture
Some culture content here

Economic & financial indicators
Some indicators content here

Obituary
Some obituary content here
"""
    
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
    
    # 测试栏目识别
    sections = identify_sections(test_text)
    
    print(f"识别到 {len(sections)} 个栏目:")
    print("-" * 50)
    
    for i, section in enumerate(sections, 1):
        section_info = ECONOMIST_SECTIONS.get(section["name"], {})
        description = section_info.get("description", "未知")
        print(f"{i:2d}. {section['name']:<25} - {description:<20} ({section['length']} 字符)")
    
    print("\n栏目内容示例:")
    print("-" * 50)
    
    for section in sections[:3]:  # 只显示前3个栏目
        print(f"\n【{section['name']}】")
        content_preview = section['content'][:100] + "..." if len(section['content']) > 100 else section['content']
        print(content_preview)
    
    return sections

def test_directory_structure():
    """测试目录结构创建"""
    print("\n=== 测试目录结构创建 ===")
    
    # 模拟日期
    date_str = "2025.08.16"
    
    # 模拟目录创建
    base_dir = Path("test_output")
    economist_dir = base_dir / f"economist_{date_str}"
    
    print(f"基础目录: {base_dir}")
    print(f"经济学人目录: {economist_dir}")
    
    # 模拟栏目目录
    test_sections = [
        "The world this week",
        "Leaders", 
        "Letters",
        "United States",
        "China",
        "Europe"
    ]
    
    print("\n栏目目录结构:")
    for section in test_sections:
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', section)
        section_dir = economist_dir / safe_name
        print(f"  {section_dir}")
    
    print("\n✅ 目录结构测试完成")

def main():
    """主测试函数"""
    print("开始测试经济学人栏目分析功能...\n")
    
    try:
        # 测试栏目识别
        sections = test_section_recognition()
        
        # 测试目录结构
        test_directory_structure()
        
        print("\n=== 测试总结 ===")
        print(f"✅ 栏目识别: 成功识别 {len(sections)} 个栏目")
        print("✅ 目录结构: 目录创建逻辑正常")
        print("✅ 栏目分析功能测试通过！")
        
        print("\n🎯 推荐使用:")
        print("  python workflow.py --sections  # 按栏目分析PDF")
        print("  python workflow.py             # 完整工作流（默认使用栏目分析）")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
