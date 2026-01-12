#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@file: config.py
@desc: Configuration settings for GitHub Trending Reporter
"""

import os
from dotenv import load_dotenv

load_dotenv()

# GitHub Trending URL
GITHUB_TRENDING_URL = "https://github.com/trending"

# LLM Configuration
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
LLM_MODEL = os.getenv("LLM_MODEL", "glm-4.5-flash")

# GitHub API Token (for avoiding rate limits when scraping)
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN", "")

# GitHub Configuration for pushing data
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
DATA_REPO_OWNER = os.getenv("DATA_REPO_OWNER", "")
DATA_REPO_NAME = os.getenv("DATA_REPO_NAME", "github-trending-reporter-data")

# Request Configuration
REQUEST_TIMEOUT = 30
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# GitHub API Headers (with token for rate limiting)
def get_github_api_headers():
    """Get headers for GitHub API requests"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Trending-Reporter",
    }
    if GITHUB_API_TOKEN:
        headers["Authorization"] = f"token {GITHUB_API_TOKEN}"
    return headers

# Output Configuration
OUTPUT_FORMAT = "markdown"  # markdown or json
