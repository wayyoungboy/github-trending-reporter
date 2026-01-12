#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@file: trending_scraper.py
@desc: Scrape GitHub Trending repositories
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import config


class TrendingScraper:
    """Scraper for GitHub Trending page"""

    def __init__(self, language: Optional[str] = None, since: str = "daily"):
        """
        Initialize the scraper
        
        Args:
            language: Programming language filter (e.g., 'python', 'javascript')
            since: Time range - 'daily', 'weekly', or 'monthly'
        """
        self.base_url = config.GITHUB_TRENDING_URL
        self.github_api_url = "https://api.github.com"
        self.language = language
        self.since = since
        self.headers = config.REQUEST_HEADERS
        self.api_headers = config.get_github_api_headers()
        self.timeout = config.REQUEST_TIMEOUT

    def _build_url(self) -> str:
        """Build the trending URL with filters"""
        url = self.base_url
        if self.language:
            url = f"{url}/{self.language}"
        params = []
        if self.since and self.since != "daily":
            params.append(f"since={self.since}")
        if params:
            url = f"{url}?{'&'.join(params)}"
        return url

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch_page(self) -> str:
        """Fetch the trending page HTML with retry logic"""
        url = self._build_url()
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def _parse_repository(self, article: BeautifulSoup) -> Dict:
        """Parse a single repository article element"""
        repo_data = {}

        # Repository name and owner
        h2 = article.find("h2", class_="h3")
        if h2:
            a_tag = h2.find("a")
            if a_tag:
                href = a_tag.get("href", "").strip("/")
                parts = href.split("/")
                if len(parts) >= 2:
                    repo_data["owner"] = parts[0]
                    repo_data["name"] = parts[1]
                    repo_data["full_name"] = f"{parts[0]}/{parts[1]}"
                    repo_data["url"] = f"https://github.com/{href}"

        # Description
        p_tag = article.find("p", class_="col-9")
        if p_tag:
            repo_data["description"] = p_tag.get_text(strip=True)
        else:
            repo_data["description"] = ""

        # Programming language
        lang_span = article.find("span", itemprop="programmingLanguage")
        if lang_span:
            repo_data["language"] = lang_span.get_text(strip=True)
        else:
            repo_data["language"] = "Unknown"

        # Stars count
        stars_link = article.find("a", href=lambda x: x and "/stargazers" in x)
        if stars_link:
            stars_text = stars_link.get_text(strip=True).replace(",", "")
            repo_data["stars"] = self._parse_number(stars_text)
        else:
            repo_data["stars"] = 0

        # Forks count
        forks_link = article.find("a", href=lambda x: x and "/forks" in x)
        if forks_link:
            forks_text = forks_link.get_text(strip=True).replace(",", "")
            repo_data["forks"] = self._parse_number(forks_text)
        else:
            repo_data["forks"] = 0

        # Today's stars
        today_stars_span = article.find("span", class_="d-inline-block float-sm-right")
        if today_stars_span:
            today_text = today_stars_span.get_text(strip=True)
            # Extract number from text like "1,234 stars today"
            repo_data["stars_today"] = self._parse_number(today_text.split()[0])
        else:
            repo_data["stars_today"] = 0

        # Built by (contributors)
        built_by = []
        built_by_spans = article.find_all("a", href=lambda x: x and x.startswith("/") and "/commits" not in x)
        for span in built_by_spans:
            img = span.find("img")
            if img and img.get("alt"):
                username = img.get("alt").replace("@", "")
                if username and username not in ["", repo_data.get("owner", "")]:
                    built_by.append(username)
        repo_data["built_by"] = list(set(built_by))[:5]  # Limit to 5 unique contributors

        return repo_data

    def _parse_number(self, text: str) -> int:
        """Parse number from text, handling k/m suffixes"""
        text = text.lower().replace(",", "").strip()
        try:
            if "k" in text:
                return int(float(text.replace("k", "")) * 1000)
            elif "m" in text:
                return int(float(text.replace("m", "")) * 1000000)
            else:
                return int(float(text))
        except (ValueError, AttributeError):
            return 0

    def scrape(self, enrich_with_api: bool = True) -> List[Dict]:
        """
        Scrape trending repositories
        
        Args:
            enrich_with_api: Whether to enrich data using GitHub API
        
        Returns:
            List of repository dictionaries
        """
        html = self._fetch_page()
        soup = BeautifulSoup(html, "lxml")
        
        articles = soup.find_all("article", class_="Box-row")
        repositories = []
        
        for article in articles:
            try:
                repo_data = self._parse_repository(article)
                if repo_data.get("full_name"):
                    repositories.append(repo_data)
            except Exception as e:
                print(f"Error parsing repository: {e}")
                continue
        
        # Enrich with GitHub API data if token is available
        if enrich_with_api and config.GITHUB_API_TOKEN:
            print(f"Enriching {len(repositories)} repositories with GitHub API...")
            repositories = self._enrich_with_api(repositories)
        
        return repositories

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch_repo_api(self, full_name: str) -> Optional[Dict]:
        """Fetch repository details from GitHub API"""
        try:
            url = f"{self.github_api_url}/repos/{full_name}"
            response = requests.get(url, headers=self.api_headers, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                print(f"GitHub API rate limit exceeded for {full_name}")
                return None
            else:
                return None
        except Exception as e:
            print(f"Error fetching API data for {full_name}: {e}")
            return None

    def _fetch_readme(self, full_name: str) -> Optional[str]:
        """Fetch repository README content"""
        try:
            url = f"{self.github_api_url}/repos/{full_name}/readme"
            response = requests.get(url, headers=self.api_headers, timeout=self.timeout)
            
            if response.status_code == 200:
                import base64
                data = response.json()
                content = base64.b64decode(data.get("content", "")).decode("utf-8")
                # 截取前 2000 字符，避免太长
                return content[:2000] if len(content) > 2000 else content
            return None
        except Exception as e:
            print(f"Error fetching README for {full_name}: {e}")
            return None

    def _fetch_recent_commits(self, full_name: str, count: int = 5) -> List[Dict]:
        """Fetch recent commits"""
        try:
            url = f"{self.github_api_url}/repos/{full_name}/commits?per_page={count}"
            response = requests.get(url, headers=self.api_headers, timeout=self.timeout)
            
            if response.status_code == 200:
                commits = response.json()
                return [
                    {
                        "sha": c.get("sha", "")[:7],
                        "message": c.get("commit", {}).get("message", "").split("\n")[0][:100],
                        "date": c.get("commit", {}).get("committer", {}).get("date"),
                        "author": c.get("commit", {}).get("author", {}).get("name")
                    }
                    for c in commits
                ]
            return []
        except Exception as e:
            print(f"Error fetching commits for {full_name}: {e}")
            return []

    def _fetch_languages(self, full_name: str) -> Dict[str, int]:
        """Fetch repository languages breakdown"""
        try:
            url = f"{self.github_api_url}/repos/{full_name}/languages"
            response = requests.get(url, headers=self.api_headers, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Error fetching languages for {full_name}: {e}")
            return {}

    def _enrich_with_api(self, repositories: List[Dict], fetch_details: bool = True) -> List[Dict]:
        """
        Enrich repository data with GitHub API information
        
        Args:
            repositories: List of repository dictionaries from scraping
            fetch_details: Whether to fetch README, commits, languages (more API calls)
        
        Returns:
            Enriched list of repository dictionaries
        """
        enriched = []
        
        for i, repo in enumerate(repositories):
            full_name = repo.get("full_name")
            if not full_name:
                enriched.append(repo)
                continue
            
            print(f"  [{i+1}/{len(repositories)}] Enriching {full_name}...")
            
            api_data = self._fetch_repo_api(full_name)
            
            if api_data:
                # Basic API data
                repo["stars"] = api_data.get("stargazers_count", repo.get("stars", 0))
                repo["forks"] = api_data.get("forks_count", repo.get("forks", 0))
                repo["watchers"] = api_data.get("watchers_count", 0)
                repo["open_issues"] = api_data.get("open_issues_count", 0)
                repo["license"] = api_data.get("license", {}).get("spdx_id") if api_data.get("license") else None
                repo["created_at"] = api_data.get("created_at")
                repo["updated_at"] = api_data.get("updated_at")
                repo["pushed_at"] = api_data.get("pushed_at")
                repo["topics"] = api_data.get("topics", [])
                repo["homepage"] = api_data.get("homepage")
                repo["default_branch"] = api_data.get("default_branch")
                repo["archived"] = api_data.get("archived", False)
                repo["size"] = api_data.get("size", 0)  # KB
                repo["has_wiki"] = api_data.get("has_wiki", False)
                repo["has_pages"] = api_data.get("has_pages", False)
                repo["has_discussions"] = api_data.get("has_discussions", False)
                
                # Use API description if scraped one is empty
                if not repo.get("description") and api_data.get("description"):
                    repo["description"] = api_data.get("description")
                
                # Fetch additional details for top projects (limit API calls)
                if fetch_details and i < 10:  # Only top 10 projects
                    # README
                    readme = self._fetch_readme(full_name)
                    if readme:
                        repo["readme_excerpt"] = readme
                    
                    # Recent commits
                    commits = self._fetch_recent_commits(full_name, 5)
                    if commits:
                        repo["recent_commits"] = commits
                    
                    # Languages breakdown
                    languages = self._fetch_languages(full_name)
                    if languages:
                        repo["languages"] = languages
            
            enriched.append(repo)
        
        return enriched


def fetch_trending(language: Optional[str] = None, since: str = "daily") -> List[Dict]:
    """
    Convenience function to fetch trending repositories
    
    Args:
        language: Programming language filter
        since: Time range - 'daily', 'weekly', or 'monthly'
    
    Returns:
        List of trending repository dictionaries
    """
    scraper = TrendingScraper(language=language, since=since)
    return scraper.scrape()


if __name__ == "__main__":
    # Test the scraper
    repos = fetch_trending()
    print(f"Found {len(repos)} trending repositories")
    for repo in repos[:5]:
        print(f"- {repo['full_name']}: {repo['description'][:50]}...")
