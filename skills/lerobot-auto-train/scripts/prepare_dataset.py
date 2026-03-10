#!/usr/bin/env python3
"""
LeRobot Dataset Preparation Script

Automatically split raw dataset into training and validation sets.
"""

import os
import shutil
import json
import random
import argparse
from pathlib import Path
from typing import List, Tuple


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
    
    Args:
        episodes: List of episode directories
        train_ratio: Ratio of training set (default: 0.8)
        random_seed: Random seed for reproducibility
    
    Returns:
        Tuple of (train_episodes, val_episodes)
    """
    # Shuffle episodes
    random.seed(random_seed)
    shuffled = episodes.copy()
    random.shuffle(shuffled)
    
    # Split
    split_idx = int(len(shuffled) * train_ratio)
    train_episodes = shuffled[:split_idx]
    val_episodes = shuffled[split_idx:]
    
    return train_episodes, val_episodes


def copy_episodes(
    episodes: List[Path],
    target_dir: Path,
    prefix: str = "episode"
) -> int:
    """
    Copy episodes to target directory with sequential naming.
    
    Args:
        episodes: List of episode directories to copy
        target_dir: Target directory
        prefix: Prefix for episode naming
    
    Returns:
        Number of episodes copied
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    
    for i, ep_dir in enumerate(episodes, 1):
        target_ep_dir = target_dir / f"{prefix}_{i:03d}"
        
        # Remove existing directory if exists
        if target_ep_dir.exists():
            shutil.rmtree(target_ep_dir)
        
        # Copy episode
        shutil.copytree(ep_dir, target_ep_dir)
        
    return len(episodes)


def generate_split_info(
    output_file: Path,
    total_episodes: int,
    train_episodes: int,
    val_episodes: int,
    train_ratio: float,
    random_seed: int,
    train_sources: List[str],
    val_sources: List[str]
) -> None:
    """Generate split information JSON file."""
    info = {
        "total_episodes": total_episodes,
        "train_episodes": train_episodes,
        "val_episodes": val_episodes,
        "train_ratio": train_ratio,
        "random_seed": random_seed,
        "train_episode_sources": train_sources,
        "val_episode_sources": val_sources,
        "statistics": {
            "train_size_mb": 0,
            "val_size_mb": 0
        }
    }
    
    with open(output_file, "w") as f:
        json.dump(info, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Prepare LeRobot dataset by splitting into train/val sets"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        required=True,
        help="Directory containing raw episode data"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Output directory for processed data"
    )
    
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="Training set ratio (default: 0.8)"
    )
    
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate episodes before splitting"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without copying"
    )
    
    args = parser.parse_args()
    
    # Convert to Path objects
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    print("="*60)
    print("  LeRobot Dataset Preparation")
    print("="*60)
    print()
    
    # Step 1: Collect episodes
    print(f"📂 Step 1: Collecting episodes from {data_dir}")
    episodes = collect_episodes(data_dir)
    
    if not episodes:
        print(f"❌ No valid episodes found in {data_dir}")
        return 1
    
    print(f"   Found {len(episodes)} episodes")
    print()
    
    # Step 2: Validate episodes (optional)
    if args.validate:
        print("🔍 Step 2: Validating episodes...")
        valid_episodes = []
        for ep in episodes:
            if validate_episode(ep):
                valid_episodes.append(ep)
            else:
                print(f"   ⚠️  Invalid: {ep.name}")
        
        episodes = valid_episodes
        print(f"   Valid episodes: {len(episodes)}")
        print()
    
    # Step 3: Split episodes
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
        print("🔍 Dry run mode - showing split without copying:")
        print()
        print("   Training episodes:")
        for ep in train_episodes:
            print(f"     - {ep.name}")
        print()
        print("   Validation episodes:")
        for ep in val_episodes:
            print(f"     - {ep.name}")
        return 0
    
    # Step 4: Create output directories
    print("📁 Step 4: Creating output directories...")
    train_dir = output_dir / "train"
    val_dir = output_dir / "val"
    
    # Clean old data
    if train_dir.exists():
        print(f"   Removing existing train directory...")
        shutil.rmtree(train_dir)
    if val_dir.exists():
        print(f"   Removing existing val directory...")
        shutil.rmtree(val_dir)
    
    print(f"   Train: {train_dir}")
    print(f"   Val: {val_dir}")
    print()
    
    # Step 5: Copy episodes
    print("💾 Step 5: Copying episodes...")
    
    print(f"\n   Copying training set ({len(train_episodes)} episodes):")
    train_count = copy_episodes(train_episodes, train_dir, "episode")
    
    print(f"\n   Copying validation set ({len(val_episodes)} episodes):")
    val_count = copy_episodes(val_episodes, val_dir, "episode")
    
    print()
    
    # Step 6: Generate split info
    print("📄 Step 6: Generating split information...")
    split_info_file = output_dir / "split_info.json"
    
    generate_split_info(
        split_info_file,
        total_episodes=len(episodes),
        train_episodes=train_count,
        val_episodes=val_count,
        train_ratio=args.train_ratio,
        random_seed=args.random_seed,
        train_sources=[ep.name for ep in train_episodes],
        val_sources=[ep.name for ep in val_episodes]
    )
    
    print(f"   Saved: {split_info_file}")
    print()
    
    # Step 7: Summary
    print("="*60)
    print("✅ Dataset preparation complete!")
    print("="*60)
    print(f"Training set:   {train_dir} ({train_count} episodes)")
    print(f"Validation set: {val_dir} ({val_count} episodes)")
    print(f"Split info:     {split_info_file}")
    print()
    print("Next steps:")
    print(f"  1. Train with: --data-sources {train_dir}")
    print(f"  2. Validate with: --validation-data {val_dir}")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    exit(main())
