# Training Troubleshooting Guide

## Common Issues and Solutions

### 1. Out of Memory (OOM) Errors

**Symptoms:**
- CUDA out of memory error
- Training crashes after a few steps
- GPU memory usage hits 100%

**Causes:**
- Batch size too large for GPU memory
- Model too large for available VRAM
- Memory leak in data loader

**Solutions:**
1. **Reduce batch size** (most effective)
   ```bash
   # Try reducing by half
   --batch_size=16  # was 32
   ```

2. **Reduce number of workers**
   ```bash
   --num_workers=8  # was 16
   ```

3. **Use gradient checkpointing** (if available)
   - Saves memory by recomputing activations

4. **Clear GPU cache between runs**
   ```bash
   nvidia-smi --gpu-reset -i 0  # requires sudo
   ```

**Prevention:**
- Start with smaller batch size, increase gradually
- Monitor GPU memory during first few epochs
- Check `nvidia-smi` before starting training

### 2. Training Slow or Stalling

**Symptoms:**
- Very slow step times (>10s per step)
- Training appears frozen
- CPU at 100%, GPU at 0%

**Causes:**
- Data loading bottleneck
- Network issues (remote dataset)
- Insufficient workers

**Solutions:**
1. **Increase data loading workers**
   ```bash
   --num_workers=16  # or more
   ```

2. **Use local dataset**
   - Download HuggingFace dataset first
   - Use local path instead of repo_id

3. **Check disk I/O**
   ```bash
   iostat -x 1  # monitor disk usage
   ```

4. **Preload data to RAM** (if dataset fits)

### 3. SSH Connection Issues

**Symptoms:**
- Connection timeout
- Permission denied
- Connection refused

**Solutions:**
1. **Check SSH service**
   ```bash
   systemctl status sshd
   ```

2. **Verify network connectivity**
   ```bash
   ping 192.168.136.168
   nc -zv 192.168.136.168 22
   ```

3. **Use SSH key authentication**
   ```bash
   ssh-copy-id user@192.168.136.168
   ```

4. **Check firewall**
   ```bash
   sudo ufw allow 22
   ```

### 4. Lerobot Command Not Found

**Symptoms:**
- `lerobot-train: command not found`
- Training fails to start

**Causes:**
- LeRobot not installed
- Virtual environment not activated
- PATH not configured

**Solutions:**
1. **Install LeRobot**
   ```bash
   pip install lerobot
   ```

2. **Activate virtual environment**
   ```bash
   source /path/to/venv/bin/activate
   ```

3. **Add to PATH**
   ```bash
   export PATH=$PATH:~/.local/bin
   ```

### 5. Dataset Not Found

**Symptoms:**
- `Dataset not found` error
- Hugging Face download fails

**Solutions:**
1. **Check internet connection**
   ```bash
   curl https://huggingface.co
   ```

2. **Use HF token for private datasets**
   ```bash
   huggingface-cli login
   ```

3. **Download dataset locally**
   ```bash
   git lfs clone https://huggingface.co/datasets/user/dataset
   ```

### 6. Training Loss Not Decreasing

**Symptoms:**
- Loss stays constant
- Loss increases instead of decreasing
- NaN loss values

**Causes:**
- Learning rate too high/low
- Bad initialization
- Data issues

**Solutions:**
1. **Check learning rate**
   - Too high: loss oscillates or explodes
   - Too low: loss decreases very slowly

2. **Check data quality**
   - Verify dataset format
   - Check for corrupted samples

3. **Reduce learning rate**
   - Try 10x smaller learning rate

4. **Use gradient clipping**
   - Prevents gradient explosion

### 7. Checkpoint Loading Errors

**Symptoms:**
- Failed to load checkpoint
- Model architecture mismatch

**Solutions:**
1. **Verify checkpoint path**
   ```bash
   ls -la /path/to/checkpoint
   ```

2. **Check model compatibility**
   - Ensure same architecture as training

3. **Use correct pretrained path**
   ```bash
   --policy.pretrained_path=lerobot/smolvla_base
   ```

### 8. GPU Not Detected

**Symptoms:**
- `CUDA not available`
- Training runs on CPU

**Solutions:**
1. **Check NVIDIA drivers**
   ```bash
   nvidia-smi
   ```

2. **Install CUDA toolkit**
   ```bash
   sudo apt install nvidia-cuda-toolkit
   ```

3. **Check PyTorch CUDA**
   ```python
   import torch
   print(torch.cuda.is_available())
   ```

## Monitoring Commands

### Check GPU Status
```bash
nvidia-smi
watch -n 1 nvidia-smi  # continuous monitoring
```

### Check Training Process
```bash
ps aux | grep lerobot
htop  # CPU/RAM usage
```

### Check Disk Space
```bash
df -h
du -sh outputs/
```

### Check Logs
```bash
tail -f training.log
grep -i error training.log
```

## Getting Help

1. **Check logs first**
   - Look for error messages
   - Note the exact error and when it occurs

2. **Search documentation**
   - LeRobot docs: https://github.com/huggingface/lerobot
   - PyTorch docs: https://pytorch.org/docs

3. **Check GPU memory**
   - Most issues are memory-related
   - Reduce batch size as first step

4. **Simplify and test**
   - Use smaller dataset
   - Use fewer steps
   - Isolate the problem

## Prevention Tips

1. **Start small**
   - Test with small batch size first
   - Verify on small subset of data

2. **Monitor early**
   - Watch first few epochs closely
   - Check GPU memory usage

3. **Save frequently**
   - Use `--save_freq=1000` initially
   - Don't lose hours of training

4. **Document everything**
   - Record working configurations
   - Note what changes helped
