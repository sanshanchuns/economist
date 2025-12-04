# API 配置说明

## 当前配置

脚本已配置使用以下 API key：
- API Key: `key_44f382602be16ab92c4cdae476cf9d42ac9e2f086085ee77c95d08f44b33a708`

## 问题说明

Cursor API key 可能不是标准的 OpenAI API key，无法直接用于 OpenAI API endpoint。

## 解决方案

### 方案1：使用 OpenAI API（推荐）

如果您有 OpenAI API key，可以：

1. 修改脚本中的配置：
```python
CURSOR_API_KEY = "your-openai-api-key-here"
CURSOR_API_BASE = "https://api.openai.com/v1"
```

2. 或者设置环境变量：
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 方案2：使用 Cursor 的实际 API

如果 Cursor 有独立的 API endpoint，需要：
1. 查找 Cursor API 的正确 endpoint URL
2. 修改脚本中的 `CURSOR_API_BASE` 配置

### 方案3：使用其他 AI API

脚本支持任何 OpenAI 兼容的 API，例如：
- Anthropic Claude API
- 其他 OpenAI 兼容的服务

## 当前脚本行为

脚本会自动尝试多个 endpoint：
1. 用户指定的 endpoint
2. `https://api.openai.com/v1` (OpenAI 标准)
3. `https://api.cursor.sh/v1` (Cursor 可能的 endpoint)

如果所有尝试都失败，脚本会回退到模板模式，生成需要手动填写的注释模板。

## 测试 API

可以运行以下命令测试 API 是否工作：
```bash
python3 translate_articles_with_annotations.py
```

如果看到 `[DEBUG] 成功使用 endpoint:` 消息，说明 API 配置正确。

