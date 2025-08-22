#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济学人自动化工作流脚本
整合下载PDF和分析分类功能
"""

import os
import sys
import time
import logging
from pathlib import Path
import subprocess
import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workflow.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_script(script_name, description):
    """运行指定的Python脚本"""
    logger.info(f"开始执行: {description}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} 执行成功")
            if result.stdout:
                logger.info(f"输出: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"❌ {description} 执行失败")
            if result.stderr:
                logger.error(f"错误: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 执行 {script_name} 时出错: {e}")
        return False

def check_dependencies():
    """检查必要的依赖是否已安装"""
    logger.info("检查依赖包...")
    
    required_packages = ['requests', 'PyPDF2']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"❌ {package} 未安装")
    
    if missing_packages:
        logger.info("正在安装缺失的依赖包...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True)
            logger.info("✅ 依赖包安装完成")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 依赖包安装失败: {e}")
            return False
    
    return True

def check_pdf_exists():
    """检查是否已有PDF文件"""
    pdf_dir = Path("economist_pdfs")
    if not pdf_dir.exists():
        return False
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    return len(pdf_files) > 0

def get_latest_pdf_info():
    """获取最新PDF文件信息"""
    pdf_dir = Path("economist_pdfs")
    if not pdf_dir.exists():
        return None
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        return None
    
    latest_pdf = max(pdf_files, key=lambda x: x.stat().st_mtime)
    file_size = latest_pdf.stat().st_size / (1024 * 1024)  # MB
    mod_time = datetime.datetime.fromtimestamp(latest_pdf.stat().st_mtime)
    
    return {
        "path": latest_pdf,
        "name": latest_pdf.name,
        "size": file_size,
        "modified": mod_time
    }

def check_analysis_exists(pdf_info):
    """检查是否已经分析过该PDF"""
    if not pdf_info:
        return False
    
    # 从文件名提取日期
    filename = pdf_info["name"]
    import re
    date_match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', filename)
    if not date_match:
        return False
    
    date_str = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    analysis_dir = Path("economist_pdfs") / f"economist_{date_str}"
    
    return analysis_dir.exists() and any(analysis_dir.iterdir())

def display_status():
    """显示当前状态"""
    logger.info("=" * 60)
    logger.info("经济学人自动化工作流状态")
    logger.info("=" * 60)
    
    # 检查PDF状态
    pdf_info = get_latest_pdf_info()
    if pdf_info:
        logger.info(f"📄 最新PDF: {pdf_info['name']}")
        logger.info(f"📏 文件大小: {pdf_info['size']:.2f} MB")
        logger.info(f"🕒 下载时间: {pdf_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 检查分析状态
        if check_analysis_exists(pdf_info):
            logger.info("✅ PDF已分析完成")
        else:
            logger.info("⏳ PDF待分析")
    else:
        logger.info("❌ 未找到PDF文件")
    
    logger.info("=" * 60)

def run_full_workflow():
    """运行完整工作流"""
    logger.info("🚀 开始执行完整工作流")
    
    # 步骤1: 检查依赖
    if not check_dependencies():
        logger.error("依赖检查失败，工作流终止")
        return False
    
    # 步骤2: 下载PDF（如果需要）
    if not check_pdf_exists():
        logger.info("未找到PDF文件，开始下载...")
        if not run_script("download_economist_pdf.py", "PDF下载"):
            logger.error("PDF下载失败，工作流终止")
            return False
    else:
        logger.info("PDF文件已存在，跳过下载步骤")
    
    # 步骤3: 分析PDF（默认使用栏目分析）
    pdf_info = get_latest_pdf_info()
    if pdf_info and not check_analysis_exists(pdf_info):
        logger.info("开始分析PDF（按栏目分类）...")
        if not run_script("economist_sections.py", "PDF栏目分析"):
            logger.error("PDF栏目分析失败，工作流终止")
            return False
    else:
        logger.info("PDF已分析完成，跳过分析步骤")
    
    # 步骤4: 显示最终状态
    display_status()
    
    logger.info("🎉 完整工作流执行完成！")
    return True

def run_analysis_only():
    """仅运行分析步骤"""
    logger.info("🔍 开始执行PDF分析任务")
    
    if not check_dependencies():
        logger.error("依赖检查失败")
        return False
    
    pdf_info = get_latest_pdf_info()
    if not pdf_info:
        logger.error("未找到PDF文件，请先下载")
        return False
    
    if check_analysis_exists(pdf_info):
        logger.info("PDF已分析完成，无需重复分析")
        return True
    
    return run_script("smart_analyzer.py", "PDF智能分析")

def run_section_analysis():
    """运行按栏目分析"""
    logger.info("📰 开始执行PDF栏目分析任务")
    
    if not check_dependencies():
        logger.error("依赖检查失败")
        return False
    
    pdf_info = get_latest_pdf_info()
    if not pdf_info:
        logger.error("未找到PDF文件，请先下载")
        return False
    
    return run_script("economist_sections.py", "PDF栏目分析")

def run_download_only():
    """仅运行下载步骤"""
    logger.info("⬇️ 开始执行PDF下载任务")
    
    if not check_dependencies():
        logger.error("依赖检查失败")
        return False
    
    return run_script("download_economist_pdf.py", "PDF下载")

def show_help():
    """显示帮助信息"""
    help_text = """
经济学人自动化工作流脚本

使用方法:
  python workflow.py [选项]

选项:
  --full, -f          执行完整工作流（下载+分析）
  --download, -d      仅下载PDF
  --analyze, -a       仅分析PDF（按主题分类）
  --sections, -s      按栏目分析PDF（推荐）
  --status, -st       显示当前状态
  --help, -h          显示此帮助信息

示例:
  python workflow.py --full      # 执行完整工作流
  python workflow.py --download  # 仅下载PDF
  python workflow.py --analyze   # 按主题分类分析
  python workflow.py --sections  # 按栏目分析（推荐）
  python workflow.py --status    # 查看状态

默认行为:
  如果不指定选项，将执行完整工作流

注意:
  --sections 选项按照经济学人的实际栏目结构分类，更准确
  --analyze 选项按照文章内容主题分类，适合内容研究
"""
    print(help_text)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="经济学人自动化工作流")
    parser.add_argument('--full', '-f', action='store_true', help='执行完整工作流')
    parser.add_argument('--download', '-d', action='store_true', help='仅下载PDF')
    parser.add_argument('--analyze', '-a', action='store_true', help='仅分析PDF（按主题分类）')
    parser.add_argument('--sections', '-s', action='store_true', help='按栏目分析PDF（推荐）')
    parser.add_argument('--status', '-st', action='store_true', help='显示当前状态')
    
    args = parser.parse_args()
    
    # 如果没有指定参数，显示状态
    if not any([args.full, args.download, args.analyze, args.sections, args.status]):
        args.status = True
    
    try:
        if args.status:
            display_status()
        elif args.download:
            run_download_only()
        elif args.analyze:
            run_analysis_only()
        elif args.sections:
            run_section_analysis()
        elif args.full:
            run_full_workflow()
            
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"工作流执行出错: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
