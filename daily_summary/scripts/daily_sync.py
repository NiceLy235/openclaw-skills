#!/usr/bin/env python3
"""
Daily memory sync - Main orchestrator.

Orchestrates:
1. Generate daily summary
2. Extract experiences
3. Push to GitHub

Can be run manually or via cron/heartbeat.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class DailyMemorySync:
    """Orchestrate daily memory sync."""

    def __init__(self):
        self.base_dir = Path.home() / ".openclaw"
        self.memory_dir = self.base_dir / "memory"
        self.scripts_dir = self.base_dir / "workspace" / "daily_summary" / "scripts"

    def run_daily_sync(self, date: Optional[str] = None, push: bool = True) -> None:
        """
        Run complete daily sync process.

        Args:
            date: Date to sync (YYYY-MM-DD), defaults to today
            push: Whether to push to GitHub
        """
        target_date = date or datetime.now().strftime("%Y-%m-%d")

        print("="*60)
        print(f"🚀 Daily Memory Sync - {target_date}")
        print("="*60)

        # Step 1: Generate summary
        print("\n📊 Step 1/3: Generating daily summary...")
        self._run_summarize(target_date)

        # Step 2: (Future) Analyze patterns
        print("\n🔍 Step 2/3: Analyzing patterns...")
        # TODO: Add pattern analysis

        # Step 3: Push to GitHub
        if push:
            print("\n📤 Step 3/3: Pushing to GitHub...")
            self._run_push(target_date)
        else:
            print("\n⏭️  Step 3/3: Skipping GitHub push (--no-push)")

        print("\n" + "="*60)
        print("✅ Daily memory sync completed!")
        print("="*60)

    def _run_summarize(self, date: str) -> None:
        """Run summarize_day.py"""
        script = self.scripts_dir / "summarize_day.py"

        if not script.exists():
            print(f"❌ Script not found: {script}")
            return

        try:
            result = subprocess.run(
                [sys.executable, str(script), "--date", date],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Summary generation failed:")
            print(e.stderr)

    def _run_push(self, date: str) -> None:
        """Run push_to_github.sh"""
        script = self.scripts_dir / "push_to_github.sh"

        if not script.exists():
            print(f"❌ Script not found: {script}")
            return

        try:
            result = subprocess.run(
                [str(script), "--date", date],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ GitHub push failed:")
            print(e.stderr)


def setup_github_repo(repo_url: str) -> None:
    """
    Set up GitHub repository for memory storage.

    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/user/repo.git)
    """
    memory_dir = Path.home() / ".openclaw" / "memory"

    print(f"📦 Setting up memory repository...")
    print(f"   Directory: {memory_dir}")
    print(f"   Remote: {repo_url}")

    # Create directory
    memory_dir.mkdir(parents=True, exist_ok=True)

    # Initialize git
    if not (memory_dir / ".git").exists():
        subprocess.run(["git", "init"], cwd=memory_dir, check=True)
        print("✅ Git initialized")

    # Add remote
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=memory_dir,
        capture_output=True
    )

    if result.returncode != 0:
        subprocess.run(
            ["git", "remote", "add", "origin", repo_url],
            cwd=memory_dir,
            check=True
        )
        print("✅ Remote added")
    else:
        print("✅ Remote already exists")

    # Create .gitignore
    gitignore = memory_dir / ".gitignore"
    with open(gitignore, 'w') as f:
        f.write("# Temporary files\n*.tmp\n*.log\n")
    print("✅ .gitignore created")

    # Create README
    readme = memory_dir / "README.md"
    if not readme.exists():
        with open(readme, 'w') as f:
            f.write("# OpenClaw Memory\n\n")
            f.write("This repository stores OpenClaw's daily memories and experiences.\n\n")
            f.write("## Structure\n\n")
            f.write("- `conversations/` - Daily conversation logs\n")
            f.write("- `daily/` - Daily summaries\n")
            f.write("- `experiences/` - Lessons learned\n")
            f.write("- `errors/` - Error logs\n")
        print("✅ README.md created")

    # Initial commit
    subprocess.run(["git", "add", "-A"], cwd=memory_dir, check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: Initialize memory repository"],
        cwd=memory_dir,
        check=True
    )
    print("✅ Initial commit created")

    print("\n✅ Repository setup complete!")
    print("\nNext steps:")
    print("1. Push to GitHub:")
    print(f"   cd {memory_dir}")
    print("   git push -u origin main")
    print("\n2. Or run daily sync:")
    print("   python daily_sync.py")


def main():
    parser = argparse.ArgumentParser(
        description="Daily memory sync orchestrator"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Run sync
    sync_parser = subparsers.add_parser("run", help="Run daily sync")
    sync_parser.add_argument("--date", help="Date to sync (YYYY-MM-DD)")
    sync_parser.add_argument("--no-push", action="store_true", help="Skip GitHub push")

    # Setup
    setup_parser = subparsers.add_parser("setup", help="Setup GitHub repository")
    setup_parser.add_argument("--repo-url", required=True, help="GitHub repository URL")

    # Status
    status_parser = subparsers.add_parser("status", help="Check sync status")

    args = parser.parse_args()

    if args.command == "run":
        syncer = DailyMemorySync()
        syncer.run_daily_sync(date=args.date, push=not args.no_push)

    elif args.command == "setup":
        setup_github_repo(args.repo_url)

    elif args.command == "status":
        memory_dir = Path.home() / ".openclaw" / "memory"

        print("📁 Memory Directory Status")
        print("="*60)
        print(f"Location: {memory_dir}")

        if memory_dir.exists():
            # Check if git repo
            if (memory_dir / ".git").exists():
                print("✅ Git repository initialized")

                # Check remote
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=memory_dir,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✅ Remote: {result.stdout.strip()}")
                else:
                    print("⚠️  No remote configured")

                # Check last commit
                result = subprocess.run(
                    ["git", "log", "-1", "--format=%cd"],
                    cwd=memory_dir,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"📅 Last commit: {result.stdout.strip()}")
            else:
                print("⚠️  Not a git repository")

            # Count files
            conv_count = len(list((memory_dir / "conversations").glob("*.md")))
            summary_count = len(list((memory_dir / "daily").glob("*-summary.md")))
            exp_count = len(list((memory_dir / "experiences").glob("*.md")))

            print(f"\n📊 Content:")
            print(f"  - Conversations: {conv_count}")
            print(f"  - Summaries: {summary_count}")
            print(f"  - Experiences: {exp_count}")
        else:
            print("❌ Memory directory does not exist")
            print("\nTo set up, run:")
            print("  python daily_sync.py setup --repo-url <your-repo-url>")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
