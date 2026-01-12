#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@file: llm_analyzer.py
@desc: LLM-based analysis for GitHub trending repositories
"""

import json
from typing import List, Dict, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import config


class LLMAnalyzer:
    """Analyzer using LLM to provide insights on trending repositories"""

    def __init__(self):
        """Initialize the LLM client"""
        self.client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL
        )
        self.model = config.LLM_MODEL

    def _build_repos_summary(self, repos: List[Dict]) -> str:
        """Build a text summary of repositories for LLM input"""
        summary_parts = []
        for i, repo in enumerate(repos, 1):
            topics = ", ".join(repo.get("topics", [])[:5]) if repo.get("topics") else "无"
            summary_parts.append(
                f"{i}. **{repo.get('full_name', 'Unknown')}** ({repo.get('language', 'Unknown')})\n"
                f"   - ⭐ Stars: {repo.get('stars', 0):,} (+{repo.get('stars_today', 0):,} today)\n"
                f"   - 🍴 Forks: {repo.get('forks', 0):,}\n"
                f"   - 📝 Description: {repo.get('description', 'No description')}\n"
                f"   - 🏷️ Topics: {topics}\n"
                f"   - 🔗 URL: {repo.get('url', '')}"
            )
        return "\n\n".join(summary_parts)

    def _build_detailed_repo_info(self, repo: Dict) -> str:
        """Build detailed repository info including README excerpt"""
        info_parts = [
            f"## 项目: {repo.get('full_name', 'Unknown')}",
            f"- **编程语言**: {repo.get('language', 'Unknown')}",
            f"- **Star 数**: {repo.get('stars', 0):,} (+{repo.get('stars_today', 0):,} today)",
            f"- **Fork 数**: {repo.get('forks', 0):,}",
            f"- **Open Issues**: {repo.get('open_issues', 0):,}",
            f"- **License**: {repo.get('license', 'Unknown')}",
            f"- **项目描述**: {repo.get('description', 'No description')}",
        ]
        
        # Topics
        if repo.get("topics"):
            info_parts.append(f"- **Topics**: {', '.join(repo['topics'][:10])}")
        
        # Languages breakdown
        if repo.get("languages"):
            total = sum(repo["languages"].values())
            lang_breakdown = ", ".join([
                f"{lang}: {bytes/total*100:.1f}%" 
                for lang, bytes in list(repo["languages"].items())[:5]
            ])
            info_parts.append(f"- **语言分布**: {lang_breakdown}")
        
        # Recent commits
        if repo.get("recent_commits"):
            info_parts.append("\n**最近提交**:")
            for commit in repo["recent_commits"][:3]:
                info_parts.append(f"  - [{commit['sha']}] {commit['message']}")
        
        # README excerpt
        if repo.get("readme_excerpt"):
            # 截取 README 的前 800 字符
            readme = repo["readme_excerpt"][:800]
            info_parts.append(f"\n**README 摘要**:\n```\n{readme}\n```")
        
        return "\n".join(info_parts)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def analyze_trends(self, repos: List[Dict], analysis_type: str = "comprehensive") -> str:
        """Analyze trending repositories using LLM"""
        repos_summary = self._build_repos_summary(repos)
        
        prompts = {
            "comprehensive": """你是一位资深的技术分析师，请对以下 GitHub 热门项目进行全面分析：

## 今日 GitHub Trending 项目列表：

{repos}

请提供以下分析内容（使用中文）：

### 1. 📊 趋势概览
简要总结今日热门项目的整体趋势，包括主要技术方向和热点领域。

### 2. 🌟 重点项目推荐（选择3-5个最值得关注的项目）
对每个推荐项目进行详细分析：
- 项目亮点和创新点
- 适用场景和目标用户
- 技术栈和实现特点
- 学习价值和实用价值

### 3. 🔍 技术洞察
- 从这些项目中观察到的技术趋势
- 值得关注的新兴技术或框架
- 开发者社区的关注焦点

### 4. 💡 建议
- 对开发者的学习建议
- 哪些项目值得深入研究
- 潜在的应用机会

请确保分析内容专业、有深度，对开发者有实际参考价值。""",

            "brief": """你是一位技术编辑，请对以下 GitHub 热门项目进行简要分析：

## 今日 GitHub Trending 项目列表：

{repos}

请用中文提供简洁的分析摘要（300字以内），包括：
1. 今日主要技术趋势
2. 3个最值得关注的项目及原因
3. 一句话总结今日热点""",

            "technical": """你是一位高级软件工程师，请对以下 GitHub 热门项目进行技术层面的深度分析：

## 今日 GitHub Trending 项目列表：

{repos}

请用中文提供技术分析，包括：

### 1. 技术栈分布
分析今日热门项目使用的主要技术栈和编程语言分布。

### 2. 架构特点
选择2-3个项目分析其架构设计和技术实现的亮点。

### 3. 代码质量指标
基于 star/fork 比例等数据分析项目的社区参与度和代码质量。

