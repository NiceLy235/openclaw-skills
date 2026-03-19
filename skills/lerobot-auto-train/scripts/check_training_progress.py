#!/usr/bin/env python3
"""
Check training progress and send updates to Feishu.

This script is called by OpenClaw cron job every 5 minutes.
It checks all running training tasks and sends progress updates to Feishu.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def check_training_progress():
    """Check all running training tasks and return progress info."""
    tasks_dir = Path.home() / ".openclaw" / "tasks"

    if not tasks_dir.exists():
        print("No tasks directory found")
        return []

    running_tasks = []

    for task_dir in tasks_dir.iterdir():
        if not task_dir.is_dir():
            continue

        meta_file = task_dir / "meta.json"
        if not meta_file.exists():
            continue

        try:
            with open(meta_file) as f:
                meta = json.load(f)

            # Only check running tasks
            if meta.get("status") not in ["training", "preparing_data"]:
                continue

            task_id = meta.get("task_id")
            log_file = Path(meta.get("log_file", ""))

            # Parse progress from log
            progress = parse_progress_from_log(log_file)

            # Calculate elapsed time
            started = meta.get("timestamps", {}).get("started")
            if started:
                start_time = datetime.fromisoformat(started)
                elapsed = datetime.now() - start_time
                elapsed_str = format_duration(elapsed)
            else:
                elapsed_str = "未知"

            running_tasks.append({
                "task_id": task_id,
                "status": meta.get("status"),
                "elapsed": elapsed_str,
                "progress": progress
            })

        except Exception as e:
            print(f"Error processing task {task_dir.name}: {e}")

    return running_tasks


def parse_progress_from_log(log_file: Path) -> dict:
    """Parse training progress from log file."""
    progress = {
        "current_step": None,
        "total_steps": None,
        "loss": None,
        "lr": None
    }

    if not log_file.exists():
        return progress

    try:
        with open(log_file) as f:
            # Read last 100 lines
            lines = f.readlines()[-100:]

            # Parse step/loss/lr from lerobot output
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
        print(f"Error parsing log: {e}")

    return progress


def format_duration(duration) -> str:
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


def main():
    """Main function - check training progress and print summary."""
    tasks = check_training_progress()

    if not tasks:
        print("No running training tasks")
        return

    # Print progress summary
    print(f"\n📊 训练进度更新 ({datetime.now().strftime('%H:%M:%S')})")
    print("=" * 60)

    for task in tasks:
        print(f"\n任务 ID: {task['task_id']}")
        print(f"状态: {task['status']}")
        print(f"已用时间: {task['elapsed']}")

        progress = task['progress']
        if progress.get('current_step'):
            print(f"Step: {progress['current_step']}")
        if progress.get('loss'):
            print(f"Loss: {progress['loss']:.4f}")
        if progress.get('lr'):
            print(f"LR: {progress['lr']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
