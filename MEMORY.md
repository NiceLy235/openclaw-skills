# MEMORY.md - Long-Term Memory

This file contains important decisions, preferences, and lessons learned that should persist across sessions.

---

## 📱 Feishu Operations - Real-Time Feedback (2026-03-13)

### Critical Decision

**All Feishu tasks MUST show real-time progress feedback.**

### Context

User requested (2026-03-13):
> "我希望让后面所有飞书机器人执行任务的时候，必须把每个步骤都及时展示出来，不能在执行完成后，才返回消息。"

### Implementation

1. **Created Skill**: `feishu-realtime` at `skills/feishu-realtime/SKILL.md`
   - Pushed to GitHub: `NiceLy235/openclaw-skills`
   - Contains detailed real-time feedback workflow

2. **Updated AGENTS.md**: Added mandatory Feishu real-time feedback section
   - Applies to ALL Feishu operations
   - Enforced regardless of which skill is active
   - Persists across all future sessions

3. **Standard Workflow**:
   ```
   🚀 开始执行任务：[任务名称]
   ✅ 步骤 1/N 完成：[步骤描述]
   ✅ 步骤 2/N 完成：[步骤描述]
   ...
   🎉 全部完成！[结果摘要]
   ```

### Rules

- **NEVER** execute >3 Feishu API calls without progress message
- **ALWAYS** send start message before first API call
- **ALWAYS** send completion message after last API call
- **ALWAYS** report errors immediately

### Why Important

- User experience: No silent waits
- Transparency: User knows exactly what's happening
- Better UX for long-running operations

### Applies To

- Document operations (read, write, append, create)
- Wiki navigation (list spaces, create nodes, get nodes)
- Drive management (list folders, create folders, move files)
- Bitable operations (get meta, list fields, create records)
- ALL multi-step Feishu tasks

### Verification

To verify this rule is working:
1. Request any Feishu task with multiple steps
2. Observe real-time progress messages after each step
3. No long silent waits

---

## 🌐 Remote Server V2Ray & Environment Setup (2026-03-17)

### V2Ray Configuration for Remote Servers

**Default V2Ray Config Location:**
- Local: `/usr/local/etc/v2ray/config.json`
- Remote: `/etc/v2ray/config.json` (after installation)

**Installation Pattern:**

1. **Install from apt (quick but old):**
   ```bash
   apt-get update && apt-get install -y v2ray
   ```
   ⚠️ **Warning:** apt version (4.x) has bugs:
   - `crypto/hmac: hash generation function does not produce unique values`
   - Must upgrade to 5.x+

2. **Upgrade from local machine:**
   ```bash
   # On local machine
   cd /tmp
   tar -czf v2ray-new.tar.gz \
     -C /usr/local/bin v2ray \
     -C /usr/local/share/v2ray geoip.dat geosite.dat

   # Upload to remote
   scp -P PORT v2ray-new.tar.gz user@remote:/tmp/

   # On remote server
   tar -xzf /tmp/v2ray-new.tar.gz
   mv v2ray /usr/local/bin/v2ray
   mv geoip.dat geosite.dat /usr/local/share/v2ray/
   ```

3. **Configuration:**
   - Copy local working config to remote `/etc/v2ray/config.json`
   - Required files: `geoip.dat`, `geosite.dat` in same directory as v2ray binary
   - Start: `nohup /usr/local/bin/v2ray run -c /etc/v2ray/config.json > /tmp/v2ray.log 2>&1 &`

4. **Proxy Configuration:**
   ```bash
   export HTTP_PROXY=http://127.0.0.1:10809
   export HTTPS_PROXY=http://127.0.0.1:10809
   export ALL_PROXY=socks5://127.0.0.1:10808
   ```

### LeRobot Environment Installation

**Best Practice Pattern:**

