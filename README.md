# GitHub Trending Reporter

Automatically fetch GitHub Trending data, perform intelligent analysis using LLM, and generate a visualized report website.

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

## Related Links

- [GitHub Trending](https://github.com/trending)
- [Docusaurus](https://docusaurus.io/)
- [ai-git-trending](https://github.com/lgy1027/ai-git-trending) - Inspiration Source

---

Built with Python + Docusaurus
