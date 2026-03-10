# Configuration Schema

## Task Submission Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `task_type` | string | Training type: "bc" or "rl" | `"bc"` |
| `data_sources` | list | Data source paths/URLs | `["data/episode1.h5", "hf://dataset/v2"]` |
| `model_name` | string | Model architecture | `"smolvla_base"` |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_dir` | string | `"./output"` | Output directory for model/logs |
| `epochs` | int | 100 | Training epochs |
| `batch_size` | int | 32 | Batch size |
| `learning_rate` | float | 0.001 | Learning rate |
| `device` | string | `"cuda"` | Device: cuda/cpu |
| `background` | bool | true | Background execution |
| `progress_interval` | int | 60 | Progress update interval (seconds) |
| `priority` | int | 5 | Task priority (1-10) |
| `notify_on_complete` | bool | false | Notification on completion |

### Advanced Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `save_freq` | int | 10 | Checkpoint save frequency (epochs) |
| `eval_freq` | int | 10 | Validation frequency (epochs) |
| `num_workers` | int | 4 | Data loader workers |
| `wandb_enable` | bool | false | Enable Weights & Biases logging |
| `push_to_hub` | bool | false | Push model to HuggingFace Hub |
| `train_expert_only` | bool | false | Train only expert network |

## Task Metadata Schema

### Structure

```json
{
  "task_id": "train_20260310_143000_abc123",
  "task_type": "bc",
  "status": "training",
  "priority": 5,
  "config": {
    "data_sources": ["data/episode1.h5"],
    "model_name": "smolvla_base",
    "output_dir": "./output",
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001,
    "device": "cuda"
  },
  "execution": {
    "background": true,
    "progress_interval": 60,
    "notify_on_complete": false
  },
  "progress": {
    "current_epoch": 45,
    "total_epochs": 100,
    "train_loss": 0.234,
    "val_loss": 0.198,
    "best_val_loss": 0.195,
    "elapsed_time": "2h 15m",
    "estimated_remaining": "2h 45m"
  },
  "resource": {
    "gpu_utilization": "85%",
    "gpu_memory_used": "7.2GB / 12GB",
    "cpu_usage": "45%"
  },
  "timestamps": {
    "submitted": "2026-03-10T14:30:00",
    "started": "2026-03-10T14:30:05",
    "completed": null
  },
  "pid": 12345,
  "log_file": "~/.openclaw/tasks/train_20260310_143000_abc123/training_train_20260310_143000_abc123.log",
  "checkpoint_dir": "./output/checkpoints"
}
```

### Field Descriptions

#### Top-Level Fields

- `task_id`: Unique identifier (format: `train_<timestamp>_<uuid>`)
- `task_type`: Training type ("bc" or "rl")
- `status`: Current task state (see task_states.md)
- `priority`: Task priority (1-10, higher = more important)

#### `config` Object

Training configuration parameters (immutable after submission).

#### `execution` Object

Execution settings:
- `background`: Whether task runs in background
- `progress_interval`: How often progress updates (seconds)
- `notify_on_complete`: Whether to notify on completion

#### `progress` Object

Real-time training progress:
- `current_epoch`: Current epoch number
- `total_epochs`: Total epochs to train
- `train_loss`: Current training loss
- `val_loss`: Current validation loss
- `best_val_loss`: Best validation loss achieved
- `elapsed_time`: Time since training started (human-readable)
- `estimated_remaining`: Estimated time to completion

#### `resource` Object

Resource utilization:
- `gpu_utilization`: GPU utilization percentage
- `gpu_memory_used`: GPU memory usage (used / total)
- `cpu_usage`: CPU usage percentage

#### `timestamps` Object

Important timestamps (ISO 8601 format):
- `submitted`: When task was submitted
- `started`: When training started
- `completed`: When training completed (null if not completed)

#### `error` Object (Optional)

Present only if status is `failed`:

```json
{
  "error": {
    "message": "CUDA out of memory",
    "traceback": "...",
    "timestamp": "2026-03-10T16:45:00"
  }
}
```

## Environment Check Report Schema

```json
{
  "environment_check": {
    "in_lerobot_repo": true,
    "python_env_active": true,
    "cuda_available": true,
    "cuda_version": "12.1",
    "dependencies": {
      "status": "complete",
      "installed": ["torch", "numpy", "gym", "lerobot"],
      "missing": [],
      "can_auto_install": true
    },
    "configs": {
      "status": "ok",
      "training_config": "exists",
      "model_def": "exists"
    },
    "overall_status": "ready",
    "fix_suggestions": []
  }
}
```

### Status Values

- `overall_status`:
  - `ready`: All checks passed, can start training
  - `needs_fix`: Some issues, can auto-fix or manual fix
  - `failed`: Critical issues, cannot proceed

- `dependencies.status`:
  - `complete`: All dependencies installed
  - `incomplete`: Missing dependencies
  - `unknown`: Check not performed

- `configs.status`:
  - `ok`: All config files present
  - `incomplete`: Some configs missing

## Data Source Formats

### Local Paths

```json
{
  "data_sources": [
    "/absolute/path/to/data.h5",
    "relative/path/to/episode1.h5",
    "data/episode2.h5"
  ]
}
```

### HuggingFace Datasets

```json
{
  "data_sources": [
    "hf://username/dataset-name",
    "lerobot/pusht"
  ]
}
```

### Remote URLs

```json
{
  "data_sources": [
    "https://example.com/data/episode1.h5",
    "s3://bucket/data/episode2.h5"
  ]
}
```

## Example Usage

### Submit Training Task

```bash
python task_manager.py submit \
  --task-type bc \
  --data-sources data/episode1.h5 data/episode2.h5 \
  --model-name smolvla_base \
  --epochs 100 \
  --batch-size 32 \
  --learning-rate 0.001 \
  --output-dir ./output/my_training \
  --background \
  --progress-interval 60 \
  --priority 7 \
  --notify-on-complete
```

### Minimal Submission

```bash
python task_manager.py submit \
  --task-type bc \
  --data-sources data/episodes.h5 \
  --model-name smolvla_base
```

### Query Task Status

```bash
# JSON output
python task_manager.py status train_20260310_143000_abc123

# Human-readable monitoring
python progress_monitor.py train_20260310_143000_abc123
```

### Environment Check

```bash
# Full check
python check_environment.py

# JSON output
python check_environment.py --json

# Auto-fix
python check_environment.py --auto-fix
```

## Configuration Files

### Training Config (YAML)

Location: `config/training_config.yaml`

```yaml
model:
  name: smolvla_base
  pretrained_path: lerobot/smolvla_base

training:
  epochs: 100
  batch_size: 32
  learning_rate: 0.001
  device: cuda

checkpoint:
  save_freq: 10
  eval_freq: 10

logging:
  wandb_enable: false
  tensorboard: true
```

### Default Config

Location: `config/training_config.default.yaml`

Copy and customize:
```bash
cp config/training_config.default.yaml config/training_config.yaml
```
