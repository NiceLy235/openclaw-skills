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
---

# Environment Setup Skill

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

## Installation Workflow

Each installation follows these steps with **real-time progress display**:

1. **Network & Proxy Check** (New!)
   - Detect V2Ray proxy (SOCKS5/HTTP)
   - Test HuggingFace connectivity
   - Configure proxy automatically

2. **Environment Detection**
   - Check OS version and architecture
   - Verify disk space (minimum 2GB)
   - Test network connectivity
   - Detect existing installations

3. **CUDA Detection** (Enhanced!)
   - Auto-detect CUDA version
   - Map to correct PyTorch index
   - Verify GPU functionality

4. **Smart Dependency Installation** (Enhanced!)
   - Install required system packages
   - Set up Python environment (for lerobot)
   - Install PyTorch with correct CUDA version
   - Resolve version conflicts automatically

5. **Main Program Installation**
   - Download and install the software
   - Install all required dependencies
   - Handle version constraints

6. **Comprehensive Verification** (Enhanced!)
   - Test PyTorch/torchvision compatibility
   - Verify all imports
   - Test CUDA operations
   - Generate installation report

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

Example with custom path:
```bash
INSTALL_PATH=~/custom/path bash scripts/install_v2ray.sh
```

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

**Connectivity Test:**

The installation automatically tests proxy connectivity:
- Tests Google access via SOCKS5 proxy
- Tests GitHub access via HTTP proxy
- Reports success/failure for troubleshooting

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

**After Installation:**

```bash
# Activate environment (with auto proxy configuration)
source ~/opt/lerobot/activate.sh

# Or manually
source ~/opt/lerobot/venv/bin/activate

# Verify installation
python3 -c "import lerobot; print(lerobot.__version__)"
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Check for dependency issues
python3 ~/.openclaw/workspace/skills/env-setup/scripts/resolve_dependencies.py --check
```

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

### Issue 1: PyTorch/torchvision Version Mismatch

**Symptom**: `RuntimeError: operator torchvision::nms does not exist`

**Solution**:
```bash
python3 scripts/resolve_dependencies.py --fix
```

### Issue 2: Cannot Access HuggingFace

**Symptom**: `OSError: Can't load processor for ...`

**Solution**:
1. Start V2Ray: `sudo systemctl start v2ray`
2. Use activation script: `source ~/opt/lerobot/activate.sh`
3. Or manually: `export HTTPS_PROXY=http://127.0.0.1:10809`

### Issue 3: Missing Dependencies

**Symptom**: `ImportError: Package 'num2words' is required`

**Solution**:
```bash
source ~/opt/lerobot/venv/bin/activate
pip install num2words transformers accelerate sentencepiece
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
