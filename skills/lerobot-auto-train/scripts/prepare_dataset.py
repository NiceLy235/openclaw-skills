#!/usr/bin/env python3
"""
LeRobot Dataset Preparation Script

Supports:
1. Split raw episodes into train/val sets
2. Merge episodes using lerobot_edit_dataset
3. Generate combined datasets for training

Usage:
  # Step 1: Split episodes into train/val directories
  python prepare_dataset.py split --data-dir /path/to/episodes --output-dir ./processed

  # Step 2: Merge episodes into combined dataset
  python prepare_dataset.py merge --episodes-dir ./processed/train --repo-id ly/train_merged
  python prepare_dataset.py merge --episodes-dir ./processed/val --repo-id ly/val_merged
"""

import os
import shutil
import json
import random
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional


def collect_episodes(data_dir: Path) -> List[Path]:
    """Collect all episode directories from data directory."""
    episodes = []
    
    for item in sorted(data_dir.iterdir()):
        if item.is_dir():
            # Check if it's a valid LeRobot episode
            if (item / "meta" / "info.json").exists():
                episodes.append(item)
            # Also check for episode_XXX pattern
            elif item.name.startswith("episode") or item.name.startswith("episodes"):
                if (item / "meta").exists():
                    episodes.append(item)
    
    return episodes


def validate_episode(episode_dir: Path) -> bool:
    """Validate that episode directory has required structure."""
    required_files = [
        episode_dir / "meta" / "info.json",
        episode_dir / "data"
    ]
    
    return all(f.exists() for f in required_files)


def split_episodes(
    episodes: List[Path],
    train_ratio: float = 0.8,
    random_seed: int = 42
) -> Tuple[List[Path], List[Path]]:
    """
    Split episodes into training and validation sets.
    """
    random.seed(random_seed)
    shuffled = episodes.copy()
    random.shuffle(shuffled)
    
    split_idx = int(len(shuffled) * train_ratio)
    train_episodes = shuffled[:split_idx]
    val_episodes = shuffled[split_idx:]
    
    return train_episodes, val_episodes


def copy_episodes(
    episodes: List[Path],
    target_dir: Path,
    prefix: str = "episode"
) -> int:
    """Copy episodes to target directory with sequential naming."""
    target_dir.mkdir(parents=True, exist_ok=True)
    
    for i, ep_dir in enumerate(episodes, 1):
        target_ep_dir = target_dir / f"{prefix}_{i-1:03d}"
        
        if target_ep_dir.exists():
            shutil.rmtree(target_ep_dir)
        
        shutil.copytree(ep_dir, target_ep_dir)
        
    return len(episodes)