1. **Install Miniconda:**
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
   ```

2. **Create Environment:**
   ```bash
   conda create -n lerobot python=3.10 -y
   conda activate lerobot
   ```

3. **Install PyTorch GPU:**
   - ⚠️ **pip is more reliable than conda**
   - Use background script with nohup to avoid SSH timeout
   - Example script: `/tmp/install_pytorch_gpu.sh`

   ```bash
   # Create script
   cat > /tmp/install_pytorch_gpu.sh << 'EOF'
   #!/bin/bash
   export HTTP_PROXY=http://127.0.0.1:10809
   export HTTPS_PROXY=http://127.0.0.1:10809
   source $HOME/miniconda3/etc/profile.d/conda.sh
   conda activate lerobot
   pip install torch torchvision torchaudio \
     --index-url https://download.pytorch.org/whl/cu124 \
     --timeout 300
   EOF

   # Run in background
   nohup bash /tmp/install_pytorch_gpu.sh > /tmp/pytorch_nohup.log 2>&1 &
   ```

4. **Install LeRobot:**
   ```bash
   git clone https://gitcode.com/openeuler/lerobot_ros2 ~/lerobot_ros2
   cd ~/lerobot_ros2
   pip install -e . --timeout 600
   ```

### Common Issues

**Issue 1: PyTorch Download Timeout**
- **Cause:** Large files (768MB+), slow proxy
- **Solution:** Use background script with nohup
- **Monitor:** `tail -f /tmp/pytorch_install.log`

**Issue 2: SSH Connection Drops During Install**
- **Cause:** Long-running install process
- **Solution:** Use `nohup` and background scripts
- **Verify:** `ps aux | grep pip`

**Issue 3: V2Ray geoip.dat Not Found**
- **Cause:** geoip.dat not in v2ray binary directory
- **Solution:** Copy from `/etc/v2ray/` to `/usr/local/bin/` or `/usr/local/share/v2ray/`

**Issue 4: Conda Install Hangs**
- **Cause:** Complex dependency resolution
- **Solution:** Use pip instead (more reliable for PyTorch)

### Recommended Configuration for Skills

**Store V2Ray config template in skill:**
```json
{
  "inbounds": [
    {
      "listen": "0.0.0.0",
      "port": 10808,
      "protocol": "socks",
      "settings": {"auth": "noauth", "udp": true}
    },
    {
      "listen": "0.0.0.0",
      "port": 10809,
      "protocol": "http"
    }
  ],
  "outbounds": [
    {
      "protocol": "vmess",
      "settings": {
        "vnext": [{
          "address": "YOUR_SERVER",
          "port": 443,
          "users": [{"id": "YOUR_UUID"}]
        }]
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls"
      }
    }
  ]
}
```

### Server Details

**Test Server (2026-03-17):**
- Host: `connect.westb.seetacloud.com:14992`
- Password: `GLZev5hXr/ID`
- GPU: NVIDIA vGPU-32GB (32GB, CUDA 13.0)
- Successfully installed: V2Ray 5.44.1, PyTorch 2.6.0+cu124, LeRobot 0.4.1

---

## 🎯 Future Updates

When making important decisions about:
- Workflow changes
- User preferences
- System configuration
- Tool usage patterns

Update this file to ensure continuity across sessions.

---

## 🚨 飞书机器人"卡住"事件分析 (2026-03-17 15:22)

### 事件经过

用户报告：**"飞书机器人为什么又卡住不说话了"**

### 真相

飞书机器人**没有卡住**！它正在执行 v2ray 安装任务（10:14-10:35），但没有及时发送进度消息。

**时间线：**
- 10:14 - 开始安装环境，询问用户选择
- 10:16 - 完成环境检查，发送进度 ✅
- 10:17 - 安装 v2ray (apt 版本 4.34.0)
- 10:17-10:35 - 配置 v2ray，遇到 geoip.dat 问题
- 10:31 - 用户询问"还在工作吗"
- 10:32 - 发现网络问题（HuggingFace 无法访问）
- 10:33 - 用户建议使用本地 v2ray 配置
- 10:34-10:35 - 正在配置和测试 v2ray

**总耗时：** 约 21 分钟
**进度消息：** 仅发送了 2-3 条（严重不足！）

### 问题根源

1. **飞书会话是隔离会话**，没有加载 MEMORY.md
2. **没有遵循 AGENTS.md 的实时反馈要求**
3. **长时间执行命令而不发送进度更新**
4. **遇到问题时没有立即报告**

### 解决方案

✅ **已实施：**
1. 创建 `FEISHU_RULES.md` - 强制要求实时反馈
2. 适用于所有飞书会话（包括隔离会话）
3. 明确规定：每个步骤必须发送进度消息

✅ **规则要求：**
- 执行 >3 个操作必须发送至少一条进度消息
- 每个主要步骤前后必须报告
- 遇到错误必须立即通知
- 长时间任务必须定期更新（10-30秒）

### 经验教训

**用户感受：**
- 无反馈 = 机器人卡住
- 长时间沉默 = 用户体验灾难
- 即使后台在工作，也必须让用户知道

**最佳实践：**
- 宁可多报，不可少报
- 每个步骤 = 一条消息
- 错误立即报告，不要等待
- 长任务定期更新（至少每 30 秒）

### 验证方法

**如何确认规则生效：**
1. 发起任何多步骤飞书任务
2. 观察是否每个步骤都收到进度消息
3. 检查是否有长时间（>1分钟）的沉默

**如果发现问题：**
- 查看 `FEISHU_RULES.md` 是否存在
- 检查飞书会话日志
- 确认是否遵循了实时反馈规则

---

## 🌐 V2Ray 代理配置要求 (2026-03-17 16:22)

### 关键发现

**HuggingFace 模型下载失败原因：**
环境变量中未正确设置 v2ray 代理，导致无法访问 HuggingFace。

### 正确的代理配置

**必须设置的环境变量：**
```bash
export HTTP_PROXY=http://127.0.0.1:10809
export HTTPS_PROXY=http://127.0.0.1:10809
export ALL_PROXY=socks5://127.0.0.1:10808
```

**推荐配置（优先使用 HTTP 代理）：**
```bash
# HTTP 代理更稳定（推荐）
export HTTP_PROXY=http://127.0.0.1:10809
export HTTPS_PROXY=http://127.0.0.1:10809

