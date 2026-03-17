---
name: env-setup
description: >
  Automatically set up development environments on new machines with dependency
  conflict resolution and proxy configuration. Supports v2ray proxy and lerobot
  robot learning framework. Enhanced version handles PyTorch/torchvision version
  mismatches, dependency conflicts, and network proxy setup automatically.

  Use when: (1) Setting up a new development machine, (2) Installing v2ray for
  network proxy, (3) Installing lerobot for robot learning, (4) Fixing dependency
  conflicts, (5) Configuring proxy for HuggingFace access, (6) User mentions
  'setup environment', 'install v2ray', 'install lerobot', 'fix dependencies',
  or asks to configure development tools.
metadata:
  {
    "openclaw": {
      "emoji": "🔧"
    }
  }
---

# Environment Setup Skill

⚠️ **CRITICAL: Execute steps in strict order as listed below. Do NOT skip any step.**

---

## MANDATORY Execution Rules

1. **Execute steps sequentially** - Complete Step 1 before starting Step 2
2. **Report progress after EACH step** - Inform user of completion before proceeding
3. **Do NOT skip verification steps** - Always run tests/checks as specified
4. **Stop on error** - If any step fails, report the error and stop

---

# Installation Workflow

## Standard Execution Pattern

When executing any installation or task, follow this pattern:

### Step-by-Step Execution Template

```markdown
## Executing Installation Task

### Step 1: [Task Name]
- **Action**: [What you're doing]
- **Command**: [Exact command to run]
- **Expected**: [What should happen]
**[Run command and report output]**

### Step 2: [Verification]
- **Check**: [What to verify]
- **Expected**: [Success criteria]
**[Run verification and report result]**

### Step 3: [Next Task]
...
```

### Progress Reporting Rules

1. **Start each step** with: `### Step X: [Name]`
2. **After each step**, report: `✅ Step X completed: [summary]`
3. **If a step fails**, report: `❌ Step X failed: [error details]`
4. **Before next step**, ask: `Proceeding to Step X+1...`

---

# Installation Workflow

Automate the installation and configuration of development environments on Ubuntu/Debian/macOS systems.

## ✨ Key Features

### 🔧 Automatic Dependency Resolution
- ✅ Detects and fixes PyTorch/torchvision version mismatches
- ✅ Resolves huggingface-hub, protobuf, packaging conflicts
- ✅ Installs all required dependencies (num2words, transformers, etc.)
- ✅ Verifies package compatibility

### 🌐 Smart Proxy Configuration
- ✅ Auto-detects V2Ray proxy (SOCKS5/HTTP)
- ✅ Configures environment for HuggingFace access
- ✅ Tests network connectivity before installation

### 🎯 CUDA-Aware Installation
- ✅ Detects CUDA version automatically
- ✅ Installs matching PyTorch version
- ✅ Falls back to CPU mode if no GPU

### 📊 Comprehensive Verification
- ✅ Tests all imports and dependencies
- ✅ Verifies CUDA functionality
- ✅ Generates detailed reports

## Supported Environments

- **v2ray** - Network proxy tool for bypassing restrictions
- **lerobot** - Robot learning and reinforcement learning framework

## Quick Start

### Install an Environment

```bash
# Install v2ray
bash scripts/install_v2ray.sh

# Install lerobot (enhanced version with dependency resolution)
bash scripts/install_lerobot_enhanced.sh

# Legacy version (if you prefer)
bash scripts/install_lerobot.sh
```

### Fix Dependency Conflicts

If you already have lerobot installed but encountering issues:

```bash
# Check for conflicts
python3 scripts/resolve_dependencies.py --check

# Automatically fix conflicts
python3 scripts/resolve_dependencies.py --fix

# Generate detailed report
python3 scripts/resolve_dependencies.py --report
```

### Check System Requirements

```bash
# Verify environment before installation
bash scripts/check_environment.sh v2ray
bash scripts/check_environment.sh lerobot
```

### Test V2Ray Connectivity (MANDATORY!)

**After installing V2Ray, you MUST test it before proceeding:**

```bash
# Test proxy connectivity to Google and HuggingFace
bash scripts/test_proxy.sh

# Expected output if successful:
# ✅ Google:      PASSED
# ✅ HuggingFace: PASSED
# ✅ ALL CRITICAL TESTS PASSED!

# If tests fail, check:
# 1. V2Ray config: /usr/local/etc/v2ray/config.json
# 2. V2Ray service: systemctl status v2ray
# 3. Network connectivity
```

