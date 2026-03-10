---
name: lerobot-auto-train
description: >
  Automate lerobot_ros2 training and inference workflows with background task
  execution and real-time progress monitoring. Use when users want to: (1) Train
  models on GPU with automated pipeline, (2) Run training tasks in background
  while continuing other work, (3) Monitor training progress in real-time,
  (4) Test trained models with inference validation, (5) Manage training tasks
  (submit/stop/resume). Triggers on keywords like "训练模型", "训练任务",
  "GPU训练", "lerobot训练", "自动化训练", "后台训练", "训练监控", "推理测试".
---

# Lerobot Auto Train

Automate complete training lifecycle: data preparation → training → validation → inference testing.

**Key Features**:
- ✅ Background task execution (non-blocking)
- ✅ Real-time progress monitoring
- ✅ Automatic checkpoint and recovery
- ✅ Environment validation
- ✅ Inference testing
- ✅ Automatic validation during training
- ✅ Loss curve visualization

## Prerequisites

**CRITICAL**: Tasks MUST run inside `lerobot_ros2` repository.

Before starting:
```bash
cd /path/to/lerobot_ros2
```

## Quick Start

### 0. Prepare Dataset

**CRITICAL**: Prepare training/validation split BEFORE training.

**Minimal** (with auto-split):
```bash
python scripts/prepare_dataset.py \
  --data-dir /path/to/raw_data \
  --output-dir ./processed_data \
  --train-ratio 0.8
```

**Full parameters**:
```bash
python scripts/prepare_dataset.py \
  --data-dir /path/to/raw_data \
  --output-dir ./processed_data \
  --train-ratio 0.8 \
  --random-seed 42 \
  --validate
```

**What it does**:
1. Scans all episodes in `--data-dir`
2. Randomly splits into train/val sets
3. Copies to `--output-dir/train/` and `--output-dir/val/`
4. Generates `split_info.json` with split details

**Output structure**:
```
processed_data/
├── train/
│   ├── episode_001/
│   ├── episode_002/
│   └── ...
├── val/
│   ├── episode_001/
│   └── ...
└── split_info.json
```

**For training**, use:
```bash
--data-sources processed_data/train/
```

**For validation**, use:
```bash
--validation-data processed_data/val/
```

### 1. Check Environment

Always verify environment first:

```bash
python scripts/check_environment.py
```

**With auto-fix**:
```bash
python scripts/check_environment.py --auto-fix
```

**JSON output** (for scripts):
```bash
python scripts/check_environment.py --json
```

### 2. Submit Training Task

**Minimal**:
```bash
python scripts/task_manager.py submit \
  --task-type bc \
  --data-sources data/episodes.h5 \
  --model-name smolvla_base
```

**Full parameters**:
```bash
python scripts/task_manager.py submit \
  --task-type bc \
  --data-sources data/ep1.h5 data/ep2.h5 \
  --model-name smolvla_base \
  --output-dir ./output/my_training \
  --epochs 100 \
  --batch-size 32 \
  --learning-rate 0.001 \
  --device cuda \
  --background \
  --progress-interval 60 \
  --priority 7 \
  --notify-on-complete
```

**Returns**: Task ID (e.g., `train_20260310_143000_abc123`)

### 3. Monitor Progress

**Real-time monitoring**:
```bash
python scripts/progress_monitor.py <task_id>
```

**JSON status** (one-shot):
```bash
python scripts/progress_monitor.py <task_id> --json
```

### 4. Manage Tasks

**Check status**:
```bash
python scripts/task_manager.py status <task_id>
```

**List tasks**:
```bash
python scripts/task_manager.py list
python scripts/task_manager.py list --status training
```

**Stop task**:
```bash
python scripts/task_manager.py stop <task_id>
```

**Resume task**:
```bash
python scripts/task_manager.py resume <task_id>
```

**View logs**:
```bash
python scripts/task_manager.py logs <task_id> --lines 100
```

### 5. Inference Testing

After training completes:

**Full test suite**:
```bash
python scripts/inference_test.py ./output/model.pt full --output report.md
```

