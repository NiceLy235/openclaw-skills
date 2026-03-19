#!/usr/bin/env python3
"""
Universal progress monitor for all long-running tasks.

Monitors:
- LeRobot training tasks
- Long-running commands (pip install, git clone, etc.)
- Background processes
- Any task registered in ~/.openclaw/tasks/

Sends progress updates every 5 minutes to Feishu.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class UniversalProgressMonitor:
    """Monitor all long-running tasks and send progress updates."""

    def __init__(self):
        self.tasks_dir = Path.home() / ".openclaw" / "tasks"
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

    def check_all_tasks(self) -> List[Dict[str, Any]]:
        """Check all running tasks and return progress info."""
        all_tasks = []

        # Check LeRobot training tasks
        all_tasks.extend(self._check_lerobot_tasks())

        # Check long-running processes
        all_tasks.extend(self._check_long_running_processes())

        # Check registered tasks
        all_tasks.extend(self._check_registered_tasks())

        return all_tasks

    def _check_lerobot_tasks(self) -> List[Dict[str, Any]]:
        """Check LeRobot training tasks."""
        tasks = []

        if not self.tasks_dir.exists():
            return tasks

        for task_dir in self.tasks_dir.iterdir():
            if not task_dir.is_dir():
                continue

            meta_file = task_dir / "meta.json"
            if not meta_file.exists():
                continue

            try:
                with open(meta_file) as f:
                    meta = json.load(f)

                if meta.get("status") not in ["training", "preparing_data", "running"]:
                    continue

                task_id = meta.get("task_id")
                log_file = Path(meta.get("log_file", ""))
                started = meta.get("timestamps", {}).get("started")

                # Parse progress
                progress = self._parse_lerobot_progress(log_file)

                # Calculate elapsed time
                elapsed_str = "未知"
                if started:
                    start_time = datetime.fromisoformat(started)
                    elapsed = datetime.now() - start_time
                    elapsed_str = self._format_duration(elapsed)

                tasks.append({
                    "type": "LeRobot 训练",
                    "task_id": task_id,
                    "status": meta.get("status"),
                    "elapsed": elapsed_str,
                    "progress": progress
                })

            except Exception as e:
                pass

        return tasks

    def _check_long_running_processes(self) -> List[Dict[str, Any]]:
        """Check long-running system processes."""
        tasks = []

        try:
            # Check for common long-running commands
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return tasks

            lines = result.stdout.strip().split('\n')

            for line in lines[1:]:  # Skip header
                parts = line.split(None, 10)
                if len(parts) < 11:
                    continue

                command = parts[10]
                pid = parts[1]
                elapsed = parts[9]

                # Check for long-running training/install commands
                keywords = [
                    "python.*lerobot",
                    "pip install",
                    "conda install",
                    "git clone",
                    "wget",
                    "curl.*download",
                    "python.*train"
                ]

                import re
                for keyword in keywords:
                    if re.search(keyword, command, re.IGNORECASE):
                        # Parse elapsed time (format: MM:SS or HH:MM:SS)
                        elapsed_minutes = self._parse_elapsed_time(elapsed)

                        # Only report if > 5 minutes
                        if elapsed_minutes >= 5:
                            tasks.append({
                                "type": "后台进程",
                                "task_id": f"PID:{pid}",
                                "status": "运行中",
                                "elapsed": f"{elapsed_minutes}分钟",
                                "progress": {
                                    "command": command[:50] + "..." if len(command) > 50 else command
                                }
                            })
                        break

        except Exception as e:
            pass

        return tasks

    def _check_registered_tasks(self) -> List[Dict[str, Any]]:
        """Check tasks registered in ~/.openclaw/tasks/registry.json"""
        tasks = []
        registry_file = self.tasks_dir / "registry.json"

        if not registry_file.exists():
            return tasks

        try:
            with open(registry_file) as f:
                registry = json.load(f)

            for task_id, task_info in registry.items():
                if task_info.get("status") != "running":
                    continue

                started = task_info.get("started")
                if started:
                    start_time = datetime.fromisoformat(started)
                    elapsed = datetime.now() - start_time
                    elapsed_str = self._format_duration(elapsed)

                    tasks.append({
                        "type": task_info.get("type", "自定义任务"),
                        "task_id": task_id,
                        "status": "运行中",
                        "elapsed": elapsed_str,
                        "progress": task_info.get("progress", {})
                    })

        except Exception as e:
            pass

        return tasks

    def _parse_lerobot_progress(self, log_file: Path) -> dict:
        """Parse LeRobot training progress from log file."""
        progress = {"current_step": None, "loss": None, "lr": None}

        if not log_file.exists():
            return progress

        try:
            with open(log_file) as f:
                lines = f.readlines()[-100:]

                for line in reversed(lines):
                    if "step:" in line:
                        parts = line.split()
                        for part in parts:
                            if part.startswith("step:"):
                                progress["current_step"] = int(part.split(":")[1])
                            elif part.startswith("loss:"):
                                progress["loss"] = float(part.split(":")[1])
                            elif part.startswith("lr:"):
                                progress["lr"] = part.split(":")[1]
                        break

        except Exception as e:
            pass

        return progress

    def _parse_elapsed_time(self, elapsed: str) -> int:
        """Parse elapsed time (MM:SS or HH:MM:SS) to minutes."""
        try:
            parts = elapsed.split(':')
            if len(parts) == 2:
                return int(parts[0])
            elif len(parts) == 3:
                return int(parts[0]) * 60 + int(parts[1])
            return 0
        except:
            return 0

    def _format_duration(self, duration) -> str:
        """Format duration as human-readable string."""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        elif minutes > 0:
            return f"{minutes}分钟"
        else:
            return f"{total_seconds % 60}秒"

    def generate_progress_report(self) -> str:
        """Generate progress report for all running tasks."""
        tasks = self.check_all_tasks()

        if not tasks:
            return ""

        lines = [
            f"📊 任务进度更新 ({datetime.now().strftime('%H:%M:%S')})",
            "━" * 40,
            ""
        ]

        for idx, task in enumerate(tasks, 1):
            lines.append(f"[{idx}] {task['type']}")
            lines.append(f"    任务 ID: {task['task_id']}")
            lines.append(f"    状态: {task['status']}")
            lines.append(f"    已用时间: {task['elapsed']}")

            progress = task.get('progress', {})
            if task['type'] == "LeRobot 训练":
                if progress.get('current_step'):
                    lines.append(f"    Step: {progress['current_step']}")
                if progress.get('loss'):
                    lines.append(f"    Loss: {progress['loss']:.4f}")
            elif task['type'] == "后台进程":
                if progress.get('command'):
                    lines.append(f"    命令: {progress['command']}")

            lines.append("")

        lines.append("━" * 40)
        lines.append(f"共 {len(tasks)} 个任务正在运行")

        return "\n".join(lines)


def main():
    """Main function - check tasks and output progress report."""
    monitor = UniversalProgressMonitor()
    report = monitor.generate_progress_report()

    if report:
        print(report)
    else:
        print("无正在运行的任务")


if __name__ == "__main__":
    main()