## ⚠️ MANDATORY REQUIREMENT: V2Ray Configuration and Testing

**Before installing ANY other components (Python, PyTorch, LeRobot, etc.), you MUST:**

1. ✅ Install and configure V2Ray
2. ✅ Start V2Ray service
3. ✅ Test proxy connectivity (Google + HuggingFace)
4. ✅ Verify tests pass successfully

**This is NON-NEGOTIABLE. If proxy tests fail, installation will STOP.**

### Why This Requirement?

- LeRobot requires downloading large files from HuggingFace
- PyTorch installation needs access to download.pytorch.org
- Without working proxy, installation will fail and waste time
- **Save time: Fix proxy first, then proceed**

### How to Satisfy This Requirement

```bash
# Step 1: Install V2Ray
bash scripts/install_v2ray.sh

# Step 2: Test proxy connectivity (MANDATORY)
bash scripts/test_proxy.sh

# If tests pass, you'll see:
# ✅ ALL CRITICAL TESTS PASSED!
# You can now proceed with other installations.

# Step 3: Only then install other components
bash scripts/install_lerobot_enhanced.sh
```

**If you need to bypass this check (not recommended):**
```bash
NO_PROXY_REQUIRED=true bash scripts/install_lerobot_enhanced.sh
```

## Installation Workflow

Each installation follows these steps with **real-time progress display**:

### For V2Ray Installation

1. **Environment Check**
   - Verify OS and architecture
   - Check system requirements

2. **Install V2Ray Core**
   - Download from official repository
   - Install to system path

3. **Configure Proxy**
   - Create complete config with routing rules
   - Set up SOCKS5 (10808) and HTTP (10809) proxies

4. **Start Service**
   - Enable systemd service (Linux) or provide manual start command (macOS)
   - Verify service is running

5. **Test Connectivity** ⚠️ **MANDATORY**
   - Test Google access via SOCKS5 proxy
   - Test HuggingFace access via HTTP proxy
   - **ALL tests must pass before proceeding**

### For LeRobot Installation

**⚠️ Pre-requisite Check (MANDATORY):**
- Script will check if V2Ray is configured and tested
- If not, installation will STOP with error message
- You must run V2Ray installation and testing first

#### Step 1: V2Ray Verification
```bash
# Action: Verify V2Ray is configured and tested
# Command:
test -f /usr/local/etc/v2ray/config.json && bash scripts/test_proxy.sh
# Expected: V2Ray config exists and all proxy tests pass
# If failed: STOP and report error. Do NOT proceed to Step 2.
```

#### Step 2: Environment Detection
```bash
# Action: Check system requirements
# Command:
bash scripts/check_environment.sh lerobot
# Expected: System meets minimum requirements
# If failed: Report missing requirements and suggest fixes
```

#### Step 3: CUDA Detection
```bash
# Action: Detect CUDA version and GPU availability
# Command:
nvidia-smi --query-gpu=name,driver_version,cuda_version --format=csv,noheader || echo "No GPU detected"
# Expected: CUDA version reported or "No GPU detected"
# Note: Report detected version before proceeding
```

#### Step 4: Smart Dependency Installation
```bash
# Action: Install PyTorch with correct CUDA version and resolve conflicts
# Command:
bash scripts/install_lerobot_enhanced.sh
# Expected: Dependencies installed, PyTorch version matched to CUDA
# Progress: Monitor and report script output every 30 seconds
```

#### Step 5: Main Program Installation
```bash
# Action: Clone and install LeRobot from openeuler repository
# Command: (executed as part of install_lerobot_enhanced.sh)

# Step 5.1: Clone repository
git clone https://gitcode.com/openeuler/lerobot_ros2 ~/lerobot_ros2

# Step 5.2: Install in editable mode
cd ~/lerobot_ros2 && pip install -e .

# Expected: LeRobot installed successfully from openeuler repository
# Note: This repository contains customized lerobot with modifications
# If failed: Report specific error and retry with --fix flag
```

#### Step 6: Comprehensive Verification
```bash
# Action: Verify installation and test functionality
# Command:
source ~/opt/lerobot/activate.sh
python3 -c "import lerobot; print(lerobot.__version__)"
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
# Expected: All imports work, CUDA status reported
# Report: Final installation summary
```

### Progress Display Features

The installation scripts now include:

