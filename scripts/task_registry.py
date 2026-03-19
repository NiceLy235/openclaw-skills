#!/usr/bin/env python3
"""
Task registry for long-running tasks.

Usage:
    # Register a task
    python task_registry.py register \
        --task-id "my_task_123" \
        --type "模型下载" \
        --description "正在下载 lerobot/smolvla_base"

    # Update task progress
    python task_registry.py update \
        --task-id "my_task_123" \
        --progress '{"current": "45%", "speed": "5MB/s"}'

    # Complete a task
    python task_registry.py complete \
        --task-id "my_task_123"

    # List all tasks
    python task_registry.py list
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


class TaskRegistry:
    """Registry for long-running tasks."""

    def __init__(self):
        self.registry_dir = Path.home() / ".openclaw" / "tasks"
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.registry_dir / "registry.json"

    def _load_registry(self) -> dict:
        """Load registry from file."""
        if not self.registry_file.exists():
            return {}

        with open(self.registry_file) as f:
            return json.load(f)

    def _save_registry(self, registry: dict):
        """Save registry to file."""
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)

    def register_task(self, task_id: str, task_type: str, description: str = ""):
        """Register a new task."""
        registry = self._load_registry()

        registry[task_id] = {
            "type": task_type,
            "description": description,
            "status": "running",
            "started": datetime.now().isoformat(),
            "progress": {}
        }

        self._save_registry(registry)
        print(f"✅ Task registered: {task_id}")

    def update_task(self, task_id: str, progress: dict):
        """Update task progress."""
        registry = self._load_registry()

        if task_id not in registry:
            print(f"❌ Task not found: {task_id}")
            return False

        registry[task_id]["progress"].update(progress)
        registry[task_id]["last_updated"] = datetime.now().isoformat()

        self._save_registry(registry)
        print(f"✅ Task updated: {task_id}")

    def complete_task(self, task_id: str, success: bool = True):
        """Mark task as completed."""
        registry = self._load_registry()

        if task_id not in registry:
            print(f"❌ Task not found: {task_id}")
            return False

        registry[task_id]["status"] = "completed" if success else "failed"
        registry[task_id]["completed"] = datetime.now().isoformat()

        self._save_registry(registry)
        print(f"✅ Task completed: {task_id}")

    def list_tasks(self, running_only: bool = False):
        """List all tasks."""
        registry = self._load_registry()

        if not registry:
            print("No tasks registered")
            return

        for task_id, task_info in registry.items():
            if running_only and task_info.get("status") != "running":
                continue

            print(f"\nTask ID: {task_id}")
            print(f"  Type: {task_info.get('type')}")
            print(f"  Status: {task_info.get('status')}")
            print(f"  Started: {task_info.get('started')}")
            if task_info.get('progress'):
                print(f"  Progress: {json.dumps(task_info['progress'])}")


def main():
    parser = argparse.ArgumentParser(description="Task registry")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Register command
    register_parser = subparsers.add_parser("register", help="Register a new task")
    register_parser.add_argument("--task-id", required=True, help="Task ID")
    register_parser.add_argument("--type", required=True, help="Task type")
    register_parser.add_argument("--description", default="", help="Task description")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update task progress")
    update_parser.add_argument("--task-id", required=True, help="Task ID")
    update_parser.add_argument("--progress", required=True, help="Progress JSON")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark task as completed")
    complete_parser.add_argument("--task-id", required=True, help="Task ID")
    complete_parser.add_argument("--success", type=bool, default=True, help="Success or failed")

    # List command
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument("--running-only", action="store_true", help="List only running tasks")

    args = parser.parse_args()

    registry = TaskRegistry()

    if args.command == "register":
        registry.register_task(args.task_id, args.type, args.description)
    elif args.command == "update":
        try:
            progress = json.loads(args.progress)
        except:
            progress = {"raw": args.progress}
        registry.update_task(args.task_id, progress)
    elif args.command == "complete":
        registry.complete_task(args.task_id, args.success)
    elif args.command == "list":
        registry.list_tasks(args.running_only)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