def merge_episodes_with_lerobot(
    episodes_dir: Path,
    repo_id: str,
    push_to_hub: bool = False,
    conda_env: str = "ly_robot",
    proxy: Optional[str] = None
) -> bool:
    """
    Merge episodes using lerobot_edit_dataset.
    
    Args:
        episodes_dir: Directory containing episode directories
        repo_id: Target repo ID (e.g., ly/train_merged)
        push_to_hub: Whether to push to HuggingFace Hub
        conda_env: Conda environment name
        proxy: Proxy URL (e.g., http://127.0.0.1:10809)
    
    Returns:
        True if successful
    """
    # Collect episode paths
    episode_paths = collect_episodes(episodes_dir)
    
    if not episode_paths:
        print(f"❌ No valid episodes found in {episodes_dir}")
        return False
    
    print(f"📂 Found {len(episode_paths)} episodes to merge")
    
    # Build command
    episode_patterns = [f'"{str(ep)}"' for ep in episode_paths]
    patterns_str = f'[{", ".join(episode_patterns)}]'
    
    # Find lerobot_edit_dataset.py
    script_dir = Path(__file__).parent
    lerobot_edit_script = script_dir.parent.parent.parent / "lerobot_ros2" / "src" / "lerobot" / "scripts" / "lerobot_edit_dataset.py"
    
    if not lerobot_edit_script.exists():
        # Try common locations
        possible_paths = [
            Path.home() / "lerobot_ros2" / "src" / "lerobot" / "scripts" / "lerobot_edit_dataset.py",
            Path("/home/nice/ly/lerobot_ros2/src/lerobot/scripts/lerobot_edit_dataset.py"),
        ]
        for p in possible_paths:
            if p.exists():
                lerobot_edit_script = p
                break
    
    # Build shell command
    cmd_parts = [
        f"source ~/miniconda3/etc/profile.d/conda.sh",
        f"conda activate {conda_env}",
    ]
    
    if proxy:
        cmd_parts.append(f"export HTTP_PROXY={proxy}")
        cmd_parts.append(f"export HTTPS_PROXY={proxy}")
    
    cmd_parts.append(f"cd {lerobot_edit_script.parent.parent.parent}")
    
    python_cmd = f'python {lerobot_edit_script} --repo_id {repo_id} --operation.type merge --operation.repo_id_patterns=\'{patterns_str}\' --push_to_hub {str(push_to_hub).lower()}'
    cmd_parts.append(python_cmd)
    
    full_cmd = " && ".join(cmd_parts)
    
    print(f"\n🔧 Executing merge command...")
    print(f"   Repo ID: {repo_id}")
    print(f"   Episodes: {len(episode_paths)}")
    
    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Merge successful: {repo_id}")
            # Check for output path in stdout
            for line in result.stdout.split("\n"):
                if "Merged dataset saved" in line or "Episodes:" in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print(f"❌ Merge failed:")
            print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Merge timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error during merge: {e}")
        return False


def cmd_split(args):
    """Handle split command."""
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    print("="*60)
    print("  LeRobot Dataset Split")
    print("="*60)
    print()
    
    # Collect episodes
    print(f"📂 Step 1: Collecting episodes from {data_dir}")
    episodes = collect_episodes(data_dir)
    
    if not episodes:
        print(f"❌ No valid episodes found in {data_dir}")
        return 1
    
    print(f"   Found {len(episodes)} episodes")
    print()
    
    # Validate
    if args.validate:
        print("🔍 Step 2: Validating episodes...")
        valid_episodes = [ep for ep in episodes if validate_episode(ep)]
        episodes = valid_episodes
        print(f"   Valid episodes: {len(episodes)}")
        print()
    
    # Split
    print(f"📊 Step 3: Splitting dataset (train={args.train_ratio*100}%)")
    train_episodes, val_episodes = split_episodes(
        episodes,
        train_ratio=args.train_ratio,
        random_seed=args.random_seed
    )
    
    print(f"   Training set: {len(train_episodes)} episodes")
    print(f"   Validation set: {len(val_episodes)} episodes")
    print()
    
    if args.dry_run:
        print("🔍 Dry run - showing split without copying")
        return 0
    
    # Create directories
    train_dir = output_dir / "train"
    val_dir = output_dir / "val"
    
    if train_dir.exists():
        shutil.rmtree(train_dir)
    if val_dir.exists():
        shutil.rmtree(val_dir)
    
    # Copy
    print("💾 Step 4: Copying episodes...")
    train_count = copy_episodes(train_episodes, train_dir, "episodes")
    val_count = copy_episodes(val_episodes, val_dir, "episodes")
    
    # Save split info
    split_info = {
        "total_episodes": len(episodes),
        "train_episodes": train_count,
        "val_episodes": val_count,
        "train_ratio": args.train_ratio,
        "random_seed": args.random_seed,
        "train_dir": str(train_dir),
        "val_dir": str(val_dir)
    }
    
    with open(output_dir / "split_info.json", "w") as f:
        json.dump(split_info, f, indent=2)
    
    print()
    print("="*60)
    print("✅ Dataset split complete!")
    print("="*60)
    print(f"Training:   {train_dir} ({train_count} episodes)")
    print(f"Validation: {val_dir} ({val_count} episodes)")
    print()
    print("Next step - merge datasets:")
    print(f"  python prepare_dataset.py merge --episodes-dir {train_dir} --repo-id ly/train_merged")
    print(f"  python prepare_dataset.py merge --episodes-dir {val_dir} --repo-id ly/val_merged")
    
    return 0