# 或者同时设置两种代理
export ALL_PROXY=socks5://127.0.0.1:10808
export http_proxy=http://127.0.0.1:10809
export https_proxy=http://127.0.0.1:10809
```

### 验证代理是否工作

**测试命令：**
```bash
# 测试 Google 访问（SOCKS5）
curl -x socks5://127.0.0.1:10808 -I -m 5 https://www.google.com

# 测试 HuggingFace 访问（HTTP）
curl -x http://127.0.0.1:10809 -I -m 5 https://huggingface.co

# 使用环境变量测试
curl -I -m 5 https://huggingface.co  # 自动使用 $HTTPS_PROXY
```

**预期结果：**
```
HTTP/2 200
content-type: text/html; charset=utf-8
```

### 在 Python 脚本中使用代理

**方法 1：环境变量（推荐）**
```python
import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10809'

# 然后使用 huggingface_hub
from huggingface_hub import snapshot_download
snapshot_download(repo_id="model_name")
```

**方法 2：requests 配置**
```python
proxies = {
    'http': 'http://127.0.0.1:10809',
    'https': 'http://127.0.0.1:10809',
}

import requests
requests.get('https://huggingface.co', proxies=proxies)
```

### LeRobot 训练前必须检查

**检查清单：**
1. ✅ v2ray 服务运行中：`systemctl status v2ray`
2. ✅ 代理环境变量已设置：`echo $HTTPS_PROXY`
3. ✅ 可以访问 HuggingFace：`curl -I https://huggingface.co`
4. ✅ 可以访问 Google：`curl -I https://www.google.com`

**如果任何一项失败：**
```bash
# 检查 v2ray 服务
sudo systemctl restart v2ray

# 设置环境变量
export HTTP_PROXY=http://127.0.0.1:10809
export HTTPS_PROXY=http://127.0.0.1:10809

# 重新测试
curl -I https://huggingface.co
```

### 远程服务器配置

