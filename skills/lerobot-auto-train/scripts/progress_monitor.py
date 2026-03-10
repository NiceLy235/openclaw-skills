#!/usr/bin/env python3
"""
Progress monitor for training tasks.

Provides real-time monitoring with:
- Live progress updates
- Resource utilization tracking
- Log streaming
- Alert on completion/failure
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class ProgressMonitor:
    """Monitor training task progress in real-time."""

    def __init__(self, task_id: str, tasks_dir: Path):
        self.task_id = task_id
        self.tasks_dir = tasks_dir
        self.task_file = tasks_dir / task_id / "meta.json"
        self.last_update = None

    def get_current_status(self) -> Optional[Dict]:
        """Get current task status."""
        if not self.task_file.exists():
            return None

        with open(self.task_file, 'r') as f:
            return json.load(f)

    def watch(
        self,
        interval: int = 5,
        verbose: bool = True,
        alert_on_complete: bool = True
    ) -> None:
        """
        Watch task progress with periodic updates.

        Args:
            interval: Update interval in seconds
            verbose: Print detailed progress
            alert_on_complete: Alert when task completes
        """
        print(f"👀 Watching task: {self.task_id}")
        print(f"Press Ctrl+C to stop\n")

        try:
            while True:
                status = self.get_current_status()

                if not status:
                    print(f"❌ Task not found: {self.task_id}")
                    break

                # Check if status changed
                if status != self.last_update:
                    self._print_status(status, verbose)
                    self.last_update = status

                    # Check for completion
                    if status["status"] in ["completed", "failed", "stopped"]:
                        if alert_on_complete:
                            print(f"\n🔔 Task {status['status']}!")

                        if status["status"] == "completed":
                            self._print_summary(status)
                        elif status["status"] == "failed":
                            print(f"\n❌ Error: {status.get('error', {}).get('message', 'Unknown')}")

                        break

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped")

    def _print_status(self, status: Dict, verbose: bool) -> None:
        """Print current status."""
        task_status = status["status"]
        progress = status["progress"]

        # Status icon
        icon = {
            "pending": "⏳",
            "preparing_data": "📦",
            "initializing": "🔧",
            "training": "🚀",
            "validating": "📊",
            "exporting": "💾",
            "completed": "✅",
            "failed": "❌",
            "stopped": "⏹️ ",
            "paused": "⏸️ "
        }.get(task_status, "❓")

        # Progress bar (if training)
        if task_status == "training" and progress["total_epochs"] > 0:
            percent = progress["current_epoch"] / progress["total_epochs"] * 100
            bar_length = 30
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)

            print(
                f"\r{icon} [{bar}] {percent:.1f}% "
                f"Epoch {progress['current_epoch']}/{progress['total_epochs']} "
                f"| Loss: {progress['train_loss'] or 0:.4f}",
                end='', flush=True
            )
        else:
            # Just status
            print(f"\r{icon} Status: {task_status}...", end='', flush=True)

        if verbose and task_status == "training":
            self._print_resource(status["resource"])

    def _print_resource(self, resource: Dict) -> None:
        """Print resource utilization."""
        gpu_util = resource.get("gpu_utilization", "N/A")
        gpu_mem = resource.get("gpu_memory_used", "N/A")

        if gpu_util != "N/A":
            print(f" | GPU: {gpu_util}, {gpu_mem}", end='')

    def _print_summary(self, status: Dict) -> None:
        """Print training summary."""
        config = status["config"]
        progress = status["progress"]
        timestamps = status["timestamps"]

        print("\n\n" + "="*60)
        print("TRAINING SUMMARY")
        print("="*60)

        print(f"\nTask ID: {status['task_id']}")
        print(f"Model: {config['model_name']}")
        print(f"Dataset: {', '.join(config['data_sources'])}")

        print(f"\nTraining Results:")
        print(f"  - Total Epochs: {progress['total_epochs']}")
        print(f"  - Best Val Loss: {progress['best_val_loss']:.4f}")
        print(f"  - Final Train Loss: {progress['train_loss']:.4f}")

        print(f"\nTime:")
        print(f"  - Started: {timestamps['started']}")
        print(f"  - Completed: {timestamps['completed']}")
        print(f"  - Duration: {progress['elapsed_time']}")

        print(f"\nOutput:")
        print(f"  - Model: {config['output_dir']}/model.pt")
        print(f"  - Logs: {status['log_file']}")

        print("\n" + "="*60)

    def get_progress_json(self) -> str:
        """Get progress as JSON (for programmatic access)."""
        status = self.get_current_status()

        if not status:
            return json.dumps({"error": "Task not found"})

        # Extract just the progress info
        progress_info = {
            "task_id": status["task_id"],
            "status": status["status"],
            "progress": status["progress"],
            "resource": status["resource"],
            "timestamp": datetime.now().isoformat()
        }

        return json.dumps(progress_info, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Monitor training task progress"
    )

    parser.add_argument("task_id", help="Task ID to monitor")
    parser.add_argument(
        "--tasks-dir",
        default="~/.openclaw/tasks",
        help="Tasks directory"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Update interval in seconds (default: 5)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output (just progress bar)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (one-shot, no continuous monitoring)"
    )
    parser.add_argument(
        "--no-alert",
        action="store_true",
        help="Don't alert on completion"
    )

    args = parser.parse_args()

    tasks_dir = Path(args.tasks_dir).expanduser()
    monitor = ProgressMonitor(args.task_id, tasks_dir)

    if args.json:
        # Just print current status as JSON
        print(monitor.get_progress_json())
    else:
        # Continuous monitoring
        monitor.watch(
            interval=args.interval,
            verbose=not args.quiet,
            alert_on_complete=not args.no_alert
        )


if __name__ == "__main__":
    main()
