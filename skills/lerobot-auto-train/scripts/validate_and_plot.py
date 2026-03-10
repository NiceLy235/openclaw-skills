#!/usr/bin/env python3
"""
Validation and Loss Curve Plotting Script

Validates model on validation set during training and plots loss curves.
"""

import os
import json
import argparse
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np


class LossTracker:
    """Track training and validation losses."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.train_losses: List[Dict] = []
        self.val_losses: List[Dict] = []
        
        self.loss_file = self.output_dir / "loss_history.json"
        self.load()
    
    def load(self):
        """Load existing loss history."""
        if self.loss_file.exists():
            with open(self.loss_file, 'r') as f:
                data = json.load(f)
                self.train_losses = data.get('train', [])
                self.val_losses = data.get('val', [])
    
    def save(self):
        """Save loss history to file."""
        data = {
            'train': self.train_losses,
            'val': self.val_losses
        }
        with open(self.loss_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_train_loss(self, step: int, epoch: int, loss: float):
        """Add training loss."""
        self.train_losses.append({
            'step': step,
            'epoch': epoch,
            'loss': loss
        })
        self.save()
    
    def add_val_loss(self, step: int, epoch: int, loss: float, metrics: Dict = None):
        """Add validation loss."""
        entry = {
            'step': step,
            'epoch': epoch,
            'loss': loss
        }
        if metrics:
            entry['metrics'] = metrics
        
        self.val_losses.append(entry)
        self.save()
    
    def plot_curves(self, save_path: Path = None):
        """Plot training and validation loss curves."""
        if not self.train_losses:
            print("⚠️  No training losses recorded")
            return
        
        # Extract data
        train_steps = [x['step'] for x in self.train_losses]
        train_losses = [x['loss'] for x in self.train_losses]
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot training loss
        ax1.plot(train_steps, train_losses, 'b-', label='Training Loss', linewidth=2)
        ax1.set_xlabel('Step', fontsize=12)
        ax1.set_ylabel('Loss', fontsize=12)
        ax1.set_title('Training Loss Curve', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=10)
        
        # Plot validation loss if available
        if self.val_losses:
            val_steps = [x['step'] for x in self.val_losses]
            val_losses = [x['loss'] for x in self.val_losses]
            
            ax2.plot(val_steps, val_losses, 'r-', label='Validation Loss', linewidth=2, marker='o')
            ax2.set_xlabel('Step', fontsize=12)
            ax2.set_ylabel('Loss', fontsize=12)
            ax2.set_title('Validation Loss Curve', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend(fontsize=10)
            
            # Find best validation loss
            best_idx = np.argmin(val_losses)
            best_loss = val_losses[best_idx]
            best_step = val_steps[best_idx]
            ax2.axhline(y=best_loss, color='g', linestyle='--', alpha=0.5, label=f'Best: {best_loss:.4f}')
            ax2.plot(best_step, best_loss, 'g*', markersize=15, label=f'Best @ step {best_step}')
            ax2.legend(fontsize=9)
        else:
            ax2.text(0.5, 0.5, 'No validation data', ha='center', va='center', fontsize=14)
            ax2.set_title('Validation Loss Curve', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            save_path = self.output_dir / "loss_curves.png"
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ Loss curves saved to: {save_path}")
        
        # Also save as PDF for high quality
        pdf_path = save_path.with_suffix('.pdf')
        plt.savefig(pdf_path, dpi=300, bbox_inches='tight')
        print(f"✅ PDF version saved to: {pdf_path}")
        
        plt.close()
    
    def plot_combined(self, save_path: Path = None):
        """Plot training and validation loss on same axis."""
        if not self.train_losses:
            print("⚠️  No training losses recorded")
            return
        
        # Extract data
        train_steps = [x['step'] for x in self.train_losses]
        train_losses = [x['loss'] for x in self.train_losses]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot training loss
        ax.plot(train_steps, train_losses, 'b-', label='Training Loss', linewidth=2, alpha=0.7)
        
        # Plot validation loss if available
        if self.val_losses:
            val_steps = [x['step'] for x in self.val_losses]
            val_losses = [x['loss'] for x in self.val_losses]
            ax.plot(val_steps, val_losses, 'r-', label='Validation Loss', linewidth=2, marker='o', markersize=6)
            
            # Mark best validation loss
            best_idx = np.argmin(val_losses)
            best_loss = val_losses[best_idx]
            best_step = val_steps[best_idx]
            ax.plot(best_step, best_loss, 'g*', markersize=20, label=f'Best Val Loss: {best_loss:.4f}')
        
        ax.set_xlabel('Step', fontsize=12)
        ax.set_ylabel('Loss', fontsize=12)
        ax.set_title('Training and Validation Loss Curves', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            save_path = self.output_dir / "loss_curves_combined.png"
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ Combined loss curves saved to: {save_path}")
        
        plt.close()


def validate_model(
    model_path: Path,
    val_data_dir: Path,
    output_dir: Path,
    step: int,
    epoch: int
) -> Tuple[float, Dict]:
    """
    Validate model on validation set.
    
    Args:
        model_path: Path to model checkpoint
        val_data_dir: Path to validation data directory
        output_dir: Output directory for results
        step: Current training step
        epoch: Current epoch
    
    Returns:
        Tuple of (validation_loss, metrics_dict)
    """
    import torch
    from lerobot.common.datasets.lerobot_dataset import LeRobotDataset
    from lerobot.common.policies.factory import make_policy
    
    print(f"🔍 Validating model at step {step}...")
    
    # Load model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    checkpoint = torch.load(model_path, map_location=device)
    
    # Load validation dataset
    val_dataset = LeRobotDataset(
        repo_id=val_data_dir.name,
        root=val_data_dir.parent
    )
    
    # Create data loader
    val_loader = torch.utils.data.DataLoader(
        val_dataset,
        batch_size=32,
        shuffle=False,
        num_workers=4
    )
    
    # Compute validation loss
    model = make_policy(checkpoint['policy_config'])
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    total_loss = 0.0
    num_batches = 0
    
    with torch.no_grad():
        for batch in val_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            loss = model.compute_loss(batch)
            total_loss += loss.item()
            num_batches += 1
    
    avg_loss = total_loss / num_batches if num_batches > 0 else float('inf')
    
    metrics = {
        'val_loss': avg_loss,
        'num_batches': num_batches,
        'val_dataset_size': len(val_dataset)
    }
    
    print(f"✅ Validation complete: Loss = {avg_loss:.4f}")
    
    return avg_loss, metrics


def main():
    parser = argparse.ArgumentParser(
        description="Validate model and plot loss curves"
    )
    
    parser.add_argument(
        "--model-path",
        type=str,
        help="Path to model checkpoint (for validation)"
    )
    
    parser.add_argument(
        "--val-data",
        type=str,
        help="Path to validation data directory"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Output directory for loss history and plots"
    )
    
    parser.add_argument(
        "--step",
        type=int,
        help="Current training step"
    )
    
    parser.add_argument(
        "--epoch",
        type=int,
        help="Current epoch"
    )
    
    parser.add_argument(
        "--train-loss",
        type=float,
        help="Training loss to record"
    )
    
    parser.add_argument(
        "--plot-only",
        action="store_true",
        help="Only plot curves, skip validation"
    )
    
    parser.add_argument(
        "--plot-combined",
        action="store_true",
        help="Plot combined train/val curves"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    tracker = LossTracker(output_dir)
    
    # Record training loss if provided
    if args.train_loss is not None and args.step is not None:
        tracker.add_train_loss(args.step, args.epoch or 0, args.train_loss)
        print(f"✅ Recorded training loss: {args.train_loss:.4f} at step {args.step}")
    
    # Validate if model and val data provided
    if not args.plot_only and args.model_path and args.val_data:
        model_path = Path(args.model_path)
        val_data_dir = Path(args.val_data)
        
        if model_path.exists() and val_data_dir.exists():
            val_loss, metrics = validate_model(
                model_path,
                val_data_dir,
                output_dir,
                args.step or 0,
                args.epoch or 0
            )
            tracker.add_val_loss(args.step or 0, args.epoch or 0, val_loss, metrics)
        else:
            print(f"⚠️  Model or validation data not found, skipping validation")
    
    # Plot curves
    if args.plot_combined:
        tracker.plot_combined()
    else:
        tracker.plot_curves()
    
    print()
    print("="*60)
    print(f"📊 Loss History Summary")
    print("="*60)
    print(f"Training samples: {len(tracker.train_losses)}")
    print(f"Validation samples: {len(tracker.val_losses)}")
    print(f"Loss history file: {tracker.loss_file}")
    print("="*60)


if __name__ == "__main__":
    main()