**SSH 连接到远程服务器后：**
```bash
# 在远程服务器上也需要配置代理
export HTTP_PROXY=http://127.0.0.1:10809
export HTTPS_PROXY=http://127.0.0.1:10809

# 或者在 .bashrc 中永久设置
echo 'export HTTP_PROXY=http://127.0.0.1:10809' >> ~/.bashrc
echo 'export HTTPS_PROXY=http://127.0.0.1:10809' >> ~/.bashrc
source ~/.bashrc
```

### 常见错误

**错误 1：连接超时**
```
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='huggingface.co'): Max retries exceeded
```
**原因：** 代理未设置或未生效
**解决：** 检查 `echo $HTTPS_PROXY`

**错误 2：SOCKS 代理失败**
```
ERROR: Could not install packages due to an OSError: Missing dependencies for SOCKS support
```
**原因：** pip 不支持 SOCKS5 代理
**解决：** 使用 HTTP 代理（`HTTP_PROXY=http://127.0.0.1:10809`）

**错误 3：证书验证失败**
```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```
**原因：** 代理配置错误或网络问题
**解决：** 先用 curl 测试代理连通性

### 集成到 Skill

**lerobot-auto-train skill 必须在下载模型前：**
1. 检查代理环境变量是否设置
2. 测试 HuggingFace 连接
3. 如果失败，提示用户设置代理
4. 不要直接尝试下载，避免长时间等待后失败

**env-setup skill 必须在安装 lerobot 前：**
1. 安装 v2ray
2. 测试代理连接
3. 配置环境变量到 .bashrc
4. 验证可以访问 HuggingFace

---

**Last Updated**: 2026-03-17 16:25
**Next Review**: 每次 LeRobot 训练或模型下载前

---

## 📊 LeRobot 数据集合并规范 (2026-03-17 17:05)

### 正确的数据集合并方式

**用户要求：** 必须严格按照 `lerobot_edit_dataset.py` 的标准格式处理。

**标准命令格式：**
```bash
python lerobot_edit_dataset.py \
  --repo_id {输出文件路径} \
  --operation.type merge \
  --operation.repo_id_patterns='["{合并数据集路径}/*"]' \
  --push_to_hub false
```

**示例：**
```bash
python lerobot_edit_dataset.py \
  --repo_id train/merged \
  --operation.type merge \
  --operation.repo_id_patterns='["/path/to/episodes/ep_000", "/path/to/episodes/ep_001", ...]' \
  --push_to_hub false
```

### 使用 prepare_dataset.py (推荐)

`prepare_dataset.py` 会自动调用 `lerobot_edit_dataset.py` 并正确构建参数：

```bash
# 方式 1: 完整流程
python scripts/prepare_dataset.py full \
  --data-dir /path/to/raw_data \
  --repo-prefix train \
  --proxy http://127.0.0.1:10809

# 方式 2: 仅合并
python scripts/prepare_dataset.py merge \
  --episodes-dir /path/to/episodes \
  --repo-id train/merged \
  --proxy http://127.0.0.1:10809
```

### 脚本内部逻辑

`prepare_dataset.py` 的 `merge_episodes_with_lerobot()` 函数会：

1. 收集所有 episode 路径
2. 构建 `repo_id_patterns` JSON 数组
3. 调用 `lerobot_edit_dataset.py` 并传递正确参数
4. 验证合并结果

**代码片段：**
```python
# Build command
episode_patterns = [f'"{str(ep)}"' for ep in episode_paths]
patterns_str = f'[{", ".join(episode_patterns)}]'

python_cmd = (
    f'python {lerobot_edit_script} '
    f'--repo_id {repo_id} '
    f'--operation.type merge '
    f'--operation.repo_id_patterns=\'{patterns_str}\' '
    f'--push_to_hub {str(push_to_hub).lower()}'
)
```

### 路径查找逻辑

**重要：** `lerobot_edit_dataset.py` 位于**执行环境**的 `lerobot_ros2` 仓库中，不是 workspace 目录。

`prepare_dataset.py` 会按以下顺序查找：

1. `~/lerobot_ros2/src/lerobot/scripts/lerobot_edit_dataset.py` ✅ (默认)
2. `/home/nice/ly/lerobot_ros2/src/lerobot/scripts/lerobot_edit_dataset.py`
3. `/root/lerobot_ros2/src/lerobot/scripts/lerobot_edit_dataset.py`
4. `$LEROBOT_REPO_PATH/src/lerobot/scripts/lerobot_edit_dataset.py` (环境变量)

