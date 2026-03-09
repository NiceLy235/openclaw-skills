---
name: env-setup
description: "Automatically set up development environments on new machines. Supports v2ray proxy and lerobot robot learning framework with full dependency installation, configuration, and verification. Use when: (1) Setting up a new development machine, (2) Installing v2ray for network proxy, (3) Installing lerobot for robot learning, (4) Automating environment setup tasks, (5) User mentions 'setup environment', 'install v2ray', 'install lerobot', or asks to configure development tools."
---

# Environment Setup Skill

Automate the installation and configuration of development environments on Ubuntu/Debian/macOS systems.

## Supported Environments

- **v2ray** - Network proxy tool for bypassing restrictions
- **lerobot** - Robot learning and reinforcement learning framework

## Quick Start

### Install an Environment

```bash
# Install v2ray
bash scripts/install_v2ray.sh

# Install lerobot
bash scripts/install_lerobot.sh
```

### Check System Requirements

```bash
# Verify environment before installation
bash scripts/check_environment.sh v2ray
bash scripts/check_environment.sh lerobot
```

## Installation Workflow

Each installation follows these steps with **real-time progress display**:

1. **Environment Detection**
   - Check OS version and architecture
   - Verify disk space (minimum 2GB)
   - Test network connectivity
   - Detect existing installations

2. **Dependency Installation**
   - Install required system packages
   - Set up Python environment (for lerobot)
   - Install CUDA support if available

3. **Main Program Installation**
   - Download and install the software
   - Configure default settings
   - Set up system services (for v2ray)

4. **Verification**
   - Test installation integrity
   - Verify service status
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
- Default proxy: SOCKS5 on `127.0.0.1:1080`

**For advanced configuration**, see [references/v2ray_guide.md](references/v2ray_guide.md)

### LeRobot

**After Installation:**

```bash
# Activate environment
source ~/opt/lerobot/activate.sh

# Or manually
source ~/opt/lerobot/venv/bin/activate

# Verify installation
python3 -c "import lerobot; print(lerobot.__version__)"
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

**GPU Support:**
- Automatically detects and configures CUDA if available
- Falls back to CPU-only mode if no GPU detected

**For detailed usage**, see [references/lerobot_guide.md](references/lerobot_guide.md)

## Error Handling

The scripts handle these common errors:

| Error | Strategy |
|-------|----------|
| Network failure | Retry 3 times with delay |
| Disk space insufficient | Alert user, stop installation |
| Permission denied | Prompt for sudo or directory change |
| Dependency conflict | Stop and report details |
| Already installed | Skip or offer to reinstall |

**For troubleshooting**, see [references/troubleshooting.md](references/troubleshooting.md)

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
| `scripts/install_lerobot.sh` | LeRobot installation automation |

All scripts are idempotent and can be safely run multiple times.

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
