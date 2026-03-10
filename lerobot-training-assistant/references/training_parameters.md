# LeRobot Training Parameters Reference

## Core Parameters

### Policy Configuration

**--policy.pretrained_path**
- Default: `lerobot/smolvla_base`
- Description: Path to pretrained model weights
- Can be Hugging Face model ID or local path
- Examples:
  - `lerobot/smolvla_base` (download from HF)
  - `/path/to/local/model`

**--policy.type**
- Default: `smolvla`
- Description: Policy architecture type
- Options: `smolvla`, `vla`, other LeRobot policies

**--policy.load_vlm_weights**
- Default: `true`
- Description: Whether to load vision-language model weights
- Use `false` for training from scratch

**--policy.device**
- Required: `cuda`
- Description: Device to use for training
- Always use `cuda` for GPU training

### Dataset Configuration

**--dataset.repo_id**
- Required: Yes
- Description: Hugging Face dataset ID or local path
- Examples:
  - `hezhenhao/merged_two_data_github`
  - `/data/local_dataset`

**--output_dir**
- Default: `outputs/train`
- Description: Directory to save training outputs
- Checkpoints, logs, and final model will be saved here

**--job_name**
- Default: `train_job`
- Description: Name for this training job
- Used for logging and identification

### Training Hyperparameters

**--batch_size**
- Default: 32
- Description: Batch size for training
- ⚠️ Adjust based on GPU memory:
  - 24GB VRAM: 16-32
  - 16GB VRAM: 8-16
  - 8GB VRAM: 4-8

**--steps**
- Default: 200000
- Description: Total number of training steps
- Longer training = better performance but more time

**--save_freq**
- Default: 10000
- Description: Save checkpoint every N steps
- Recommended: 5000-10000 for long runs

**--eval_freq**
- Default: -1 (disabled)
- Description: Evaluate every N steps
- Use -1 to disable evaluation

**--num_workers**
- Default: 16
- Description: Number of data loading workers
- Adjust based on CPU cores (typically 4-16)

### Optional Parameters

**--wandb.enable**
- Default: `false`
- Description: Enable Weights & Biases logging
- Set to `true` for experiment tracking

**--policy.repo_id**
- Optional: Hugging Face repo for pushing model
- Required if `--policy.push_to_hub=true`

**--policy.push_to_hub**
- Default: `false`
- Description: Push trained model to Hugging Face Hub
- Requires `--policy.repo_id` and HF token

**--policy.train_expert_only**
- Default: `false`
- Description: Train only expert parameters
- Use `true` for fine-tuning

## Example Configurations

### Small Dataset, Quick Test
```bash
lerobot-train \
  --dataset.repo_id=user/small_dataset \
  --batch_size=16 \
  --steps=10000 \
  --save_freq=2000
```

### Full Training on 24GB GPU
```bash
lerobot-train \
  --policy.pretrained_path=lerobot/smolvla_base \
  --dataset.repo_id=user/large_dataset \
  --batch_size=24 \
  --steps=200000 \
  --save_freq=10000 \
  --wandb.enable=true
```

### Fine-tuning Existing Model
```bash
lerobot-train \
  --policy.pretrained_path=user/existing_model \
  --dataset.repo_id=user/new_data \
  --batch_size=32 \
  --steps=50000 \
  --policy.train_expert_only=true
```

## GPU Memory Guidelines

| GPU Model | VRAM | Recommended Batch Size |
|-----------|------|------------------------|
| RTX 3090 | 24GB | 20-32 |
| RTX 4090 | 24GB | 24-32 |
| A100 | 40GB | 32-48 |
| V100 | 32GB | 28-40 |
| RTX 3080 | 10GB | 8-12 |
| RTX 2080 Ti | 11GB | 8-12 |

## Common Parameter Adjustments

### Out of Memory Error
1. Reduce `--batch_size` by half
2. Reduce `--num_workers` to 4-8
3. Use gradient accumulation (if available)

### Slow Training
1. Increase `--batch_size` (if GPU memory allows)
2. Increase `--num_workers` to match CPU cores
3. Use mixed precision training

### Overfitting
1. Decrease `--steps`
2. Add data augmentation (in dataset)
3. Use regularization (in policy config)