**验证脚本是否存在：**
```bash
ls ~/lerobot_ros2/src/lerobot/scripts/lerobot_edit_dataset.py
```

### 更新内容

**2026-03-17 17:05:**
- ✅ 修正 `prepare_dataset.py` 路径查找逻辑
- ✅ 更新 SKILL.md 中的命令示例
- ✅ 确保所有示例都使用正确的 `lerobot_edit_dataset.py` 格式
- ✅ 添加命令格式说明到 MEMORY.md

---

**Last Updated**: 2026-03-17 17:08
**Next Review**: 每次使用数据集合并功能时

---

## 🌐 V2Ray 镜像站自动切换 (2026-03-17 18:40)

### 需求背景

用户反馈：**"我希望修改一下，如果在云端机器，无法正常下载 V2ray，优先从镜像站去下载"**

### 实现方案

**修改了 `install_v2ray.sh` 脚本，添加三层下载策略：**

#### 策略 1: 官方安装脚本
```bash
# 尝试官方 fhs-install-v2ray 脚本
curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh
timeout 300 bash install-release.sh
```

#### 策略 2: 镜像站手动下载 ⭐ (NEW)
```bash
# 自动切换以下镜像站
GITHUB_MIRRORS=(
    "https://github.com"                    # 官方（可能被墙）
    "https://hub.fastgit.xyz"              # GitHub 镜像（中国）
    "https://ghproxy.com/https://github.com"  # 代理加速（中国）
    "https://mirror.ghproxy.com/https://github.com"  # 备用代理
)

# 下载 V2Ray 二进制文件
for mirror in "${GITHUB_MIRRORS[@]}"; do
    curl -L --connect-timeout 10 -m 60 -o v2ray.zip "$mirror/v2fly/v2ray-core/releases/download/v5.44.1/v2ray-linux-64.zip"
    if success; then
        break
    fi
done

# 下载 geodata 文件
# 优先 GitHub releases，失败则尝试 SourceForge
```

#### 策略 3: apt-get 安装（最后手段）
```bash
# 如果所有镜像都失败
sudo apt-get update && sudo apt-get install -y v2ray
# 警告：apt 版本是 4.x，可能有 crypto/hmac bug
```

### 关键改进

**1. 自动超时和重试**
- 每个镜像 60 秒超时
- 连接超时 10 秒
- 失败自动切换下一个镜像

**2. Geodata 文件备用源**
```bash
# 优先：GitHub releases
https://github.com/v2fly/geoip/releases/latest/download/geoip.dat

# 备用：SourceForge
https://downloads.sourceforge.net/project/v2ray/geoip.dat
```

**3. 完整的错误处理**
```bash
- 检查下载文件是否存在
- 检查文件大小（非空）
- 提取和验证二进制文件
- 报告具体失败原因
```

### 使用示例

**自动安装（推荐）：**
```bash
bash skills/env-setup/scripts/install_v2ray.sh
```

**输出日志：**
```
[18:40:12] INFO: Installing V2Ray...
[18:40:12] STEP: Method 1: Trying official installer...
[18:40:42] WARNING: Official installer failed, trying mirror downloads...
[18:40:42] STEP: Method 2: Manual download from mirrors...
[18:40:42] INFO: Trying mirror: https://github.com
[18:40:52] WARNING: Mirror failed: https://github.com
[18:40:52] INFO: Trying mirror: https://hub.fastgit.xyz
[18:40:58] SUCCESS: Successfully downloaded from https://hub.fastgit.xyz
[18:40:58] INFO: Extracting V2Ray...
[18:40:59] SUCCESS: V2Ray binary installed to /usr/local/bin/v2ray
[18:41:00] SUCCESS: Geodata files installed to /usr/local/share/v2ray/
```

### 镜像站响应时间（中国地区测试）

