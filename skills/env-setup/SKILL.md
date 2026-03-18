# Env Setup Skill - Development Environment Configuration

**Purpose**: Automatically set up development environments with dependency conflict resolution and proxy configuration.

**Supports**:
- V2Ray proxy installation (with mirror fallback)
- LeRobot (robot learning framework) installation
- Ubuntu/Debian, macOS
- Automatic proxy configuration for HuggingFace access

---

## Quick Start

```bash
# Install V2Ray (with automatic mirror fallback)
bash skills/env-setup/scripts/install_v2ray.sh

# Install LeRobot
bash skills/env-setup/scripts/install_lerobot.sh
```

---

## Installation Workflows

### V2Ray Installation (Enhanced with Mirror Fallback)

**Download Strategy (Automatic Fallback):**

```
Attempt 0: GitCode Mirror (NEW - Optimized for China)
  ↓ Failed
Attempt 1: Official Installer (GitHub)
  ↓ Failed (timeout/blocked)
Attempt 2: Manual Download from Mirror Sites
  ↓ Mirror 1: GitCode (fallback)
  ↓ Mirror 2: fastgit.xyz
  ↓ Mirror 3: ghproxy.com  
  ↓ Mirror 4: mirror.ghproxy.com
  ↓ Mirror 5: SourceForge (geodata only)
  ↓ All Failed
Attempt 3: apt-get (last resort, old version)
```

**Steps**:
1. Install dependencies (curl, wget, unzip)
2. **Try Method 0**: GitCode mirror (complete package, fastest for China) ⭐ NEW
3. **Try Method 1**: Official installer (2 min timeout)
4. **Try Method 2**: Manual download with mirror fallback
   - Download V2Ray binary from fastest mirror
   - Download geoip.dat / geosite.dat
   - Manual installation to `/usr/local/bin/`
5. **Try Method 3**: apt-get (if available)
6. Create configuration with SOCKS5 + HTTP proxy
7. Start V2Ray service (systemd or manual)
8. Test connection to Google and HuggingFace

**Mirror Sites (Priority Order):**
1. `https://gitcode.com/nicely235/place` - GitCode (fastest for China) ⭐ NEW
2. `https://github.com` - Official (may be blocked)
3. `https://hub.fastgit.xyz` - GitHub mirror (China)
4. `https://ghproxy.com/https://github.com` - Proxy (China)
5. `https://mirror.ghproxy.com/https://github.com` - Backup proxy
6. `https://downloads.sourceforge.net/project/v2ray` - SourceForge (geodata only)

**Output**:
- SOCKS5 proxy: `127.0.0.1:10808`
- HTTP proxy: `127.0.0.1:10809`
- Configuration: `/usr/local/etc/v2ray/config.json`

**Usage**:
```bash
# V2Ray 安装完成后会自动配置环境变量
# 如果手动配置，运行：
source ~/.bashrc  # 或 source ~/.zshrc

# 验证环境变量
echo $HTTP_PROXY
# 输出: http://127.0.0.1:10809

# 测试连接
curl -I https://huggingface.co
# 应该看到: HTTP/2 200

# 测试代理
curl -x http://127.0.0.1:10809 -I https://www.google.com
```

**Quick Start After Installation**:

```bash
# 1. 编辑配置文件（填入你的服务器信息）
sudo nano /usr/local/etc/v2ray/config.json

# 2. 重启服务
sudo systemctl restart v2ray

# 3. 应用环境变量
source ~/.bashrc

# 4. 测试连接
curl -I https://huggingface.co
```

**Failure Recovery:**

If all automatic methods fail:
```bash
# Manual installation from local machine
# 1. Package V2Ray from local
tar -czf /tmp/v2ray.tar.gz \
  /usr/local/bin/v2ray \
  /usr/local/share/v2ray/geoip.dat \
  /usr/local/share/v2ray/geosite.dat

# 2. Upload to remote
scp -P <port> /tmp/v2ray.tar.gz user@remote:/tmp/

# 3. Extract on remote
tar -xzf /tmp/v2ray.tar.gz -C /

# 4. Configure and start
bash skills/env-setup/scripts/install_v2ray.sh --skip-download
```

---

### LeRobot Installation

**Steps**:
1. **Environment Detection**
   - Check OS and architecture
   - Verify internet connectivity
   - Check for existing installations

2. **CUDA Detection**
   - Detect NVIDIA GPU
   - Check CUDA version
   - Identify compatible PyTorch version

3. **Smart Dependency Installation**
   - Resolve version conflicts
   - Install Miniconda if needed
   - Create isolated environment
   - Install PyTorch with CUDA support
   - Install torchvision with matching version

4. **LeRobot Installation**
   - Clone from openeuler mirror (faster for China)
   - Install in editable mode (`pip install -e .`)
   - Verify import and CUDA support

5. **Verification**
   - Test LeRobot import
   - Test CUDA availability
   - Test basic functionality

**Requirements**:
- Python 3.10+
- NVIDIA GPU (recommended)
- CUDA 11.8+ (recommended)
- Git, wget, curl

**Output**:
- Conda environment: `lerobot`
- Repository: `~/lerobot_ros2`
- Python packages: torch, torchvision, lerobot

---

## Advanced Features

### V2Ray Mirror Fallback System