- ✅ **Visual Progress Bar**: Shows completion percentage
- ✅ **Step-by-Step Indicators**: Clear display of current step
- ✅ **Real-time Logs**: Important output displayed as it happens
- ✅ **Color-coded Status**: Easy to identify success/warnings/errors
- ✅ **Installation Summary**: Final report with all details

Example output:
```
════════════════════════════════════════════════════════
  Installation Progress - Total Steps: 6
════════════════════════════════════════════════════════

Step 1/6: Environment Check
Progress: [████████████████░░░░░░░░] 16%
Status: ⏳ running

ℹ [15:30:45] Checking network connectivity...
✓ [15:30:45] Network connectivity check passed
```

## Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| env_type | string | Yes | - | Environment type: `v2ray` or `lerobot` |
| INSTALL_PATH | string | No | `~/opt/<env>` | Installation directory (set as environment variable) |
| CONDA_ENV_NAME | string | No | `lerobot` | Conda environment name (unified for env-setup and lerobot-auto-train) |
| REPO_PATH | string | No | `~/lerobot_ros2` | LeRobot repository path (for editable install) |
| REPO_URL | string | No | `https://gitcode.com/openeuler/lerobot_ros2` | Git repository URL for cloning (openeuler customized version) |

Example with custom paths:
```bash
# Install v2ray with custom path
INSTALL_PATH=~/custom/path bash scripts/install_v2ray.sh

# Install lerobot with custom conda environment name
CONDA_ENV_NAME=my_lerobot bash scripts/install_lerobot_enhanced.sh

# Install lerobot with existing repository (if already cloned)
REPO_PATH=/home/nice/data/lerobot_ros2 bash scripts/install_lerobot_enhanced.sh

# Note: Default repository is https://gitcode.com/openeuler/lerobot_ros2
# This repository contains customized lerobot with modifications
```

### Repository Configuration (LeRobot)

LeRobot is installed from **openeuler customized repository** in **editable mode** (`pip install -e .`) to allow:
- ✅ Using scripts from the workspace directory
- ✅ Using customized lerobot with modifications from openeuler
- ✅ Modifying source code without reinstalling
- ✅ Running `python -m lerobot.scripts.*` commands

**Default Repository:**
- URL: `https://gitcode.com/openeuler/lerobot_ros2`
- Contains customized lerobot with openeuler modifications
- Always clone from this repository (not from huggingface/lerobot)

**Auto-Detection Order:**
1. `REPO_PATH` environment variable (if set)
2. Existing directory: `~/lerobot_ros2`
3. Clone from `https://gitcode.com/openeuler/lerobot_ros2` to `~/lerobot_ros2`

## Output

### Installation Report

After successful installation, you'll receive a report with:
- Environment type and version
- Installation path
- System information (OS, architecture)
- Log file location

### Log Files

All operations are logged to:
```
~/.openclaw/install_<env_type>_<YYYYMMDD_HHMMSS>.log
```

## Environment-Specific Usage

### V2Ray

**After Installation:**

Linux (systemd):
```bash
# Check status
sudo systemctl status v2ray

# Start/stop/restart
sudo systemctl start v2ray
sudo systemctl stop v2ray
sudo systemctl restart v2ray

# View logs
sudo journalctl -u v2ray -f
```

macOS:
```bash
# Start manually
v2ray run -c /usr/local/etc/v2ray/config.json
```

**Configuration:**
- Config file: `/usr/local/etc/v2ray/config.json`
- SOCKS5 proxy: `127.0.0.1:10808`
- HTTP proxy: `127.0.0.1:10809`
- Includes complete proxy configuration with routing rules
- Automatic backup of existing configuration

**Connectivity Test:** ⚠️ **MANDATORY**

**You MUST test V2Ray before proceeding with other installations:**

```bash
# Test proxy connectivity
bash scripts/test_proxy.sh

# This will test:
# - Google access (via SOCKS5)
# - HuggingFace access (via HTTP)
# - GitHub access (via HTTP)

# If tests pass:
# ✅ You can proceed with other installations
# ✅ HuggingFace model downloads will work
# ✅ PyTorch installation will succeed

# If tests fail:
# ❌ STOP and fix V2Ray configuration
# ❌ Do NOT proceed with other installations
# ❌ Check config file and restart V2Ray
```

**Using the Proxy:**

```bash
# Method 1: Specify proxy for single command
curl -x socks5://127.0.0.1:10808 https://www.google.com
wget -e use_proxy=yes -e https_proxy=127.0.0.1:10809 https://github.com

# Method 2: Set environment variable (recommended)
export ALL_PROXY=socks5://127.0.0.1:10808
curl https://www.google.com  # Automatically uses proxy

# Method 3: Permanent configuration
echo 'export ALL_PROXY=socks5://127.0.0.1:10808' >> ~/.bashrc
source ~/.bashrc
```

