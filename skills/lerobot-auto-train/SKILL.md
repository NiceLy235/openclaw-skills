---
name: lerobot-auto-train
description: >
  Automate lerobot_ros2 training and inference workflows with background task
  execution and real-time progress monitoring. Use when users want to: (1) Train
  models on GPU with automated pipeline, (2) Run training tasks in background
  while continuing other work, (3) Monitor training progress in real-time,
  (4) Test trained models with inference validation, (5) Manage training tasks
  (submit/stop/resume). Triggers on keywords like "开始训练", "训练", "训练模型",
  "训练任务", "GPU训练", "lerobot训练", "自动化训练", "后台训练", "训练监控",
  "推理测试", "启动训练", "进行训练", "运行训练", "模型训练". **CRITICAL: When user
  mentions any training-related keywords, MUST activate this skill FIRST instead
  of manually executing commands.**

  MANDATORY: Execute steps in strict order. Stop on any error.
metadata:
  {
    "openclaw": {
      "emoji": "🤖"
    }
  }
---

# Lerobot Auto Train

自动化完整训练流程：数据准备 → 数据集合并 → 训练 → 验证 → 推理测试

⚠️ **CRITICAL: Execute steps in strict order as listed below. Do NOT skip any step.**

---

## MANDATORY Execution Rules

1. **Execute steps sequentially** - Complete Step 1 before starting Step 2
2. **Report progress after EACH step** - Inform user of completion before proceeding
3. **Do NOT skip verification steps** - Always verify dataset exists before training
4. **Stop on error** - If any step fails, report the error and STOP. Do NOT proceed with remaining steps
5. **Require user confirmation** - MUST get user confirmation before submitting training task
6. **Monitor training progress** - Report training progress every 30 seconds

---

## Progress Reporting Rules

1. **Start each step** with: `### Step X: [Name]`
2. **After each step**, report: `✅ Step X completed: [summary]`
3. **If a step fails**, report: `❌ Step X failed: [error details]`
4. **Before next step**, indicate: `→ Proceeding to Step X+1...`
5. **During training**, report: `📊 训练进度：[current]/[total] (loss: [value])`

---

## Error Handling

### Step Failure Protocol

**When a step fails:**

1. **Immediately report error:**
   ```
   ❌ 步骤 X 失败：[具体错误信息]
   错误详情：[command output]
   ```

2. **Attempt recovery (if applicable):**
   ```
   🔧 正在尝试恢复...
   恢复方案：[description]
   ```

3. **If recovery succeeds:**
   ```
   ✅ 恢复成功，继续执行
   ```

4. **If recovery fails or not applicable:**
   ```
   ❌ 无法恢复，停止训练
   已完成步骤：X-1
   失败步骤：X
   ```

### Error Recovery Strategies

| Error Type | Recovery Strategy |
|------------|------------------|
| lerobot_ros2 repository not found | Run `env-setup` skill to install lerobot first |
| Training script not found | Verify repository integrity, re-clone if needed |
| Dataset not found | Check `--dataset-repo-id`, verify dataset exists |
| CUDA OOM | Reduce `--batch-size` and retry |
| HuggingFace inaccessible | Check proxy configuration, verify V2Ray running |
| Conda environment not found | Verify conda environment name, create if needed |
| Disk space full | Clean up checkpoints and retry |

---

## Core Features

- ✅ 使用 `lerobot_edit_dataset` 合并数据集
- ✅ 使用 `lerobot_train` 进行训练
- ✅ 后台执行（不阻塞）
- ✅ 实时进度监控
- ✅ 代理和 HuggingFace Token 配置
- ✅ 自动验证和恢复
- ⚠️ **训练前必须确认参数**（见下方流程）

---

## Step-by-Step Execution Template

Use this template for ANY training operation:

