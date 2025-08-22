#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证经济学人下载脚本的主要功能
"""

import datetime
from download_economist_pdf import get_latest_economist_date, format_date_for_url

def test_date_calculation():
    """测试日期计算功能"""
    print("=== 测试日期计算功能 ===")
    
    # 获取最新日期
    latest_date = get_latest_economist_date()
    date_str = format_date_for_url(latest_date)
    
    print(f"今天是: {datetime.date.today().strftime('%Y年%m月%d日')}")
    print(f"最新经济学人发布日期: {latest_date.strftime('%Y年%m月%d日')}")
    print(f"格式化后的日期字符串: {date_str}")
    
    # 验证是否为周六
    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    print(f"发布日期是: {weekday_names[latest_date.weekday()]}")
    
    # 验证日期格式
    expected_format = latest_date.strftime("%Y.%m.%d")
    print(f"期望格式: {expected_format}")
    print(f"实际格式: {date_str}")
    
    if date_str == expected_format:
        print("✅ 日期格式正确")
    else:
        print("❌ 日期格式错误")
    
    print()

def test_url_generation():
    """测试URL生成功能"""
    print("=== 测试URL生成功能 ===")
    
    # 使用示例日期
    test_date = datetime.date(2025, 8, 16)
    date_str = format_date_for_url(test_date)
    
    base_url = "https://raw.githubusercontent.com/hehonghui/awesome-english-ebooks/master/01_economist"
    folder_name = f"te_{date_str.replace('.', '.')}"
    filename = f"TheEconomist.{date_str.replace('.', '.')}.pdf"
    
    url = f"{base_url}/{folder_name}/{filename}"
    
    print(f"测试日期: {test_date.strftime('%Y年%m月%d日')}")
    print(f"格式化日期: {date_str}")
    print(f"文件夹名: {folder_name}")
    print(f"文件名: {filename}")
    print(f"完整URL: {url}")
    
    # 验证URL格式
    expected_url = "https://raw.githubusercontent.com/hehonghui/awesome-english-ebooks/master/01_economist/te_2025.08.16/TheEconomist.2025.08.16.pdf"
    
    if url == expected_url:
        print("✅ URL生成正确")
    else:
        print("❌ URL生成错误")
        print(f"期望: {expected_url}")
    
    print()

def main():
    """主测试函数"""
    print("开始测试经济学人下载脚本...\n")
    
    try:
        test_date_calculation()
        test_url_generation()
        
        print("=== 测试完成 ===")
        print("如果所有测试都通过，说明脚本功能正常！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
