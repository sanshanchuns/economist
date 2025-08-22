#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动下载《经济学人》PDF脚本
每周六自动执行，下载最新期刊到economist_pdfs目录
"""

import os
import requests
import datetime
from pathlib import Path
import logging
import sys

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

def download_economist_pdf(date_str):
    """
    下载指定日期的经济学人PDF
    """
    # 创建下载目录
    download_dir = Path("economist_pdfs")
    download_dir.mkdir(exist_ok=True)
    
    # 构建下载URL
    base_url = "https://raw.githubusercontent.com/hehonghui/awesome-english-ebooks/master/01_economist"
    folder_name = f"te_{date_str.replace('.', '.')}"
    filename = f"TheEconomist.{date_str.replace('.', '.')}.pdf"
    
    url = f"{base_url}/{folder_name}/{filename}"
    
    # 构建本地文件路径
    local_file = download_dir / filename
    
    logger.info(f"开始下载: {url}")
    logger.info(f"保存到: {local_file}")
    
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
        
        logger.info(f"下载完成: {filename}")
        logger.info(f"文件大小: {downloaded_size / (1024*1024):.2f} MB")
        
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"下载失败: {e}")
        return False
    except Exception as e:
        logger.error(f"未知错误: {e}")
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
        
        # 下载PDF
        success = download_economist_pdf(date_str)
        
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