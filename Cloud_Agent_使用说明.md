# Cursor Cloud Agent API 使用说明

## 概述

Cursor Cloud Agent API 允许您创建和管理在代码仓库上运行的 Cloud Agents 来完成翻译任务。

## 工作原理

1. **创建 Agent**：在指定的 GitHub 仓库上创建一个 Cloud Agent
2. **发送任务**：Agent 接收翻译任务并开始处理
3. **等待完成**：Agent 自动处理任务（可能需要几分钟到几小时）
4. **获取结果**：从代码仓库的分支或 PR 中获取翻译结果

## 前置要求

### 1. GitHub 仓库

Cloud Agent 需要在 GitHub 仓库上运行，因此需要：

- ✅ 一个 GitHub 账户
- ✅ 一个代码仓库（可以是空的，用于存放翻译结果）
- ✅ 仓库已授权给 Cursor

### 2. 设置仓库

有两种方式指定仓库：

**方式1：自动检测**
```bash
# 脚本会自动列出您可访问的仓库
python3 translate_with_cursor_agent.py
```

**方式2：手动指定**
```bash
export CURSOR_REPOSITORY='https://github.com/your-username/your-repo'
python3 translate_with_cursor_agent.py
```

## 使用步骤

### 1. 准备仓库

创建一个 GitHub 仓库（如果还没有）：
```bash
# 在 GitHub 上创建新仓库，或使用现有仓库
```

### 2. 授权 Cursor

确保仓库已授权给 Cursor：
- 访问 Cursor 设置
- 连接 GitHub 账户
- 授权访问仓库

### 3. 运行脚本

```bash
python3 translate_with_cursor_agent.py
```

脚本会：
1. 列出可用模型
2. 列出可用仓库
3. 为每篇文章创建 Cloud Agent
4. 等待 Agent 完成
5. 提供结果链接

## 工作流程

```
文章文件 → Cloud Agent → GitHub 分支 → 翻译结果
```

1. **启动 Agent**：脚本为每篇文章创建一个 Cloud Agent
2. **Agent 处理**：Agent 在代码仓库上创建新分支，处理翻译任务
3. **结果输出**：翻译结果保存在新分支的文件中
4. **查看结果**：可以通过 PR 或直接查看分支获取结果

## 优缺点

### 优点

- ✅ 使用 Cursor 的强大 AI 模型（claude-4.5-opus, gpt-5.1-codex 等）
- ✅ Agent 可以自主规划和处理复杂任务
- ✅ 结果保存在代码仓库中，便于版本管理
- ✅ 可以处理大量文章

### 缺点

- ❌ 需要 GitHub 仓库
- ❌ 处理时间较长（每篇文章可能需要几分钟到几小时）
- ❌ 不适合实时翻译需求
- ❌ 需要等待 Agent 完成，无法立即获取结果

## 替代方案

如果不想使用 Cloud Agent，可以使用：

1. **直接 API 调用**（推荐）：
   ```bash
   # 使用 OpenAI API
   export OPENAI_API_KEY="your-key"
   python3 translate_articles_with_annotations.py
   ```

2. **模板模式**：
   ```bash
   # 生成模板，手动填写
   python3 translate_articles_with_annotations.py
   ```

## 示例

### 基本使用

```bash
# 1. 设置仓库（可选）
export CURSOR_REPOSITORY='https://github.com/your-username/translation-repo'

# 2. 运行脚本
python3 translate_with_cursor_agent.py
```

### 监控 Agent 状态

脚本会自动监控 Agent 状态，您也可以手动查看：

1. 访问 Agent URL：`https://cursor.com/agents?id={agent_id}`
2. 查看 GitHub PR（如果启用了 autoCreatePr）
3. 查看代码仓库的新分支

## 注意事项

1. **API 限流**：脚本会在请求之间添加延迟，避免触发限流
2. **处理时间**：Cloud Agent 处理时间取决于文章长度和复杂度
3. **仓库权限**：确保 Cursor 有权限在仓库上创建分支和提交
4. **成本**：使用 Cloud Agent 可能产生费用（取决于 Cursor 的定价）

## 故障排除

### 问题：未找到可用仓库

**解决方案**：
1. 检查 GitHub 账户是否已连接
2. 在 Cursor 设置中授权仓库访问
3. 手动设置 `CURSOR_REPOSITORY` 环境变量

### 问题：Agent 失败

**解决方案**：
1. 查看 Agent 状态和会话历史
2. 检查仓库权限
3. 确保仓库不是空的（至少有一个文件）

### 问题：处理时间过长

**解决方案**：
1. 这是正常的，Cloud Agent 需要时间处理
2. 可以分批处理文章
3. 考虑使用直接 API 调用方式

