# Task States Reference

## State Machine

```
pending → preparing_data → initializing → training → validating → exporting → completed
   ↓           ↓               ↓            ↓           ↓            ↓
   └───────────┴───────────────┴────────────┴───────────┴────────────→ failed
                                                ↓
                                            stopped
                                                ↓
                                            paused
```

## State Definitions

| State | Description | Transitions To |
|-------|-------------|----------------|
| `pending` | Task submitted, waiting in queue | `preparing_data`, `failed` |
| `preparing_data` | Loading and merging data sources | `initializing`, `failed` |
| `initializing` | Setting up training configuration | `training`, `failed` |
| `training` | Active training loop running | `validating`, `failed`, `stopped`, `paused` |
| `validating` | Running model validation | `exporting`, `failed` |
| `exporting` | Exporting model for inference | `completed`, `failed` |
| `completed` | Training finished successfully | (terminal) |
| `failed` | Training encountered error | (terminal, can retry) |
| `stopped` | User manually stopped | `paused` (can resume) |
| `paused` | Task paused, checkpoint saved | `training` (can resume) |

## State Durations

Typical time in each state (varies by task):

| State | Typical Duration |
|-------|------------------|
| `pending` | Seconds to minutes (queue wait) |
| `preparing_data` | Minutes to hours (depends on data size) |
| `initializing` | Seconds |
| `training` | Hours to days |
| `validating` | Minutes |
| `exporting` | Seconds to minutes |
| `completed` | Terminal |

## Progress Tracking

### During Training (`training` state)

Progress metadata includes:

```json
{
  "current_epoch": 45,
  "total_epochs": 100,
  "train_loss": 0.234,
  "val_loss": 0.198,
  "best_val_loss": 0.195,
  "elapsed_time": "2h 15m",
  "estimated_remaining": "2h 45m"
}
```

### Resource Monitoring

```json
{
  "gpu_utilization": "85%",
  "gpu_memory_used": "7.2GB / 12GB",
  "cpu_usage": "45%"
}
```

## State Transition Triggers

### Automatic Transitions

- Task starts → `pending` → `preparing_data`
- Data ready → `preparing_data` → `initializing`
- Init complete → `initializing` → `training`
- Epochs complete → `training` → `validating`
- Validation complete → `validating` → `exporting`
- Export complete → `exporting` → `completed`
- Error occurs → any → `failed`
- SIGTERM received → `training` → `paused`

### Manual Transitions

- User stops → `training` → `stopped`
- User resumes → `stopped`/`paused` → `training`

## Terminal States

Tasks cannot transition from terminal states:

- `completed`: Success, no further action needed
- `failed`: Error, may retry with `--resume` or investigate logs
- `stopped`: User stopped, can resume from checkpoint

## Recovery from Failure

### Automatic Recovery

1. Training interrupted (Ctrl+C/SIGTERM) → `paused`
2. Checkpoint automatically saved
3. Resume with: `task_manager.py resume <task_id>`

### Manual Recovery from `failed`

1. Check logs: `task_manager.py logs <task_id>`
2. Fix the error (e.g., data issue, config error)
3. Resume: `task_manager.py resume <task_id>`
4. Or submit new task with fixes

## Status Query Examples

```bash
# Check task status
python task_manager.py status train_20260310_143000_abc123

# List all training tasks
python task_manager.py list --status training

# Watch task progress
python progress_monitor.py train_20260310_143000_abc123

# Get JSON status
python progress_monitor.py train_20260310_143000_abc123 --json
```
