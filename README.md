# GitHub Trending Reporter

Automatically fetch GitHub Trending data, perform intelligent analysis using LLM, and generate a visualized report website.

[中文文档](README.zh-CN.md) | [English](README.md)

## Online Access

**Website**: https://wayyoungboy.github.io/github-trending-reporter/

## Features

- **Automatic Scraping** - Automatically fetch GitHub Trending hot projects daily
- **AI Analysis** - Use LLM for deep analysis and trend insights on projects
- **Visual Display** - Generate beautiful report websites using Docusaurus
- **Automated Scheduling** - Fully automated through GitHub Actions

## Project Structure

```
github-trending-reporter/
├── .github/workflows/
│   └── daily_report.yml     # Automated workflow
├── src/                     # Docusaurus frontend source
├── reports/                 # Markdown reports
├── data/                    # JSON raw data
├── scripts/                 # Utility scripts
├── main.py                  # Main program
├── trending_scraper.py      # Scraper module
├── llm_analyzer.py          # LLM analysis module
├── data_pusher.py           # Data push module
├── config.py                # Configuration file
├── docusaurus.config.js     # Docusaurus configuration
├── package.json             # Node.js dependencies
└── requirements.txt         # Python dependencies
```

## Quick Start

### Local Run (Report Generation Only)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and fill in API Key

# Generate report
python main.py --local --no-push
```

### Local Preview Website

```bash
# Install Node.js dependencies
npm install

# Start development server
npm start
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `LLM_API_KEY` | LLM API key |
| `LLM_BASE_URL` | LLM API URL |
| `LLM_MODEL` | Model name |
| `GITHUB_API_TOKEN` | GitHub API Token (for fetching detailed info) |
| `GITHUB_TOKEN` | GitHub Token (for pushing data) |

### GitHub Actions Secrets

Configure in repository Settings → Secrets:
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `GITHUB_API_TOKEN`

## Automation Workflow

1. **Scheduled Trigger** - Runs automatically every day
2. **Data Collection** - Scrape GitHub Trending page
3. **API Enhancement** - Fetch detailed info via GitHub API
4. **LLM Analysis** - AI deep analysis of projects
5. **Report Generation** - Output Markdown format reports
6. **Website Deployment** - Automatically build and deploy to GitHub Pages

## Command Line Options

```bash
python main.py [OPTIONS]

Options:
  -l, --language TEXT    Filter by programming language (e.g., python, javascript)
  -s, --since TEXT       Time range: daily, weekly, monthly (default: daily)
  --no-push              Don't push to GitHub repository
  --local                Save to local files
  --date TEXT            Specify date (format: YYYY-MM-DD)
  --no-detailed          Skip detailed project analysis
```

## Inspiration

This project is inspired by [ai-git-trending](https://github.com/lgy1027/ai-git-trending), an automated bot for analyzing GitHub Trending. During development, we referenced the project's core architecture and implementation ideas, including:

- GitHub Trending data scraping mechanism
- LLM intelligent analysis workflow
- Automated report generation solution
- Overall project architecture design

We appreciate the excellent work of the original project author for providing valuable reference and inspiration for this project.

## API Integration

You can fetch GitHub Trending reports via HTTP and integrate them into your own agent or application.

### Endpoints

| Type | URL Pattern |
|------|-------------|
| Report Page (HTML) | `https://wayyoungboy.github.io/github-trending-reporter/reports/YYYY/MM/YYYY-MM-DD` |
| Raw Data (JSON) | `https://wayyoungboy.github.io/github-trending-reporter/data/YYYY/MM/YYYY-MM-DD.json` |

### Fetch JSON Data

```bash
curl https://wayyoungboy.github.io/github-trending-reporter/data/2026/05/2026-05-27.json
```

### JSON Response Format

```json
{
  "date": "2026-05-27",
  "generated_at": "2026-05-27T00:05:00.000000",
  "total_repos": 25,
  "repositories": [
    {
      "owner": "xxx",
      "name": "xxx",
      "full_name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "description": "Original description",
      "llm_summary": "AI-generated concise summary",
      "language": "Python",
      "stars": 12345,
      "stars_today": 567,
      "forks": 890,
      "topics": ["ai", "llm"],
      "license": "MIT"
    }
  ]
}
```

### Key Fields

| Field | Description |
|-------|-------------|
| `full_name` | Repository full name (owner/name) |
| `url` | GitHub repository URL |
| `description` | Original description from GitHub |
| `llm_summary` | AI-generated concise summary (15-25 chars) |
| `language` | Primary programming language |
| `stars` | Total star count |
| `stars_today` | Stars gained today |
| `forks` | Fork count |
| `topics` | Repository topics/tags |

### Agent Integration Example (Python)

```python
import requests
from datetime import datetime

def get_trending_report(date_str=None):
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    year, month = date_str[:4], date_str[5:7]
    url = f"https://wayyoungboy.github.io/github-trending-reporter/data/{year}/{month}/{date_str}.json"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

# Usage
data = get_trending_report("2026-05-27")
for repo in data["repositories"][:5]:
    print(f"{repo['full_name']}: {repo.get('llm_summary') or repo['description']}")
```

## Related Links

- [GitHub Trending](https://github.com/trending)
- [Docusaurus](https://docusaurus.io/)
- [ai-git-trending](https://github.com/lgy1027/ai-git-trending) - Inspiration Source

---

Built with Python + Docusaurus
