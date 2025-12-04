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
# GitHub 仓库地址（SSH 格式转换为 HTTPS）
DEFAULT_REPOSITORY = "https://github.com/sanshanchuns/economist.git"


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
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('error', response.text)
            
            # 检查是否需要连接 GitHub
            if 'connect your GitHub account' in error_msg.lower() or 'connect-github' in error_msg.lower():
                # 尝试提取连接链接
                import re
                connect_url_match = re.search(r'https://cursor\.com/api/auth/connect-github[^\s"]+', error_msg)
                if connect_url_match:
                    connect_url = connect_url_match.group(0)
                    print(f"\n[重要] 需要连接 GitHub 账户到 Cursor")
                    print(f"[操作] 请访问以下链接完成连接：")
                    print(f"       {connect_url}")
                    print(f"\n[提示] 连接完成后，重新运行脚本")
                else:
                    print(f"[ERROR] 启动 Agent 失败: {error_msg}")
                    print(f"[提示] 请访问 Cursor 设置连接 GitHub 账户")
            else:
                print(f"[ERROR] 启动 Agent 失败: {response.status_code} - {error_msg}")
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
    # 限制文章内容长度，避免 prompt 过长
    max_content_length = 5000
    content_preview = article_content[:max_content_length]
    if len(article_content) > max_content_length:
        content_preview += "\n\n[... 文章内容已截断，请处理完整文件 ...]"
    
    prompt = f"""请按照标注风格翻译以下文章。

## 任务要求

1. **保留英文原文**：不要翻译正文，只添加词汇注释
2. **识别超纲词汇**：识别超出2000词汇量的单词（不包括基础词汇如 the, a, is, are, have, do 等）
3. **添加词汇注释**：每个超纲词汇添加注释，格式如下：
   ```
   - **词汇**：/[国际音标]/ "中文释义"；文中用来表达xxx意思；补充说明（如有）
   ```

## 文章信息

- 文件名：{article_path.name}
- 标题：{article_path.stem}

## 文章内容

```
{content_preview}
```

## 输出要求

1. 创建新文件：`output/TheEconomist-2025-11-29/translate_sections/{article_path.stem}_Annotated.md`
2. 保留原文的所有格式（标题、图片、HTML样式等）
3. 在每个英文段落下方添加该段落中的超纲词汇注释
4. 使用 Markdown 格式，词汇使用 `**词汇**` 标记
5. 音标使用 IPA 格式，用 `/[音标]/` 包裹
6. 中文释义用引号包裹

## 注意事项

- 只注释超纲词汇，不要注释基础词汇
- 每个词汇的注释必须包含：音标、中文释义、文中用法说明
- 保持原文格式不变，只在段落下方添加注释

完成后，请提交文件并告诉我已完成。"""
    
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
    
    # 允许手动指定仓库，优先使用环境变量，然后是默认仓库
    selected_repo = os.getenv("CURSOR_REPOSITORY", DEFAULT_REPOSITORY)
    
    # 如果从环境变量或默认值获取，检查是否在可用仓库列表中
    if repositories:
        print(f"   找到 {len(repositories)} 个仓库:")
        for idx, repo in enumerate(repositories[:10], start=1):  # 显示前10个
            repo_url = repo.get('repository')
            print(f"   {idx}. {repo_url}")
            # 如果找到匹配的仓库，使用它
            if repo_url == selected_repo or repo_url.replace('.git', '') == selected_repo.replace('.git', ''):
                selected_repo = repo_url
                print(f"\n[INFO] 使用匹配的仓库: {selected_repo}")
                break
        else:
            # 如果不在列表中，使用默认值
            print(f"\n[INFO] 使用指定的仓库: {selected_repo}")
    else:
        # 如果没有获取到仓库列表，使用默认值
        print(f"[INFO] 使用默认仓库: {selected_repo}")
        print("[WARN] 无法获取仓库列表，使用默认仓库")
        print("[提示] 如果失败，请确保：")
        print("  1. 已连接 GitHub 账户到 Cursor")
        print("  2. 仓库已授权给 Cursor")
        print("  3. 仓库地址正确")
    
    # 4. 查找需要翻译的文章
    base_dir = Path(__file__).resolve().parent
    latest_dir = None
    
    # 尝试找到最新的输出目录
    output_dir = base_dir / "output"
    if output_dir.exists():
        economist_dirs = [d for d in output_dir.iterdir() 
                         if d.is_dir() and d.name.startswith("TheEconomist-")]
        if economist_dirs:
            economist_dirs.sort(key=lambda x: x.name, reverse=True)
            latest_dir = economist_dirs[0]
    
    if not latest_dir or not latest_dir.exists():
        print(f"[ERROR] 未找到输出目录")
        print(f"[提示] 请先运行 split_pdf_to_markdown.py 生成文章")
        return
    
    print(f"[INFO] 使用目录: {latest_dir.name}")
    
    list_file = latest_dir / "适合英文学习的文章列表.md"
    if not list_file.exists():
        print(f"[WARN] 未找到文章列表文件，将处理所有文章")
        sections_dir = latest_dir / "sections"
        article_files = list(sections_dir.glob("*.md"))
    else:
        # 解析文章列表，获取需要翻译的文章
        sections_dir = latest_dir / "sections"
        article_files = list(sections_dir.glob("*.md"))
    
    if not article_files:
        print("[ERROR] 未找到文章文件")
        return
    
    # 限制处理数量（测试模式）
    max_articles = int(os.getenv("MAX_ARTICLES", "3"))
    article_files = article_files[:max_articles]
    
    if not article_files:
        print("[ERROR] 未找到文章文件")
        return
    
    print(f"\n[3] 找到 {len(article_files)} 篇文章（将处理前{len(article_files)}篇）")
    print(f"[提示] 设置 MAX_ARTICLES 环境变量可调整处理数量")
    
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