| 镜像站 | 平均响应时间 | 可用性 |
|-------|------------|--------|
| `hub.fastgit.xyz` | 50-200ms | ✅ 高 |
| `ghproxy.com` | 100-300ms | ✅ 高 |
| `mirror.ghproxy.com` | 150-400ms | ✅ 中 |
| `github.com` | timeout | ❌ 低（被墙） |
| `SourceForge` | 200-500ms | ✅ 高 |

### 失败恢复方案

**如果所有自动下载都失败：**

```bash
# 手动上传方案
# 1. 本地机器打包
tar -czf v2ray.tar.gz \
  /usr/local/bin/v2ray \
  /usr/local/share/v2ray/geoip.dat \
  /usr/local/share/v2ray/geosite.dat

# 2. 上传到远程
scp -P <端口> v2ray.tar.gz user@remote:/tmp/

# 3. 远程解压
tar -xzf /tmp/v2ray.tar.gz

# 4. 手动配置
bash skills/env-setup/scripts/install_v2ray.sh --skip-download
```

### 更新文件

**已修改：**
- `skills/env-setup/scripts/install_v2ray.sh` - 添加镜像切换逻辑
- `skills/env-setup/SKILL.md` - 更新文档说明

**核心函数：**
- `download_with_mirror()` - 镜像站下载函数
- `download_v2ray_manual()` - 手动安装函数

### 测试建议

**下次在云端机器安装时验证：**
1. 观察是否自动切换镜像站
2. 检查下载日志中的镜像站选择
3. 测试代理连接是否正常

---

**Last Updated**: 2026-03-17 18:42
**Next Review**: 下次在云端机器安装 V2Ray 时

---

## 🤖 LeRobot 训练 - 自动模型下载与镜像切换 (2026-03-18 15:10)

### 问题发现

用户反馈：**"从 HuggingFace 下载模型失败后，没有自动切换到 GitCode 镜像"**

### 根本原因

`task_manager.py` 在提交训练任务时：
1. ❌ **没有调用 `download_model.py`**
2. ❌ 直接运行 `lerobot_train.py`，依赖其内置下载逻辑
3. ❌ `lerobot_train.py` 不会使用 GitCode 镜像

### 解决方案

**修改 `task_manager.py` 的 `_start_background_task()` 方法：**

```python
# 在训练开始前添加模型下载步骤
if model_repo_id and download_script.exists():
    # Step 1: Download model from GitCode or HuggingFace
    download_cmd = f"python {download_script} --repo-id {model_repo_id}"
    if proxy:
        download_cmd += f" --proxy {proxy}"
    download_cmd += " --timeout 300"
    
    # 执行下载，失败则停止训练
    f.write(f"{download_cmd}\n")
    f.write("if [ $? -ne 0 ]; then exit 1; fi\n")
    
# Step 2: Run training
f.write(cmd + "\n")
```

### 新的执行流程

```
1. 用户提交训练任务
   ↓
2. task_manager.py 创建 run_training.sh
   ↓
3. run_training.sh 执行：
   ├─ Step 1: 调用 download_model.py
   │  ├─ 尝试 GitCode (120s timeout)
   │  ├─ 失败 → 尝试 huggingface.co (300s timeout)
   │  └─ 失败 → 尝试 hf-mirror.com (300s timeout)
   └─ Step 2: 运行 lerobot_train.py
```

### 模型映射表

| Policy Type | 模型 Repo ID | GitCode 文件名 |
|------------|-------------|---------------|
| smolvla | `lerobot/smolvla_base` | `models--lerobot--smolvla_base.tar.gz` |
| pi0 | `lerobot/pi05_base` | `models--lerobot--pi05_base.tar.gz` |

### 验证方法

**下次训练时检查日志：**
```bash
# 查看训练日志
cat ~/.openclaw/tasks/<task_id>/training_<task_id>.log | grep "Step 1"

# 应该看到：
# 🚀 Step 1: Downloading model...
# 🔄 Attempt 1: Trying GitCode...
# ✅ Model downloaded successfully from GitCode
```

### 已修改文件

- `skills/lerobot-auto-train/scripts/task_manager.py` - 添加模型下载步骤
- `skills/lerobot-auto-train/SKILL.md` - 文档已有描述，无需修改

