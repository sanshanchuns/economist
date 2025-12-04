# GitHub 账户连接说明

## 当前状态

脚本已配置使用仓库：`https://github.com/sanshanchuns/economist.git`

但需要先连接 GitHub 账户到 Cursor 才能使用 Cloud Agent API。

## 连接步骤

### 方法1：使用错误信息中的链接

运行脚本时，如果出现需要连接 GitHub 的错误，脚本会显示连接链接，例如：

```
[重要] 需要连接 GitHub 账户到 Cursor
[操作] 请访问以下链接完成连接：
       https://cursor.com/api/auth/connect-github?auth_id=...
```

直接访问该链接完成连接。

### 方法2：通过 Cursor 设置

1. 打开 Cursor 编辑器
2. 进入设置（Settings）
3. 找到 "GitHub" 或 "Integrations" 部分
4. 点击 "Connect GitHub" 或 "授权 GitHub"
5. 完成 OAuth 授权流程

### 方法3：直接访问连接页面

访问 Cursor 的 GitHub 连接页面：
- https://cursor.com/settings
- 找到 GitHub 集成部分
- 完成授权

## 验证连接

连接完成后，运行脚本测试：

```bash
python3 translate_with_cursor_agent.py
```

如果连接成功，脚本应该能够：
1. 列出可用仓库（包括 `sanshanchuns/economist`）
2. 成功启动 Cloud Agent

## 仓库要求

确保仓库：
- ✅ 存在且可访问
- ✅ 已授权给 Cursor
- ✅ 有适当的权限（至少可以创建分支）

## 故障排除

### 问题：仍然提示需要连接

**解决方案**：
1. 检查是否已完成授权流程
2. 尝试重新授权
3. 检查仓库是否在授权列表中

### 问题：仓库不在列表中

**解决方案**：
1. 确保仓库是公开的，或者
2. 确保 Cursor 有访问私有仓库的权限
3. 检查 GitHub 账户是否正确连接

## 下一步

连接完成后，可以：

1. **运行翻译脚本**：
   ```bash
   python3 translate_with_cursor_agent.py
   ```

2. **调整处理数量**（可选）：
   ```bash
   export MAX_ARTICLES=5  # 处理5篇文章
   python3 translate_with_cursor_agent.py
   ```

3. **监控 Agent 状态**：
   - 脚本会自动显示 Agent URL
   - 可以在浏览器中查看 Agent 进度
   - 查看 GitHub 仓库的新分支

