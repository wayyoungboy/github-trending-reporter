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

    def _build_repos_table(self, repos: List[Dict]) -> str:
        """Build a markdown table of repositories"""
        # 按今日star数排序
        sorted_repos = sorted(repos, key=lambda x: x.get('stars_today', 0), reverse=True)
        
        table_parts = [
            "| 排名 | 项目 | 语言 | 今日 | 总计 | 简介 |",
            "|:---:|------|:----:|------:|-----:|------|"
        ]
        
        for i, repo in enumerate(sorted_repos[:12]):  # 最多显示12个
            rank = i + 1
            name = repo.get('full_name', 'Unknown')
            url = repo.get('url', f"https://github.com/{name}")
            language = repo.get('language', 'Unknown') or 'Unknown'
            stars_today = repo.get('stars_today', 0)
            stars = repo.get('stars', 0)
            desc = repo.get('description', 'No description') or 'No description'
            # 截断描述
            if len(desc) > 30:
                desc = desc[:27] + "..."
            
            table_parts.append(
                f"| {rank} | [{name}]({url}) | {language} | +{stars_today:,} | {stars:,} | {desc} |"
            )
        
        return "\n".join(table_parts)

    def _build_repos_summary_for_llm(self, repos: List[Dict]) -> str:
        """Build a text summary of repositories for LLM input"""
        summary_parts = []
        for i, repo in enumerate(repos, 1):
            topics = ", ".join(repo.get("topics", [])[:5]) if repo.get("topics") else "无"
            summary_parts.append(
                f"{i}. **{repo.get('full_name', 'Unknown')}** ({repo.get('language', 'Unknown')})\n"
                f"   - Stars: {repo.get('stars', 0):,} (+{repo.get('stars_today', 0):,} today)\n"
                f"   - Forks: {repo.get('forks', 0):,}\n"
                f"   - Description: {repo.get('description', 'No description')}\n"
                f"   - Topics: {topics}\n"
                f"   - URL: {repo.get('url', '')}"
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
            if total > 0:
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

    def _categorize_repos(self, repos: List[Dict]) -> Dict[str, int]:
        """Categorize repositories by domain/type"""
        categories = {
            "AI/ML 工具": 0,
            "开发框架": 0,
            "多媒体应用": 0,
            "智能家居": 0,
            "媒体资源": 0,
            "项目管理": 0,
            "开发工具": 0,
            "移动开发": 0,
            "Web 应用": 0,
            "游戏相关": 0,
            "数据分析": 0,
            "安全工具": 0,
            "其他": 0,
        }
        
        # 简单的关键词分类
        for repo in repos:
            desc = (repo.get('description', '') or '').lower()
            name = (repo.get('full_name', '') or '').lower()
            topics = [t.lower() for t in repo.get('topics', [])]
            combined = f"{desc} {name} {' '.join(topics)}"
            
            if any(kw in combined for kw in ['ai', 'ml', 'machine learning', 'llm', 'gpt', 'claude', 'agent', 'neural', 'deep learning']):
                categories["AI/ML 工具"] += 1
            elif any(kw in combined for kw in ['framework', 'fullstack', 'react', 'vue', 'angular', 'dioxus', 'flutter']):
                categories["开发框架"] += 1
            elif any(kw in combined for kw in ['video', 'audio', 'media', 'cam', 'face', 'image', 'deepfake']):
                categories["多媒体应用"] += 1
            elif any(kw in combined for kw in ['home', 'assistant', 'smart', 'iot', 'automation']):
                categories["智能家居"] += 1
            elif any(kw in combined for kw in ['iptv', 'streaming', 'tv', 'channel']):
                categories["媒体资源"] += 1
            elif any(kw in combined for kw in ['project', 'management', 'kanban', 'task']):
                categories["项目管理"] += 1
            elif any(kw in combined for kw in ['cli', 'tool', 'utility', 'terminal', 'shell']):
                categories["开发工具"] += 1
            elif any(kw in combined for kw in ['crawler', 'scraper', 'data', 'analysis', 'analytics']):
                categories["数据分析"] += 1
            elif any(kw in combined for kw in ['security', 'crypto', 'encryption', 'auth']):
                categories["安全工具"] += 1
            else:
                categories["其他"] += 1
        
        # 过滤掉数量为0的分类
        return {k: v for k, v in categories.items() if v > 0}

    def _build_category_chart(self, categories: Dict[str, int]) -> str:
        """Build an ASCII bar chart for categories"""
        if not categories:
            return ""
        
        max_count = max(categories.values())
        max_bar_width = 24
        
        lines = ["```"]
        lines.append("┌─────────────────────────────────────────────────────────────────┐")
        
        for category, count in sorted(categories.items(), key=lambda x: -x[1]):
            bar_width = int((count / max_count) * max_bar_width)
            bar = "█" * bar_width
            padding = " " * (max_bar_width - bar_width)
            lines.append(f"│  {category:<16} {bar}{padding}  {count} 个项目{' ' * 8}│")
        
        lines.append("└─────────────────────────────────────────────────────────────────┘")
        lines.append("```")
        
        return "\n".join(lines)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def analyze_trends(self, repos: List[Dict]) -> str:
        """Analyze trending repositories using LLM - generate hot topic summary"""
        repos_summary = self._build_repos_summary_for_llm(repos)
        
        prompt = f"""你是一位资深的技术分析师，请对以下 GitHub 热门项目进行分析：

## 今日 GitHub Trending 项目列表：

{repos_summary}

请用中文提供以下内容：

### 热点总结
用一段话（50-80字）概括今日GitHub热榜的主要热点和趋势，要抓住最核心的1-2个趋势。这段话将作为报告的开篇摘要。

### 关键观察
用3-4个要点（每个20-40字）列出今日最值得关注的技术趋势或现象，使用 markdown 加粗标注关键词。

格式要求：
1. 热点总结直接输出一段话，不需要标题
2. 关键观察用 "- **关键词**：说明" 的格式
3. 语言要精炼有力，避免废话
4. 内容要有洞察力，不要泛泛而谈"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位专业的技术分析师，擅长用精炼的语言总结技术趋势。你的分析应该有洞察力、有深度。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def analyze_single_repo_detailed(self, repo: Dict, rank: int) -> str:
        """
        Analyze a single repository in detail with new format
        
        Args:
            repo: Repository dictionary with enriched data
            rank: Rank of the repository
        
        Returns:
            Detailed analysis text in new format
        """
        repo_info = self._build_detailed_repo_info(repo)
        
        prompt = f"""请对以下 GitHub 项目进行深度分析，生成结构化的报告：

{repo_info}

请严格按照以下格式输出（使用中文）：

### {rank}. {repo.get('full_name', 'Unknown')} — [项目简短定位，5-10个字]

> **一句话总结**：[用一句话概括项目的核心价值和特点，30-50字]

#### 价值主张

| 维度 | 说明 |
|------|------|
| **解决痛点** | [项目解决的核心问题，20-40字] |
| **目标用户** | [主要使用人群，15-30字] |
| **核心亮点** | [3-5个关键特性，用 + 连接] |

#### 技术架构

[如果项目有明确的技术流程，用mermaid图展示，格式如下：]
```mermaid
graph LR
    A[输入] --> B[处理]
    B --> C[输出]
```

**技术特色**：
- [技术亮点1，15-30字]
- [技术亮点2，15-30字]
- [技术亮点3，15-30字]

#### 热度分析

- [基于Star/Fork数据的增长分析，20-40字]
- [社区活跃度或生态位置分析，20-40字]

#### 快速上手

```bash
# 简洁的上手命令示例（2-4行）
```

#### 注意事项

- [注意事项1]
- [注意事项2]

---

要求：
1. 内容要精炼，避免冗长
2. 技术分析要有深度和洞察
3. mermaid图要简洁清晰，节点不超过6个
4. 代码示例要实用可运行
5. 如果项目信息不足以生成mermaid图，可以省略该部分
6. 不要使用emoji"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位资深的开源项目分析师，擅长用结构化、精炼的方式解读项目。你的分析要有技术深度，格式要严格遵循模板。"
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

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_recommendations(self, repos: List[Dict]) -> str:
        """Generate recommendation table based on different scenarios"""
        repos_summary = self._build_repos_summary_for_llm(repos[:10])
        
        prompt = f"""基于以下GitHub热门项目，生成一个推荐表格：

{repos_summary}

请生成一个markdown表格，格式如下：

| 主题 | 推荐项目 | 亮点 |
|------|----------|------|
| [使用场景1] | [项目名](URL) | [一句话亮点] |
| [使用场景2] | [项目名](URL) | [一句话亮点] |
| [使用场景3] | [项目名](URL) | [一句话亮点] |
| [使用场景4] | [项目名](URL) | [一句话亮点] |

要求：
1. 选择4-5个不同的使用场景
2. 场景要具体，如"想入坑AI开发"、"学习新框架"等
3. 每个亮点不超过15字
4. 只输出表格，不要其他内容"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位技术顾问，擅长根据用户需求推荐合适的开源项目。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_short_summaries(self, repos: List[Dict]) -> Dict[str, str]:
        """
        Generate a short LLM summary for each project (for DingTalk etc.)

        Args:
            repos: List of repository dictionaries

        Returns:
            Dict mapping full_name to short summary string
        """
        repos_brief = []
        for i, repo in enumerate(repos, 1):
            repos_brief.append(
                f"{i}. {repo.get('full_name', 'Unknown')} ({repo.get('language', 'Unknown')}): "
                f"{repo.get('description', 'No description')}"
            )

        prompt = f"""请为以下每个 GitHub 项目生成一句简短的中文介绍（15-25字），要求突出项目的核心价值。

项目列表：
{chr(10).join(repos_brief)}

请严格按照以下 JSON 格式输出，不要输出其他内容：
{{
  "owner/name": "简短介绍",
  ...
}}

要求：
1. 每个介绍 15-25 个字
2. 用中文
3. 突出核心功能或亮点
4. 只输出 JSON，不要其他内容"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位技术编辑，擅长用精炼的语言描述开源项目。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=2000
        )

        content = response.choices[0].message.content.strip()
        # Extract JSON from response (handle markdown code blocks)
        if "```" in content:
            import re
            json_match = re.search(r'```(?:json)?\s*(.*?)```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1).strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print(f"  [WARN] Failed to parse short summaries JSON")
            return {}

    def generate_daily_report(self, repos: List[Dict], date_str: str, detailed_analysis: bool = True) -> str:
        """
        Generate a complete daily report with new beautiful format
        
        Args:
            repos: List of repository dictionaries
            date_str: Date string for the report
            detailed_analysis: Whether to include detailed analysis for top projects
        
        Returns:
            Complete markdown report with Docusaurus frontmatter
        """
        # 获取热点总结
        print("Generating trend analysis...")
        trend_analysis = self.analyze_trends(repos)
        
        # 解析热点总结
        hot_topic = ""
        key_observations = ""
        
        if "### 热点总结" in trend_analysis:
            parts = trend_analysis.split("### 热点总结")
            if len(parts) > 1:
                rest = parts[1]
                if "### 关键观察" in rest:
                    hot_parts = rest.split("### 关键观察")
                    hot_topic = hot_parts[0].strip()
                    key_observations = hot_parts[1].strip() if len(hot_parts) > 1 else ""
                else:
                    hot_topic = rest.strip()
        else:
            # 如果格式不匹配，直接使用返回内容
            hot_topic = trend_analysis.split("\n")[0] if trend_analysis else "今日GitHub热榜项目精彩纷呈。"
        
        # 分类统计
        categories = self._categorize_repos(repos)
        category_chart = self._build_category_chart(categories)
        
        # 构建报告
        report_parts = [
            "---",
            "sidebar_position: 1",
            f"title: {date_str} 日报",
            f"description: GitHub Trending 每日热门项目报告 - {date_str}",
            "---\n",
            f"## 今日热点\n",
            f"{hot_topic}\n",
            "---\n",
            "## 热门项目一览\n",
            self._build_repos_table(repos),
            "\n---\n",
            "## 趋势洞察\n",
            category_chart,
        ]
        
        # 添加关键观察
        if key_observations:
            report_parts.extend([
                "\n**关键观察**：",
                key_observations,
            ])
        
        report_parts.append("\n---\n")
        
        # 深度解读
        if detailed_analysis:
            report_parts.append("## 项目深度解读\n")
            
            # 按今日star数排序，全部项目都进行深度解读
            top_repos = sorted(repos, key=lambda x: x.get('stars_today', 0), reverse=True)
            
            for i, repo in enumerate(top_repos, 1):
                print(f"  Analyzing project {i}/{len(top_repos)}: {repo.get('full_name')}...")
                
                try:
                    detailed = self.analyze_single_repo_detailed(repo, i)
                    report_parts.append(detailed)
                    report_parts.append("\n")
                except Exception as e:
                    print(f"  [WARN] Error analyzing {repo.get('full_name')}: {e}")
                    # 生成简化版本
                    report_parts.append(self._generate_fallback_analysis(repo, i))
                    report_parts.append("\n---\n")
        
        # 今日推荐
        report_parts.append("## 今日推荐\n")
        try:
            print("Generating recommendations...")
            recommendations = self.generate_recommendations(repos)
            # 检查是否为空，如果为空则使用 fallback
            if recommendations and recommendations.strip():
                report_parts.append(recommendations)
            else:
                print("  Recommendations empty, using fallback...")
                report_parts.append(self._generate_fallback_recommendations(repos))
        except Exception as e:
            print(f"  Error generating recommendations: {e}")
            report_parts.append(self._generate_fallback_recommendations(repos))
        
        # Footer
        report_parts.extend([
            "\n---\n",
            '<div align="center">\n',
            f"*Generated on {date_str} | Powered by GitHub Trending Reporter*\n",
            "</div>"
        ])
        
        return "\n".join(report_parts)

    def _generate_fallback_analysis(self, repo: Dict, rank: int) -> str:
        """Generate a fallback analysis when LLM fails"""
        name = repo.get('full_name', 'Unknown')
        desc = repo.get('description', 'No description')
        language = repo.get('language', 'Unknown')
        stars = repo.get('stars', 0)
        stars_today = repo.get('stars_today', 0)
        url = repo.get('url', f'https://github.com/{name}')
        
        return f"""### {rank}. {name}

> **项目简介**：{desc}

#### 🎯 基本信息

| 维度 | 说明 |
|------|------|
| **语言** | {language} |
| **今日Star** | +{stars_today:,} |
| **总Star** | {stars:,} |

#### 🔗 链接

- GitHub: [{name}]({url})

---"""

    def _generate_fallback_recommendations(self, repos: List[Dict]) -> str:
        """Generate fallback recommendations when LLM fails"""
        top_repos = sorted(repos, key=lambda x: x.get('stars_today', 0), reverse=True)[:4]
        
        table_parts = [
            "| 主题 | 推荐项目 | 亮点 |",
            "|------|----------|------|"
        ]
        
        scenarios = ["今日最热", "值得关注", "快速上手", "长期潜力"]
        
        for i, repo in enumerate(top_repos):
            name = repo.get('full_name', 'Unknown')
            url = repo.get('url', f'https://github.com/{name}')
            desc = repo.get('description', 'No description') or 'No description'
            if len(desc) > 20:
                desc = desc[:17] + "..."
            
            table_parts.append(f"| {scenarios[i]} | [{name}]({url}) | {desc} |")
        
        return "\n".join(table_parts)


def analyze_trending(repos: List[Dict], analysis_type: str = "comprehensive") -> str:
    """Convenience function to analyze trending repositories"""
    analyzer = LLMAnalyzer()
    return analyzer.analyze_trends(repos)


if __name__ == "__main__":
    print("LLM Analyzer module - requires valid API key to test")
