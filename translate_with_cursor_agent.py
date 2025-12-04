#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Cursor Cloud Agent API 完成翻译任务

根据 https://cursor.com/cn/docs/cloud-agent/api/endpoints
使用 Cloud Agent 来处理翻译工作
"""

import os
import requests
import base64
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import sys

CURSOR_API_KEY = "key_44f382602be16ab92c4cdae476cf9d42ac9e2f086085ee77c95d08f44b33a708"
CURSOR_API_BASE = "https://api.cursor.com/v0"


def get_auth_headers():
    """获取认证头"""
    auth_header = base64.b64encode(f"{CURSOR_API_KEY}:".encode()).decode()
    return {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/json'
    }


def list_repositories():
    """列出可用的 GitHub 仓库"""
    headers = get_auth_headers()
    try:
        response = requests.get(
            f"{CURSOR_API_BASE}/repositories",
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get('repositories', [])
        else:
            print(f"[ERROR] 获取仓库列表失败: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"[ERROR] 获取仓库列表异常: {e}")
        return []


def list_models():
    """列出可用的模型"""
    headers = get_auth_headers()
    try:
        response = requests.get(
            f"{CURSOR_API_BASE}/models",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('models', [])
        else:
            print(f"[ERROR] 获取模型列表失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"[ERROR] 获取模型列表异常: {e}")
        return []


def launch_agent(repository: str, prompt: str, model: Optional[str] = None, branch_name: Optional[str] = None):
    """
    启动一个 Cloud Agent
    
    根据文档：https://cursor.com/cn/docs/cloud-agent/api/endpoints#launch-an-agent
    """
    headers = get_auth_headers()
    
    payload = {
        "source": {
            "repository": repository,
            "ref": "main"  # 或 "master"，根据仓库默认分支
        },
        "prompt": {
            "text": prompt
        },
        "target": {
            "autoCreatePr": False,  # 不自动创建 PR
            "openAsCursorGithubApp": False,
            "skipReviewerRequest": False
        }
    }
    
    if model:
        payload["model"] = model
    
    if branch_name:
        payload["target"]["branchName"] = branch_name
    
    try:
        response = requests.post(
            f"{CURSOR_API_BASE}/agents",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            print(f"[ERROR] 启动 Agent 失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] 启动 Agent 异常: {e}")
        return None


def get_agent_status(agent_id: str):
    """获取 Agent 状态"""
    headers = get_auth_headers()
    try:
        response = requests.get(
            f"{CURSOR_API_BASE}/agents/{agent_id}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] 获取 Agent 状态失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] 获取 Agent 状态异常: {e}")
        return None


def get_agent_conversation(agent_id: str):
    """获取 Agent 会话历史"""
    headers = get_auth_headers()
    try:
        response = requests.get(
            f"{CURSOR_API_BASE}/agents/{agent_id}/conversation",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] 获取 Agent 会话失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] 获取 Agent 会话异常: {e}")
        return None


def send_followup(agent_id: str, prompt_text: str):
    """发送后续指令给 Agent"""
    headers = get_auth_headers()
    payload = {
        "prompt": {
            "text": prompt_text
        }
    }
    
    try:
        response = requests.post(
            f"{CURSOR_API_BASE}/agents/{agent_id}/followup",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] 发送后续指令失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] 发送后续指令异常: {e}")
        return None


def wait_for_agent_completion(agent_id: str, max_wait_time: int = 3600, check_interval: int = 10):
    """
    等待 Agent 完成
    
    Args:
        agent_id: Agent ID
        max_wait_time: 最大等待时间（秒）
        check_interval: 检查间隔（秒）
    """
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        status = get_agent_status(agent_id)
        if not status:
            print("[WARN] 无法获取 Agent 状态")
            time.sleep(check_interval)
            continue
        
        agent_status = status.get('status', 'UNKNOWN')
        print(f"[INFO] Agent 状态: {agent_status}")
        
        if agent_status == 'FINISHED':
            return True, status
        elif agent_status == 'FAILED' or agent_status == 'STOPPED':
            return False, status
        
        time.sleep(check_interval)
    
    return False, None


def create_translation_prompt(article_path: Path, article_content: str) -> str:
    """创建翻译任务的 prompt"""
    prompt = f"""请按照标注风格翻译以下文章，要求：

1. 保留英文原文，不进行翻译
2. 识别超纲词汇（超出2000词汇量的单词）
3. 为每个超纲词汇添加注释，格式：
   - **词汇**：/[国际音标]/ "中文释义"；文中用来表达xxx意思；补充说明（如有）

文章标题：{article_path.stem}
文章内容：
{article_content[:2000]}  # 限制长度

请创建一个新的 Markdown 文件，文件名：{article_path.stem}_Annotated.md
文件应包含：
- 保留原文的标题、图片等格式
- 每个段落下方添加该段落中的超纲词汇注释
- 使用 Markdown 格式，词汇使用 **词汇** 标记