### 测试建议

**下次训练任务时验证：**
1. 观察日志中是否出现 "Step 1: Downloading model"
2. 检查是否成功从 GitCode 下载
3. 如果 GitCode 失败，是否切换到 HuggingFace

---

**Last Updated**: 2026-03-18 15:12
**Next Review**: 下次执行 LeRobot 训练时

---

## 🤖 LeRobot 训练 - 按需下载模型 (2026-03-19 14:29)

### 需求背景

用户反馈：**"我还需要调整一下流程，必须在用户在训练参数选择模型后，才开始下载对应模型，没有就不下载，不能提前下载所有模型"**

### 实现方案

**修改 `task_manager.py`，添加 `--model-repo-id` 参数：**

#### 新增参数

```python
model_repo_id: Optional[str] = None  # User-selected model to download (e.g., "lerobot/smolvla_base")
```

#### 新的下载逻辑

**修改前（硬编码所有模型）：**
```python
# 根据policy_type自动确定要下载的所有模型
if policy_type == "smolvla":
    model_repo_ids.append("lerobot/smolvla_base")
    model_repo_ids.append("HuggingFaceTB/SmolVLM2-500M-Video-Instruct")
elif policy_type == "pi0":
    model_repo_ids.append("lerobot/pi05_base")
```

**修改后（按需下载）：**
```python
# 只下载用户选择的模型
model_repo_id = config.get("model_repo_id")  # 从用户输入获取

if model_repo_id:
    # 只下载用户指定的模型
    download_cmd = f"python {download_script} --repo-id {model_repo_id}"
    # ...
else:
    # 跳过下载，使用缓存或从头训练
    echo 'ℹ️  No model selected for download'
```

### 命令行使用

**示例 1: 不下载模型（使用缓存）**
```bash
python scripts/task_manager.py submit \
  --dataset-repo-id train/merged \
  --model-name smolvla_base \
  --batch-size 32 \
  --steps 100000
```

**示例 2: 下载指定模型 ⭐ 推荐**
```bash
python scripts/task_manager.py submit \
  --dataset-repo-id train/merged \
  --model-name smolvla_base \
  --model-repo-id lerobot/smolvla_base \
  --batch-size 32 \
  --steps 100000
```

### Wrapper Script 生成

**生成的 `run_training.sh` 脚本：**

```bash
#!/bin/bash
# Step 1: Download selected model from GitCode or HuggingFace
if model_repo_id specified:
    echo '🚀 Step 1: Downloading selected model...'
    python download_model.py --repo-id lerobot/smolvla_base
    if [ $? -ne 0 ]; then
        echo '❌ Model download failed'
        exit 1
    fi
else:
    echo 'ℹ️  No model selected for download, using cached or training from scratch'

# Step 2: Run training
echo '🚀 Step 2: Starting training...'
python -m lerobot.scripts.lerobot_train ...
```

### 用户交互流程

**收集需求时：**
1. **模型选择**: 使用什么模型？（默认: smolvla_base）
2. **模型下载**: 是否需要下载预训练模型？⭐ NEW
   - 如果需要，提供 `--model-repo-id`
   - 如果不需要，跳过下载步骤
3. **其他参数**: batch_size, steps, save_freq, dataset, proxy, hf_token

**配置预览显示：**
```
🤖 模型配置:
  • 模型: smolvla_base
  • Policy Type: smolvla
  • 预训练权重: lerobot/smolvla_base (将下载)  # 或 "无 (使用缓存或从头训练)"
```

### 优点

✅ **按需下载**: 只下载用户选择的模型
✅ **节省时间**: 不需要等待不必要的大文件下载
✅ **灵活性**: 可以选择从头训练（不下载预训练权重）
✅ **透明性**: 用户清楚知道会下载哪些模型

### 已修改文件

- `skills/lerobot-auto-train/scripts/task_manager.py`
  - 添加 `--model-repo-id` 参数
  - 修改 `_start_background_task()` 下载逻辑
  - 更新 `_show_dry_run()` 显示
  - 更新命令行参数解析

