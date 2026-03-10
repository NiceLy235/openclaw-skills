#!/usr/bin/env python3
"""
Generate daily summary from conversations and operations.

Analyzes the day's activities and creates structured summary.
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import re


class DailySummarizer:
    """Generate daily summaries."""

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or os.path.expanduser("~/.openclaw/memory"))
        self.conversations_dir = self.base_dir / "conversations"
        self.daily_dir = self.base_dir / "daily"
        self.experiences_dir = self.base_dir / "experiences"

        for d in [self.daily_dir, self.experiences_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def generate_summary(self, date: Optional[str] = None) -> Dict:
        """
        Generate daily summary.

        Args:
            date: Date to summarize (YYYY-MM-DD), defaults to today

        Returns:
            Summary data
        """
        target_date = date or datetime.now().strftime("%Y-%m-%d")

        print(f"📊 Generating summary for {target_date}...")

        # Collect data
        conversations = self._load_conversations(target_date)
        interactions = self._load_interactions(target_date)
        logs = self._load_logs(target_date)

        # Analyze
        summary = {
            "date": target_date,
            "generated_at": datetime.now().isoformat(),
            "statistics": {
                "total_conversations": len(conversations),
                "total_interactions": len(interactions),
                "total_logs": len(logs),
            },
            "activities": self._categorize_activities(interactions),
            "key_operations": self._extract_key_operations(interactions),
            "errors_encountered": self._extract_errors(interactions),
            "lessons_learned": self._extract_lessons(interactions),
            "topics_discussed": self._extract_topics(conversations),
        }

        # Save summary
        summary_file = self.daily_dir / f"{target_date}-summary.md"
        self._save_summary_markdown(summary, summary_file)

        # Generate experience document if there are lessons
        if summary["lessons_learned"]:
            exp_file = self.experiences_dir / f"{target_date}-experience.md"
            self._save_experience_markdown(summary, exp_file)

        return summary

    def _load_conversations(self, date: str) -> List[Dict]:
        """Load conversations for date."""
        conv_file = self.conversations_dir / f"{date}.md"
        if not conv_file.exists():
            return []

        with open(conv_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse conversations
        conversations = []
        pattern = r'## (\d{2}:\d{2}:\d{2})\n(.*?)(?=\n## |\Z)'
        matches = re.findall(pattern, content, re.DOTALL)

        for time_str, conv in matches:
            conversations.append({
                "time": time_str,
                "content": conv
            })

        return conversations

    def _load_interactions(self, date: str) -> List[Dict]:
        """Load interactions for date."""
        int_file = self.conversations_dir / f"{date}-interactions.md"
        if not int_file.exists():
            return []

        with open(int_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse interactions
        interactions = []
        pattern = r'## (\d{2}:\d{2}:\d{2}) - (.*?)\n(.*?)(?=\n## |\Z)'
        matches = re.findall(pattern, content, re.DOTALL)

        for time_str, int_type, details in matches:
            interactions.append({
                "time": time_str,
                "type": int_type,
                "content": details
            })

        return interactions

    def _load_logs(self, date: str) -> List[Dict]:
        """Load logs for date."""
        log_file = self.conversations_dir / f"{date}-log.md"
        if not log_file.exists():
            return []

        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse logs
        logs = []
        pattern = r'## (\d{2}:\d{2}:\d{2}) - (.*?)\n(.*?)(?=\n## |\Z)'
        matches = re.findall(pattern, content, re.DOTALL)

        for time_str, log_type, message in matches:
            logs.append({
                "time": time_str,
                "type": log_type,
                "message": message.strip()
            })

        return logs

    def _categorize_activities(self, interactions: List[Dict]) -> Dict[str, int]:
        """Categorize activities by type."""
        categories = {}

        for interaction in interactions:
            int_type = interaction.get("type", "other")
            categories[int_type] = categories.get(int_type, 0) + 1

        return categories

    def _extract_key_operations(self, interactions: List[Dict]) -> List[str]:
        """Extract key operations performed."""
        operations = []

        for interaction in interactions:
            if interaction.get("type") in ["training", "skill_creation", "error_fix", "deployment"]:
                # Extract first line as summary
                content = interaction.get("content", "")
                first_line = content.split('\n')[0][:100]
                operations.append(f"{interaction['time']} - {interaction['type']}: {first_line}")

        return operations

    def _extract_errors(self, interactions: List[Dict]) -> List[Dict]:
        """Extract errors encountered."""
        errors = []

        for interaction in interactions:
            if "error" in interaction.get("type", "").lower():
                errors.append({
                    "time": interaction["time"],
                    "type": interaction["type"],
                    "content": interaction["content"][:200]
                })

        return errors

    def _extract_lessons(self, interactions: List[Dict]) -> List[str]:
        """Extract lessons learned."""
        lessons = []

        for interaction in interactions:
            content = interaction.get("content", "")
            if "Lessons Learned" in content:
                # Extract lessons section
                lesson_match = re.search(r'\*\*Lessons Learned\*\*:\s*(.*?)(?:\n---|\Z)', content, re.DOTALL)
                if lesson_match:
                    lesson = lesson_match.group(1).strip()
                    lessons.append(lesson)

        return lessons

    def _extract_topics(self, conversations: List[Dict]) -> List[str]:
        """Extract main topics discussed."""
        topics = set()

        # Keywords to look for
        keywords = [
            "训练", "CUDA", "GPU", "skill", "环境", "配置",
            "错误", "修复", "安装", "部署", "测试"
        ]

        for conv in conversations:
            content = conv.get("content", "")
            for keyword in keywords:
                if keyword in content:
                    topics.add(keyword)

        return list(topics)

    def _save_summary_markdown(self, summary: Dict, output_file: Path) -> None:
        """Save summary as markdown."""
        lines = [
            f"# 每日总结 - {summary['date']}\n",
            f"**生成时间**: {summary['generated_at']}\n",
            "---\n",
            "## 📊 统计\n",
        ]

        stats = summary["statistics"]
        lines.append(f"- 对话次数: {stats['total_conversations']}")
        lines.append(f"- 交互操作: {stats['total_interactions']}")
        lines.append(f"- 日志条目: {stats['total_logs']}\n")

        if summary["activities"]:
            lines.append("## 🎯 活动分类\n")
            for activity, count in summary["activities"].items():
                lines.append(f"- {activity}: {count}")
            lines.append("")

        if summary["key_operations"]:
            lines.append("## 🔑 关键操作\n")
            for op in summary["key_operations"]:
                lines.append(f"- {op}")
            lines.append("")

        if summary["errors_encountered"]:
            lines.append("## ❌ 遇到的错误\n")
            for error in summary["errors_encountered"]:
                lines.append(f"- **{error['time']}** ({error['type']}): {error['content'][:100]}...")
            lines.append("")

        if summary["lessons_learned"]:
            lines.append("## 💡 经验教训\n")
            for i, lesson in enumerate(summary["lessons_learned"], 1):
                lines.append(f"{i}. {lesson}")
            lines.append("")

        if summary["topics_discussed"]:
            lines.append("## 📝 讨论主题\n")
            lines.append(f"{', '.join(summary['topics_discussed'])}\n")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"✅ Summary saved to {output_file}")

    def _save_experience_markdown(self, summary: Dict, output_file: Path) -> None:
        """Save experience document."""
        lines = [
            f"# 经验文档 - {summary['date']}\n",
            f"**生成时间**: {summary['generated_at']}\n",
            "---\n",
            "## 💡 经验教训\n",
        ]

        for i, lesson in enumerate(summary["lessons_learned"], 1):
            lines.append(f"\n### 经验 {i}\n")
            lines.append(lesson)
            lines.append("")

        if summary["errors_encountered"]:
            lines.append("\n## 🔍 相关错误\n")
            for error in summary["errors_encountered"]:
                lines.append(f"- {error['type']}: {error['content'][:100]}...")
            lines.append("")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"✅ Experience saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate daily summary"
    )

    parser.add_argument(
        "--date",
        help="Date to summarize (YYYY-MM-DD), defaults to today"
    )
    parser.add_argument(
        "--base-dir",
        help="Base directory for memory storage"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    summarizer = DailySummarizer(base_dir=args.base_dir)
    summary = summarizer.generate_summary(date=args.date)

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f"\n✅ Summary generated for {summary['date']}")


if __name__ == "__main__":
    main()