**Benchmark performance**:
```bash
python scripts/inference_test.py ./output/model.pt benchmark --runs 100
```

**Single inference**:
```bash
python scripts/inference_test.py ./output/model.pt single --input '{"obs": "test"}'
```

## Workflow

### Standard Workflow

1. **Navigate to repo**:
   ```bash
   cd /path/to/lerobot_ros2
   ```

2. **Prepare dataset** (if not already done):
   ```bash
   python scripts/prepare_dataset.py \
     --data-dir /path/to/raw_data \
     --output-dir ./processed_data \
     --train-ratio 0.8 \
     --validate
   ```

3. **Check environment**:
   ```bash
   python scripts/check_environment.py
   ```

4. **Submit task** (runs in background):
   ```bash
   python scripts/task_manager.py submit \
     --data-sources ./processed_data/train/ \
     --validation-data ./processed_data/val/ \
     --background
   ```

5. **Continue other work** while training runs

6. **Check progress** periodically:
   ```bash
   python scripts/progress_monitor.py <task_id>
   ```

7. **Test model** when complete:
   ```bash
   python scripts/inference_test.py ./output/model.pt full
   ```

8. **View loss curves** (auto-generated):
   ```bash
   # Training and validation loss curves
   ls output/loss_curves.png
   ls output/loss_curves_combined.png
   
   # Or manually generate
   python scripts/validate_and_plot.py \
     --output-dir ./output \
     --plot-only
   ```

### Validation During Training

**Automatic validation** happens at every checkpoint save:
- ✅ Validates on validation set
- ✅ Records validation loss
- ✅ Tracks best validation loss
- ✅ Generates loss curves on completion

**Manual validation**:
```bash
python scripts/validate_and_plot.py \
  --model-path ./output/checkpoints/checkpoint_010000.pt \
  --val-data ./processed_data/val/ \
  --output-dir ./output \
  --step 10000 \
  --epoch 10
```

**Plot only** (skip validation):
```bash
python scripts/validate_and_plot.py \
  --output-dir ./output \
  --plot-only
```

**Combined plot** (train + val on same axis):
```bash
python scripts/validate_and_plot.py \
  --output-dir ./output \
  --plot-only \
  --plot-combined
```

**Output files**:
```
output/
├── loss_history.json           # Loss data (train + val)
├── loss_curves.png             # Separate train/val curves
├── loss_curves.pdf             # High-quality PDF
└── loss_curves_combined.png    # Combined train/val curves
```

### Real-Time Feedback Pattern

**IMPORTANT**: Provide real-time feedback during long operations.

When executing long tasks:
1. Start with short `yieldMs` (10-15s)
2. Poll with short timeout (5s)
3. Report progress to user
4. Continue until complete

**Example** (monitoring training):
```javascript
// Start monitoring
exec("python progress_monitor.py <task_id>", { yieldMs: 10000 })

// Poll every 5 seconds
process poll (timeout: 5000)
// → Report: "Epoch 45/100, Loss: 0.234"

process poll (timeout: 5000)
// → Report: "Epoch 50/100, Loss: 0.198"

// Continue until complete
```

## Task States

See `references/task_states.md` for complete state machine.

**Key states**:
- `pending`: Waiting in queue
- `training`: Active training (progress updates)
- `completed`: Success
- `failed`: Error (check logs)
- `paused`: Stopped, can resume

## Error Handling

See `references/error_handling.md` for detailed troubleshooting.

**Common issues**:

### Not in lerobot_ros2 repo
```bash
# Fix: Navigate to repo
cd /path/to/lerobot_ros2
```

### CUDA not available
```bash
# Check driver
nvidia-smi

# Or use CPU
python task_manager.py submit ... --device cpu
```

### GPU OOM
```bash
# Auto-recovery: batch_size reduced automatically
# Manual fix:
python task_manager.py submit ... --batch-size 16
```

### Resume failed task
```bash
# 1. Check logs
python task_manager.py logs <task_id>

# 2. Fix issue

# 3. Resume
python task_manager.py resume <task_id>
```

## Configuration

See `references/config_schema.md` for complete schema.

