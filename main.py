#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@file: main.py
@desc: Main entry point for GitHub Trending Reporter
"""

import argparse
import sys
from datetime import datetime
from typing import Optional

from trending_scraper import fetch_trending
from llm_analyzer import LLMAnalyzer
from data_pusher import DataPusher
import config


def run_report(
    language: Optional[str] = None,
    since: str = "daily",
    analysis_type: str = "comprehensive",
    push_to_repo: bool = True,
    output_local: bool = False,
    date_str: Optional[str] = None,
    detailed_analysis: bool = True
) -> bool:
    """
    Run the complete trending report workflow
    
    Args:
        language: Programming language filter
        since: Time range - 'daily', 'weekly', 'monthly'
        analysis_type: Type of LLM analysis
        push_to_repo: Whether to push results to GitHub repository
        output_local: Whether to save results locally
        date_str: Override date string (for testing)
        detailed_analysis: Whether to include detailed analysis for top projects
    
    Returns:
        True if successful
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    print(f"[START] GitHub Trending Report for {date_str}")
    print(f"  Language filter: {language or 'All'}")
    print(f"  Time range: {since}")
    print(f"  Analysis type: {analysis_type}")
    print(f"  Detailed analysis: {'Yes' if detailed_analysis else 'No'}")
    print()
    
    # Step 1: Fetch trending repositories
    print("[1/4] Fetching trending repositories...")
    try:
        repos = fetch_trending(language=language, since=since)
        print(f"  Found {len(repos)} repositories")
    except Exception as e:
        print(f"[ERROR] Fetching trending data: {e}")
        return False
    
    if not repos:
        print("[WARN] No repositories found")
        return False
    
    # Step 2: Analyze with LLM
    print("[2/4] Analyzing with LLM...")
    try:
        analyzer = LLMAnalyzer()
        report = analyzer.generate_daily_report(repos, date_str, detailed_analysis=detailed_analysis)
        print("  Analysis complete")
    except Exception as e:
        print(f"[ERROR] LLM analysis: {e}")
        # Generate basic report without LLM analysis
        report = generate_basic_report(repos, date_str)
        print("  Generated basic report without LLM analysis")
    
    # Step 3: Save locally if requested
    if output_local:
        print("[3/4] Saving locally...")
        try:
            save_local(repos, report, date_str)
            print("  Saved to local files")
        except Exception as e:
            print(f"[WARN] Saving locally: {e}")
    
    # Step 4: Push to repository if requested
    if push_to_repo:
        print("[4/4] Pushing to repository...")
        try:
            pusher = DataPusher()
            results = pusher.push_all(repos, report, date_str)
            pusher.update_readme(date_str)
            
            if results["raw_data"] and results["report"]:
                print("  Successfully pushed to repository")
            else:
                print("[WARN] Some files failed to push")
                return False
        except Exception as e:
            print(f"[ERROR] Pushing to repository: {e}")
            return False
    
    print()
    print("[DONE] Report generation complete!")
    return True


def generate_basic_report(repos: list, date_str: str) -> str:
    """
    Generate a basic report without LLM analysis (new beautiful format)
    
    Args:
        repos: List of repository dictionaries
        date_str: Date string
    
    Returns:
        Basic markdown report with Docusaurus frontmatter
    """
    # 按今日star数排序
    sorted_repos = sorted(repos, key=lambda x: x.get('stars_today', 0), reverse=True)
    
    report_parts = [
        "---",
        "sidebar_position: 1",
        f"title: {date_str} 日报",
        f"description: GitHub Trending 每日热门项目报告 - {date_str}",
        "---\n",
        f"## 今日热点\n",
        f"今日 GitHub 热榜共收录 **{len(repos)}** 个热门项目。\n",
        "---\n",
        "## 热门项目一览\n",
        "| 排名 | 项目 | 语言 | 今日 | 总计 | 简介 |",
        "|:---:|------|:----:|------:|-----:|------|",
    ]
    
    for i, repo in enumerate(sorted_repos[:12]):
        rank = i + 1
        name = repo.get('full_name', 'Unknown')
        url = repo.get('url', f"https://github.com/{name}")
        language = repo.get('language', 'Unknown') or 'Unknown'
        stars_today = repo.get('stars_today', 0)
        stars = repo.get('stars', 0)
        desc = repo.get('description', 'No description') or 'No description'
        if len(desc) > 30:
            desc = desc[:27] + "..."
        
        report_parts.append(
            f"| {rank} | [{name}]({url}) | {language} | +{stars_today:,} | {stars:,} | {desc} |"
        )
    
    # 简单项目列表
    report_parts.extend([
        "\n---\n",
        "## 项目详情\n",
    ])
    
    for i, repo in enumerate(sorted_repos[:5], 1):
        name = repo.get('full_name', 'Unknown')
        url = repo.get('url', f"https://github.com/{name}")
        desc = repo.get('description', 'No description') or 'No description'
        language = repo.get('language', 'Unknown')
        stars = repo.get('stars', 0)
        stars_today = repo.get('stars_today', 0)
        forks = repo.get('forks', 0)
        
        report_parts.append(f"""### {i}. {name}

> {desc}

| 指标 | 数值 |
|------|------|
| 语言 | {language} |
| 今日 | +{stars_today:,} |
| 总计 | {stars:,} |
| Forks | {forks:,} |

[GitHub]({url})

---
""")
    
    report_parts.extend([
        '<div align="center">\n',
        f"*Generated on {date_str} | Powered by GitHub Trending Reporter*\n",
        "</div>"
    ])
    
    return "\n".join(report_parts)


def save_local(repos: list, report: str, date_str: str):
    """
    Save results to local files
    
    Args:
        repos: List of repository dictionaries
        report: Markdown report content
        date_str: Date string
    """
    import json
    import os
    
    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save report
    report_path = os.path.join(output_dir, f"{date_str}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    # Save raw data
    data_path = os.path.join(output_dir, f"{date_str}.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "total_repos": len(repos),
            "repositories": repos
        }, f, indent=2, ensure_ascii=False)


def main():
    """Main entry point with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description="GitHub Trending Reporter - Fetch, analyze, and report trending repositories"
    )
    
    parser.add_argument(
        "-l", "--language",
        type=str,
        default=None,
        help="Filter by programming language (e.g., python, javascript)"
    )
    
    parser.add_argument(
        "-s", "--since",
        type=str,
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="Time range for trending (default: daily)"
    )
    
    parser.add_argument(
        "-a", "--analysis",
        type=str,
        choices=["comprehensive", "brief", "technical"],
        default="comprehensive",
        help="Type of LLM analysis (default: comprehensive)"
    )
    
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Don't push results to GitHub repository"
    )
    
    parser.add_argument(
        "--local",
        action="store_true",
        help="Save results to local files"
    )
    
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Override date string (format: YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--no-detailed",
        action="store_true",
        help="Skip detailed analysis for individual projects"
    )
    
    args = parser.parse_args()
    
    success = run_report(
        language=args.language,
        since=args.since,
        analysis_type=args.analysis,
        push_to_repo=not args.no_push,
        output_local=args.local,
        date_str=args.date,
        detailed_analysis=not args.no_detailed
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
