# Dataset Preparation Guide

This guide explains how to prepare datasets for training with lerobot-auto-train.

## Overview

Before training, you need to split your raw data into training and validation sets. This ensures:
- ✅ Proper model evaluation during training
- ✅ Prevents overfitting
- ✅ Reproducible experiments

## Quick Start

```bash
python scripts/prepare_dataset.py \
  --data-dir /path/to/raw_data \
  --output-dir ./processed_data \
  --train-ratio 0.8
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--data-dir` | (required) | Directory containing raw episode data |
| `--output-dir` | (required) | Output directory for processed data |
| `--train-ratio` | 0.8 | Training set ratio (0.0-1.0) |
| `--random-seed` | 42 | Random seed for reproducibility |
| `--validate` | false | Validate episodes before splitting |
| `--dry-run` | false | Show split without copying |

## Input Structure

Your raw data directory should contain LeRobot episode directories:

```
/path/to/raw_data/
├── episode_001/
│   ├── data/
│   ├── meta/
│   │   ├── info.json
│   │   └── stats.json
│   └── videos/
├── episode_002/
├── episode_003/
└── ...
```

**Required files**:
- `meta/info.json` - Episode metadata
- `data/` - Episode data (parquet files)

## Output Structure

After running `prepare_dataset.py`:

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

### split_info.json

Contains split details:

```json
{
  "total_episodes": 15,
  "train_episodes": 12,
  "val_episodes": 3,
  "train_ratio": 0.8,
  "random_seed": 42,
  "train_episode_sources": ["episode_3", "episode_8", ...],
  "val_episode_sources": ["episode_0", "episode_1", ...]
}
```

## Usage Examples

### Basic Usage

```bash
# Split with default 80/20 ratio
python scripts/prepare_dataset.py \
  --data-dir ~/data/raw_episodes \
  --output-dir ./processed_data
```

### Custom Split Ratio

```bash
# 90% training, 10% validation
python scripts/prepare_dataset.py \
  --data-dir ~/data/raw_episodes \
  --output-dir ./processed_data \
  --train-ratio 0.9
```

### With Validation

```bash
# Validate episodes before splitting
python scripts/prepare_dataset.py \
  --data-dir ~/data/raw_episodes \
  --output-dir ./processed_data \
  --validate
```

### Dry Run (Preview)

```bash
# See what would be done without copying
python scripts/prepare_dataset.py \
  --data-dir ~/data/raw_episodes \
  --output-dir ./processed_data \
  --dry-run
```

## Training with Prepared Data

After preparing your dataset:

### Training Only

```bash
python scripts/task_manager.py submit \
  --data-sources ./processed_data/train/ \
  --model-name smolvla_base \
  --epochs 100
```

### Training with Validation

```bash
python scripts/task_manager.py submit \
  --data-sources ./processed_data/train/ \
  --validation-data ./processed_data/val/ \
  --model-name smolvla_base \
  --epochs 100
```

## Best Practices

### 1. Split Ratio

- **Small datasets (<100 episodes)**: Use 80/20 split
- **Medium datasets (100-1000)**: Use 90/10 split
- **Large datasets (>1000)**: Use 95/5 split

### 2. Random Seed

Always use a fixed random seed for reproducibility:

```bash
--random-seed 42
```

### 3. Validation

Use `--validate` flag to ensure data quality:

```bash
--validate
```

### 4. Check Output

Always verify the split:

```bash
# Check episode counts
ls processed_data/train/ | wc -l
ls processed_data/val/ | wc -l

# Check split info
cat processed_data/split_info.json
```

## Common Issues

### Issue: No episodes found

**Cause**: Incorrect data directory structure

**Solution**:
```bash
# Check directory structure
ls -la /path/to/raw_data/

# Ensure episodes have meta/info.json
find /path/to/raw_data -name "info.json"
```

### Issue: Invalid episodes

**Cause**: Missing required files

**Solution**:
```bash
# Use --validate to check
python scripts/prepare_dataset.py \
  --data-dir /path/to/raw_data \
  --output-dir ./processed_data \
  --validate
```

### Issue: Uneven split

**Cause**: Small number of episodes

**Solution**:
- Use at least 10 episodes for meaningful split
- Consider using cross-validation for very small datasets

## Advanced Usage

### Multiple Datasets

```bash
# Prepare multiple datasets
for dataset in dataset1 dataset2 dataset3; do
  python scripts/prepare_dataset.py \
    --data-dir ~/data/$dataset \
    --output-dir ./processed_$dataset \
    --random-seed 42
done
```

### Custom Random Seeds

```bash
# Different random seeds for experiments
for seed in 42 123 456; do
  python scripts/prepare_dataset.py \
    --data-dir ~/data/raw_episodes \
    --output-dir ./processed_data_seed_$seed \
    --random-seed $seed
done
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No episodes found | Check data directory structure |
| Invalid episodes | Use `--validate` flag |
| Low episode count | Ensure enough data (≥10 episodes) |
| Copy errors | Check disk space and permissions |
| Slow copying | Use SSD for better performance |

## Next Steps

After preparing your dataset:

1. ✅ Verify split quality: `cat processed_data/split_info.json`
2. ✅ Start training: `python scripts/task_manager.py submit ...`
3. ✅ Monitor progress: `python scripts/progress_monitor.py <task_id>`
4. ✅ Test model: `python scripts/inference_test.py output/model.pt full`
