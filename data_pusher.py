#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@file: data_pusher.py
@desc: Push trending data and reports to a separate GitHub repository
"""

import json
import base64
from datetime import datetime
from typing import Dict, List, Optional
from github import Github, GithubException
from tenacity import retry, stop_after_attempt, wait_exponential
import config


class DataPusher:
    """Push data to a GitHub repository for persistence"""

    def __init__(self):
        """Initialize the GitHub client"""
        self.github = Github(config.GITHUB_TOKEN)
        self.repo_owner = config.DATA_REPO_OWNER
        self.repo_name = config.DATA_REPO_NAME
        self._repo = None

    @property
    def repo(self):
        """Get or create the data repository"""
        if self._repo is None:
            try:
                self._repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
            except GithubException as e:
                print(f"Error accessing repository: {e}")
                raise
        return self._repo

    def _get_file_path(self, date_str: str, file_type: str = "report") -> str:
        """
        Generate file path based on date
        
        Structure:
        - reports/2026/01/2026-01-12.md (markdown reports)
        - data/2026/01/2026-01-12.json (raw JSON data)
        """
        year = date_str[:4]
        month = date_str[5:7]
        
        if file_type == "report":
            return f"reports/{year}/{month}/{date_str}.md"
        elif file_type == "data":
            return f"data/{year}/{month}/{date_str}.json"
        else:
            raise ValueError(f"Unknown file type: {file_type}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def push_report(self, content: str, date_str: str) -> bool:
        """
        Push markdown report to the repository
        
        Args:
            content: Markdown content of the report
            date_str: Date string (e.g., '2026-01-12')
        
        Returns:
            True if successful
        """
        file_path = self._get_file_path(date_str, "report")
        commit_message = f"📈 Add trending report for {date_str}"
        
        return self._create_or_update_file(file_path, content, commit_message)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def push_raw_data(self, repos: List[Dict], date_str: str) -> bool:
        """
        Push raw JSON data to the repository
        
        Args:
            repos: List of repository dictionaries
            date_str: Date string (e.g., '2026-01-12')
        
        Returns:
            True if successful
        """
        file_path = self._get_file_path(date_str, "data")
        
        data = {
            "date": date_str,
            "generated_at": datetime.utcnow().isoformat(),
            "total_repos": len(repos),
            "repositories": repos
        }
        
        content = json.dumps(data, indent=2, ensure_ascii=False)
        commit_message = f"📊 Add raw data for {date_str}"
        
        return self._create_or_update_file(file_path, content, commit_message)

    def _create_or_update_file(self, file_path: str, content: str, commit_message: str) -> bool:
        """
        Create or update a file in the repository
        
        Args:
            file_path: Path to the file in the repository
            content: File content
            commit_message: Git commit message
        
        Returns:
            True if successful
        """
        try:
            # Try to get existing file
            try:
                existing_file = self.repo.get_contents(file_path)
                # Update existing file
                self.repo.update_file(
                    file_path,
                    commit_message,
                    content,
                    existing_file.sha
                )
                print(f"Updated file: {file_path}")
            except GithubException as e:
                if e.status == 404:
                    # File doesn't exist, create it
                    self.repo.create_file(
                        file_path,
                        commit_message,
                        content
                    )
                    print(f"Created file: {file_path}")
                else:
                    raise
            return True
        except GithubException as e:
            print(f"Error pushing to repository: {e}")
            return False

    def push_all(self, repos: List[Dict], report: str, date_str: str) -> Dict[str, bool]:
        """
        Push both raw data and report
        
        Args:
            repos: List of repository dictionaries
            report: Markdown report content
            date_str: Date string
        
        Returns:
            Dictionary with success status for each push
        """
        results = {
            "raw_data": self.push_raw_data(repos, date_str),
            "report": self.push_report(report, date_str)
        }
        return results

    def update_readme(self, date_str: str) -> bool:
        """
        Update the README.md with the latest report link
        
        Args:
            date_str: Date string of the latest report
        
        Returns:
            True if successful
        """
        readme_content = f"""# 📈 GitHub Trending Reporter Data

This repository stores daily GitHub trending data and AI-generated analysis reports.

## 📅 Latest Report

📄 **[{date_str}](reports/{date_str[:4]}/{date_str[5:7]}/{date_str}.md)**

## 📁 Repository Structure

```
├── reports/          # Markdown reports with AI analysis
│   └── YYYY/
│       └── MM/
│           └── YYYY-MM-DD.md
├── data/             # Raw JSON data
│   └── YYYY/
│       └── MM/
│           └── YYYY-MM-DD.json
└── README.md
```

## 🔗 Links

- [GitHub Trending](https://github.com/trending)
- [Source Code](https://github.com/{self.repo_owner}/github-trending-reporter)

## 📊 Data Format

Each JSON file contains:
- `date`: Report date
- `generated_at`: Generation timestamp
- `total_repos`: Number of repositories
- `repositories`: Array of repository objects

---

*This data is automatically updated daily by GitHub Actions.*
"""
        
        return self._create_or_update_file("README.md", readme_content, f"📝 Update README for {date_str}")


def push_data(repos: List[Dict], report: str, date_str: str) -> Dict[str, bool]:
    """
    Convenience function to push data to repository
    
    Args:
        repos: List of repository dictionaries
        report: Markdown report content
        date_str: Date string
    
    Returns:
        Dictionary with success status
    """
    pusher = DataPusher()
    results = pusher.push_all(repos, report, date_str)
    pusher.update_readme(date_str)
    return results


if __name__ == "__main__":
    print("DataPusher module - requires GITHUB_TOKEN to test")