### Step 1: Pre-flight Checks
- **Action**: Verify lerobot_ros2 repository (installed by env-setup skill), conda environment and GPU availability
- **Command**:
  ```bash
  # 1.1 Check lerobot_ros2 repository location (env-setup installs to ~/lerobot_ros2)
  LEROBOT_DIR=""
  if [ -d ~/lerobot_ros2 ]; then
    LEROBOT_DIR=~/lerobot_ros2
    echo "✅ lerobot_ros2 仓库存在: ~/lerobot_ros2"
  elif [ -d /root/lerobot_ros2 ]; then
    LEROBOT_DIR=/root/lerobot_ros2
    echo "✅ lerobot_ros2 仓库存在: /root/lerobot_ros2"
  else
    echo "❌ lerobot_ros2 仓库不存在"
  fi

  # 1.2 Check training script exists (lerobot_train.py is inside lerobot_ros2 repo)
  if [ -n "$LEROBOT_DIR" ]; then
    test -f $LEROBOT_DIR/src/lerobot/scripts/lerobot_train.py && \
      echo "✅ 训练脚本存在: $LEROBOT_DIR/src/lerobot/scripts/lerobot_train.py" || \
      echo "❌ 训练脚本不存在"
  fi

  # 1.3 Check conda environment (default: lerobot, created by env-setup skill)
  CONDA_ENV_NAME="${CONDA_ENV_NAME:-lerobot}"
  conda env list | grep -q "^${CONDA_ENV_NAME} " && \
    echo "✅ Conda 环境存在: $CONDA_ENV_NAME" || \
    echo "❌ Conda 环境不存在: $CONDA_ENV_NAME (请先运行 env-setup skill)"

  # 1.4 Check GPU
  nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || echo "❌ 无 GPU"

  # 1.5 Check lerobot import (must run from lerobot_ros2 directory)
  cd $LEROBOT_DIR 2>/dev/null && conda activate $CONDA_ENV_NAME && \
    python -c "import lerobot; print(f'LeRobot: {lerobot.__version__}')" || \
    echo "❌ lerobot 无法导入"
  ```
- **Expected**:
  - ✅ `lerobot_ros2` 仓库存在于 `~/lerobot_ros2` 或 `/root/lerobot_ros2`
  - ✅ 训练脚本存在于 `<repo>/src/lerobot/scripts/lerobot_train.py`
  - ✅ Conda environment `lerobot` exists (created by env-setup)
  - ✅ CUDA available, GPU memory reported
  - ✅ LeRobot can be imported (when running from repo directory)
- **If Failed**:
  - If repository not found: Run `env-setup` skill first to install lerobot
  - If training script missing: Re-clone repository
  - If conda env not found: Run `env-setup` skill to create environment
  - If no GPU: Training requires GPU, cannot proceed
**[Run command and report output]**

### Step 2: Collect User Requirements
- **Action**: Ask user for training parameters
- **Required inputs**:
  - Model name (default: smolvla_base)
  - Dataset path or repo_id
  - Batch size, steps, save_freq
  - Proxy and HuggingFace token
- **Expected**: All required parameters provided
**[Ask user, verify inputs]**

### Step 3: Prepare Dataset
- **Action**: Merge episodes into training dataset
- **Command**:
  ```bash
  python scripts/prepare_dataset.py full \
    --data-dir /path/to/data \
    --repo-prefix train \
    --proxy http://127.0.0.1:10809
  ```
- **Expected**: Dataset merged successfully, repo_id returned
**[Run command, verify, report]**

### Step 4: Generate Configuration Preview
- **Action**: Generate complete training configuration
- **Command**:
  ```bash
  python scripts/task_manager.py submit \
    --dataset-repo-id train/merged \
    --model-name smolvla_base \
    --batch-size 32 \
    --steps 100000 \
    --dry-run
  ```
- **Expected**: Full configuration displayed
**[Run command, display config to user]**

### Step 5: Wait for User Confirmation
- **Action**: Present configuration and ask for confirmation
- **Message**:
  ```
  📋 训练配置预览
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [Full configuration details]

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  确认启动训练？(yes/no)
  ```
