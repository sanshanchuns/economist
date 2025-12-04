#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动下载《经济学人》PDF脚本
每周六自动执行，下载最新期刊到economist_pdfs目录
支持格式：PDF > EPUB > MOBI（优先级顺序）
如果下载的是 EPUB 或 MOBI，会自动转换为 PDF
"""

import os
import requests
import datetime
from pathlib import Path
import logging
import sys
import subprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('economist_download.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_latest_economist_date():
    """
    获取最新的经济学人发布日期
    经济学人每周六发布新期刊
    """
    today = datetime.date.today()
    
    # 找到最近的周六
    days_since_saturday = (today.weekday() - 5) % 7
    if days_since_saturday == 0:
        # 今天是周六
        latest_saturday = today
    else:
        # 找到最近的周六
        latest_saturday = today - datetime.timedelta(days=days_since_saturday)
    
    return latest_saturday

def format_date_for_url(date_obj):
    """
    将日期格式化为URL中使用的格式 (YYYY.MM.DD)
    """
    return date_obj.strftime("%Y.%m.%d")

def download_file(url, local_file):
    """
    下载文件到本地
    返回: (成功标志, 文件大小)
    """
    try:
        # 发送HTTP请求
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        # 检查文件大小
        total_size = int(response.headers.get('content-length', 0))
        if total_size == 0:
            logger.warning("无法获取文件大小信息")
        
        # 下载文件
        downloaded_size = 0
        with open(local_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        logger.info(f"下载进度: {progress:.1f}%")
        
        logger.info(f"下载完成: {local_file.name}")
        logger.info(f"文件大小: {downloaded_size / (1024*1024):.2f} MB")
        
        return True, downloaded_size
        
    except requests.exceptions.RequestException as e:
        logger.error(f"下载失败: {e}")
        return False, 0
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return False, 0

def convert_to_pdf(source_file, target_pdf):
    """
    将 EPUB 或 MOBI 文件转换为 PDF
    使用 calibre 的 ebook-convert 工具
    """
    try:
        logger.info(f"开始转换: {source_file.name} -> {target_pdf.name}")
        
        # 检查 ebook-convert 是否可用（尝试运行，如果 FileNotFoundError 则说明未安装）
        try:
            subprocess.run(
                ['ebook-convert', '--version'],
                capture_output=True,
                text=True,
                timeout=5,
                check=False  # 不检查返回码，只要命令能运行即可
            )
        except FileNotFoundError:
            logger.error("未找到 ebook-convert 工具")
            logger.error("请安装 Calibre: https://calibre-ebook.com/download")
            logger.error("macOS: brew install calibre")
            logger.error("Linux: sudo apt-get install calibre")
            return False
        
        # 执行转换
        cmd = [
            'ebook-convert',
            str(source_file),
            str(target_pdf),
            '--enable-heuristics',
            '--embed-font-family',
            'Times New Roman'
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            if target_pdf.exists():
                pdf_size = target_pdf.stat().st_size / (1024*1024)
                logger.info(f"转换成功: {target_pdf.name} ({pdf_size:.2f} MB)")
                # 删除原始文件
                source_file.unlink()
                logger.info(f"已删除原始文件: {source_file.name}")
                return True
            else:
                logger.error("转换完成但未找到输出文件")
                return False
        else:
            logger.error(f"转换失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("转换超时（超过5分钟）")
        return False
    except FileNotFoundError:
        logger.error("未找到 ebook-convert 工具")
        logger.error("请安装 Calibre: https://calibre-ebook.com/download")
        return False
    except Exception as e:
        logger.error(f"转换过程出错: {e}")
        return False

def download_economist_file(date_str):
    """
    下载指定日期的经济学人文件
    按优先级尝试：PDF > EPUB > MOBI
    如果下载的是 EPUB 或 MOBI，会自动转换为 PDF
    """
    # 创建下载目录
    download_dir = Path("economist_pdfs")
    download_dir.mkdir(exist_ok=True)
    
    # 格式优先级列表
    formats = ['pdf', 'epub', 'mobi']
    
    # 构建基础URL
    base_url = "https://raw.githubusercontent.com/hehonghui/awesome-english-ebooks/master/01_economist"
    folder_name = f"te_{date_str.replace('.', '.')}"
    
    # 目标PDF文件名
    target_pdf_filename = f"TheEconomist.{date_str.replace('.', '.')}.pdf"
    target_pdf = download_dir / target_pdf_filename
    
    # 按优先级尝试下载
    for fmt in formats:
        filename = f"TheEconomist.{date_str.replace('.', '.')}.{fmt}"
        url = f"{base_url}/{folder_name}/{filename}"
        local_file = download_dir / filename
        
        logger.info(f"尝试下载 {fmt.upper()} 格式: {url}")
        
        # 尝试下载
        success, file_size = download_file(url, local_file)
        
        if success:
            # 如果下载的是 PDF，直接返回
            if fmt == 'pdf':
                logger.info("成功下载 PDF 文件")
                return True
            
            # 如果下载的是 EPUB 或 MOBI，需要转换为 PDF
            logger.info(f"成功下载 {fmt.upper()} 文件，开始转换为 PDF")
            if convert_to_pdf(local_file, target_pdf):
                logger.info("转换完成")
                return True
            else:
                logger.error("转换失败")
                # 保留原始文件以便手动转换
                logger.info(f"原始文件保留在: {local_file}")
                return False
        else:
            logger.warning(f"{fmt.upper()} 格式不可用，尝试下一个格式")
            # 如果文件存在但下载失败，删除不完整的文件
            if local_file.exists():
                local_file.unlink()
    
    # 所有格式都下载失败
    logger.error("所有格式（PDF、EPUB、MOBI）都无法下载")
    return False

def main():
    """
    主函数
    """
    logger.info("开始执行经济学人PDF下载任务")
    
    try:
        # 获取最新日期
        latest_date = get_latest_economist_date()
        date_str = format_date_for_url(latest_date)
        
        logger.info(f"目标下载日期: {latest_date.strftime('%Y年%m月%d日')}")
        logger.info(f"格式化日期: {date_str}")
        
        # 检查文件是否已存在
        download_dir = Path("economist_pdfs")
        filename = f"TheEconomist.{date_str.replace('.', '.')}.pdf"
        local_file = download_dir / filename
        
        if local_file.exists():
            file_size = local_file.stat().st_size / (1024*1024)
            logger.info(f"文件已存在: {filename} ({file_size:.2f} MB)")
            logger.info("跳过下载")
            return
        
        # 下载文件（支持 PDF、EPUB、MOBI）
        success = download_economist_file(date_str)
        
        if success:
            logger.info("下载任务完成")
        else:
            logger.error("下载任务失败")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()