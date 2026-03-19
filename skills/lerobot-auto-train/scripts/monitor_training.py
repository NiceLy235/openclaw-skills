#!/usr/bin/env python3
"""
Check training progress and output message for OpenClaw to send.

This script is designed to be called by OpenClaw cron job.
It outputs a progress message if there are running training tasks.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def main():
    tasks_dir = Path.home() / ".openclaw" / "tasks"

    if not tasks_dir.exists():
        return

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

            if meta.get("status") not in ["training", "preparing_data"]:
                continue

            task_id = meta.get("task_id")
            log_file = Path(meta.get("log_file", ""))
            started = meta.get("timestamps", {}).get("started")

            # Parse progress
            progress = {"current_step": None, "loss": None, "lr": None}
            if log_file.exists():
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
                            break

            # Calculate elapsed time
            elapsed_str = "未知"
            if started:
                start_time = datetime.fromisoformat(started)
                elapsed = datetime.now() - start_time
                total_seconds = int(elapsed.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                if hours > 0:
                    elapsed_str = f"{hours}小时{minutes}分钟"
                else:
                    elapsed_str = f"{minutes}分钟"

            running_tasks.append({
                "task_id": task_id,
                "status": meta.get("status"),
                "elapsed": elapsed_str,
                "progress": progress
            })

        except Exception as e:
            pass

    # Output progress message if there are running tasks
    if running_tasks:
        message_lines = [
            f"📊 训练进度更新 ({datetime.now().strftime('%H:%M:%S')})",
            "━" * 40,
            ""
        ]

        for task in running_tasks:
            message_lines.append(f"• 任务 ID: {task['task_id']}")
            message_lines.append(f"• 状态: {task['status']}")
            message_lines.append(f"• 已用时间: {task['elapsed']}")

            progress = task['progress']
            if progress.get('current_step'):
                message_lines.append(f"• Step: {progress['current_step']}")
            if progress.get('loss'):
                message_lines.append(f"• Loss: {progress['loss']:.4f}")
            message_lines.append("")

        message_lines.append("━" * 40)

        # Print message for OpenClaw to send
        print("\n".join(message_lines))


if __name__ == "__main__":
    main()
