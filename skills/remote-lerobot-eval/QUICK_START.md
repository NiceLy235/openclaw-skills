# Remote Lerobot Evaluation - Quick Start

## 🎯 功能概述

远程执行和监控 lerobot 评估任务，支持：
- ✅ 通过跳板机连接目标机器人
- ✅ tmux 持久会话管理
- ✅ GPU 加速评估
- ✅ 实时终端窗口可视化
- ✅ 图形界面远程访问

## 📋 使用方法

### 方法 1：直接调用 Skill

```
帮我执行远程 lerobot 评估，配置如下：
- 跳板机：192.168.136.128 (nice/NICE)
- 目标机器：10.10.10.54 (root/Nice@123)
- 模型：/home/nice/ly/lerobot_ros2/outputs/mylerobot_train/0106_smolvla_000/checkpoints/020000/pretrained_model
- 数据集：ly/eval_dataset
```

### 方法 2：使用自动化脚本

```bash
# 编辑配置
nano ~/.openclaw/workspace/skills/remote-lerobot-eval/scripts/run_remote_eval.sh

# 修改以下变量：
JUMP_SERVER_IP="192.168.136.128"
JUMP_USER="nice"
JUMP_PASS="NICE"
TARGET_IP="10.10.10.54"
TARGET_USER="root"
TARGET_PASS="Nice@123"
MODEL_PATH="/home/nice/ly/lerobot_ros2/outputs/..."
DATASET_ID="ly/eval_dataset"

# 运行
bash ~/.openclaw/workspace/skills/remote-lerobot-eval/scripts/run_remote_eval.sh
```

## 🖥️ 查看终端窗口

### 在跳板机上

```bash
# 附加到 tmux 会话
tmux attach-session -t lerobot_eval

# 快捷键
Ctrl+B, 0  → 窗口 0（目标机器）
Ctrl+B, 1  → 窗口 1（评估脚本）
Ctrl+B, D  → 退出（进程继续运行）
```

### 远程监控

```bash
# 查看评估窗口
ssh nice@192.168.136.128 'tmux capture-pane -t lerobot_eval:1 -p | tail -30'

# 实时监控
watch -n 2 'ssh nice@192.168.136.128 "tmux capture-pane -t lerobot_eval:1 -p | tail -20"'
```

## 🖼️ 查看图形界面

### 选项 1：VNC 远程桌面

```bash
# 在跳板机上启动 VNC
vncserver :1 -geometry 1920x1080

# 用 VNC 客户端连接
192.168.136.128:5901
```

### 选项 2：Rerun 查看器

```bash
# 在任意机器上
pip install rerun-sdk
rerun --connect rerun+http://192.168.136.128:9876/proxy
```

## ⚠️ 常见问题

### 1. 数据集目录已存在

```bash
tmux send-keys -t lerobot_eval:1 "rm -rf /home/nice/.cache/huggingface/lerobot/ly/eval_dataset" Enter
```

### 2. 电机连接失败

- 检查机器人硬件连接到 `/dev/ttyACM0`
- 确认机器人已上电
- 重启窗口 0 的 cmd.sh

### 3. 网络不可达

```bash
# 确保代理设置
export ALL_PROXY=socks5://127.0.0.1:10808
pip install "httpx[socks]"
```

## 📦 Skill 文件

- **SKILL.md**：完整文档和步骤
- **scripts/run_remote_eval.sh**：自动化执行脚本
- **remote-lerobot-eval.skill**：打包的 skill 文件

## 🔄 重启评估

```bash
# 停止旧进程
pkill -f "evaluate.py"

# 清理缓存
rm -rf /home/nice/.cache/huggingface/lerobot/ly/eval_dataset

# 在窗口 1 中重启
tmux send-keys -t lerobot_eval:1 "python examples/lekiwi/evaluate.py ..." Enter
```

## 📊 正常运行指标

- **CPU**: 200-500%
- **内存**: 2-4 GB
- **GPU**: RTX 4080 活跃推理
- **窗口 0**: 持续输出 `WARNING:root:No command available`
- **窗口 1**: 显示 `Starting evaluate loop...`

---

**Skill 已推送到 GitHub**: `NiceLy235/openclaw-skills`