**Key parameters**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `epochs` | 100 | Training epochs |
| `batch_size` | 32 | Batch size (reduce if OOM) |
| `learning_rate` | 0.001 | Learning rate |
| `device` | cuda | Device (cuda/cpu) |
| `background` | true | Background execution |
| `progress_interval` | 60 | Progress update frequency (s) |

## Scripts Reference

### Environment

- `check_environment.py` - Validate and fix environment

### Data Preparation

- `prepare_dataset.py` - Split dataset into train/val sets

### Task Management

- `task_manager.py` - Submit/manage tasks
- `progress_monitor.py` - Monitor progress

### Training

- `train_worker.py` - Training worker (internal)

### Validation and Plotting

- `validate_and_plot.py` - Validate model and plot loss curves

### Inference

- `inference_test.py` - Test trained models

## Best Practices

1. **Always check environment first**
   ```bash
   python scripts/check_environment.py --dry-run
   ```

2. **Use appropriate batch size**:
   - RTX 4090/3090: 32-64
   - RTX 4080/3080: 16-32
   - Smaller GPUs: 8-16

3. **Monitor training periodically**
   ```bash
   python scripts/progress_monitor.py <task_id>
   ```

4. **Save checkpoints frequently**
   ```bash
   --save-freq 10  # Every 10 epochs
   ```

5. **Test with small dataset first**, then scale up

6. **Use background execution** (--background) for long tasks

## Output Structure

```
output/
├── model.pt              # Final trained model
├── checkpoints/
│   ├── best_model.pt     # Best validation model
│   ├── checkpoint_epoch_10.pt
│   └── checkpoint_epoch_20.pt
├── logs/
│   └── training.log      # Training logs
├── loss_history.json     # Train/val loss history
├── loss_curves.png       # Loss curves (separate)
├── loss_curves.pdf       # High-quality PDF
└── loss_curves_combined.png  # Combined train/val curves

~/.openclaw/tasks/<task_id>/
├── meta.json             # Task metadata
└── training_<task_id>.log # Full log
```

## References

For detailed information:

- **Dataset preparation**: `references/dataset_preparation.md`
- **Loss curve visualization**: `references/loss_curve_visualization.md`
- **Task states**: `references/task_states.md`
- **Error handling**: `references/error_handling.md`
- **Config schema**: `references/config_schema.md`
- **Task template**: `assets/task_meta_template.json`

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Not in repo | `cd /path/to/lerobot_ros2` |
| CUDA unavailable | Check driver, or use `--device cpu` |
| GPU OOM | Reduce `--batch-size` |
| Task failed | Check logs, fix, resume |
| No progress | Check task status |
| Slow training | Monitor GPU utilization |

## Example Session

```bash
# User: "Train a model with episodes 1-5"
# Agent:

"Starting training pipeline..."

# 0. Prepare dataset (if not already done)
$ python scripts/prepare_dataset.py \
  --data-dir data/raw_episodes \
  --output-dir ./processed_data \
  --train-ratio 0.8
📂 Step 1: Collecting episodes...
   Found 5 episodes
📊 Step 3: Splitting dataset (train=80%)
   Training set: 4 episodes
   Validation set: 1 episodes
✅ Dataset preparation complete!
Training set: ./processed_data/train/ (4 episodes)
Validation set: ./processed_data/val/ (1 episodes)

# 1. Check environment
$ python scripts/check_environment.py
✅ Environment ready

# 2. Submit task
$ python scripts/task_manager.py submit \
  --task-type bc \
  --data-sources ./processed_data/train/ \
  --validation-data ./processed_data/val/ \
  --model-name smolvla_base \
  --epochs 100 \
  --background
✅ Task submitted: train_20260310_143000_abc123
🚀 Training started in background

# 3. Monitor (real-time)
$ python scripts/progress_monitor.py train_20260310_143000_abc123
👀 Watching task...
🚀 [███████░░░] 70.0% Epoch 70/100 | Loss: 0.234

# 4. Complete
✅ Training completed!
📊 Best validation loss: 0.195

# 5. Test
$ python scripts/inference_test.py output/model.pt full
✅ Inference test passed
⚡ Throughput: 42.3 FPS
```