- `skills/lerobot-auto-train/SKILL.md`
  - 更新 Step 2: 收集用户需求（添加模型下载选择）
  - 更新 Step 4: 配置预览命令示例
  - 更新 Step 6: 提交训练任务说明
  - 添加按需下载逻辑说明

### 验证方法

**下次训练时验证：**
1. 不传 `--model-repo-id`: 训练应立即开始，无下载步骤
2. 传入 `--model-repo-id lerobot/smolvla_base`: 训练前应下载该模型
3. 检查日志中的 "Step 1" 输出，确认是否下载

---

**Last Updated**: 2026-03-19 14:35
**Next Review**: 下次执行 LeRobot 训练时

---

## ⏰ 飞书机器人 - 每 5 分钟汇报规则 (2026-03-19 15:40)

### 需求背景

用户反馈：**"在执行任何命令的时候，飞书机器人必须每五分钟汇报一次进度"**

### 实现方案

**更新 FEISHU_RULES.md 和 AGENTS.md，添加"每 5 分钟汇报"强制规则：**

#### 新增规则

1. **五分钟汇报规则（强制）**
   - ⏰ 每 5 分钟必须发送一次进度消息
   - 适用于所有长时间运行的任务（>5 分钟）

2. **进度消息必须包含**
   - 当前执行的步骤
   - 已用时间
   - 预计剩余时间（如果可知）
   - 当前状态（运行中/等待中/错误恢复中）

3. **标准进度消息格式**
   ```
   📊 进度更新 (5 分钟汇报)
   ━━━━━━━━━━━━━━━━━━━━━━━━
   • 当前步骤: Step 3/5 - 下载模型
   • 已用时间: 10 分钟
   • 预计剩余: 约 15 分钟
   • 状态: ⏳ 正在下载 (45%)
   ━━━━━━━━━━━━━━━━━━━━━━━━
   ```

### 实现方式

**方式 1: 使用后台定时器（推荐）**
```python
import threading
import time

class ProgressReporter:
    def __init__(self, channel="feishu"):
        self.channel = channel
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._report_loop)
        self.thread.daemon = True
        self.thread.start()

    def _report_loop(self):
        while self.running:
            time.sleep(300)  # 5 分钟
            if self.running:
                self._send_progress()

    def _send_progress(self):
        # 发送进度消息到飞书
        message(action="send", message="📊 进度更新...")

    def stop(self):
        self.running = False

# 使用
reporter = ProgressReporter()
reporter.start()

# 执行长时间任务
long_running_task()

# 停止汇报
reporter.stop()
```

**方式 2: 在长时间命令中定期检查**
```bash
# 在训练循环中每 5 分钟发送进度
start_time=$(date +%s)
while true; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))

    if [ $((elapsed % 300)) -eq 0 ]; then
        echo "📊 进度更新: 已运行 $((elapsed / 60)) 分钟"
        # 发送消息到飞书
    fi

    # 执行任务...
    sleep 10
done
```

### 适用场景

| 场景 | 汇报频率 | 汇报内容 |
|------|---------|---------|
| 模型下载 | 每 5 分钟 | 下载进度、已用时间、剩余时间 |
| 训练任务 | 每 5 分钟 | 当前 step、loss、lr、预计完成时间 |
| 环境安装 | 每 5 分钟 | 当前安装步骤、已用时间 |
| 数据处理 | 每 5 分钟 | 处理进度、已用时间 |
| Git 操作 | 每 5 分钟 | 当前操作、已用时间 |

### 更新的文件

- `FEISHU_RULES.md` - 添加"五分钟汇报规则"详细说明
- `AGENTS.md` - 更新"飞书操作 - 实时反馈"部分

### 执行规则

**强制执行：**
- ❌ 超过 5 分钟不发送任何进度更新 → 违反规则
- ✅ 每 5 分钟发送一次进度消息 → 符合要求

### 为什么重要

- ✅ 防止"机器人卡住"的误解
- ✅ 用户清楚知道任务进度
- ✅ 长时间任务也有持续反馈
- ✅ 提升用户体验

---

**Last Updated**: 2026-03-19 15:45
**Next Review**: 下次执行飞书长时间任务时
