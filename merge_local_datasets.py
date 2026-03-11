#!/usr/bin/env python3
"""
合并本地 LeRobot 数据集

用法:
    python3 merge_local_datasets.py \
        --input-dir /path/to/episodes \
        --output-dir /path/to/merged \
        --pattern "episode_*"
"""

import argparse
import json
import shutil
from pathlib import Path
from typing import List, Dict
import pyarrow.parquet as pq
import pyarrow as pa


def merge_local_datasets(
    input_dir: Path,
    output_dir: Path,
    pattern: str = "episode_*",
):
    """
    合并本地 LeRobot 数据集
    
    Args:
        input_dir: 包含多个 episode 数据集的目录
        output_dir: 输出目录
        pattern: episode 目录的匹配模式
    """
    print("="*60)
    print("  📦 合并本地 LeRobot 数据集")
    print("="*60)
    print()
    
    # 1. 查找所有 episode 目录
    print(f"1️⃣ 查找 episode 目录 (pattern: {pattern})...")
    episode_dirs = sorted(input_dir.glob(pattern))
    
    if not episode_dirs:
        print(f"❌ 没有找到匹配的目录")
        return
    
    print(f"✅ 找到 {len(episode_dirs)} 个 episodes:")
    for ep_dir in episode_dirs[:5]:
        print(f"   - {ep_dir.name}")
    if len(episode_dirs) > 5:
        print(f"   ... 还有 {len(episode_dirs) - 5} 个")
    print()
    
    # 2. 验证每个 episode 都是完整的 LeRobot 数据集
    print("2️⃣ 验证数据集格式...")
    valid_episodes = []
    for ep_dir in episode_dirs:
        required = [
            ep_dir / "meta" / "info.json",
            ep_dir / "data",
        ]
        if all(p.exists() for p in required):
            valid_episodes.append(ep_dir)
        else:
            print(f"   ⚠️  跳过 {ep_dir.name} (不完整)")
    
    print(f"✅ 有效 episodes: {len(valid_episodes)}")
    print()
    
    if not valid_episodes:
        print("❌ 没有有效的数据集")
        return
    
    # 3. 读取第一个 episode 的 meta 信息作为模板
    print("3️⃣ 读取元数据...")
    with open(valid_episodes[0] / "meta" / "info.json") as f:
        meta_info = json.load(f)
    
    print(f"   Robot type: {meta_info.get('robot_type')}")
    print(f"   FPS: {meta_info.get('fps')}")
    print()
    
    # 4. 创建输出目录
    print("4️⃣ 创建输出目录...")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "data" / "chunk-000").mkdir(parents=True, exist_ok=True)
    (output_dir / "meta").mkdir(parents=True, exist_ok=True)
    
    # 复制 videos 目录（如果存在）
    if (valid_episodes[0] / "videos").exists():
        (output_dir / "videos").mkdir(parents=True, exist_ok=True)
    
    print(f"✅ 输出目录: {output_dir}")
    print()
    
    # 5. 合并数据
    print("5️⃣ 合并数据...")
    all_data = []
    episode_index_offset = 0
    frame_index_offset = 0
    total_frames = 0
    total_episodes = len(valid_episodes)
    
    for i, ep_dir in enumerate(valid_episodes):
        print(f"   处理 {ep_dir.name} ({i+1}/{total_episodes})...", end=" ")
        
        # 读取数据
        data_files = list((ep_dir / "data" / "chunk-000").glob("*.parquet"))
        if data_files:
            table = pq.read_table(data_files[0])
            df = table.to_pandas()
            
            # 更新 index
            if 'episode_index' in df.columns:
                df['episode_index'] = df['episode_index'] + episode_index_offset
            if 'frame_index' in df.columns:
                df['frame_index'] = df['frame_index'] + frame_index_offset
            if 'index' in df.columns:
                df['index'] = df['index'] + frame_index_offset
            
            all_data.append(df)
            total_frames += len(df)
            
            # 更新 offset
            episode_index_offset += 1
            frame_index_offset += len(df)
        
        print("✅")
    
    print()
    
    # 6. 合并并写入
    print("6️⃣ 写入合并数据...")
    if all_data:
        import pandas as pd
        merged_df = pd.concat(all_data, ignore_index=True)
        merged_table = pa.Table.from_pandas(merged_df)
        pq.write_table(
            merged_table,
            output_dir / "data" / "chunk-000" / "file-000.parquet"
        )
        print(f"✅ 写入 {len(merged_df)} frames")
    print()
    
    # 7. 更新 meta 信息
    print("7️⃣ 更新元数据...")
    meta_info['total_episodes'] = total_episodes
    meta_info['total_frames'] = total_frames
    meta_info['splits'] = {"train": f"0:{total_episodes}"}
    
    with open(output_dir / "meta" / "info.json", 'w') as f:
        json.dump(meta_info, f, indent=4)
    
    print(f"✅ 总 episodes: {total_episodes}")
    print(f"✅ 总 frames: {total_frames}")
    print()
    
    # 8. 复制 videos（简单方式：复制第一个 episode 的 videos 结构）
    print("8️⃣ 处理 videos...")
    # 这里简化处理，实际可能需要更复杂的逻辑
    print("⚠️  Videos 需要手动处理或使用 lerobot 的完整 merge 功能")
    print()
    
    print("="*60)
    print("  ✅ 合并完成！")
    print("="*60)
    print(f"输出目录: {output_dir}")
    print(f"Episodes: {total_episodes}")
    print(f"Frames: {total_frames}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="合并本地 LeRobot 数据集")
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="包含多个 episode 数据集的目录"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="输出目录"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="episode_*",
        help="episode 目录的匹配模式 (默认: episode_*)"
    )
    
    args = parser.parse_args()
    
    merge_local_datasets(
        input_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir),
        pattern=args.pattern,
    )


if __name__ == "__main__":
    main()
