# Training Memory Schema

This document defines the data structure for training experiences and memories.

## User Identification

### current_user.json

Tracks users by their LAN IP addresses.

```json
{
  "192.168.136.168": {
    "user_id": "user_1",
    "first_seen": "2026-03-05T10:00:00",
    "last_seen": "2026-03-05T14:30:00",
    "training_count": 3
  },
  "192.168.136.200": {
    "user_id": "user_2",
    "first_seen": "2026-03-05T11:00:00",
    "last_seen": "2026-03-05T12:00:00",
    "training_count": 1
  }
}
```

**Fields:**
- `user_id`: Unique identifier (user_1, user_2, etc.)
- `first_seen`: ISO timestamp of first training request
- `last_seen`: ISO timestamp of most recent activity
- `training_count`: Number of training jobs started

## Training Experience

### memory_YYYY-MM-DD.json

Daily memory files store individual training experiences.

```json
[
  {
    "timestamp": "2026-03-05T10:24:15.123456",
    "user_id": "user_1",
    "user_ip": "192.168.136.168",
    "config": {
      "pretrained_path": "lerobot/smolvla_base",
      "policy_type": "smolvla",
      "dataset": "hezhenhao/merged_two_data_github",
      "output_dir": "outputs/mylerobot_train/0106_smolvla_000",
      "batch_size": 32,
      "steps": 200000,
      "save_freq": 10000,
      "num_workers": 16,
      "wandb_enable": false
    },
    "issue": "CUDA out of memory after 500 steps",
    "solution": "Reduced batch_size from 32 to 16",
    "status": "resolved",
    "notes": "RTX 3090 24GB can handle batch_size=16 with this model",
    "gpu_info": "RTX 3090, 24GB"
  },
  {
    "timestamp": "2026-03-05T14:00:00.000000",
    "user_id": "user_1",
    "user_ip": "192.168.136.168",
    "config": {
      "pretrained_path": "lerobot/smolvla_base",
      "policy_type": "smolvla",
      "dataset": "hezhenhao/merged_two_data_github",
      "batch_size": 16,
      "steps": 200000
    },
    "issue": null,
    "solution": null,
    "status": "success",
    "notes": "Training completed successfully in 12 hours",
    "gpu_info": "RTX 4090, 24GB"
  }
]
```

**Experience Fields:**
- `timestamp`: ISO timestamp of the experience
- `user_id`: Reference to user
- `user_ip`: User's LAN IP (for quick lookup)
- `config`: Training configuration used
- `issue`: Problem encountered (null if none)
- `solution`: How the problem was solved (null if none)
- `status`: One of "success", "failed", "resolved"
- `notes`: Additional context or observations
- `gpu_info`: GPU model and memory

## Configuration Schema

### config object

```json
{
  "pretrained_path": "string",
  "policy_type": "string",
  "load_vlm_weights": "boolean",
  "dataset": "string",
  "output_dir": "string",
  "job_name": "string",
  "batch_size": "integer",
  "steps": "integer",
  "save_freq": "integer",
  "eval_freq": "integer",
  "num_workers": "integer",
  "wandb_enable": "boolean",
  "policy_repo_id": "string (optional)",
  "push_to_hub": "boolean",
  "train_expert_only": "boolean",
  "gpu_info": "string (optional)"
}
```

## Status Values

- `success`: Training completed without issues
- `failed`: Training failed and was not resolved
- `resolved`: Training had issues but they were fixed

## Common Issues Catalog

### GPU Memory Issues
- `"CUDA out of memory"`
- `"RuntimeError: CUDA error: out of memory"`
- `"GPU memory exceeded"`

### Dataset Issues
- `"Dataset not found"`
- `"Failed to download dataset"`
- `"Data loading error"`

### Network Issues
- `"Connection timeout"`
- `"SSH connection failed"`
- `"Permission denied"`

### Training Issues
- `"Loss is NaN"`
- `"Training not converging"`
- `"Gradient explosion"`

## GitHub Repository Structure

When memories are uploaded to GitHub:

```
training-memories/
├── current_user.json
├── training_memories/
│   ├── memory_2026-03-05.json
│   ├── memory_2026-03-04.json
│   └── ...
└── README.md
```

## Query Patterns

### By User
```python
experiences = [e for e in all_experiences if e['user_ip'] == '192.168.136.168']
```

### By Issue Type
```python
oom_issues = [e for e in all_experiences if 'out of memory' in str(e.get('issue', ''))]
```

### By Status
```python
successful = [e for e in all_experiences if e['status'] == 'success']
```

### By GPU Model
```python
rtx4090 = [e for e in all_experiences if 'RTX 4090' in e.get('gpu_info', '')]
```

## Data Retention

- Daily files are kept indefinitely
- Old files can be compressed after 30 days
- Summary statistics can be extracted monthly
- Critical issues should be preserved even if old

## Privacy Considerations

- User IPs are stored for identification only
- No personal information beyond IP and training config
- Users can request deletion of their data
- GitHub repo should be private if training data is sensitive