完成后，请告诉我文件已创建。"""
    
    return prompt


def translate_with_agent(article_path: Path, repository: str, model: Optional[str] = None):
    """使用 Cloud Agent 翻译单篇文章"""
    print(f"\n[INFO] 开始翻译: {article_path.name}")
    
    # 读取文章内容
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] 读取文章失败: {e}")
        return None
    
    # 创建翻译 prompt
    prompt = create_translation_prompt(article_path, content)
    
    # 生成分支名
    branch_name = f"cursor/translate-{article_path.stem.lower().replace('_', '-')}"
    
    # 启动 Agent
    print(f"[INFO] 启动 Cloud Agent...")
    agent_result = launch_agent(
        repository=repository,
        prompt=prompt,
        model=model,
        branch_name=branch_name
    )
    
    if not agent_result:
        print("[ERROR] 启动 Agent 失败")
        return None
    
    agent_id = agent_result.get('id')
    print(f"[INFO] Agent ID: {agent_id}")
    print(f"[INFO] Agent URL: https://cursor.com/agents?id={agent_id}")
    
    # 等待 Agent 完成
    print(f"[INFO] 等待 Agent 完成...")
    success, final_status = wait_for_agent_completion(agent_id)
    
    if success:
        print(f"[OK] Agent 已完成")
        
        # 获取会话历史
        conversation = get_agent_conversation(agent_id)
        if conversation:
            messages = conversation.get('messages', [])
            print(f"[INFO] 会话消息数: {len(messages)}")
            
            # 显示最后几条消息
            for msg in messages[-3:]:
                msg_type = msg.get('type', '')
                msg_text = msg.get('text', '')[:200]
                print(f"  [{msg_type}]: {msg_text}...")
        
        return {
            'agent_id': agent_id,
            'status': final_status,
            'branch_name': branch_name,
            'pr_url': final_status.get('target', {}).get('prUrl') if final_status else None
        }
    else:
        print(f"[ERROR] Agent 未成功完成")
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("使用 Cursor Cloud Agent API 进行翻译")
    print("=" * 60)
    
    # 1. 列出可用模型
    print("\n[1] 获取可用模型...")
    models = list_models()
    if models:
        print(f"   可用模型: {', '.join(models)}")
        recommended_model = models[0] if models else None
    else:
        recommended_model = None
    
    # 2. 列出可用仓库
    print("\n[2] 获取可用仓库...")
    repositories = list_repositories()
    
    # 允许手动指定仓库
    selected_repo = os.getenv("CURSOR_REPOSITORY")
    
    if not repositories and not selected_repo:
        print("[WARN] 未找到可用仓库")
        print("[提示] Cloud Agent API 需要 GitHub 仓库才能工作")
        print("[选项1] 设置环境变量指定仓库：")
        print("  export CURSOR_REPOSITORY='https://github.com/your-username/your-repo'")
        print("[选项2] 确保：")
        print("  1. 已连接 GitHub 账户到 Cursor")
        print("  2. 有可访问的代码仓库")
        print("  3. 仓库已授权给 Cursor")
        print("\n[提示] 或者使用 translate_articles_with_annotations.py 直接调用 API")
        return
    
    if not selected_repo:
        if repositories:
            print(f"   找到 {len(repositories)} 个仓库:")
            for idx, repo in enumerate(repositories[:10], start=1):  # 显示前10个
                print(f"   {idx}. {repo.get('repository')}")
            
            # 选择仓库（使用第一个）
            selected_repo = repositories[0].get('repository')
            print(f"\n[INFO] 使用第一个仓库: {selected_repo}")
        else:
            print("[ERROR] 无法获取仓库列表，且未设置 CURSOR_REPOSITORY")
            return
    else:
        print(f"[INFO] 使用指定的仓库: {selected_repo}")
    
    # 4. 查找需要翻译的文章
    base_dir = Path(__file__).resolve().parent
    latest_dir = base_dir / "output" / "TheEconomist-2025-11-29"
    
    if not latest_dir.exists():
        print(f"[ERROR] 未找到输出目录: {latest_dir}")
        return
    
    list_file = latest_dir / "适合英文学习的文章列表.md"
    if not list_file.exists():
        print(f"[ERROR] 未找到文章列表文件")
        return
    
    # 解析文章列表（简化版）
    sections_dir = latest_dir / "sections"
    article_files = list(sections_dir.glob("*.md"))[:3]  # 先测试3篇
    
    if not article_files:
        print("[ERROR] 未找到文章文件")
        return
    
    print(f"\n[3] 找到 {len(article_files)} 篇文章（测试模式，只处理前3篇）")
    
    # 5. 使用 Agent 翻译
    results = []
    for article_file in article_files:
        result = translate_with_agent(
            article_file,
            repository=selected_repo,
            model=recommended_model
        )
        if result:
            results.append(result)
        
        # 添加延迟，避免 API 限流
        if article_file != article_files[-1]:
            print("\n[INFO] 等待 30 秒后处理下一篇...")
            time.sleep(30)
    
    # 6. 总结
    print("\n" + "=" * 60)
    print("翻译任务完成")
    print("=" * 60)
    print(f"成功: {len(results)}/{len(article_files)}")
    
    for result in results:
        print(f"\nAgent ID: {result['agent_id']}")
        print(f"分支: {result['branch_name']}")
        if result.get('pr_url'):
            print(f"PR: {result['pr_url']}")


if __name__ == "__main__":
    main()