- **Required**: User must respond "yes" or "确认"
**[Wait for user response]**

### Step 6: Submit Training Task
- **Action**: Submit training task (only after user confirmation)
- **Command**:
  ```bash
  python scripts/task_manager.py submit \
    --dataset-repo-id train/merged \
    --model-name smolvla_base \
    --batch-size 32 \
    --steps 100000 \
    --proxy http://127.0.0.1:10809 \
    --hf-token YOUR_TOKEN
  ```
- **Expected**: Task ID returned, training started
**[Run command, verify, report task ID]**

### Step 7: Monitor Training Progress
- **Action**: Monitor training progress in real-time
- **Command**:
  ```bash
  python scripts/task_manager.py status <task_id>
  ```
- **Interval**: Report every 30 seconds
- **Expected**: Progress updates (current_step, loss, lr)
**[Monitor and report regularly]**

### Step 8: Generate Training Report
- **Action**: Generate final training report
- **Command**:
  ```bash
  python scripts/task_manager.py logs <task_id> --tail 100
  ```
- **Expected**: Training summary with final metrics
**[Run command, display report]**

---

## ⚠️ 训练前确认流程（强制）

**在提交任何训练任务之前，Agent 必须执行以下确认步骤：**

### 步骤 1: 收集用户需求

询问用户：
1. **模型选择**: 使用什么模型？（默认: smolvla_base）
2. **训练参数**: batch_size, steps, save_freq 等
3. **数据集**: 数据集路径或已合并的 repo_id
4. **其他配置**: 代理、HuggingFace Token 等

### 步骤 2: 生成配置预览

使用 `task_manager.py submit --dry-run` 生成完整配置：

```bash
python scripts/task_manager.py submit \
  --dataset-repo-id train/merged \
  --model-name smolvla_base \
  --batch-size 32 \
  --steps 100000 \
  --dry-run
```

### 步骤 3: 展示给用户

**必须展示以下信息：**

```
📋 训练配置预览
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 数据集信息:
  • 数据集: train/merged
  • Episodes: 15
  • 位置: ~/.cache/huggingface/lerobot/train/merged

🤖 模型配置:
  • 模型: smolvla_base
  • Policy Type: smolvla
  • 预训练权重: lerobot/smolvla_base

📊 训练参数:
  • Batch Size: 32
  • Steps: 100000
  • Save Frequency: 每 5000 步
  • Eval Frequency: 每 1000 步
  • Workers: 16

💻 执行环境:
  • 脚本位置: /home/nice/ly/lerobot_ros2/src/lerobot/scripts/lerobot_train.py
  • Conda 环境: lerobot
  • 设备: cuda
  • 输出目录: outputs/mylerobot_train/0313_1052

🔧 完整命令:
```bash
python -m lerobot.scripts.lerobot_train \
  --policy.type smolvla \
  --policy.pretrained_path lerobot/smolvla_base \
  --policy.load_vlm_weights true \
  --policy.device cuda \
  --policy.repo_id train/smolvla_base_policy \
  --policy.push_to_hub false \
  --dataset.repo_id train/merged \
  --output_dir outputs/mylerobot_train/0313_1052 \
  --job_name train_smolvla_base_20260313_1052 \
  --batch_size 32 \
  --steps 100000 \
  --save_freq 5000 \
  --eval_freq 1000 \
  --num_workers 16 \
  --wandb.enable false
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

确认启动训练？(yes/no)
```

### 步骤 4: 等待用户确认

- 用户回复 "yes" → 提交训练任务
- 用户回复 "no" → 取消或修改参数
- 用户未回复 → **不要提交任务**

### 步骤 5: 提交任务

确认后执行：

```bash
python scripts/task_manager.py submit \
  --dataset-repo-id train/merged \
  --model-name smolvla_base \
  --batch-size 32 \
  --steps 100000 \
  --proxy http://127.0.0.1:10809 \
  --hf-token YOUR_TOKEN
