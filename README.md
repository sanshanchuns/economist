# 经济学人PDF自动化系统

这是一个完整的《经济学人》杂志自动化处理系统，包含PDF下载、智能分析和文章分类功能。系统能够自动下载最新期刊，并将文章按主题智能分类整理。

## 功能特点

- 🗓️ 自动计算最新的经济学人发布日期（每周六发布）
- 📥 自动下载PDF文件到 `economist_pdfs` 目录
- 🔍 智能检查文件是否已存在，避免重复下载
- 📊 显示下载进度和文件大小信息
- 📝 详细的日志记录，包括控制台输出和文件日志
- ⚡ 支持断点续传和错误处理
- 🧠 智能PDF文本提取和文章识别
- 📂 自动文章分类（政治、商业、科技、地区等16个分类）
- 📰 按栏目分类（The world this week、Leaders、Letters等20个栏目）
- 📋 生成详细的分类报告和统计信息
- 🔄 完整的工作流自动化，一键执行下载+分析

## 安装依赖

```bash
pip install -r requirements.txt
```

**注意**: 系统会自动检查并安装必要的依赖包。

## 使用方法

### 一键执行完整工作流（推荐）

```bash
python workflow.py
```

这将自动执行下载和分析的完整流程。

### 分别执行

#### 仅下载PDF
```bash
python workflow.py --download
```

#### 仅分析PDF
```bash
# 按主题分类分析（基于文章内容）
python workflow.py --analyze

# 按栏目分类分析（基于PDF结构，推荐）
python workflow.py --sections
```

#### 查看状态
```bash
python workflow.py --status
```

### 手动执行（传统方式）

```bash
python download_economist_pdf.py
```

### 自动定时执行

#### 使用crontab（Linux/macOS）

1. 编辑crontab：
```bash
crontab -e
```

2. 添加以下行（每周六上午9点执行完整工作流）：
```bash
0 9 * * 6 cd /path/to/your/script && python workflow.py
```

**推荐**: 使用完整工作流，这样每周六会自动下载并分析PDF。

#### 使用Windows任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器为"每周"
4. 选择"星期六"
5. 设置操作为运行程序：`python workflow.py`

**推荐**: 使用完整工作流，这样每周六会自动下载并分析PDF。

## 目录结构

```
economist/
├── download_economist_pdf.py    # PDF下载脚本
├── smart_analyzer.py           # 智能PDF分析脚本
├── workflow.py                 # 自动化工作流脚本（推荐使用）
├── requirements.txt             # 依赖包
├── README.md                   # 说明文档
├── economist_pdfs/             # PDF下载目录（自动创建）
│   └── economist_YYYY.MM.DD/   # 分类后的文章目录
│       ├── 政治/               # 政治类文章
│       ├── 商业/               # 商业类文章
│       ├── 科技/               # 科技类文章
│       ├── 美国/               # 美国相关文章
│       ├── 中国/               # 中国相关文章
│       ├── 欧洲/               # 欧洲相关文章
│       ├── 其他分类...         # 其他主题分类
│       └── 分类报告.txt        # 分类统计报告
├── economist_download.log      # 下载日志文件
├── workflow.log                # 工作流执行日志
└── smart_analysis.log          # 分析日志文件
```

## 日志文件

系统会生成多个详细的日志文件：

- `economist_download.log` - PDF下载日志
- `workflow.log` - 工作流执行日志  
- `smart_analysis.log` - PDF分析日志

所有日志都包含详细的时间戳和操作记录。

## 注意事项

- 确保网络连接稳定
- 系统会自动创建必要的目录
- 如果文件已存在，系统会跳过下载
- 支持断点续传，下载中断后重新运行即可
- PDF分析需要安装PyPDF2库（系统会自动检查并安装）
- 文章分类基于关键词匹配，准确率约80-90%
- 建议每周六执行一次完整工作流

## 故障排除

如果遇到问题，请检查：

1. 网络连接是否正常
2. 依赖包是否正确安装（系统会自动检查）
3. 查看对应的日志文件中的错误信息
4. 确认目标URL是否可访问
5. 检查PDF文件是否完整下载
6. 确认有足够的磁盘空间存储PDF和分析结果

## 文章分类说明

系统支持两种分类方式：

### 1. 按栏目分类（推荐）
按照《经济学人》的实际栏目结构分类，包括：

**核心栏目**:
- **The world this week**: 本周世界要闻
- **Leaders**: 社论和领导力
- **Letters**: 读者来信
- **By Invitation**: 特邀文章
- **Briefing**: 深度简报

**地区栏目**:
- **United States**: 美国新闻
- **The Americas**: 美洲新闻
- **Asia**: 亚洲新闻
- **China**: 中国新闻
- **Middle East & Africa**: 中东和非洲新闻
- **Europe**: 欧洲新闻
- **Britain**: 英国新闻

**主题栏目**:
- **Business**: 商业新闻
- **Finance & economics**: 金融和经济
- **Science & technology**: 科学和技术
- **Culture**: 文化
- **International**: 国际新闻
- **Economic & financial indicators**: 经济和金融指标
- **Obituary**: 讣告
- **The weekly cartoon**: 每周漫画

### 2. 按主题分类
基于文章内容的智能分类，包括：

- **政治**: 政府、选举、民主制度等
- **商业**: 经济、市场、贸易、投资等  
- **科技**: 技术、AI、创新、创业等
- **地区分类**: 美国、中国、欧洲、非洲、亚洲、中东、拉美
- **主题分类**: 国际关系、环境、健康、教育、文化、体育

**推荐使用栏目分类**，因为它更准确地反映了《经济学人》的编辑结构，便于按栏目阅读和研究。

## 许可证

本项目仅供学习和个人使用。