**Important Notes:**
- ❌ `ping` command does NOT use proxy (ICMP protocol limitation)
- ✅ Use `curl` or `wget` with proxy to test connectivity
- ✅ Configure browser or applications to use SOCKS5/HTTP proxy

**For advanced configuration**, see [references/v2ray_guide.md](references/v2ray_guide.md)

## Environment-Specific Usage

### LeRobot

**⚠️ PRE-REQUISITE: V2Ray MUST be configured and tested first!**

**Before installing LeRobot:**
1. ✅ Install V2Ray: `bash scripts/install_v2ray.sh`
2. ✅ Test proxy: `bash scripts/test_proxy.sh`
3. ✅ Verify all tests pass
4. **Only then** install LeRobot

**Installation will STOP if V2Ray tests have not passed.**

```bash
# Activate environment (with auto workspace configuration)
source ~/opt/lerobot/activate.sh

# This will:
# 1. Activate conda environment (default: lerobot)
# 2. Configure V2Ray proxy (if running)
# 3. Change to workspace directory
# 4. Set LEROBOT_WORKSPACE environment variable

# Or manually activate conda environment:
conda activate lerobot

# Verify installation
python3 -c "import lerobot; print(lerobot.__version__)"
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Use workspace scripts
python -m lerobot.scripts.lerobot_train --help
python -m lerobot.scripts.lerobot_record --help
python -m lerobot.scripts.lerobot_replay --help

# Check for dependency issues
python3 ~/.openclaw/workspace/skills/env-setup/scripts/resolve_dependencies.py --check
```

**Editable Install Benefits:**
- ✅ Use `python -m lerobot.scripts.*` to run workspace scripts
- ✅ Modify source code and changes take effect immediately
- ✅ Full access to all lerobot tools and utilities

**GPU Support:**
- Automatically detects and configures CUDA if available
- Falls back to CPU-only mode if no GPU detected
- Verifies PyTorch/torchvision compatibility

**Proxy Support:**
- Activation script automatically configures proxy if V2Ray is running
- Ensures HuggingFace models can be downloaded
- Tests network connectivity

**Troubleshooting:**

If you encounter dependency issues:
```bash
# Run diagnostic tool
python3 scripts/resolve_dependencies.py --report

# Fix conflicts automatically
python3 scripts/resolve_dependencies.py --fix
```

For detailed troubleshooting, see [references/troubleshooting_lerobot.md](references/troubleshooting_lerobot.md)

**For detailed usage**, see [references/lerobot_guide.md](references/lerobot_guide.md)

## Error Handling

The scripts handle these common errors:

| Error | Strategy |
|-------|----------|
| Network failure | Retry 3 times with delay |
| Disk space insufficient | Alert user, stop installation |
| Permission denied | Prompt for sudo or directory change |
| Dependency conflict | **Auto-resolve version conflicts** |
| PyTorch version mismatch | **Auto-reinstall matching versions** |
| Missing packages | **Auto-install all required deps** |
| HuggingFace inaccessible | **Auto-configure proxy** |
| Already installed | Skip or offer to reinstall |
| CUDA not available | **Fall back to CPU mode** |

**For troubleshooting**, see [references/troubleshooting_lerobot.md](references/troubleshooting_lerobot.md)

## Extending the Skill

To add support for a new environment:

1. Create `scripts/install_<env>.sh` following the pattern of existing scripts
2. Add environment detection to `scripts/check_environment.sh`
3. Create detailed guide in `references/<env>_guide.md`
4. Update this SKILL.md with new environment details

## Best Practices

1. **Always check logs** if installation fails: `tail -f ~/.openclaw/install_*.log`
2. **Verify environment** before installation: `bash scripts/check_environment.sh <env>`
3. **Use custom paths** for user-space installations: `INSTALL_PATH=~/.local bash scripts/install_*.sh`
4. **Review configuration** after installation, especially for v2ray

## Script Reference

| Script | Purpose |
|--------|---------|
| `scripts/common_utils.sh` | Shared functions (logging, retries, etc.) |
| `scripts/check_environment.sh` | System requirements validation |
| `scripts/install_v2ray.sh` | V2Ray installation automation |
| `scripts/install_lerobot.sh` | LeRobot installation (basic) |
| `scripts/install_lerobot_enhanced.sh` | **LeRobot installation (enhanced with conflict resolution)** |
| `scripts/resolve_dependencies.py` | **Dependency conflict detection and resolution** |

