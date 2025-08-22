# 经济学人自动化系统 - 快速开始指南

## 🚀 5分钟快速上手

### 第一步：安装依赖
```bash
pip install -r requirements.txt
```

### 第二步：一键执行完整工作流
```bash
python workflow.py
```

就这么简单！系统会自动：
1. 检查并安装必要的依赖包
2. 下载最新的经济学人PDF
3. 智能分析PDF内容
4. 将文章按主题分类整理
5. 生成详细的分类报告

## 📁 查看结果

执行完成后，在 `economist_pdfs` 目录中会看到：

```
economist_pdfs/
├── TheEconomist.2025.01.25.pdf          # 下载的PDF文件
└── economist_2025.01.25/                 # 分类后的文章目录
    ├── 政治/                             # 政治类文章
    │   ├── 001_article.txt
    │   └── 002_article.txt
    ├── 商业/                             # 商业类文章
    │   ├── 001_article.txt
    │   └── 002_article.txt
    ├── 科技/                             # 科技类文章
    │   └── 001_article.txt
    ├── 美国/                             # 美国相关文章
    ├── 中国/                             # 中国相关文章
    ├── 欧洲/                             # 欧洲相关文章
    ├── 其他分类...                       # 其他主题
    └── 分类报告.txt                      # 分类统计报告
```

## 🔧 常用命令

### 查看系统状态
```bash
python workflow.py --status
```

### 仅下载PDF
```bash
python workflow.py --download
```

### 仅分析PDF
```bash
python workflow.py --analyze
```

### 执行完整工作流
```bash
python workflow.py --full
```

## ⏰ 设置自动执行

### Linux/macOS (crontab)
```bash
crontab -e
```

添加以下行（每周六上午9点执行）：
```bash
0 9 * * 6 cd /path/to/economist && python workflow.py
```

### Windows (任务计划程序)
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器为"每周" → "星期六"
4. 设置操作为运行程序：`python workflow.py`

## 📊 文章分类说明

系统会自动将文章分为以下类别：

| 分类 | 关键词示例 | 说明 |
|------|------------|------|
| 政治 | politics, government, election | 政府、选举、民主制度 |
| 商业 | business, economy, market | 经济、市场、贸易 |
| 科技 | technology, AI, innovation | 技术、人工智能、创新 |
| 美国 | America, US, Washington | 美国相关新闻 |
| 中国 | China, Beijing, CCP | 中国相关新闻 |
| 欧洲 | Europe, EU, Brussels | 欧洲相关新闻 |
| 非洲 | Africa, Nigeria, Kenya | 非洲相关新闻 |
| 亚洲 | Asia, Japan, India | 亚洲相关新闻 |
| 中东 | Middle East, Iran, Israel | 中东相关新闻 |
| 拉美 | Latin America, Brazil, Mexico | 拉美相关新闻 |
| 国际关系 | diplomacy, foreign policy | 外交、国际关系 |
| 环境 | environment, climate, green | 环境、气候、可持续发展 |
| 健康 | health, medical, healthcare | 健康、医疗、保健 |
| 教育 | education, university, school | 教育、学术、研究 |
| 文化 | culture, arts, literature | 文化、艺术、文学 |
| 体育 | sports, football, olympics | 体育、运动、竞技 |

## 🐛 常见问题

### Q: 提示"PyPDF2未安装"怎么办？
A: 系统会自动安装，如果失败请手动执行：
```bash
pip install PyPDF2
```

### Q: 下载失败怎么办？
A: 检查网络连接，或稍后重试。系统支持断点续传。

### Q: 分类不准确怎么办？
A: 系统基于关键词匹配，准确率约80-90%。可以手动调整分类。

### Q: 如何查看执行日志？
A: 查看以下日志文件：
- `workflow.log` - 工作流执行日志
- `economist_download.log` - 下载日志
- `smart_analysis.log` - 分析日志

## 📈 性能优化建议

1. **首次运行**: 可能需要较长时间下载PDF
2. **后续运行**: 只分析新PDF，速度很快
3. **存储空间**: 每期PDF约50-100MB，分析结果约10-20MB
4. **网络要求**: 稳定的网络连接，建议使用VPN

## 🎯 高级用法

### 自定义分类关键词
编辑 `smart_analyzer.py` 中的 `CATEGORIES` 字典

### 调整分析参数
修改 `smart_analyzer.py` 中的文本处理逻辑

### 集成到其他系统
调用 `workflow.py` 的函数接口

---

**开始使用**: 运行 `python workflow.py` 即可体验完整的自动化流程！
