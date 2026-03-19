#!/usr/bin/env python3
"""
Progress reporter for long-running training tasks.

Sends progress updates every 5 minutes via OpenClaw message tool.
Usage:
    python progress_reporter.py --task-id <task_id> --log-file <log_file> --channel feishu
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any


class ProgressReporter:
    """Monitor training progress and send updates every 5 minutes."""

    def __init__(self, task_id: str, log_file: str, channel: str = "feishu"):
        self.task_id = task_id
        self.log_file = Path(log_file)
        self.channel = channel
        self.running = False
        self.start_time = datetime.now()
        self.last_report_time = None
        self.report_interval = 300  # 5 minutes in seconds

    def start(self):
        """Start monitoring and reporting loop."""
        self.running = True
        print(f"🔍 Progress reporter started for task {self.task_id}")
        print(f"📄 Log file: {self.log_file}")
        print(f"⏰ Report interval: {self.report_interval}s (5 minutes)")

        while self.running:
            time.sleep(self.report_interval)

            if not self.running:
                break

            # Send progress update
            self._send_progress_update()

    def stop(self):
        """Stop monitoring loop."""
        self.running = False
        print("🛑 Progress reporter stopped")

    def _send_progress_update(self):
        """Send progress update via message tool."""
        try:
            # Parse progress from log
            progress = self._parse_progress()

            # Build progress message
            elapsed = datetime.now() - self.start_time
            elapsed_str = self._format_duration(elapsed)

            # Estimated remaining time (if we have progress info)
            remaining_str = "未知"
            if progress.get("current_step") and progress.get("total_steps"):
                if progress["current_step"] > 0:
                    elapsed_steps = progress["current_step"]
                    remaining_steps = progress["total_steps"] - elapsed_steps
                    avg_time_per_step = elapsed.total_seconds() / elapsed_steps
                    remaining_seconds = remaining_steps * avg_time_per_step
                    remaining_str = self._format_duration(timedelta(seconds=remaining_seconds))

            # Build message
            message = f"""📊 进度更新 (5 分钟汇报)
━━━━━━━━━━━━━━━━━━━━━━━━
• 任务 ID: {self.task_id}
• 当前步骤: {progress.get('step', '训练中')}
• 已用时间: {elapsed_str}
• 预计剩余: {remaining_str}
• 状态: {progress.get('status', '⏳ 运行中')}
━━━━━━━━━━━━━━━━━━━━━━━━"""

            if progress.get("current_step"):
                message += f"\n• Step: {progress['current_step']}/{progress.get('total_steps', '?')}"
            if progress.get("loss"):
                message += f"\n• Loss: {progress['loss']}"
            if progress.get("lr"):
                message += f"\n• LR: {progress['lr']}"

            # Send message using OpenClaw message tool
            self._send_message(message)

            print(f"✅ Progress update sent at {datetime.now().strftime('%H:%M:%S')}")

        except Exception as e:
            print(f"❌ Failed to send progress update: {e}")

    def _parse_progress(self) -> Dict[str, Any]:
        """Parse training progress from log file."""
        progress = {
            "step": "训练中",
            "status": "⏳ 运行中",
            "current_step": None,
            "total_steps": None,
            "loss": None,
            "lr": None
        }

        if not self.log_file.exists():
            return progress

        try:
            with open(self.log_file, 'r') as f:
                # Read last 100 lines
                lines = f.readlines()[-100:]

                # Parse step/loss/lr from lerobot output
                # Format: INFO ... step:200 smpl:6K ep:8 epch:0.65 loss:0.068 grdn:0.749 lr:1.0e-05
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

                # Check for errors
                if "error" in "".join(lines[-10:]).lower():
                    progress["status"] = "❌ 遇到错误"
                elif "completed" in "".join(lines[-10:]).lower():
                    progress["status"] = "✅ 已完成"

        except Exception as e:
            print(f"⚠️  Failed to parse log: {e}")

        return progress

    def _send_message(self, message: str):
        """Send message via OpenClaw message tool."""
        try:
            # Use subprocess to call OpenClaw message CLI
            # Format: openclaw message send --channel feishu -m "message"
            result = subprocess.run(
                [
                    "openclaw",
                    "message",
                    "send",
                    "--channel", self.channel,
                    "-m", message
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                # Fallback: write to a file that OpenClaw can read
                print(f"⚠️  Failed to send via openclaw CLI (code {result.returncode})")
                print(f"   stderr: {result.stderr}")
                self._write_message_to_file(message)
            else:
                print(f"📤 Message sent via openclaw CLI")

        except FileNotFoundError:
            # openclaw CLI not found, write to file
            print(f"⚠️  openclaw CLI not found, writing to file")
            self._write_message_to_file(message)
        except subprocess.TimeoutExpired:
            print(f"⚠️  openclaw CLI timeout, writing to file")
            self._write_message_to_file(message)
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            self._write_message_to_file(message)

    def _write_message_to_file(self, message: str):
        """Write message to a file as fallback."""
        message_file = self.log_file.parent / f"progress_{self.task_id}.txt"
        with open(message_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[{datetime.now().isoformat()}]\n")
            f.write(message)
            f.write(f"\n{'='*60}\n")

    def _format_duration(self, duration: timedelta) -> str:
        """Format duration as human-readable string."""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        elif minutes > 0:
            return f"{minutes}分钟"
        else:
            return f"{seconds}秒"


def main():
    parser = argparse.ArgumentParser(description="Progress reporter for training tasks")
    parser.add_argument("--task-id", required=True, help="Task ID")
    parser.add_argument("--log-file", required=True, help="Log file path")
    parser.add_argument("--channel", default="feishu", help="Message channel (default: feishu)")
    parser.add_argument("--interval", type=int, default=300, help="Report interval in seconds (default: 300)")

    args = parser.parse_args()

    reporter = ProgressReporter(
        task_id=args.task_id,
        log_file=args.log_file,
        channel=args.channel
    )
    reporter.report_interval = args.interval

    try:
        reporter.start()
    except KeyboardInterrupt:
        reporter.stop()
        print("\n👋 Reporter stopped by user")


if __name__ == "__main__":
    main()
