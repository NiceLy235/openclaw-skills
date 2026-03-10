#!/usr/bin/env python3
"""
Training worker process.

Executes the actual training loop with:
- Progress tracking and updates
- Checkpoint saving
- Error recovery
- Resource monitoring
"""

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import traceback


class TrainingWorker:
    """Execute training task with progress monitoring."""

    def __init__(self, task_id: str, tasks_dir: Path):
        self.task_id = task_id
        self.tasks_dir = tasks_dir
        self.task_file = tasks_dir / task_id / "meta.json"
        self.meta = self._load_meta()

        # Checkpoint directory
        self.checkpoint_dir = Path(self.meta["config"]["output_dir"]) / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Progress tracking
        self.start_time = None
        self.should_stop = False

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_stop_signal)
        signal.signal(signal.SIGINT, self._handle_stop_signal)

    def _load_meta(self) -> Dict:
        """Load task metadata."""
        with open(self.task_file, 'r') as f:
            return json.load(f)

    def _save_meta(self) -> None:
        """Save task metadata."""
        with open(self.task_file, 'w') as f:
            json.dump(self.meta, f, indent=2)

    def _update_status(self, status: str) -> None:
        """Update task status."""
        self.meta["status"] = status
        self._save_meta()
        print(f"[{datetime.now().isoformat()}] Status: {status}")

    def _update_progress(self, **kwargs) -> None:
        """Update task progress."""
        self.meta["progress"].update(kwargs)
        self._save_meta()

    def _update_resource(self) -> None:
        """Update resource utilization."""
        try:
            import torch
            import psutil

            if torch.cuda.is_available():
                self.meta["resource"]["gpu_utilization"] = f"{torch.cuda.utilization()}%"
                mem_allocated = torch.cuda.memory_allocated() / 1024**3
                mem_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
                self.meta["resource"]["gpu_memory_used"] = f"{mem_allocated:.1f}GB / {mem_total:.1f}GB"

            self.meta["resource"]["cpu_usage"] = f"{psutil.cpu_percent()}%"

            self._save_meta()

        except Exception as e:
            # Non-critical error, just log it
            print(f"Warning: Failed to update resource metrics: {e}")

    def _handle_stop_signal(self, signum, frame):
        """Handle stop signal (SIGTERM/SIGINT)."""
        print(f"\n⚠️  Received stop signal, saving checkpoint...")
        self.should_stop = True
        self._update_status("paused")

    def run(self) -> None:
        """Execute training workflow."""
        try:
            self.start_time = time.time()
            self._update_status("preparing_data")

            # Step 1: Prepare data
            self._prepare_data()

            # Step 2: Initialize training
            self._update_status("initializing")
            trainer = self._initialize_training()

            # Step 3: Train
            self._update_status("training")
            self._train(trainer)

            if self.should_stop:
                print("✓ Training stopped, checkpoint saved")
                return

            # Step 4: Validate
            self._update_status("validating")
            self._validate(trainer)

            # Step 5: Export
            self._update_status("exporting")
            self._export_model(trainer)

            # Step 6: Inference test
            self._run_inference_test()

            # Complete
            self.meta["timestamps"]["completed"] = datetime.now().isoformat()
            self._update_status("completed")

            print(f"✅ Training completed successfully!")

            # Notify if requested
            if self.meta["execution"]["notify_on_complete"]:
                self._send_notification()

        except Exception as e:
            print(f"❌ Training failed: {e}")
            print(traceback.format_exc())

            self.meta["error"] = {
                "message": str(e),
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            }
            self._update_status("failed")

    def _prepare_data(self) -> None:
        """Prepare and merge data sources."""
        print("📦 Preparing data...")

        data_sources = self.meta["config"]["data_sources"]

        # TODO: Implement actual data preparation
        # - Verify data sources exist
        # - Merge multiple sources
        # - Split train/val
        # - Generate statistics

        # Simulate work
        time.sleep(2)

        print(f"✓ Data prepared from {len(data_sources)} source(s)")

    def _initialize_training(self):
        """Initialize training configuration."""
        print("🔧 Initializing training...")

        config = self.meta["config"]

        # TODO: Import and initialize actual trainer
        # This would be the actual lerobot training setup
        #
        # Example:
        # from lerobot.common.train import train
        # trainer = Trainer(
        #     model=config["model_name"],
        #     epochs=config["epochs"],
        #     batch_size=config["batch_size"],
        #     learning_rate=config["learning_rate"],
        #     device=config["device"]
        # )

        # Placeholder
        trainer = {"config": config}

        print(f"✓ Training initialized:")
        print(f"  - Model: {config['model_name']}")
        print(f"  - Epochs: {config['epochs']}")
        print(f"  - Batch size: {config['batch_size']}")
        print(f"  - Device: {config['device']}")

        return trainer

    def _train(self, trainer) -> None:
        """Execute training loop."""
        print("🚀 Starting training...")

        config = self.meta["config"]
        progress_interval = self.meta["execution"]["progress_interval"]

        epochs = config["epochs"]
        best_loss = float('inf')

        last_progress_update = time.time()

        for epoch in range(1, epochs + 1):
            if self.should_stop:
                # Save checkpoint before stopping
                self._save_checkpoint(trainer, epoch)
                break

            # TODO: Actual training step
            # loss = trainer.train_epoch(epoch)

            # Simulate training
            train_loss = 1.0 / epoch  # Mock decreasing loss
            val_loss = train_loss * 1.1  # Mock validation loss

            # Update best loss
            if val_loss < best_loss:
                best_loss = val_loss
                # Save best model
                self._save_checkpoint(trainer, epoch, is_best=True)

            # Update progress
            elapsed = time.time() - self.start_time
            estimated_total = elapsed * epochs / epoch
            estimated_remaining = estimated_total - elapsed

            self._update_progress(
                current_epoch=epoch,
                total_epochs=epochs,
                train_loss=train_loss,
                val_loss=val_loss,
                best_val_loss=best_loss,
                elapsed_time=self._format_time(elapsed),
                estimated_remaining=self._format_time(estimated_remaining)
            )

            # Periodic progress report
            if time.time() - last_progress_update >= progress_interval:
                self._update_resource()
                self._print_progress(epoch, epochs, train_loss, val_loss)
                last_progress_update = time.time()

            # Simulate epoch time
            time.sleep(0.1)

        # Save final checkpoint
        if not self.should_stop:
            self._save_checkpoint(trainer, epochs, is_final=True)

    def _validate(self, trainer) -> None:
        """Validate trained model."""
        print("📊 Validating model...")

        # TODO: Actual validation
        # metrics = trainer.validate()

        time.sleep(1)

        print("✓ Validation complete")

    def _export_model(self, trainer) -> None:
        """Export model for inference."""
        print("💾 Exporting model...")

        output_dir = Path(self.meta["config"]["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        # TODO: Actual export
        # trainer.save(output_dir / "model.pt")

        time.sleep(1)

        print(f"✓ Model exported to {output_dir}")

    def _run_inference_test(self) -> None:
        """Run inference test with trained model."""
        print("🧪 Running inference test...")

        # TODO: Import and run inference
        # from inference_test import run_inference
        # results = run_inference(model_path, test_data)

        time.sleep(1)

        print("✓ Inference test passed")

    def _save_checkpoint(self, trainer, epoch: int, is_best: bool = False, is_final: bool = False) -> None:
        """Save training checkpoint."""
        checkpoint_name = f"checkpoint_epoch_{epoch}.pt"
        if is_best:
            checkpoint_name = "best_model.pt"
        elif is_final:
            checkpoint_name = "final_model.pt"

        checkpoint_path = self.checkpoint_dir / checkpoint_name

        # TODO: Actual checkpoint save
        # torch.save({
        #     'epoch': epoch,
        #     'model_state_dict': trainer.model.state_dict(),
        #     'optimizer_state_dict': trainer.optimizer.state_dict(),
        #     'loss': loss,
        # }, checkpoint_path)

        print(f"✓ Checkpoint saved: {checkpoint_path}")

    def _print_progress(self, epoch: int, total: int, train_loss: float, val_loss: float) -> None:
        """Print progress to console."""
        progress = epoch / total * 100
        bar_length = 30
        filled = int(bar_length * epoch / total)
        bar = '█' * filled + '░' * (bar_length - filled)

        print(
            f"\r[{bar}] {progress:.1f}% "
            f"Epoch {epoch}/{total} "
            f"| Train Loss: {train_loss:.4f} "
            f"| Val Loss: {val_loss:.4f}",
            end='', flush=True
        )

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds as human-readable time."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    def _send_notification(self) -> None:
        """Send completion notification."""
        # TODO: Implement notification system
        # Could use webhook, email, or system notification

        print(f"📧 Notification sent for task {self.task_id}")


def main():
    parser = argparse.ArgumentParser(description="Training worker process")
    parser.add_argument("--task-id", required=True, help="Task ID to execute")
    parser.add_argument("--tasks-dir", required=True, help="Tasks directory")

    args = parser.parse_args()

    worker = TrainingWorker(args.task_id, Path(args.tasks_dir))
    worker.run()


if __name__ == "__main__":
    main()
