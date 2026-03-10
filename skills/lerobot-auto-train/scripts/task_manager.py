#!/usr/bin/env python3
"""
Task manager for background training jobs.

Provides:
- Task submission and queue management
- Background execution with progress monitoring
- Task persistence and recovery
- Status queries and control
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
import time


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    PREPARING_DATA = "preparing_data"
    INITIALIZING = "initializing"
    TRAINING = "training"
    VALIDATING = "validating"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"
    PAUSED = "paused"


class TaskManager:
    """Manage training task lifecycle."""

    def __init__(self, tasks_dir: Optional[str] = None):
        self.tasks_dir = Path(tasks_dir or os.path.expanduser("~/.openclaw/tasks"))
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.active_processes: Dict[str, subprocess.Popen] = {}

    def submit_task(
        self,
        task_type: str,
        data_sources: List[str],
        model_name: str,
        output_dir: str = "./output",
        epochs: int = 100,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        device: str = "cuda",
        background: bool = True,
        progress_interval: int = 60,
        priority: int = 5,
        notify_on_complete: bool = False,
        **kwargs
    ) -> Dict:
        """
        Submit a new training task.

        Returns:
            Task metadata with task_id
        """
        # Generate unique task ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_id = f"train_{timestamp}_{uuid.uuid4().hex[:8]}"

        # Create task metadata
        task_meta = {
            "task_id": task_id,
            "task_type": task_type,
            "status": TaskStatus.PENDING.value,
            "priority": priority,
            "config": {
                "data_sources": data_sources,
                "model_name": model_name,
                "output_dir": output_dir,
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "device": device,
                **kwargs
            },
            "execution": {
                "background": background,
                "progress_interval": progress_interval,
                "notify_on_complete": notify_on_complete
            },
            "progress": {
                "current_epoch": 0,
                "total_epochs": epochs,
                "train_loss": None,
                "val_loss": None,
                "best_val_loss": None,
                "elapsed_time": "0m",
                "estimated_remaining": "calculating..."
            },
            "resource": {
                "gpu_utilization": "N/A",
                "gpu_memory_used": "N/A",
                "cpu_usage": "N/A"
            },
            "timestamps": {
                "submitted": datetime.now().isoformat(),
                "started": None,
                "completed": None
            },
            "pid": None,
            "log_file": None,
            "checkpoint_dir": None
        }

        # Save task metadata
        task_file = self.tasks_dir / task_id / "meta.json"
        task_file.parent.mkdir(parents=True, exist_ok=True)

        with open(task_file, 'w') as f:
            json.dump(task_meta, f, indent=2)

        print(f"✅ Task submitted: {task_id}")

        # Start execution
        if background:
            self._start_background_task(task_id, task_meta)
        else:
            self._start_sync_task(task_id, task_meta)

        return task_meta

    def _start_background_task(self, task_id: str, task_meta: Dict) -> None:
        """Start task in background process."""
        # Create log file
        log_file = self.tasks_dir / task_id / f"training_{task_id}.log"
        task_meta["log_file"] = str(log_file)

        # Launch worker process
        cmd = [
            sys.executable,
            str(Path(__file__).parent / "train_worker.py"),
            "--task-id", task_id,
            "--tasks-dir", str(self.tasks_dir)
        ]

        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                cmd,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True  # Detach from parent
            )

        # Update metadata with PID
        task_meta["pid"] = process.pid
        self._update_task_meta(task_id, task_meta)

        self.active_processes[task_id] = process

        print(f"🚀 Background task started (PID: {process.pid})")
        print(f"📊 Monitor with: python task_manager.py --status {task_id}")

    def _start_sync_task(self, task_id: str, task_meta: Dict) -> None:
        """Start task synchronously (blocks until complete)."""
        # For sync tasks, just run the worker directly
        from train_worker import TrainingWorker

        worker = TrainingWorker(task_id, self.tasks_dir)
        worker.run()

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get current task status and progress."""
        task_file = self.tasks_dir / task_id / "meta.json"

        if not task_file.exists():
            return None

        with open(task_file, 'r') as f:
            return json.load(f)

    def list_tasks(self, status_filter: Optional[str] = None) -> List[Dict]:
        """List all tasks, optionally filtered by status."""
        tasks = []

        for task_dir in self.tasks_dir.iterdir():
            if not task_dir.is_dir():
                continue

            meta_file = task_dir / "meta.json"
            if not meta_file.exists():
                continue

            with open(meta_file, 'r') as f:
                task_meta = json.load(f)

            if status_filter is None or task_meta["status"] == status_filter:
                tasks.append(task_meta)

        # Sort by priority (higher first) then by submission time
        tasks.sort(key=lambda t: (-t["priority"], t["timestamps"]["submitted"]))

        return tasks

    def stop_task(self, task_id: str) -> bool:
        """Stop a running task."""
        task_meta = self.get_task_status(task_id)
        if not task_meta:
            print(f"❌ Task not found: {task_id}")
            return False

        if task_meta["status"] not in ["pending", "preparing_data", "training"]:
            print(f"❌ Cannot stop task in status: {task_meta['status']}")
            return False

        # Kill process if running
        if task_meta["pid"]:
            try:
                os.kill(task_meta["pid"], signal.SIGTERM)
                print(f"✅ Sent stop signal to task {task_id} (PID: {task_meta['pid']})")
            except ProcessLookupError:
                print(f"⚠️  Process already terminated")

        # Update status
        task_meta["status"] = TaskStatus.STOPPED.value
        task_meta["timestamps"]["completed"] = datetime.now().isoformat()
        self._update_task_meta(task_id, task_meta)

        return True

    def resume_task(self, task_id: str) -> bool:
        """Resume a paused/stopped task from checkpoint."""
        task_meta = self.get_task_status(task_id)
        if not task_meta:
            print(f"❌ Task not found: {task_id}")
            return False

        if task_meta["status"] not in ["paused", "stopped"]:
            print(f"❌ Can only resume paused or stopped tasks")
            return False

        # Restart task
        task_meta["status"] = TaskStatus.PENDING.value
        self._update_task_meta(task_id, task_meta)

        self._start_background_task(task_id, task_meta)

        return True

    def get_task_logs(self, task_id: str, lines: int = 50) -> Optional[str]:
        """Get recent task logs."""
        task_meta = self.get_task_status(task_id)
        if not task_meta or not task_meta.get("log_file"):
            return None

        log_file = Path(task_meta["log_file"])
        if not log_file.exists():
            return None

        # Read last N lines
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            return ''.join(all_lines[-lines:])

    def _update_task_meta(self, task_id: str, meta: Dict) -> None:
        """Update task metadata file."""
        task_file = self.tasks_dir / task_id / "meta.json"

        with open(task_file, 'w') as f:
            json.dump(meta, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Manage training tasks"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Submit command
    submit_parser = subparsers.add_parser("submit", help="Submit a new training task")
    submit_parser.add_argument("--task-type", required=True, choices=["bc", "rl"])
    submit_parser.add_argument("--data-sources", required=True, nargs="+")
    submit_parser.add_argument("--model-name", required=True)
    submit_parser.add_argument("--output-dir", default="./output")
    submit_parser.add_argument("--epochs", type=int, default=100)
    submit_parser.add_argument("--batch-size", type=int, default=32)
    submit_parser.add_argument("--learning-rate", type=float, default=0.001)
    submit_parser.add_argument("--device", default="cuda")
    submit_parser.add_argument("--background", action="store_true", default=True)
    submit_parser.add_argument("--progress-interval", type=int, default=60)
    submit_parser.add_argument("--priority", type=int, default=5)
    submit_parser.add_argument("--notify-on-complete", action="store_true")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check task status")
    status_parser.add_argument("task_id", help="Task ID to check")

    # List command
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument("--status", help="Filter by status")

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a task")
    stop_parser.add_argument("task_id", help="Task ID to stop")

    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume a task")
    resume_parser.add_argument("task_id", help="Task ID to resume")

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="View task logs")
    logs_parser.add_argument("task_id", help="Task ID")
    logs_parser.add_argument("--lines", type=int, default=50)

    args = parser.parse_args()

    manager = TaskManager()

    if args.command == "submit":
        meta = manager.submit_task(
            task_type=args.task_type,
            data_sources=args.data_sources,
            model_name=args.model_name,
            output_dir=args.output_dir,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            device=args.device,
            background=args.background,
            progress_interval=args.progress_interval,
            priority=args.priority,
            notify_on_complete=args.notify_on_complete
        )
        print(json.dumps(meta, indent=2))

    elif args.command == "status":
        status = manager.get_task_status(args.task_id)
        if status:
            print(json.dumps(status, indent=2))
        else:
            print(f"❌ Task not found: {args.task_id}")

    elif args.command == "list":
        tasks = manager.list_tasks(args.status)
        print(f"Found {len(tasks)} tasks")
        for task in tasks:
            print(f"  - {task['task_id']}: {task['status']} (priority {task['priority']})")

    elif args.command == "stop":
        manager.stop_task(args.task_id)

    elif args.command == "resume":
        manager.resume_task(args.task_id)

    elif args.command == "logs":
        logs = manager.get_task_logs(args.task_id, args.lines)
        if logs:
            print(logs)
        else:
            print(f"❌ No logs available for task: {args.task_id}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