### 4. 技术建议
对于想要学习或贡献这些项目的开发者的技术建议。"""
        }
        
        prompt = prompts.get(analysis_type, prompts["comprehensive"])
        formatted_prompt = prompt.format(repos=repos_summary)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位专业的技术分析师，擅长分析开源项目和技术趋势。你的分析应该专业、有深度、对开发者有实际价值。"
                },
                {
                    "role": "user",
                    "content": formatted_prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        return response.choices[0].message.content

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def analyze_single_repo_detailed(self, repo: Dict) -> str:
        """
        Analyze a single repository in detail with README context
        
        Args:
            repo: Repository dictionary with enriched data
        
        Returns:
            Detailed analysis text
        """
        repo_info = self._build_detailed_repo_info(repo)
        
        prompt = f"""请对以下 GitHub 项目进行深度分析和解读：

{repo_info}

请用中文提供详细的项目解读，包括以下内容：

### 🎯 项目定位
- 这个项目是什么？解决什么问题？
- 核心功能和特性有哪些？

### 💡 技术亮点
- 项目采用了哪些技术？有什么创新之处？
- 架构设计有什么特点？

### 👥 目标用户
- 这个项目适合谁使用？
- 有哪些典型的使用场景？

### 📈 发展潜力
- 基于当前数据，项目的发展趋势如何？
- 社区活跃度如何？

### 🔧 快速上手
- 如何快速开始使用这个项目？
- 有哪些学习资源推荐？

### ⚠️ 注意事项
- 使用时需要注意什么？
- 有哪些已知的限制或问题？

请确保分析基于提供的信息，内容专业且对开发者有实际帮助。"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位资深的开源项目分析师和技术专家。你擅长深入分析项目的技术细节、应用价值和发展潜力。请基于提供的项目信息（包括README内容）进行准确、专业的分析。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        return response.choices[0].message.content

    def generate_daily_report(self, repos: List[Dict], date_str: str, detailed_analysis: bool = True) -> str:
        """
        Generate a complete daily report with optional detailed project analysis
        
        Args:
            repos: List of repository dictionaries
            date_str: Date string for the report
            detailed_analysis: Whether to include detailed analysis for top projects
        
        Returns:
            Complete markdown report with Docusaurus frontmatter
        """
        print("🤖 Generating overall trend analysis...")
        overall_analysis = self.analyze_trends(repos, "comprehensive")
        
        # Build the report
        report_parts = [
            "---",
            f"sidebar_position: 1",
            f"title: {date_str} 日报",
            f"description: GitHub Trending 每日热门项目报告 - {date_str}",
            "---\n",
            f"# 📈 GitHub Trending 日报 - {date_str}\n",
            f"> 本报告由 AI 自动生成，分析了 GitHub 当日 {len(repos)} 个热门项目\n",
        ]
        
        # Table of Contents
        report_parts.extend([
            "## 📑 目录\n",
            "- [今日热门项目列表](#-今日热门项目列表)",
            "- [AI 趋势分析](#-ai-趋势分析)",
        ])
        
        if detailed_analysis:
            report_parts.append("- [重点项目深度解读](#-重点项目深度解读)")
        
        report_parts.append("\n---\n")
        
        # Project List
        report_parts.extend([
            "## 📋 今日热门项目列表\n",
            self._build_repos_summary(repos),
            "\n---\n",
        ])
        
        # Overall Analysis
        report_parts.extend([
            "## 🤖 AI 趋势分析\n",
            overall_analysis,
            "\n---\n",
        ])
        
        # Detailed Analysis for Top Projects
        if detailed_analysis:
            report_parts.append("## 🔬 重点项目深度解读\n")
            report_parts.append("> 以下是对今日 Top 5 热门项目的详细解读\n\n")
            
            # Analyze top 5 projects
            top_repos = repos[:5]
            for i, repo in enumerate(top_repos, 1):
                print(f"🔍 Analyzing project {i}/{len(top_repos)}: {repo.get('full_name')}...")
                
                report_parts.append(f"### {i}. {repo.get('full_name', 'Unknown')}\n")
                report_parts.append(f"![{repo.get('name')}](https://opengraph.githubassets.com/1/{repo.get('full_name')})\n")
                
                try:
                    detailed = self.analyze_single_repo_detailed(repo)
                    report_parts.append(detailed)
                except Exception as e:
                    print(f"  ⚠️ Error analyzing {repo.get('full_name')}: {e}")
                    report_parts.append(f"*分析生成失败: {str(e)}*")
                
                report_parts.append("\n---\n")
        
        # Footer
        report_parts.append(f"\n*Generated by GitHub Trending Reporter | Data collected at {date_str}*")
        
        return "\n".join(report_parts)


def analyze_trending(repos: List[Dict], analysis_type: str = "comprehensive") -> str:
    """Convenience function to analyze trending repositories"""
    analyzer = LLMAnalyzer()
    return analyzer.analyze_trends(repos, analysis_type)


if __name__ == "__main__":
    print("LLM Analyzer module - requires valid API key to test")
