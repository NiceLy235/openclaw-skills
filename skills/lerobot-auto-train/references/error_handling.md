# Error Handling Reference

## Error Categories

### 1. Environment Errors

#### Not in lerobot_ros2 Repository

**Error**: `Not in a git repository` or `Not in lerobot_ros2 repository`

**Cause**: Task submitted from wrong directory

**Fix**:
```bash
cd /path/to/lerobot_ros2
# Or use --repo-path
python check_environment.py --repo-path /path/to/lerobot_ros2
```

**Prevention**: Always check environment before submitting:
```python
python check_environment.py --dry-run
```

---

#### Python Environment Not Active

**Error**: `No virtual environment active`

**Cause**: Virtual environment or conda env not activated

**Fix**:
```bash
# Conda
conda activate myenv

# venv
source venv/bin/activate
```

**Note**: Task can continue without virtual env, but may fail due to missing dependencies

---

#### CUDA Not Available

**Error**: `CUDA not available`

**Cause**:
- NVIDIA driver not installed
- Wrong PyTorch version (CPU-only)
- CUDA version mismatch

**Fix**:
```bash
# Check driver
nvidia-smi

# Check CUDA in PyTorch
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**Alternative**: Use CPU mode:
```bash
python task_manager.py submit ... --device cpu
```

---

#### Missing Dependencies

**Error**: `Missing packages: [...]`

**Cause**: Required packages not installed

**Fix**:
```bash
# Auto-fix
python check_environment.py --auto-fix

# Manual
pip install <missing_packages>
```

---

### 2. Data Errors

#### Data Source Not Found

**Error**: `Data source not found: /path/to/data`

**Cause**: Invalid path or remote URL

**Fix**:
- Check path exists: `ls /path/to/data`
- For HuggingFace datasets, ensure repo exists
- For local data, use absolute paths

**Task Status**: Task continues with available sources, logs warning

---

#### Insufficient Data

**Error**: `Insufficient data: 50 samples (minimum 100)`

**Cause**: Dataset too small for training

**Fix**:
- Add more data sources
- Use data augmentation
- Proceed with warning (user choice)

**Task Status**: `failed` unless user confirms to continue

---

#### Data Format Mismatch

**Error**: `Data format mismatch: expected HDF5, got JSON`

**Cause**: Data format doesn't match expected schema

**Fix**:
- Check data format: `file /path/to/data`
- Convert data to expected format
- Update training config to match data format

**Task Status**: `failed`

---

### 3. Training Errors

#### GPU Out of Memory (OOM)

**Error**: `CUDA out of memory`

**Cause**: Batch size too large for GPU memory

**Auto-Recovery**:
1. Task automatically reduces batch_size (32 → 16 → 8)
2. Retries training
3. Max 3 retries

**Manual Fix**:
```bash
python task_manager.py submit ... --batch-size 16
```

**Prevention**: Check GPU memory before training:
```python
import torch
print(torch.cuda.get_device_properties(0).total_memory / 1024**3, "GB")
```

---

#### Loss Not Converging

**Error**: `Loss not converging after 50 epochs` or `Loss is NaN`

**Cause**:
- Learning rate too high
- Data issues
- Model architecture mismatch

**Fix**:
```bash
# Reduce learning rate
python task_manager.py submit ... --learning-rate 0.0001

# Check data for anomalies
python check_data.py --source /path/to/data
```

**Task Status**: `failed` after threshold epochs

---

#### Training Interrupted

**Error**: Process killed or system shutdown

**Recovery**:
- Checkpoint automatically saved
- Task status: `paused`

**Resume**:
```bash
python task_manager.py resume <task_id>
```

---

### 4. Inference Errors

#### Model Loading Failed

**Error**: `Failed to load model from /path/to/model.pt`

**Cause**:
- Checkpoint corrupted
- Wrong model format
- PyTorch version mismatch

**Fix**:
- Use `best_model.pt` instead of `final_model.pt`
- Verify checkpoint integrity
- Check PyTorch version matches training environment

---

#### Inference Timeout

**Error**: `Inference timeout after 30s`

**Cause**:
- Model too large
- Input too large
- GPU memory exhausted

**Fix**:
- Reduce input size
- Use smaller model
- Increase timeout: `--timeout 60`

---

## Error Recovery Strategies

### Automatic Recovery

| Error | Strategy | Max Attempts |
|-------|----------|--------------|
| GPU OOM | Reduce batch_size | 3 |
| Network error | Retry with backoff | 5 |
| Process killed | Resume from checkpoint | ∞ |

### Manual Recovery

```bash
# 1. Check error details
python task_manager.py logs <task_id>

# 2. Fix the issue (e.g., fix data, adjust params)

# 3. Resume task
python task_manager.py resume <task_id>
```

## Logging

All errors logged to:
- Task log: `~/.openclaw/tasks/<task_id>/training_<task_id>.log`
- Task metadata: `~/.openclaw/tasks/<task_id>/meta.json`

View logs:
```bash
# Recent logs
python task_manager.py logs <task_id> --lines 100

# Follow live logs
tail -f ~/.openclaw/tasks/<task_id>/training_<task_id>.log
```

## Error Codes

| Code | Category | Example |
|------|----------|---------|
| ENV001 | Environment | Not in lerobot_ros2 repo |
| ENV002 | Environment | CUDA not available |
| ENV003 | Environment | Missing dependencies |
| DATA001 | Data | Source not found |
| DATA002 | Data | Insufficient samples |
| DATA003 | Data | Format mismatch |
| TRAIN001 | Training | GPU OOM |
| TRAIN002 | Training | Loss not converging |
| TRAIN003 | Training | Checkpoint corrupted |
| INFER001 | Inference | Model load failed |
| INFER002 | Inference | Timeout |

## Best Practices

1. **Always check environment first**:
   ```bash
   python check_environment.py --dry-run
   ```

2. **Use appropriate batch size**:
   - RTX 3080/3090/4090: 32-64
   - RTX 3060/3070/4060/4070: 16-32
   - Smaller GPUs: 8-16

3. **Monitor training**:
   ```bash
   python progress_monitor.py <task_id>
   ```

4. **Save checkpoints frequently**:
   - Default: every 10 epochs
   - Adjust: `--save-freq 5`

5. **Test with small dataset first**:
   - Validate pipeline works
   - Estimate resource needs
   - Then scale to full dataset
