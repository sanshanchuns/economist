# API 使用说明

## 测试结果

根据测试，Cursor API key (`key_44f382602be16ab92c4cdae476cf9d42ac9e2f086085ee77c95d08f44b33a708`) 是有效的，可以成功调用：

- ✅ `/v0/me` - 获取 API Key 信息
- ✅ `/v0/models` - 列出可用模型

可用模型包括：
- `claude-4.5-opus-high-thinking`
- `claude-4.5-sonnet-thinking`
- `gpt-5.1-codex`
- `gpt-5.1-codex-high`
- `gemini-3-pro`

## 问题说明

**Cursor Cloud Agent API 主要用于管理代码仓库上的 Cloud Agents，不支持直接文本生成。**

根据 [Cursor API 文档](https://cursor.com/cn/docs/cloud-agent/api/endpoints)：
- Cloud Agent API 用于启动、停止、查询代码仓库上的 Cloud Agents
- 不支持文本生成/聊天完成功能
- Cursor API key 不能直接用于 OpenAI API

## 解决方案

### 方案1：使用 OpenAI API（推荐）

1. **获取 OpenAI API key**：
   - 访问 https://platform.openai.com/api-keys
   - 创建新的 API key

2. **设置环境变量**：
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

3. **运行脚本**：
   ```bash
   python3 translate_articles_with_annotations.py
   ```

### 方案2：使用模板模式

如果无法使用 API，脚本会自动回退到模板模式：
- 生成带注释的模板文件
- 手动填写音标、中文释义和用法说明

### 方案3：使用 Cursor Cloud Agent（不推荐）

虽然可以使用 Cursor Cloud Agent API 创建 Agent 来处理任务，但这需要：
- 将文章文件提交到代码仓库
- 创建 Cloud Agent
- 等待 Agent 处理完成
- 从代码仓库获取结果

这个过程比较复杂，不适合批量翻译任务。

## 当前脚本行为

脚本会：
1. 首先尝试使用 OpenAI API（如果设置了 `OPENAI_API_KEY`）
2. 如果失败，尝试使用配置的 API key
3. 如果所有尝试都失败，回退到模板模式

## 测试 API

运行测试脚本检查 API 配置：
```bash
python3 test_cursor_api.py
```

## 建议

**推荐使用 OpenAI API**，因为：
- 直接支持文本生成
- API 稳定可靠
- 适合批量处理任务
- 成本相对较低

