---
name: lerobot-training-assistant
description: Conversational assistant for distributed LeRobot training across LAN GPU nodes. Use when users want to: (1) Start or configure LeRobot training jobs, (2) Find and select available GPU nodes in the network, (3) Review training parameters with guidance, (4) Access historical training experiences and troubleshooting tips, (5) Deploy training scripts to remote machines via SSH. Triggers on keywords like "训练模型", "GPU训练", "LeRobot", "分布式训练", "训练助手".
---

# Lerobot Training Assistant

## Overview

This skill provides a conversational interface for managing LeRobot training jobs across local GPU clusters. It guides users through parameter configuration, node selection, and deployment while maintaining a memory system that shares experiences across users.

## Training Workflow

### Step 1: Initial Request and Node Scanning

When a user requests training:

1. **Scan GPU nodes** in the LAN using `scripts/scan_gpu_nodes.py`
2. **Check GPU availability** using `scripts/check_gpu_status.py`
3. **Present available nodes** with their specs:
   ```
   ✅ Found 3 available GPU nodes:
   - 192.168.136.80 (RTX 3090, 24GB, GPU utilization: 5%)
   - 192.168.136.168 (RTX 4090, 24GB, GPU utilization: 0%)
   - 192.168.136.200 (A100, 40GB, GPU utilization: 10%)
   ```

### Step 2: Conversational Parameter Configuration

Guide users through training parameters using natural dialogue:

**Ask about:**
1. **Dataset**: "使用默认数据集 `hezhenhao/merged_two_data_github` 吗？还是指定其他数据集？"
2. **Batch size**: "Batch size 默认 32。⚠️ 上次用户遇到 GPU 内存不足，建议改为 16。你想用多少？"
3. **Training steps**: "训练步数默认 200000，还是其他？"
4. **Output directory**: "输出目录使用默认 `outputs/mylerobot_train/` 吗？"
5. **Node selection**: "选择哪台电脑训练？（推荐 RTX 4090）"

**Reference historical issues** from memory:
- Check `scripts/memory_manager.py` for past problems
- Warn about GPU memory constraints
- Suggest proven configurations

### Step 3: Command Generation and Deployment

After configuration:

1. **Generate training command**:
   ```bash
   lerobot-train \
     --policy.pretrained_path=lerobot/smolvla_base \
     --policy.type=smolvla \
     --dataset.repo_id=<user_dataset> \
     --output_dir=<output_dir> \
     --batch_size=<batch_size> \
     --steps=<steps> \
     --policy.device=cuda
   ```

2. **Deploy via SSH** using `scripts/deploy_and_train.py`
3. **Monitor training** using `scripts/monitor_training.py`

### Step 4: Memory Recording

After training (or if issues occur):

1. **Record experience** using `scripts/memory_manager.py`:
   - User IP (from LAN node identification)
   - Configuration used
   - Problems encountered
   - Solutions applied
   - Success/failure status

2. **Upload to GitHub** repository for shared memory

## Key Parameters Reference

See `references/training_parameters.md` for complete parameter documentation.

**Essential parameters:**
- `--policy.pretrained_path`: Pretrained model (default: `lerobot/smolvla_base`)
- `--dataset.repo_id`: Hugging Face dataset or local path
- `--output_dir`: Training output directory
- `--batch_size`: Batch size (adjust based on GPU memory)
- `--steps`: Total training steps
- `--save_freq`: Save checkpoint frequency
- `--policy.device=cuda`: Use GPU

## Historical Memory System

The skill maintains a shared memory of training experiences:

- **Storage**: Automatically uploaded to GitHub repository `NiceLy235/training-memories`
- **User identification**: By LAN IP address
- **Content**: Problems, solutions, recommended configurations
- **Access**: See `scripts/memory_manager.py`

When new users start training, the assistant:
1. Checks historical issues from similar configurations
2. Warns about known problems
3. Suggests proven parameter combinations

### GitHub Configuration

The skill is pre-configured to use the repository: `NiceLy235/training-memories`

Configuration file: `github_config.json`

To update GitHub settings, edit this file with your credentials.

## Resources

### scripts/

**GPU Management:**
- `scan_gpu_nodes.py` - Scan LAN for GPU nodes
- `check_gpu_status.py` - Check GPU utilization and memory

**Training Execution:**
- `deploy_and_train.py` - SSH deploy and start training
- `monitor_training.py` - Monitor training progress

**Memory System:**
- `memory_manager.py` - Manage and upload training memories

### references/

- `training_parameters.md` - Complete parameter reference
- `troubleshooting.md` - Common issues and solutions
- `memory_schema.md` - Memory data structure

### assets/

- `config_templates/default_training.yaml` - Default configuration template