def cmd_merge(args):
    """Handle merge command."""
    episodes_dir = Path(args.episodes_dir)
    
    print("="*60)
    print("  LeRobot Dataset Merge")
    print("="*60)
    print()
    
    success = merge_episodes_with_lerobot(
        episodes_dir=episodes_dir,
        repo_id=args.repo_id,
        push_to_hub=args.push_to_hub,
        conda_env=args.conda_env,
        proxy=args.proxy
    )
    
    if success:
        print()
        print("="*60)
        print("✅ Merge complete!")
        print("="*60)
        print(f"Merged dataset: {args.repo_id}")
        print()
        print("Use in training:")
        print(f"  --dataset.repo_id {args.repo_id}")
        return 0
    else:
        return 1


def cmd_full(args):
    """Handle full pipeline (merge only, no split)."""
    data_dir = Path(args.data_dir)
    
    print("="*60)
    print("  Full Dataset Preparation Pipeline")
    print("="*60)
    print()
    
    # Step 1: Collect all episodes
    print("📁 Step 1: Collecting episodes...")
    episodes = collect_episodes(data_dir)
    
    if not episodes:
        print(f"❌ No valid episodes found in {data_dir}")
        return 1
    
    print(f"   Found {len(episodes)} episodes")
    print()
    
    # Step 2: Merge all episodes into one dataset (no split)
    print("📊 Step 2: Merging all episodes into single dataset...")
    merged_repo_id = f"{args.repo_prefix}/merged"
    
    success = merge_episodes_with_lerobot(
        episodes_dir=data_dir,
        repo_id=merged_repo_id,
        push_to_hub=False,
        conda_env=args.conda_env,
        proxy=args.proxy
    )
    
    if not success:
        print("❌ Merge failed")
        return 1
    
    print()
    print("="*60)
    print("✅ Full pipeline complete!")
    print("="*60)
    print(f"Merged dataset: {merged_repo_id}")
    print(f"Total episodes: {len(episodes)}")
    print()
    print("Ready for training:")
    print(f"  python task_manager.py submit \\")
    print(f"    --dataset-repo-id {merged_repo_id} \\")
    print(f"    --model-name smolvla_base")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Prepare LeRobot datasets"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Split command
    split_parser = subparsers.add_parser("split", help="Split raw episodes into train/val")
    split_parser.add_argument("--data-dir", required=True, help="Directory with raw episodes")
    split_parser.add_argument("--output-dir", required=True, help="Output directory")
    split_parser.add_argument("--train-ratio", type=float, default=0.8)
    split_parser.add_argument("--random-seed", type=int, default=42)
    split_parser.add_argument("--validate", action="store_true")
    split_parser.add_argument("--dry-run", action="store_true")
    
    # Merge command
    merge_parser = subparsers.add_parser("merge", help="Merge episodes with lerobot_edit_dataset")
    merge_parser.add_argument("--episodes-dir", required=True, help="Directory with episodes to merge")
    merge_parser.add_argument("--repo-id", required=True, help="Target repo ID (e.g., ly/train_merged)")
    merge_parser.add_argument("--push-to-hub", action="store_true")
    merge_parser.add_argument("--conda-env", default="ly_robot")
    merge_parser.add_argument("--proxy", help="Proxy URL (e.g., http://127.0.0.1:10809)")
    
    # Full pipeline command
    full_parser = subparsers.add_parser("full", help="Full pipeline: merge all episodes")
    full_parser.add_argument("--data-dir", required=True, help="Directory with raw episodes")
    full_parser.add_argument("--repo-prefix", default="train", help="Repo ID prefix")
    full_parser.add_argument("--conda-env", default="ly_robot")
    full_parser.add_argument("--proxy", help="Proxy URL")
    
    args = parser.parse_args()
    
    if args.command == "split":
        return cmd_split(args)
    elif args.command == "merge":
        return cmd_merge(args)
    elif args.command == "full":
        return cmd_full(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
