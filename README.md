# 📈 GitHub Trending Reporter

自动获取 GitHub Trending 数据，通过 LLM 进行智能分析，并将结果持久化到另一个仓库。

## ✨ 功能特点

- 🔍 **自动爬取** - 每日自动获取 GitHub Trending 热门项目
- 🤖 **AI 分析** - 使用 LLM 对项目进行深度分析和趋势洞察
- 📊 **多维度分析** - 支持全面分析、简要分析、技术分析三种模式
- 🌐 **语言筛选** - 支持按编程语言筛选热门项目
- 💾 **数据持久化** - 自动推送到独立仓库，保留历史数据
- ⏰ **定时运行** - 通过 GitHub Actions 实现自动化

## 🏗️ 项目结构

```
github-trending-reporter/
├── .github/
│   └── workflows/
│       └── daily_report.yml    # GitHub Actions 工作流
├── config.py                   # 配置文件
├── trending_scraper.py         # GitHub Trending 爬虫模块
├── llm_analyzer.py             # LLM 分析模块
├── data_pusher.py              # 数据推送模块
├── main.py                     # 主程序入口
├── requirements.txt            # 依赖文件
├── .env.example                # 环境变量示例
└── README.md
```

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/github-trending-reporter.git
cd github-trending-reporter
```

### 2. 安装依赖

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

### 4. 创建数据仓库

在 GitHub 上创建一个名为 `github-trending-reporter-data` 的仓库，用于存储生成的报告和数据。

### 5. 运行

```bash
# 基本运行
python main.py

# 只保存到本地，不推送
python main.py --local --no-push

# 筛选 Python 项目
python main.py -l python

# 使用简要分析模式
python main.py -a brief
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `LLM_API_KEY` | LLM API 密钥 | `e64665470c414f41...` |
| `LLM_BASE_URL` | LLM API 地址 | `https://open.bigmodel.cn/api/paas/v4/` |
| `LLM_MODEL` | 模型名称 | `glm-4.5-flash` |
| `GITHUB_API_TOKEN` | GitHub API Token（避免限流） | `github_pat_xxx` |
| `GITHUB_TOKEN` | GitHub Personal Access Token（推送数据） | `ghp_xxx` |
| `DATA_REPO_OWNER` | 数据仓库所有者 | `your-username` |
| `DATA_REPO_NAME` | 数据仓库名称 | `github-trending-reporter-data` |

### 支持的 LLM 服务

| 服务商 | Base URL | 模型示例 |
|--------|----------|----------|
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4/` | `glm-4.5-flash`, `glm-4-plus` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini`, `gpt-4o` |
| 其他兼容服务 | 自定义 URL | - |

### GitHub Actions Secrets

在仓库的 Settings -> Secrets and variables -> Actions 中添加以下 secrets：

- `LLM_API_KEY` - LLM API 密钥
- `LLM_BASE_URL` - LLM API 地址（可选，默认智谱）
- `LLM_MODEL` - 模型名称（可选，默认 glm-4.5-flash）
- `GITHUB_API_TOKEN` - GitHub API Token（避免爬取限流，推荐）
- `DATA_REPO_TOKEN` - 用于推送数据的 GitHub Token（需要 repo 权限）

## 📖 命令行参数

```
usage: main.py [-h] [-l LANGUAGE] [-s {daily,weekly,monthly}] 
               [-a {comprehensive,brief,technical}] [--no-push] [--local] [--date DATE]

参数说明:
  -l, --language    按编程语言筛选 (如: python, javascript)
  -s, --since       时间范围: daily, weekly, monthly (默认: daily)
  -a, --analysis    分析类型: comprehensive, brief, technical (默认: comprehensive)
  --no-push         不推送到 GitHub 仓库
  --local           保存到本地文件
  --date            指定日期 (格式: YYYY-MM-DD)
```

## 📊 输出格式

### Markdown 报告

生成的报告包含：
- 📋 热门项目列表（项目名、语言、Star 数、描述等）
- 📊 趋势概览
- 🌟 重点项目推荐
- 🔍 技术洞察
- 💡 学习建议

### JSON 数据

原始数据以 JSON 格式保存，包含每个项目的详细信息：

```json
{
  "date": "2026-01-12",
  "generated_at": "2026-01-12T00:00:00Z",
  "total_repos": 25,
  "repositories": [
    {
      "full_name": "owner/repo",
      "language": "Python",
      "stars": 10000,
      "stars_today": 500,
      "forks": 1000,
      "description": "...",
      "url": "https://github.com/owner/repo"
    }
  ]
}
```

## 🔄 GitHub Actions 工作流

工作流配置说明：

- **定时运行**: 每天 UTC 00:00（北京时间 08:00）自动运行
- **手动触发**: 支持通过 workflow_dispatch 手动触发
- **多语言报告**: 自动生成 Python、JavaScript、TypeScript、Go、Rust 等语言的专项报告

## 🛠️ 开发

### 本地测试

```bash
# 测试爬虫模块
python trending_scraper.py

# 测试完整流程（不推送）
python main.py --local --no-push
```

### 项目扩展

- 添加更多 LLM 分析模式
- 支持更多数据源（如 GitLab、Gitee）
- 添加邮件/Webhook 通知
- 构建数据可视化仪表板

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

Made with ❤️ by GitHub Trending Reporter
