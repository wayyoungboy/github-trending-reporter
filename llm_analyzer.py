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
            summary_parts.append(
                f"{i}. **{repo.get('full_name', 'Unknown')}** ({repo.get('language', 'Unknown')})\n"
                f"   - ⭐ Stars: {repo.get('stars', 0):,} (+{repo.get('stars_today', 0):,} today)\n"
                f"   - 🍴 Forks: {repo.get('forks', 0):,}\n"
                f"   - 📝 Description: {repo.get('description', 'No description')}\n"
                f"   - 🔗 URL: {repo.get('url', '')}"
            )
        return "\n\n".join(summary_parts)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def analyze_trends(self, repos: List[Dict], analysis_type: str = "comprehensive") -> str:
        """
        Analyze trending repositories using LLM
        
        Args:
            repos: List of repository dictionaries
            analysis_type: Type of analysis - 'comprehensive', 'brief', 'technical'
        
        Returns:
            Analysis text from LLM
        """
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
    def analyze_single_repo(self, repo: Dict) -> str:
        """
        Analyze a single repository in detail
        
        Args:
            repo: Repository dictionary
        
        Returns:
            Detailed analysis text
        """
        prompt = f"""请对以下 GitHub 项目进行详细分析：

项目名称: {repo.get('full_name', 'Unknown')}
编程语言: {repo.get('language', 'Unknown')}
Star 数: {repo.get('stars', 0):,}
今日新增 Star: {repo.get('stars_today', 0):,}
Fork 数: {repo.get('forks', 0):,}
项目描述: {repo.get('description', 'No description')}
项目链接: {repo.get('url', '')}

请用中文提供以下分析：
1. 项目定位和主要功能
2. 技术特点和创新之处
3. 适用场景和目标用户
4. 项目优势和潜在不足
5. 学习和使用建议"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位专业的开源项目分析师，擅长深入分析项目的技术特点和应用价值。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content

    def generate_daily_report(self, repos: List[Dict], date_str: str) -> str:
        """
        Generate a complete daily report
        
        Args:
            repos: List of repository dictionaries
            date_str: Date string for the report (e.g., '2026-01-12')
        
        Returns:
            Complete markdown report
        """
        analysis = self.analyze_trends(repos, "comprehensive")
        
        # Build the complete report
        report_parts = [
            f"# 📈 GitHub Trending 日报 - {date_str}\n",
            f"> 本报告由 AI 自动生成，分析了 GitHub 当日 {len(repos)} 个热门项目\n",
            "---\n",
            "## 📋 今日热门项目列表\n",
            self._build_repos_summary(repos),
            "\n---\n",
            "## 🤖 AI 分析报告\n",
            analysis,
            "\n---\n",
            f"*Generated by GitHub Trending Reporter | Data collected at {date_str}*"
        ]
        
        return "\n".join(report_parts)


def analyze_trending(repos: List[Dict], analysis_type: str = "comprehensive") -> str:
    """
    Convenience function to analyze trending repositories
    
    Args:
        repos: List of repository dictionaries
        analysis_type: Type of analysis
    
    Returns:
        Analysis text
    """
    analyzer = LLMAnalyzer()
    return analyzer.analyze_trends(repos, analysis_type)


if __name__ == "__main__":
    # Test with sample data
    sample_repos = [
        {
            "full_name": "test/repo",
            "language": "Python",
            "stars": 1000,
            "stars_today": 100,
            "forks": 50,
            "description": "A test repository",
            "url": "https://github.com/test/repo"
        }
    ]
    
    analyzer = LLMAnalyzer()
    print("Testing LLM Analyzer...")
    # Note: Will fail without valid API key