```

---

## 前置要求

**关键**: 任务必须在有 `lerobot_ros2` 的机器上运行。

```bash
# 确保已安装
cd /path/to/lerobot_ros2
conda activate lerobot
```

## 快速开始

### 完整流程（推荐）

一条命令完成：合并 → 训练

```bash
python scripts/prepare_dataset.py full \
  --data-dir /home/nice/ly/data/pre_merge_data/2026_03_04_10_06 \
  --repo-prefix train \
  --proxy http://127.0.0.1:10809

# 然后提交训练
python scripts/task_manager.py submit \
  --dataset-repo-id train/merged \
  --model-name smolvla_base \
  --proxy http://127.0.0.1:10809 \
  --hf-token YOUR_TOKEN
```

### 分步执行

#### 1. 合并数据集

使用 `lerobot_edit_dataset` 合并所有 episodes：

```bash
# 合并所有 episodes 到一个数据集
python scripts/prepare_dataset.py merge \
  --episodes-dir /path/to/raw_episodes \
  --repo-id train/merged \
  --proxy http://127.0.0.1:10809
```

**输出**: 数据集保存到 `~/.cache/huggingface/lerobot/train/merged`

#### 2. 提交训练任务

```bash
python scripts/task_manager.py submit \
  --dataset-repo-id train/merged \
  --model-name smolvla_base \
  --policy-type smolvla \
  --batch-size 32 \
  --steps 100000 \
  --save-freq 5000 \
  --eval-freq 1000 \
  --output-dir outputs/mylerobot_train/$(date +%m%d_%H%M) \
  --proxy http://127.0.0.1:10809 \
  --hf-token hf_xxx \
  --background
```

**返回**: Task ID (例如 `train_20260311_150000_abc123`)

#### 4. 监控进度

```bash
# 查看状态
python scripts/task_manager.py status <task_id>

# 查看日志
python scripts/task_manager.py logs <task_id> --lines 100

# 列出所有任务
python scripts/task_manager.py list
```

#### 5. 管理任务

```bash
# 停止任务
python scripts/task_manager.py stop <task_id>

# 查看日志
python scripts/task_manager.py logs <task_id>
```

## 配置参数

### prepare_dataset.py

#### merge 命令

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--episodes-dir` | episodes 目录 | 必填 |
| `--repo-id` | 合并后的 repo ID | 必填 |
| `--proxy` | 代理 URL | 无 |
| `--conda-env` | Conda 环境名 | lerobot |

#### full 命令

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--data-dir` | 原始数据目录 | 必填 |
| `--repo-prefix` | repo ID 前缀 | train |
| `--proxy` | 代理 URL | 无 |
| `--conda-env` | Conda 环境名 | lerobot |

### task_manager.py submit

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--dataset-repo-id` | 数据集 repo ID | 必填 |
| `--model-name` | 模型名称 | smolvla_base |
| `--policy-type` | 策略类型 | smolvla |
| `--batch-size` | 批大小 | 32 |
| `--steps` | 训练步数 | 100000 |
| `--save-freq` | 保存频率 | 5000 |
| `--eval-freq` | 评估频率 | 1000 |
| `--num-workers` | 数据加载器 workers | 16 |
| `--proxy` | 代理 URL | 无 |
| `--hf-token` | HuggingFace Token | 无 |
| `--conda-env` | Conda 环境名 | lerobot |
| `--background` | 后台运行 | True |

## 示例会话

