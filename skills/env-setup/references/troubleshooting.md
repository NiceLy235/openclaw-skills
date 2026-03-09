# Troubleshooting Guide

## Common Installation Issues

### Network and Download Issues

#### Problem: Download timeout or connection failed

**Symptoms:**
- `curl: (7) Failed to connect to ...`
- `Connection timed out`
- `Could not resolve host`

**Solutions:**
1. Check network connectivity:
   ```bash
   ping -c 3 8.8.8.8
   ping -c 3 github.com
   ```

2. Use a mirror or proxy (especially in China):
   ```bash
   # For PyPI
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple lerobot
   
   # For GitHub, use a mirror
   export REPO_URL=https://github.com.cnpmjs.org/
   ```

3. Retry with longer timeout:
   ```bash
   curl --connect-timeout 30 --max-time 300 -L -o file url
   ```

#### Problem: GitHub raw content blocked

**Symptoms:**
- `curl: (7) Failed to connect to raw.githubusercontent.com`

**Solutions:**
1. Use GitHub mirror:
   ```bash
   # Replace in scripts
   sed -i 's/raw.githubusercontent.com/raw.githubusercontent.com/g' script.sh
   ```

2. Download manually and run locally

### Permission Issues

#### Problem: Permission denied

**Symptoms:**
- `bash: ./script.sh: Permission denied`
- `mkdir: cannot create directory: Permission denied`

**Solutions:**
1. Make scripts executable:
   ```bash
   chmod +x scripts/*.sh
   ```

2. For system-wide installation, use sudo:
   ```bash
   sudo bash scripts/install_v2ray.sh
   ```

3. For user installation, change directory:
   ```bash
   export INSTALL_PATH=$HOME/.local
   ```

#### Problem: sudo required

**Symptoms:**
- `[sudo] password for user:`
- `user is not in the sudoers file`

**Solutions:**
1. Add user to sudoers (as root):
   ```bash
   usermod -aG sudo username
   ```

2. Use passwordless sudo for specific commands:
   ```bash
   echo "username ALL=(ALL) NOPASSWD: /usr/bin/apt-get" | sudo tee /etc/sudoers.d/username
   ```

### Disk Space Issues

#### Problem: No space left on device

**Symptoms:**
- `No space left on device`
- `write error (disk full?)`

**Solutions:**
1. Check disk usage:
   ```bash
   df -h
   du -sh ~/opt/* 2>/dev/null | sort -h
   ```

2. Clean package cache:
   ```bash
   sudo apt-get clean
   sudo apt-get autoremove
   ```

3. Clean Python cache:
   ```bash
   rm -rf ~/.cache/pip
   ```

4. Remove old installations:
   ```bash
   rm -rf ~/opt/old_package
   ```

### Dependency Conflicts

#### Problem: Python version conflict

**Symptoms:**
- `ModuleNotFoundError: No module named '...'`
- `ImportError: cannot import name '...'`

**Solutions:**
1. Check Python version:
   ```bash
   python3 --version
   which python3
   ```

2. Reinstall in clean virtual environment:
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   ```

#### Problem: Package already installed with different version

**Symptoms:**
- `ERROR: pip's dependency resolver does not currently take into account all the packages...`
- Version conflicts

**Solutions:**
1. Force reinstall:
   ```bash
   pip install --force-reinstall package-name
   ```

2. Create isolated environment:
   ```bash
   python3 -m venv --clear fresh_env
   ```

### CUDA/GPU Issues

#### Problem: CUDA not detected

**Symptoms:**
- `CUDA not available`
- `torch.cuda.is_available() returns False`

**Solutions:**
1. Check NVIDIA driver:
   ```bash
   nvidia-smi
   ```

2. Check CUDA installation:
   ```bash
   nvcc --version
   ls /usr/local/cuda*
   ```

3. Reinstall PyTorch with correct CUDA version:
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

4. Set CUDA path:
   ```bash
   export PATH=/usr/local/cuda/bin:$PATH
   export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
   ```

#### Problem: Out of GPU memory

**Symptoms:**
- `RuntimeError: CUDA out of memory`
- `CUDA error: out of memory`

**Solutions:**
1. Reduce batch size in your code
2. Clear cache:
   ```python
   import torch
   torch.cuda.empty_cache()
   ```

3. Use gradient checkpointing
4. Use mixed precision training

### V2Ray Specific Issues

#### Problem: Service fails to start

**Symptoms:**
- `v2ray.service: Failed with result 'exit-code'`
- `Job for v2ray.service failed`

**Solutions:**
1. Check configuration syntax:
   ```bash
   v2ray test -c /usr/local/etc/v2ray/config.json
   ```

2. Check logs:
   ```bash
   sudo journalctl -u v2ray -n 50 --no-pager
   ```

3. Check permissions:
   ```bash
   sudo chown -R root:root /usr/local/etc/v2ray
   sudo chmod 644 /usr/local/etc/v2ray/config.json
   ```

#### Problem: Cannot connect to proxy

**Symptoms:**
- Connection timeout
- Proxy refused connection

**Solutions:**
1. Check if service is running:
   ```bash
   sudo systemctl status v2ray
   ```

2. Check port is listening:
   ```bash
   sudo netstat -tlnp | grep 1080
   ```

3. Test with curl:
   ```bash
   curl --socks5 127.0.0.1:1080 https://www.google.com
   ```

4. Check firewall:
   ```bash
   sudo ufw status
   ```

### LeRobot Specific Issues

#### Problem: Import errors

**Symptoms:**
- `ModuleNotFoundError: No module named 'lerobot'`
- Missing dependencies

**Solutions:**
1. Verify virtual environment is active:
   ```bash
   which python
   # Should point to venv/bin/python
   ```

2. Reinstall lerobot:
   ```bash
   pip uninstall lerobot
   pip install lerobot
   ```

3. Install from source:
   ```bash
   git clone https://github.com/huggingface/lerobot.git
   cd lerobot
   pip install -e .
   ```

#### Problem: Model download fails

**Symptoms:**
- Cannot download from Hugging Face
- `HTTPError: 403 Forbidden`

**Solutions:**
1. Set Hugging Face mirror (China):
   ```bash
   export HF_ENDPOINT=https://hf-mirror.com
   ```

2. Download manually:
   ```bash
   git lfs install
   git clone https://huggingface.co/lerobot/act_aloha_sim_transfer_cube
   ```

## Log Files

All installation logs are saved to:
- **V2Ray**: `~/.openclaw/install_v2ray_YYYYMMDD_HHMMSS.log`
- **LeRobot**: `~/.openclaw/install_lerobot_YYYYMMDD_HHMMSS.log`

## Getting Help

1. Check the log files for detailed error messages
2. Consult the detailed guides in `references/` directory
3. Search for the error message online
4. Open an issue on GitHub with:
   - Full error message
   - Log file content
   - System information (`uname -a`, OS version, etc.)

## Quick Diagnostics

Run this to gather system information for troubleshooting:

```bash
echo "=== System Information ==="
uname -a
cat /etc/os-release 2>/dev/null || sw_vers

echo -e "\n=== Disk Space ==="
df -h | grep -E '^(/dev|Filesystem)'

echo -e "\n=== Memory ==="
free -h

echo -e "\n=== Network ==="
ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo "Internet: OK" || echo "Internet: FAILED"

echo -e "\n=== Python ==="
python3 --version 2>/dev/null || echo "Python3: NOT INSTALLED"
pip3 --version 2>/dev/null || echo "pip3: NOT INSTALLED"

echo -e "\n=== GPU ==="
nvidia-smi 2>/dev/null || echo "NVIDIA GPU: NOT DETECTED"
```