All scripts are idempotent and can be safely run multiple times.

## Common Issues and Solutions

### Issue 1: V2Ray Installation Failures

**Scenario A: Cannot Download from GitHub**
- **Symptom**: `curl: (28) Connection timed out` when downloading V2Ray
- **Cause**: GitHub blocked in restricted network environments
- **Solutions**:
  1. **Use apt (Ubuntu/Debian)**:
     ```bash
     apt-get install v2ray
     ```
     ⚠️ **Note**: apt version (4.x) is old and may have bugs:
     - `crypto/hmac: hash generation function does not produce unique values`
     - Consider upgrading if you encounter issues

  2. **Download from SourceForge mirror** (recommended):
     ```bash
     # SourceForge V2Ray project mirror
     # Visit: https://sourceforge.net/projects/v2ray/files/

     # Example: Download V2Ray 5.16.1 from SourceForge
     wget https://downloads.sourceforge.net/project/v2ray/v2ray-linux-64.zip

     # Extract and install
     unzip v2ray-linux-64.zip -d /tmp/v2ray
     sudo mkdir -p /usr/local/bin/v2ray
     sudo cp /tmp/v2ray/v2ray /usr/local/bin/v2ray/
     sudo chmod +x /usr/local/bin/v2ray/v2ray

     # Download geodata files
     wget https://downloads.sourceforge.net/project/v2ray/geoip.dat
     wget https://downloads.sourceforge.net/project/v2ray/geosite.dat
     sudo mkdir -p /usr/local/share/v2ray
     sudo mv geoip.dat geosite.dat /usr/local/share/v2ray/
     ```

  3. **Upload from local machine**:
     ```bash
     # On local machine
     tar -czf v2ray-local.tar.gz /usr/local/bin/v2ray /usr/local/share/v2ray/*.dat
     scp v2ray-local.tar.gz user@remote:/tmp/

     # On remote server
     tar -xzf /tmp/v2ray-local.tar.gz -C /
     ```

  4. **Use GitHub mirrors** (if available):
     ```bash
     # Try these mirrors
     https://hub.fastgit.xyz/v2fly/v2ray-core/...
     https://ghproxy.com/https://github.com/v2fly/...
     ```

**Scenario B: V2Ray Version Too Old (apt)**
- **Symptom**: `panic: crypto/hmac: hash generation function does not produce unique values`
- **Cause**: apt version 4.x has bugs in VMess AEAD encryption
- **Solution**: Upload newer version (5.x+) from local machine

**Scenario C: systemd Not Available (Container/WSL)**
- **Symptom**: `System has not been booted with systemd`
- **Cause**: Running in container or WSL environment
- **Solution**: Start V2Ray manually:
  ```bash
  nohup /usr/local/bin/v2ray/v2ray run -c /etc/v2ray/config.json > /tmp/v2ray.log 2>&1 &
  ```

### Issue 2: Git Clone Performance Issues

**Scenario A: Large Repository Clone Timeout**
- **Symptom**: `git clone` hangs or takes >10 minutes
- **Cause**: Large repository size, slow proxy, network issues
- **Solutions**:
  1. **Use shallow clone** (recommended):
     ```bash
     git clone --depth 1 https://github.com/user/repo.git
     ```
     - Downloads only latest commit
     - Much faster for large repos
  
  2. **Don't use proxy if server can access directly**:
     ```bash
     # Check if direct access works
     curl -I https://github.com  # If works, don't use proxy
     ```
  
  3. **Disable proxy for git**:
     ```bash
     unset ALL_PROXY
     git clone https://github.com/user/repo.git
     ```

**Scenario B: git index-pack Stuck**
- **Symptom**: `git index-pack --stdin` runs for >10 minutes
- **Cause**: Large pack file, slow I/O, or proxy issues
- **Solution**: 
  - Stop and retry with shallow clone
  - Or wait patiently (large repos can take 15-20 minutes)

### Issue 3: Real-time Installation Progress Display

**How to Show Real-time Progress During Installation:**

**Method 1: Use message tool (for chat/Feishu integration)**
```python
# In your skill script
import subprocess
import time

# Send start message
message(action="send", message="🚀 开始安装 PyTorch...")

# Run installation with output capture
proc = subprocess.Popen(
    ["pip3", "install", "torch"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Stream output and send updates
for line in proc.stdout:
    if "Downloading" in line or "%" in line:
        # Extract progress
        message(action="send", message=f"📊 {line.strip()}")

# Send completion
message(action="send", message="✅ PyTorch 安装完成！")
```

