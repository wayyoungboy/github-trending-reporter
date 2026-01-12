# GitHub Trending Reporter

自动获取 GitHub Trending 数据，通过 LLM 进行智能分析，并生成可视化报告网站。

## 在线访问

**网站地址**: https://wayyoungboy.github.io/github-trending-reporter/

## 功能特点

- **自动爬取** - 每日自动获取 GitHub Trending 热门项目
- **AI 分析** - 使用 LLM 对项目进行深度分析和趋势洞察
- **可视化展示** - 使用 Docusaurus 生成美观的报告网站
- **定时运行** - 通过 GitHub Actions 实现全自动化

## 项目结构

```
github-trending-reporter/
├── .github/workflows/
│   └── daily_report.yml     # 自动化工作流
├── src/                     # Docusaurus 前端源码
├── reports/                 # Markdown 报告
├── data/                    # JSON 原始数据
├── scripts/                 # 工具脚本
├── main.py                  # 主程序
├── trending_scraper.py      # 爬虫模块
├── llm_analyzer.py          # LLM 分析模块
├── data_pusher.py           # 数据推送模块
├── config.py                # 配置文件
├── docusaurus.config.js     # Docusaurus 配置
├── package.json             # Node.js 依赖
└── requirements.txt         # Python 依赖
```

## 快速开始

### 本地运行（仅生成报告）

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 生成报告
python main.py --local --no-push
```

### 本地预览网站

```bash
# 安装 Node.js 依赖
npm install

# 启动开发服务器
npm start
```

## 配置

### 环境变量

| 变量名 | 说明 |
|--------|------|
| `LLM_API_KEY` | LLM API 密钥 |
| `LLM_BASE_URL` | LLM API 地址 |
| `LLM_MODEL` | 模型名称 |
| `GITHUB_API_TOKEN` | GitHub API Token（用于爬取详细信息） |
| `GITHUB_TOKEN` | GitHub Token（用于推送数据） |

### GitHub Actions Secrets

在仓库 Settings → Secrets 中配置：
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `GITHUB_API_TOKEN`

## 自动化流程

1. **定时触发** - 每天自动运行
2. **数据采集** - 爬取 GitHub Trending 页面
3. **API 增强** - 通过 GitHub API 获取详细信息
4. **LLM 分析** - AI 深度分析项目
5. **生成报告** - 输出 Markdown 格式报告
6. **部署网站** - 自动构建并部署到 GitHub Pages

## 命令行参数

```bash
python main.py [OPTIONS]

Options:
  -l, --language TEXT    按编程语言筛选 (如 python, javascript)
  -s, --since TEXT       时间范围: daily, weekly, monthly (默认: daily)
  --no-push              不推送到 GitHub 仓库
  --local                保存到本地文件
  --date TEXT            指定日期 (格式: YYYY-MM-DD)
  --no-detailed          跳过项目深度分析
```

## 相关链接

- [GitHub Trending](https://github.com/trending)
- [Docusaurus](https://docusaurus.io/)

---

Built with Python + Docusaurus