```
用户: "用 15 集数据训练 SmolVLA 模型，数据在 /home/nice/ly/data/pre_merge_data/2026_03_04_10_06"

Agent:

🚀 开始完整训练流程...

# 1. 准备数据集（合并所有 episodes）
$ python scripts/prepare_dataset.py full \
  --data-dir /home/nice/ly/data/pre_merge_data/2026_03_04_10_06 \
  --repo-prefix train \
  --proxy http://127.0.0.1:10809

📁 Step 1: Collecting episodes...
   Found 15 episodes

📊 Step 2: Merging all episodes into single dataset...
✅ Merge successful: train/merged

# 2. 生成配置预览（确认步骤）
$ python scripts/task_manager.py submit \
  --dataset-repo-id train/merged \
  --model-name smolvla_base \
  --batch-size 32 \
  --steps 100000 \
  --dry-run

📋 训练配置预览
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 数据集信息:
  • 数据集: train/merged
  • Episodes: 15
  • 位置: ~/.cache/huggingface/lerobot/train/merged

🤖 模型配置:
  • 模型: smolvla_base
  • Policy Type: smolvla
  • 预训练权重: lerobot/smolvla_base

📊 训练参数:
  • Batch Size: 32
  • Steps: 100000
  • Save Frequency: 每 5000 步
  • Eval Frequency: 每 1000 步
  • Workers: 16

💻 执行环境:
  • 脚本位置: /home/nice/ly/lerobot_ros2/src/lerobot/scripts/lerobot_train.py
  • Conda 环境: lerobot
  • 设备: cuda
  • 输出目录: outputs/mylerobot_train/0313_1052

🔧 完整命令:
```bash
python -m lerobot.scripts.lerobot_train \
  --policy.type smolvla \
  --policy.pretrained_path lerobot/smolvla_base \
  --policy.load_vlm_weights true \
  --policy.device cuda \
  --policy.repo_id train/smolvla_base_policy \
  --policy.push_to_hub false \
  --dataset.repo_id train/merged \
  --output_dir outputs/mylerobot_train/0313_1052 \
  --job_name train_smolvla_base_20260313_1052 \
  --batch_size 32 \
  --steps 100000 \
  --save_freq 5000 \
  --eval_freq 1000 \
  --num_workers 16 \
  --wandb.enable false
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

确认启动训练？(yes/no)

用户: "确认，使用这些参数"

# 3. 提交训练任务（移除 --dry-run）
$ python scripts/task_manager.py submit \
  --dataset-repo-id train/merged \
  --model-name smolvla_base \
  --batch-size 32 \
  --steps 100000 \
  --proxy http://127.0.0.1:10809 \
  --hf-token hf_xxx

✅ Task submitted: train_20260311_150000_abc123
🚀 Training started (PID: 57526)

# 4. 监控
$ python scripts/task_manager.py status train_20260311_150000_abc123

{
  "task_id": "train_20260311_150000_abc123",
  "status": "training",
  "progress": {
    "current_step": 200,
    "total_steps": 100000,
    "loss": 0.068,
    "lr": "1.0e-05"
  }
}
```

## 输出结构

```
~/.openclaw/tasks/<task_id>/
├── meta.json           # 任务元数据
├── run_training.sh     # 生成的训练脚本
└── training_<task_id>.log  # 训练日志

<lerobot_dir>/outputs/<output_dir>/
├── checkpoints/
│   ├── checkpoint_05000.pt
│   └── checkpoint_10000.pt
└── models/
    └── final_model.pt
```

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 无法访问 HuggingFace | 配置 `--proxy` 和 `--hf-token` |
| CUDA OOM | 减少 `--batch-size` |
| 数据集找不到 | 检查 `--dataset-repo-id` 是否正确 |
| 训练不启动 | 检查 conda 环境和代理设置 |

## 与之前流程的对比

| 旧流程 | 新流程 (lerobot-auto-train) |
|--------|------------------------------|
| 手动调用 `lerobot_edit_dataset` | `prepare_dataset.py merge` |
| 手动编写训练脚本 | `task_manager.py submit` |
| 手动监控日志 | `task_manager.py status/logs` |

**一条命令完成所有步骤**:
```bash
python scripts/prepare_dataset.py full --data-dir ... --repo-prefix train
python scripts/task_manager.py submit --dataset-repo-id train/merged
```
