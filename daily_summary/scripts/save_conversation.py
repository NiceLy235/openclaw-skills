#!/usr/bin/env python3
"""
Save conversation to memory.

Automatically saves conversations with timestamps and context.
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys


class ConversationSaver:
    """Save and manage conversations."""

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or os.path.expanduser("~/.openclaw/memory"))
        self.conversations_dir = self.base_dir / "conversations"
        self.conversations_dir.mkdir(parents=True, exist_ok=True)

    def save_message(
        self,
        user_message: str,
        assistant_message: str,
        context: Optional[Dict] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Save a conversation exchange.

        Args:
            user_message: User's message
            assistant_message: Assistant's response
            context: Optional context metadata
            tags: Optional tags for categorization

        Returns:
            Path to saved conversation
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M:%S")

        # Daily conversation file
        conv_file = self.conversations_dir / f"{date_str}.md"

        # Format conversation entry
        entry = self._format_entry(
            timestamp=timestamp,
            time_str=time_str,
            user_message=user_message,
            assistant_message=assistant_message,
            context=context,
            tags=tags
        )

        # Append to daily file
        with open(conv_file, 'a', encoding='utf-8') as f:
            f.write(entry)

        print(f"✅ Conversation saved to {conv_file}")
        return str(conv_file)

    def _format_entry(
        self,
        timestamp: datetime,
        time_str: str,
        user_message: str,
        assistant_message: str,
        context: Optional[Dict],
        tags: Optional[List[str]]
    ) -> str:
        """Format conversation entry as markdown."""

        lines = []

        # Timestamp
        lines.append(f"\n## {time_str}\n")

        # Tags
        if tags:
            lines.append(f"**Tags**: {', '.join(tags)}\n")

        # Context
        if context:
            lines.append("**Context**:")
            lines.append(f"```json")
            lines.append(json.dumps(context, indent=2))
            lines.append(f"```\n")

        # User message
        lines.append("**User**:")
        lines.append(f"```")
        lines.append(user_message)
        lines.append(f"```\n")

        # Assistant message
        lines.append("**Assistant**:")
        lines.append(assistant_message)
        lines.append("\n")

        # Separator
        lines.append("---\n")

        return '\n'.join(lines)

    def save_interaction(
        self,
        interaction_type: str,
        details: Dict,
        outcome: str,
        lessons_learned: Optional[str] = None
    ) -> str:
        """
        Save a significant interaction/operation.

        Args:
            interaction_type: Type of interaction (e.g., "training", "error_fix", "skill_creation")
            details: Details of the interaction
            outcome: Outcome/result
            lessons_learned: Optional lessons learned

        Returns:
            Path to saved interaction
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M:%S")

        # Interactions file
        interactions_file = self.conversations_dir / f"{date_str}-interactions.md"

        # Format interaction
        lines = [
            f"\n## {time_str} - {interaction_type}\n",
            "**Details**:",
            f"```json",
            json.dumps(details, indent=2),
            f"```\n",
            "**Outcome**:",
            f"{outcome}\n"
        ]

        if lessons_learned:
            lines.append("**Lessons Learned**:")
            lines.append(f"{lessons_learned}\n")

        lines.append("---\n")

        # Append to file
        with open(interactions_file, 'a', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"✅ Interaction saved to {interactions_file}")
        return str(interactions_file)


def main():
    parser = argparse.ArgumentParser(
        description="Save conversations and interactions to memory"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Save message
    msg_parser = subparsers.add_parser("message", help="Save conversation message")
    msg_parser.add_argument("--user", required=True, help="User message")
    msg_parser.add_argument("--assistant", required=True, help="Assistant message")
    msg_parser.add_argument("--context", help="Context JSON")
    msg_parser.add_argument("--tags", nargs="+", help="Tags")

    # Save interaction
    int_parser = subparsers.add_parser("interaction", help="Save interaction")
    int_parser.add_argument("--type", required=True, help="Interaction type")
    int_parser.add_argument("--details", required=True, help="Details JSON")
    int_parser.add_argument("--outcome", required=True, help="Outcome")
    int_parser.add_argument("--lessons", help="Lessons learned")

    # Quick log
    log_parser = subparsers.add_parser("log", help="Quick log entry")
    log_parser.add_argument("message", help="Log message")
    log_parser.add_argument("--type", default="note", help="Entry type")

    args = parser.parse_args()

    saver = ConversationSaver()

    if args.command == "message":
        context = json.loads(args.context) if args.context else None
        path = saver.save_message(
            user_message=args.user,
            assistant_message=args.assistant,
            context=context,
            tags=args.tags
        )
        print(f"Saved to: {path}")

    elif args.command == "interaction":
        details = json.loads(args.details)
        path = saver.save_interaction(
            interaction_type=args.type,
            details=details,
            outcome=args.outcome,
            lessons_learned=args.lessons
        )
        print(f"Saved to: {path}")

    elif args.command == "log":
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"\n## {timestamp} - {args.type}\n{args.message}\n---\n"

        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = saver.conversations_dir / f"{date_str}-log.md"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(entry)

        print(f"✅ Log saved to {log_file}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
