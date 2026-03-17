#!/usr/bin/env python3
"""
Task manager for lerobot training jobs.

Supports:
- Submit training tasks with dataset configuration
- Background execution with progress monitoring
- Integration with lerobot_train and lerobot_edit_dataset
- Proxy and HuggingFace token configuration
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
import time


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    PREPARING_DATA = "preparing_data"
    INITIALIZING = "initializing"
    TRAINING = "training"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"
    PAUSED = "paused"


class TaskManager:
    """Manage training task lifecycle."""

    def __init__(self, tasks_dir: Optional[str] = None, lerobot_dir: Optional[str] = None):
        self.tasks_dir = Path(tasks_dir or os.path.expanduser("~/.openclaw/tasks"))
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        
        # Find lerobot_ros2 directory
        self.lerobot_dir = Path(lerobot_dir or "/home/nice/ly/lerobot_ros2")
        if not self.lerobot_dir.exists():
            # Try to find it
            possible_paths = [
                Path.home() / "lerobot_ros2",
                Path("/home/nice/ly/lerobot_ros2"),
            ]
            for p in possible_paths:
                if p.exists():
                    self.lerobot_dir = p
                    break
        
        self.active_processes: Dict[str, subprocess.Popen] = {}

    def submit_task(
        self,
        dataset_repo_id: str,
        model_name: str = "smolvla_base",
        output_dir: str = "./output",
        policy_type: str = "smolvla",
        batch_size: int = 32,
        steps: int = 100000,
        save_freq: int = 5000,
        eval_freq: int = 1000,
        num_workers: int = 16,
        device: str = "cuda",
        background: bool = True,
        priority: int = 5,
        proxy: Optional[str] = None,
        hf_token: Optional[str] = None,
        conda_env: str = "ly_robot",
        job_name: Optional[str] = None,
        dry_run: bool = False,
        **kwargs
    ) -> Dict:
        """
        Submit a new training task.

        Args:
            dry_run: If True, only show configuration without executing

        Returns:
            Task metadata with task_id
        """
        # Generate unique task ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_id = f"train_{timestamp}_{uuid.uuid4().hex[:8]}"

        if not job_name:
            job_name = f"train_{model_name}_{timestamp}"

        # Format output directory with timestamp
        output_dir_formatted = f"{output_dir}/{datetime.now().strftime('%m%d_%H%M')}"

        # Create task metadata
        task_meta = {
            "task_id": task_id,
            "status": TaskStatus.PENDING.value,
            "priority": priority,
            "config": {
                "dataset_repo_id": dataset_repo_id,
                "model_name": model_name,
                "policy_type": policy_type,
                "output_dir": output_dir_formatted,
                "batch_size": batch_size,
                "steps": steps,
                "save_freq": save_freq,
                "eval_freq": eval_freq,
                "num_workers": num_workers,
                "device": device,
                "job_name": job_name,
                **kwargs
            },
            "environment": {
                "conda_env": conda_env,
                "proxy": proxy,
                "hf_token": "***" if hf_token else None,
                "lerobot_dir": str(self.lerobot_dir)
            },
            "progress": {
                "current_step": 0,
                "total_steps": steps,
                "loss": None,
                "lr": None,
                "elapsed_time": "0m",
                "estimated_remaining": "calculating..."
            },
            "resource": {
                "gpu_utilization": "N/A",
                "gpu_memory_used": "N/A"
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

        # Dry run mode: only show configuration
        if dry_run:
            return self._show_dry_run(task_meta, proxy, hf_token, conda_env)

        # Save task metadata
        task_file = self.tasks_dir / task_id / "meta.json"
        task_file.parent.mkdir(parents=True, exist_ok=True)

        with open(task_file, 'w') as f:
            json.dump(task_meta, f, indent=2)

        print(f"✅ Task submitted: {task_id}")

        # Start execution
        if background:
            self._start_background_task(task_id, task_meta, proxy, hf_token, conda_env)
        else:
            self._start_sync_task(task_id, task_meta)

        return task_meta

    def _show_dry_run(
        self,
        task_meta: Dict,
        proxy: Optional[str] = None,
        hf_token: Optional[str] = None,
        conda_env: str = "ly_robot"
    ) -> Dict:
        """Show configuration preview in dry-run mode."""
        config = task_meta["config"]

        # Count episodes if dataset exists
        dataset_path = Path.home() / ".cache" / "huggingface" / "lerobot" / config["dataset_repo_id"]
        episode_count = "unknown"
        if dataset_path.exists():
            try:
                # Try to read meta/info.json
                info_file = dataset_path / "meta" / "info.json"
                if info_file.exists():
                    with open(info_file) as f:
                        info = json.load(f)
                        episode_count = info.get("total_episodes", "unknown")
            except:
                pass

        # Build the command
        cmd = self._build_train_command(task_meta, proxy, hf_token, conda_env)

        # Print formatted preview
        print("\n" + "="*60)
        print("📋 训练配置预览")
        print("="*60)
        print()

        print("🔄 数据集信息:")
        print(f"  • 数据集: {config['dataset_repo_id']}")
        print(f"  • Episodes: {episode_count}")
        print(f"  • 位置: ~/.cache/huggingface/lerobot/{config['dataset_repo_id']}")
        print()

        print("🤖 模型配置:")
        print(f"  • 模型: {config['model_name']}")
        print(f"  • Policy Type: {config['policy_type']}")
        if config['policy_type'] == "smolvla":
            print(f"  • 预训练权重: lerobot/smolvla_base")
        print()

        print("📊 训练参数:")
        print(f"  • Batch Size: {config['batch_size']}")
        print(f"  • Steps: {config['steps']}")
        print(f"  • Save Frequency: 每 {config['save_freq']} 步")
        print(f"  • Eval Frequency: 每 {config['eval_freq']} 步")
        print(f"  • Workers: {config['num_workers']}")
        print()

        print("💻 执行环境:")
        print(f"  • 脚本位置: {self.lerobot_dir}/src/lerobot/scripts/lerobot_train.py")
        print(f"  • Conda 环境: {conda_env}")
        print(f"  • 设备: {config['device']}")
        print(f"  • 输出目录: {config['output_dir']}")
        if proxy:
            print(f"  • 代理: {proxy}")
        print()

        print("🔧 完整命令:")
        print("```bash")
        print(cmd)
        print("```")
        print()

        print("="*60)
        print("⚠️  这是预览模式 (--dry-run)")
        print("    实际执行时请移除 --dry-run 参数")
        print("="*60)
        print()

        return task_meta

    def _start_background_task(
        self, 
        task_id: str, 
        task_meta: Dict,
        proxy: Optional[str] = None,
        hf_token: Optional[str] = None,
        conda_env: str = "ly_robot"
    ) -> None:
        """Start task in background process."""
        # Create log file
        log_file = self.tasks_dir / task_id / f"training_{task_id}.log"
        task_meta["log_file"] = str(log_file)
        
        # Build training command
        cmd = self._build_train_command(task_meta, proxy, hf_token, conda_env)
        
        # Write wrapper script
        script_file = self.tasks_dir / task_id / "run_training.sh"
        with open(script_file, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# Wrapper script for lerobot_train\n")
            f.write("# This script sets up the environment and calls the standard training script\n\n")
            
            # Conda activation
            f.write("source ~/miniconda3/etc/profile.d/conda.sh\n")
            f.write(f"conda activate {conda_env}\n\n")
            
            # Proxy configuration
            if proxy:
                f.write(f"export HTTP_PROXY={proxy}\n")
                f.write(f"export HTTPS_PROXY={proxy}\n\n")
            
            # HuggingFace token
            if hf_token:
                f.write(f"export HF_TOKEN={hf_token}\n")
                f.write(f"echo '{hf_token}' > ~/.huggingface/token\n\n")
            
            # Working directory
            f.write(f"cd {self.lerobot_dir}\n\n")
            
            # Training command
            f.write(cmd + "\n")
        
        os.chmod(script_file, 0o755)

        # Launch process
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                ["bash", str(script_file)],
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )

        # Update metadata with PID
        task_meta["pid"] = process.pid
        task_meta["status"] = TaskStatus.TRAINING.value
        task_meta["timestamps"]["started"] = datetime.now().isoformat()
        self._update_task_meta(task_id, task_meta)

        self.active_processes[task_id] = process

        print(f"🚀 Training started (PID: {process.pid})")
        print(f"📊 Monitor: python task_manager.py status {task_id}")
        print(f"📄 Log: {log_file}")

    def _build_train_command(
        self, 
        task_meta: Dict,
        proxy: Optional[str] = None,
        hf_token: Optional[str] = None,
        conda_env: str = "ly_robot"
    ) -> str:
        """Build lerobot_train command."""
        config = task_meta["config"]
        
        cmd_parts = ["python -m lerobot.scripts.lerobot_train"]
        
        # Policy configuration
        policy_type = config.get("policy_type", "smolvla")
        cmd_parts.append(f"--policy.type {policy_type}")
        
        if policy_type == "smolvla":
            cmd_parts.append("--policy.pretrained_path lerobot/smolvla_base")
            cmd_parts.append("--policy.load_vlm_weights true")
        
        cmd_parts.append(f"--policy.device {config.get('device', 'cuda')}")
        cmd_parts.append(f"--policy.repo_id train/{config['model_name']}_policy")
        cmd_parts.append("--policy.push_to_hub false")
        
        # Dataset configuration
        cmd_parts.append(f"--dataset.repo_id {config['dataset_repo_id']}")
        
        # Training configuration
        cmd_parts.append(f"--output_dir {config['output_dir']}")
        cmd_parts.append(f"--job_name {config.get('job_name', 'train')}")
        cmd_parts.append(f"--batch_size {config['batch_size']}")
        cmd_parts.append(f"--steps {config['steps']}")
        cmd_parts.append(f"--save_freq {config['save_freq']}")
        cmd_parts.append(f"--eval_freq {config['eval_freq']}")
        cmd_parts.append(f"--num_workers {config['num_workers']}")
        
        # Disable wandb by default
        cmd_parts.append("--wandb.enable false")
        
        return " \\\n  ".join(cmd_parts)

    def _start_sync_task(self, task_id: str, task_meta: Dict) -> None:
        """Start task synchronously (blocks until complete)."""
        # Run the training directly
        cmd = self._build_train_command(task_meta)
        
        task_meta["status"] = TaskStatus.TRAINING.value
        task_meta["timestamps"]["started"] = datetime.now().isoformat()
        self._update_task_meta(task_id, task_meta)
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(self.lerobot_dir),
                text=True
            )
            
            if result.returncode == 0:
                task_meta["status"] = TaskStatus.COMPLETED.value
            else:
                task_meta["status"] = TaskStatus.FAILED.value
                
        except Exception as e:
            task_meta["status"] = TaskStatus.FAILED.value
            print(f"❌ Training failed: {e}")
        
        task_meta["timestamps"]["completed"] = datetime.now().isoformat()
        self._update_task_meta(task_id, task_meta)

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get current task status and progress."""
        task_file = self.tasks_dir / task_id / "meta.json"

        if not task_file.exists():
            return None

        with open(task_file, 'r') as f:
            meta = json.load(f)
        
        # Try to parse progress from log
        log_file = self.tasks_dir / task_id / f"training_{task_id}.log"
        if log_file.exists():
            self._parse_log_progress(meta, log_file)
        
        return meta
    
    def _parse_log_progress(self, meta: Dict, log_file: Path) -> None:
        """Parse training progress from log file."""
        try:
            with open(log_file, 'r') as f:
                # Read last 100 lines
                lines = f.readlines()[-100:]
                
                for line in reversed(lines):
                    # Parse step/loss/lr from lerobot output
                    # Format: INFO ... step:200 smpl:6K ep:8 epch:0.65 loss:0.068 grdn:0.749 lr:1.0e-05
                    if "step:" in line:
                        parts = line.split()
                        for part in parts:
                            if part.startswith("step:"):
                                meta["progress"]["current_step"] = int(part.split(":")[1])
                            elif part.startswith("loss:"):
                                meta["progress"]["loss"] = float(part.split(":")[1])
                            elif part.startswith("lr:"):
                                meta["progress"]["lr"] = part.split(":")[1]
                        break
        except Exception:
            pass

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

        # Sort by submission time
        tasks.sort(key=lambda t: t["timestamps"]["submitted"], reverse=True)

        return tasks

    def stop_task(self, task_id: str) -> bool:
        """Stop a running task."""
        task_meta = self.get_task_status(task_id)
        if not task_meta:
            print(f"❌ Task not found: {task_id}")
            return False

        if task_meta["status"] not in ["pending", "training"]:
            print(f"❌ Cannot stop task in status: {task_meta['status']}")
            return False

        # Kill process if running
        if task_meta.get("pid"):
            try:
                os.killpg(os.getpgid(task_meta["pid"]), signal.SIGTERM)
                print(f"✅ Sent stop signal to task {task_id} (PID: {task_meta['pid']})")
            except ProcessLookupError:
                print(f"⚠️  Process already terminated")

        # Update status
        task_meta["status"] = TaskStatus.STOPPED.value
        task_meta["timestamps"]["completed"] = datetime.now().isoformat()
        self._update_task_meta(task_id, task_meta)

        return True

    def get_task_logs(self, task_id: str, lines: int = 50) -> Optional[str]:
        """Get recent task logs."""
        task_meta = self.get_task_status(task_id)
        if not task_meta:
            return None
        
        log_file = self.tasks_dir / task_id / f"training_{task_id}.log"
        if not log_file.exists():
            return None

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
        description="Manage lerobot training tasks"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Submit command
    submit_parser = subparsers.add_parser("submit", help="Submit training task")
    submit_parser.add_argument("--dataset-repo-id", required=True, help="Dataset repo ID (e.g., train/merged)")
    submit_parser.add_argument("--model-name", default="smolvla_base")
    submit_parser.add_argument("--policy-type", default="smolvla", choices=["smolvla", "act"])
    submit_parser.add_argument("--output-dir", default="outputs/mylerobot_train")
    submit_parser.add_argument("--batch-size", type=int, default=32)
    submit_parser.add_argument("--steps", type=int, default=100000)
    submit_parser.add_argument("--save-freq", type=int, default=5000)
    submit_parser.add_argument("--eval-freq", type=int, default=1000)
    submit_parser.add_argument("--num-workers", type=int, default=16)
    submit_parser.add_argument("--device", default="cuda")
    submit_parser.add_argument("--job-name")
    submit_parser.add_argument("--proxy", help="Proxy URL (e.g., http://127.0.0.1:10809)")
    submit_parser.add_argument("--hf-token", help="HuggingFace token")
    submit_parser.add_argument("--conda-env", default="ly_robot")
    submit_parser.add_argument("--priority", type=int, default=5)
    submit_parser.add_argument("--background", action="store_true", default=True)
    submit_parser.add_argument("--dry-run", action="store_true", help="Show configuration without executing")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check task status")
    status_parser.add_argument("task_id")

    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status")

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop task")
    stop_parser.add_argument("task_id")

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="View logs")
    logs_parser.add_argument("task_id")
    logs_parser.add_argument("--lines", type=int, default=50)

    args = parser.parse_args()

    manager = TaskManager()

    if args.command == "submit":
        meta = manager.submit_task(
            dataset_repo_id=args.dataset_repo_id,
            model_name=args.model_name,
            policy_type=args.policy_type,
            output_dir=args.output_dir,
            batch_size=args.batch_size,
            steps=args.steps,
            save_freq=args.save_freq,
            eval_freq=args.eval_freq,
            num_workers=args.num_workers,
            device=args.device,
            job_name=args.job_name,
            proxy=args.proxy,
            hf_token=args.hf_token,
            conda_env=args.conda_env,
            priority=args.priority,
            background=args.background,
            dry_run=args.dry_run
        )
        if args.dry_run:
            # Already printed preview in _show_dry_run
            pass
        else:
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
            progress = task.get("progress", {})
            step = progress.get("current_step", 0)
            total = progress.get("total_steps", "?")
            loss = progress.get("loss", "?")
            print(f"  - {task['task_id']}: {task['status']} (step {step}/{total}, loss={loss})")

    elif args.command == "stop":
        manager.stop_task(args.task_id)

    elif args.command == "logs":
        logs = manager.get_task_logs(args.task_id, args.lines)
        if logs:
            print(logs)
        else:
            print(f"❌ No logs for task: {args.task_id}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