**Method 2: Use tail -f for log files**
```bash
# In installation script
LOG_FILE="/tmp/install_progress.log"

# Send progress to log file
pip3 install torch 2>&1 | tee "$LOG_FILE" &

# User can watch progress in another terminal
tail -f "$LOG_FILE"
```

**Method 3: Use progress bar tools**
```bash
# Install with verbose output
pip3 install torch --verbose --progress-bar on

# Or use pv (pipe viewer)
pip3 download torch | pv -l > /dev/null
```

**Method 4: Poll process status periodically**
```python
# Check installation status every 30 seconds
while is_process_running("pip3 install"):
    status = check_pip_progress()
    message(action="send", message=f"🔄 进度: {status}")
    time.sleep(30)
```

### Issue 4: PyTorch Installation SOCKS Proxy Error

**Symptom**: `ERROR: Could not install packages due to an OSError: Missing dependencies for SOCKS support`

**Cause**: pip requires PySocks for SOCKS5 proxy

**Solutions**:
1. **Install PySocks**:
   ```bash
   pip3 install PySocks
   pip3 install torch --index-url https://download.pytorch.org/whl/cu121
   ```

2. **Use HTTP proxy instead**:
   ```bash
   export HTTP_PROXY=http://127.0.0.1:10809
   export HTTPS_PROXY=http://127.0.0.1:10809
   pip3 install torch
   ```

3. **Don't use proxy if server can access directly** (check first):
   ```bash
   # Test direct access
   curl -I https://download.pytorch.org/whl/torch/
   
   # If works, unset proxy
   unset ALL_PROXY HTTP_PROXY HTTPS_PROXY
   pip3 install torch
   ```

### Issue 5: LeRobot Import Failure (ModuleNotFoundError)

**Symptom**: `ModuleNotFoundError: No module named 'lerobot'` after installation

**Cause**: LeRobot uses `src/lerobot` directory structure (not standard layout)

**Solutions**:
1. **Add to PYTHONPATH**:
   ```bash
   export PYTHONPATH=/root/lerobot_ros2/src:$PYTHONPATH
   python3 -c "import lerobot; print(lerobot.__version__)"
   ```

2. **Make permanent**:
   ```bash
   echo 'export PYTHONPATH=/root/lerobot_ros2/src:$PYTHONPATH' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Use correct import path**:
   ```python
   import sys
   sys.path.insert(0, "/path/to/lerobot_ros2/src")
   import lerobot
   ```

### Issue 6: PyTorch/torchvision Version Mismatch

**Symptom**: `RuntimeError: operator torchvision::nms does not exist`

**Solution**:
```bash
python3 scripts/resolve_dependencies.py --fix
```

### Issue 7: Cannot Access HuggingFace

**Symptom**: `OSError: Can't load processor for ...`

**Solution**:
1. Start V2Ray: `sudo systemctl start v2ray`
2. Use activation script: `source ~/opt/lerobot/activate.sh`
3. Or manually: `export HTTPS_PROXY=http://127.0.0.1:10809`

### Issue 8: Missing Dependencies

**Symptom**: `ImportError: Package 'num2words' is required`

**Solution**:
```bash
source ~/opt/lerobot/venv/bin/activate
pip install num2words transformers accelerate sentencepiece
```

### Issue 9: Installation in Container Environment

**Special Considerations for Docker/LXC/Container Environments:**

1. **No systemd**: Start services manually
2. **Limited disk space**: Monitor usage carefully
3. **Network restrictions**: Test direct access first
4. **Persistent storage**: Save important data to mounted volumes

```bash
# Example: Start V2Ray in container
nohup /usr/local/bin/v2ray/v2ray run -c /etc/v2ray/config.json > /tmp/v2ray.log 2>&1 &

# Check if running
ps aux | grep v2ray
tail -f /tmp/v2ray.log
```

For more issues, see [references/troubleshooting_lerobot.md](references/troubleshooting_lerobot.md)

## System Requirements

**Minimum:**
- Ubuntu 20.04+ / Debian 11+ / macOS
- 2GB free disk space
- Stable internet connection
- sudo access (for system-wide installation)

**Recommended for lerobot:**
- 8GB RAM
- NVIDIA GPU with CUDA support
- 5GB disk space