**Automatic Switching Logic:**

```python
# Pseudocode
for mirror in [github, fastgit, ghproxy, ...]:
    try:
        download_from(mirror, timeout=60s)
        if success:
            return SUCCESS
    except Timeout:
        log(f"{mirror} failed, trying next...")
        continue

# All mirrors failed
return FALLBACK_TO_APT
```

**Mirror Response Times (China):**
- `gitcode.com/nicely235/place`: ~20-50ms ⭐ Fastest
- `hub.fastgit.xyz`: ~50-200ms
- `ghproxy.com`: ~100-300ms
- `mirror.ghproxy.com`: ~150-400ms
- `github.com`: timeout (often blocked)

**Geodata Sources:**
- Primary: GitHub releases (v2fly/geoip)
- Fallback: SourceForge (`downloads.sourceforge.net`)

### Dependency Conflict Resolution

**Problem**: PyTorch and torchvision often have version mismatches

**Solution**:
```bash
# Script automatically:
# 1. Detects CUDA version
# 2. Finds compatible PyTorch version
# 3. Matches torchvision version
# 4. Installs in correct order
```

**Example**:
```
Detected: CUDA 12.4
Selected: PyTorch 2.6.0+cu124
Matched:  torchvision 0.21.0+cu124
```

### Proxy Configuration

**Automatic Setup**:
- Detects if V2Ray is running
- Sets environment variables
- Configures HuggingFace access
- Tests connection before proceeding

**Manual Override**:
```bash
# Use custom proxy
bash install_lerobot.sh --proxy http://custom:port
```

---

## File Structure

```
skills/env-setup/
├── SKILL.md                    # This file
├── scripts/
│   ├── install_v2ray.sh        # V2Ray installer (with mirrors)
│   ├── install_lerobot.sh      # LeRobot installer
│   └── common_utils.sh         # Shared utilities
└── logs/
    └── install_*.log           # Installation logs
```

---

## Troubleshooting

### V2Ray Issues

**Problem**: All download methods failed

**Solution 1**: Manual upload from local machine
```bash
# Local machine
tar -czf v2ray.tar.gz -C /usr/local/bin v2ray -C /usr/local/share/v2ray geoip.dat geosite.dat
scp -P <port> v2ray.tar.gz user@remote:/tmp/

# Remote machine
tar -xzf /tmp/v2ray.tar.gz
sudo mv v2ray /usr/local/bin/
sudo mv geoip.dat geosite.dat /usr/local/share/v2ray/
```

**Solution 2**: Use apt (old version, may have bugs)
```bash
sudo apt-get update && sudo apt-get install -y v2ray
# Warning: apt version is 4.x, may encounter crypto/hmac errors
```

**Problem**: Connection timeout
```bash
# Check service status
systemctl status v2ray

# Restart service
sudo systemctl restart v2ray

# Test connection
curl -x http://127.0.0.1:10809 -I https://www.google.com
```

**Problem**: geoip.dat not found
```bash
# Download geodata files
wget https://downloads.sourceforge.net/project/v2ray/geoip.dat
wget https://downloads.sourceforge.net/project/v2ray/geosite.dat
sudo mv geoip.dat geosite.dat /usr/local/share/v2ray/
```

### LeRobot Issues

**Problem**: CUDA not detected
```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA
nvcc --version

# Reinstall PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

**Problem**: Import errors
```bash
# Verify environment
conda activate lerobot
python -c "import lerobot; print(lerobot.__version__)"

# Reinstall if needed
cd ~/lerobot_ros2
pip install -e . --force-reinstall
```

---

## Post-Installation

**After V2Ray installation**:
```bash
# Set proxy permanently
echo 'export HTTP_PROXY=http://127.0.0.1:10809' >> ~/.bashrc
echo 'export HTTPS_PROXY=http://127.0.0.1:10809' >> ~/.bashrc
source ~/.bashrc
```

**After LeRobot installation**:
```bash
# Activate environment
conda activate lerobot

# Verify installation
python -c "import lerobot; import torch; print(f'LeRobot: {lerobot.__version__}, CUDA: {torch.cuda.is_available()}')"
```

---

## Notes

- **Mirror fallback** automatically switches between sources
- **Proxy is mandatory** for HuggingFace access in China
- **Editable install** allows modifying LeRobot source code
- **Isolated environment** prevents system-wide conflicts
- **Logs are saved** to `~/.openclaw/logs/` for debugging

---

## Updates

**2026-03-18 10:35**:
- Added GitCode mirror as first priority (fastest for Chinese users)
- GitCode URL: https://gitcode.com/nicely235/place
- Complete package download (v2ray + geoip.dat + geosite.dat)
- Updated mirror priority: GitCode → GitHub → fastgit → ghproxy → SourceForge → apt

**2026-03-17 18:40**:
- Added automatic mirror fallback for V2Ray downloads
- Priority: GitHub → fastgit → ghproxy → SourceForge → apt
- Enhanced error handling and timeout logic
- Added manual installation fallback instructions

**2026-03-17 (Earlier)**:
- Added V2Ray installation
- Added automatic proxy configuration
- Added HuggingFace access verification
- Added mirror sites for GitHub downloads

---

**Skill Version**: 1.2
**Last Updated**: 2026-03-18 10:35
