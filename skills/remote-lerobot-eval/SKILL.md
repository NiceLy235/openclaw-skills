---
name: remote-lerobot-eval
description: >
  Remote execution and monitoring of lerobot evaluation and inference tasks via jump server with tmux session management.
  Use when: (1) Running lerobot evaluation on remote machines behind jump server, (2) Running lerobot inference
  on remote machines, (3) Need to visualize robot evaluation UI and terminal windows, (4) Managing multi-machine
  workflows with SSH tunneling, (5) Setting up persistent terminal sessions for long-running evaluation/inference
  tasks, (6) User mentions "推理", "开始推理", "运行推理", "inference", "remote evaluation", "jump server", "tmux",
  "lerobot evaluate", "lerobot inference", "robot testing".
  Trigger phrases: "推理", "开始推理", "运行推理", "执行推理", "inference", "remote evaluation", "通过跳板机评估",
  "远程机器人测试", "tmux session", "lerobot 推理".

  **CRITICAL: When user mentions "推理", "开始推理", or any inference-related keywords, MUST activate this skill FIRST.**

  MANDATORY: Execute steps in strict order. Stop on any error.
metadata:
  {
    "openclaw": {
      "emoji": "🔌"
    }
  }
---

# Remote Lerobot Evaluation

Execute and monitor lerobot evaluation tasks on remote machines via jump server with persistent terminal sessions.

⚠️ **CRITICAL: Execute steps in strict order as listed below. Do NOT skip any step.**

---

## MANDATORY Execution Rules

1. **Execute steps sequentially** - Complete Step 1 before starting Step 2
2. **Report progress after EACH step** - Inform user of completion before proceeding
3. **Do NOT skip verification steps** - Always verify tmux session and robot connection
4. **Stop on error** - If any step fails, report the error and STOP. Do NOT proceed with remaining steps
5. **Require user confirmation** - MUST confirm hardware is ready before starting
6. **Monitor evaluation progress** - Report progress every 30 seconds during evaluation

---

## Progress Reporting Rules

1. **Start each step** with: `### Step X: [Name]`
2. **After each step**, report: `✅ Step X completed: [summary]`
3. **If a step fails**, report: `❌ Step X failed: [error details]`
4. **Before next step**, indicate: `→ Proceeding to Step X+1...`
5. **During evaluation**, report: `📊 评估进度：[status]`

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
   ❌ 无法恢复，停止评估
   已完成步骤：X-1
   失败步骤：X
   ```

### Error Recovery Strategies

| Error Type | Recovery Strategy |
|------------|------------------|
| SSH connection failed | Check network, verify credentials, retry |
| tmux session not created | Install tmux, check permissions, retry |
| Robot hardware not connected | STOP - require user to connect hardware |
| Motor connection failed | Check hardware connection, restart cmd.sh |
| HuggingFace inaccessible | Check proxy configuration, verify V2Ray running |
| No X11 display | Set DISPLAY environment or use headless mode |

---

## Step-by-Step Execution Template

Use this template for ANY remote evaluation operation:

### Step 1: Collect Required Parameters and Choose Evaluation Mode
- **Action**: Ask user for evaluation mode and required parameters
- **Evaluation Modes**:
  - **Mode A**: Real Robot Evaluation (requires hardware connection)
  - **Mode B**: Local Dataset Evaluation (no hardware needed)
- **Required inputs for Mode A (Real Robot)**:
  - Jump server IP, username, password
  - Target robot IP, username, password
  - Model path, dataset ID
  - Confirmation that hardware is connected and powered
- **Required inputs for Mode B (Local Dataset)**:
  - Jump server IP, username, password
  - Model path (policy_path)
  - Dataset ID (repo_id)
  - No hardware connection required
- **Expected**: Evaluation mode selected and all required parameters provided
**[Ask user to choose mode, verify all inputs]**

---

## Mode A: Real Robot Evaluation

**Use this mode when**: You want to evaluate on physical robot hardware

**Prerequisites**: Robot hardware connected and powered

### Step A1: SSH to Jump Server
- **Action**: Connect to jump server
- **Command**:
  ```bash
  sshpass -p 'JUMP_PASS' ssh JUMP_USER@JUMP_SERVER_IP
  ```
- **Expected**: Successful SSH connection to jump server
**[Run command, verify, report]**

### Step A2: Verify Environment
- **Action**: Check tmux installation and V2Ray status
- **Command**:
  ```bash
  which tmux
  systemctl status v2ray --no-pager | head -5
  nvidia-smi --query-gpu=name --format=csv,noheader
  ```
- **Expected**: tmux installed, V2Ray running, GPU detected
**[Run commands, verify, report]**

### Step A3: Test Robot Connectivity
- **Action**: Verify connection to target robot
- **Command**:
  ```bash
  sshpass -p 'TARGET_PASS' ssh TARGET_USER@TARGET_IP 'hostname'
  ```
- **Expected**: Robot hostname returned
**[Run command, verify, report]**

### Step A4: Initialize tmux Session
- **Action**: Create tmux session for evaluation
- **Command**:
  ```bash
  tmux kill-session -t lerobot_eval 2>/dev/null
  tmux new-session -d -s lerobot_eval -x 240 -y 60
  tmux list-sessions
  ```
- **Expected**: tmux session created successfully
**[Run command, verify, report]**

### Step A5: Start Robot Host (Window 0)
- **Action**: SSH to robot and start cmd.sh
- **Command**:
  ```bash
  tmux send-keys -t lerobot_eval:0 "sshpass -p 'TARGET_PASS' ssh -t -o StrictHostKeyChecking=no -X TARGET_USER@TARGET_IP \"source /root/miniconda3/bin/activate && cd /root/workspace/lerobot_ros2 && bash cmd.sh\"" Enter
  sleep 5
  tmux send-keys -t lerobot_eval:0 "Enter"
  ```
- **Expected**: Robot host started, showing "No command available"
**[Run command, verify, report]**

### Step A6: Start Evaluation Script (Window 1)
- **Action**: Clear dataset cache and start evaluation
- **Command**:
  ```bash
  tmux new-window -t lerobot_eval -n evaluate
  tmux send-keys -t lerobot_eval:1 "rm -rf /home/JUMP_USER/.cache/huggingface/lerobot/ly/eval_dataset" Enter
  sleep 2
  tmux send-keys -t lerobot_eval:1 "source /home/JUMP_USER/miniconda3/bin/activate lerobot && export ALL_PROXY=socks5://127.0.0.1:10808 && export DISPLAY=:0 && cd /home/JUMP_USER/ly/lerobot_ros2 && python examples/lekiwi/evaluate.py --id=lekiwi --remote_ip=TARGET_IP --hf_model_id=MODEL_PATH --hf_dataset_id=DATASET_ID --is_headless_flag=False" Enter
  ```
- **Expected**: Evaluation script started, loading model
**[Run command, verify, report]**

### Step A7: Monitor Evaluation Progress
- **Action**: Monitor evaluation window periodically
- **Command**:
  ```bash
  tmux capture-pane -t lerobot_eval:1 -p | tail -30
  ps aux | grep "evaluate.py" | grep -v grep
  ```
- **Interval**: Report every 30 seconds
- **Expected**: Progress updates (loading model, inference, etc.)
**[Monitor and report regularly]**

### Step A8: Generate Evaluation Report
- **Action**: Capture final evaluation results
- **Command**:
  ```bash
  tmux capture-pane -t lerobot_eval:1 -p | tail -100
  ```
- **Expected**: Evaluation summary with success/failure status
**[Run command, display report]**

---

## Mode B: Local Dataset Evaluation

**Use this mode when**: You want to evaluate on dataset without physical robot hardware

**Prerequisites**: No hardware connection required

### Step B1: SSH to Jump Server
- **Action**: Connect to jump server
- **Command**:
  ```bash
  sshpass -p 'JUMP_PASS' ssh JUMP_USER@JUMP_SERVER_IP
  ```
- **Expected**: Successful SSH connection to jump server
**[Run command, verify, report]**

### Step B2: Verify Environment
- **Action**: Check V2Ray status and GPU
- **Command**:
  ```bash
  systemctl status v2ray --no-pager | head -5
  nvidia-smi --query-gpu=name --format=csv,noheader
  ```
- **Expected**: V2Ray running, GPU detected
**[Run commands, verify, report]**

### Step B3: Navigate to lerobot_ros2 Directory
- **Action**: Change to lerobot_ros2 directory
- **Command**:
  ```bash
  cd /home/JUMP_USER/ly/lerobot_ros2
  pwd
  ```
- **Expected**: In lerobot_ros2 directory
**[Run command, verify]**

### Step B4: Activate Conda Environment and Set Proxy
- **Action**: Activate lerobot environment and configure proxy
- **Command**:
  ```bash
  source /home/JUMP_USER/miniconda3/bin/activate lerobot
  export ALL_PROXY=socks5://127.0.0.1:10808
  ```
- **Expected**: Conda environment activated, proxy set
**[Run command, verify]**

### Step B5: Execute Dataset Evaluation
- **Action**: Run evaluate_dataset.py with specified parameters
- **Command**:
  ```bash
  python examples/lekiwi/evaluate_dataset.py \
    --policy_path=/home/JUMP_USER/ly/lerobot_ros2/outputs/mylerobot_train/0106_smolvla_000/checkpoints/020000/pretrained_model \
    --repo_id=ly/pre_training_data
  ```
- **Expected**: Evaluation started, processing dataset
**[Run command, verify, report]**

### Step B6: Monitor Evaluation Progress
- **Action**: Monitor evaluation output
- **Interval**: Report progress as it appears
- **Expected**: Progress updates (loading model, processing episodes)
**[Monitor and report regularly]**

### Step B7: Generate Evaluation Report
- **Action**: Capture final evaluation results
- **Expected**: Evaluation summary with metrics (success rate, episode results)
**[Display final results]**

---

## Use Case

This skill manages remote evaluation workflows:
- Target machine (robot hardware) behind jump server
- Evaluation script on jump server
- Persistent terminal sessions via tmux
- GPU-accelerated visualization support

## Architecture

```
[Your Machine] → SSH → [Jump Server 192.168.x.x] → SSH → [Target Robot 10.10.x.x]
                      │                                    │
                      ├─ tmux window 1: evaluate.py        ├─ tmux window 0: cmd.sh
                      ├─ GPU: RTX 4080                     ├─ Robot hardware
                      └─ Visualization UI                  └─ Motor control
```

## Quick Start

### ⚠️ CRITICAL: Ask User First

**DO NOT assume any values.** Always ask the user for evaluation mode and required parameters before executing any commands:

**Step 1: Ask for evaluation mode**
1. Which evaluation mode do you want to use?
   - **Mode A**: Real Robot Evaluation (requires hardware)
   - **Mode B**: Local Dataset Evaluation (no hardware needed)

**Step 2: Ask for required parameters based on mode**

**For Mode A (Real Robot):**
1. What is the jump server IP address? (e.g., 192.168.136.128)
2. What is the jump server username? (e.g., nice)
3. What is the jump server password? (e.g., NICE)
4. What is the target robot IP address? (e.g., 10.10.10.54)
5. What is the target robot username? (e.g., root)
6. What is the target robot password? (e.g., Nice@123)
7. Is the robot hardware connected and powered? (yes/no)

**For Mode B (Local Dataset):**
1. What is the jump server IP address? (e.g., 192.168.136.128)
2. What is the jump server username? (e.g., nice)
3. What is the jump server password? (e.g., NICE)
4. What is the model path? (policy_path, e.g., /home/nice/ly/lerobot_ros2/outputs/mylerobot_train/0106_smolvla_000/checkpoints/020000/pretrained_model)
5. What is the dataset ID? (repo_id, e.g., ly/pre_training_data)

**Wait for user to provide all answers and confirm mode before proceeding.**

---

### Mode A: Real Robot Evaluation Quick Start

**Prerequisites**:
- Jump server IP, username, password (ask user)
- Target robot IP, username, password (ask user)
- Conda environment with lerobot installed
- V2Ray proxy (if HuggingFace access needed)
- Robot hardware connected and powered (confirm with user)

### Step 1: Initialize Session

Create tmux session with large terminal:

```bash
# On jump server
tmux kill-session -t lerobot_eval 2>/dev/null
tmux new-session -d -s lerobot_eval -x 240 -y 60
```

### Step 2: Start Robot Host (Window 0)

```bash
# In tmux window 0
tmux send-keys -t lerobot_eval:0 "sshpass -p 'TARGET_PASSWORD' ssh -t -o StrictHostKeyChecking=no -X root@TARGET_IP \"source /root/miniconda3/bin/activate && cd /root/workspace/lerobot_ros2 && bash cmd.sh\"" Enter

# Wait for prompt, then press ENTER to continue
sleep 5
tmux send-keys -t lerobot_eval:0 "Enter"

# Verify robot is running (should see: WARNING:root:No command available)
```

### Step 3: Start Evaluation Script (Window 1)

```bash
# Create window 1
tmux new-window -t lerobot_eval -n evaluate

# Clear old dataset cache (if exists)
tmux send-keys -t lerobot_eval:1 "rm -rf /home/nice/.cache/huggingface/lerobot/ly/eval_dataset" Enter

# Start evaluation
tmux send-keys -t lerobot_eval:1 "source /home/nice/miniconda3/bin/activate lerobot && export ALL_PROXY=socks5://127.0.0.1:10808 && export DISPLAY=:0 && cd /home/nice/ly/lerobot_ros2 && python examples/lekiwi/evaluate.py --id=lekiwi --remote_ip=TARGET_IP --hf_model_id=MODEL_PATH --hf_dataset_id=DATASET_ID --is_headless_flag=False" Enter
```

### Step 4: Monitor Progress

```bash
# Check evaluation window
tmux capture-pane -t lerobot_eval:1 -p | tail -30

# Check robot window
tmux capture-pane -t lerobot_eval:0 -p | tail -20

# Monitor process
ps aux | grep "evaluate.py" | grep -v grep
```

---

### Mode B: Local Dataset Evaluation Quick Start

**Prerequisites**:
- Jump server IP, username, password (ask user)
- Model path (policy_path)
- Dataset ID (repo_id)
- Conda environment with lerobot installed
- V2Ray proxy (if HuggingFace access needed)
- **No hardware connection required**

### Step 1: SSH to Jump Server

```bash
# From your local machine
sshpass -p 'JUMP_PASS' ssh JUMP_USER@JUMP_SERVER_IP
```

### Step 2: Navigate to lerobot_ros2 and Activate Environment

```bash
# Navigate to repository
cd /home/JUMP_USER/ly/lerobot_ros2

# Activate conda environment
source /home/JUMP_USER/miniconda3/bin/activate lerobot

# Set proxy
export ALL_PROXY=socks5://127.0.0.1:10808
```

### Step 3: Run Dataset Evaluation

```bash
# Execute evaluation script
python examples/lekiwi/evaluate_dataset.py \
  --policy_path=/home/JUMP_USER/ly/lerobot_ros2/outputs/mylerobot_train/0106_smolvla_000/checkpoints/020000/pretrained_model \
  --repo_id=ly/pre_training_data
```

**Replace placeholders with actual values**:
- `JUMP_USER`: Jump server username (e.g., nice)
- `policy_path`: Path to pretrained model
- `repo_id`: HuggingFace dataset ID (e.g., ly/pre_training_data)

### Step 4: Monitor Progress

Evaluation will output progress directly to terminal. Wait for completion message with final metrics.

---

## Configuration

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `JUMP_SERVER_IP` | Jump server address | `192.168.136.128` |
| `JUMP_USER` | Jump server username | `nice` |
| `JUMP_PASS` | Jump server password | `NICE` |
| `TARGET_IP` | Target robot IP | `10.10.10.54` |
| `TARGET_USER` | Target robot username | `root` |
| `TARGET_PASS` | Target robot password | `Nice@123` |
| `MODEL_PATH` | Pretrained model path | `/home/nice/ly/lerobot_ros2/outputs/mylerobot_train/0106_smolvla_000/checkpoints/020000/pretrained_model` |
| `DATASET_ID` | HuggingFace dataset ID | `ly/eval_dataset` |

### Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `PROXY_PORT` | V2Ray SOCKS5 proxy port | `10808` |
| `TMUX_SESSION` | tmux session name | `lerobot_eval` |
| `DISPLAY` | X11 display | `:0` |

## Viewing Terminal Windows

### Method 1: Attach to tmux (Recommended)

```bash
# On jump server, open terminal and run:
tmux attach-session -t lerobot_eval

# Keyboard shortcuts:
# Ctrl+B, 0  → Switch to window 0 (robot host)
# Ctrl+B, 1  → Switch to window 1 (evaluation script)
# Ctrl+B, D  → Detach (processes continue running)
# Ctrl+B, [  → Scroll mode (view history)
```

### Method 2: Capture Without Attaching

```bash
# View robot host window
tmux capture-pane -t lerobot_eval:0 -p

# View evaluation window
tmux capture-pane -t lerobot_eval:1 -p

# Real-time monitoring (update every 2s)
watch -n 2 'tmux capture-pane -t lerobot_eval:1 -p | tail -30'
```

### Method 3: Remote Monitoring via SSH

```bash
# From your local machine
sshpass -p 'JUMP_PASS' ssh -o StrictHostKeyChecking=no JUMP_USER@JUMP_SERVER_IP 'tmux capture-pane -t lerobot_eval:1 -p | tail -30'
```

## Viewing Visualization UI

### Option A: Physical Access

- Directly view monitor on jump server

### Option B: VNC Remote Desktop

```bash
# Install VNC server on jump server
sudo apt-get install tigervnc-standalone-server
vncserver :1 -geometry 1920x1080

# Connect from VNC client:
# Address: JUMP_SERVER_IP:5901
```

### Option C: Rerun Viewer (Remote)

```bash
# On any machine with rerun installed
pip install rerun-sdk
rerun --connect rerun+http://JUMP_SERVER_IP:9876/proxy
```

## Troubleshooting

### Problem: Dataset Directory Exists Error

**Symptom:**
```
FileExistsError: [Errno 17] File exists: '/home/nice/.cache/huggingface/lerobot/ly/eval_dataset'
```

**Solution:**
```bash
# Clean dataset cache
tmux send-keys -t lerobot_eval:1 "rm -rf /home/nice/.cache/huggingface/lerobot/ly/eval_dataset" Enter
```

### Problem: Motor Connection Failed

**Symptom:**
```
RuntimeError: FeetechMotorsBus motor check failed
Missing motor IDs: 1-9
```

**Solution:**
1. Check robot hardware connected to `/dev/ttyACM0`
2. Ensure robot is powered on
3. Verify motor IDs match configuration
4. Restart cmd.sh in window 0

### Problem: HuggingFace Network Unreachable

**Symptom:**
```
OSError: Can't load processor for 'HuggingFaceTB/SmolVLM2-500M-Video-Instruct'
[Errno 101] Network is unreachable
```

**Solution:**
```bash
# Ensure proxy is set
export ALL_PROXY=socks5://127.0.0.1:10808

# Install SOCKS support
pip install "httpx[socks]"

# Verify proxy
curl -I --socks5 127.0.0.1:10808 https://huggingface.co
```

### Problem: No X11 Display

**Symptom:**
```
ImportError: this platform is not supported: ('failed to acquire X connection')
```

**Solution:**
```bash
# Set DISPLAY environment
export DISPLAY=:0

# Or run in headless mode
--is_headless_flag=True
```

## Monitoring Commands

### Check Process Status

```bash
# On jump server
ps aux | grep "evaluate.py" | grep -v grep
```

### Monitor GPU Usage

```bash
# Watch GPU every 1 second
watch -n 1 nvidia-smi
```

### Real-time Log Monitoring

```bash
# Monitor evaluation window
watch -n 2 'tmux capture-pane -t lerobot_eval:1 -p | tail -30'

# Monitor robot window
watch -n 2 'tmux capture-pane -t lerobot_eval:0 -p | tail -10'
```

## Complete Example

**IMPORTANT: Replace all placeholders with actual values provided by the user.**

```bash
# One-time setup on jump server
# 1. Ensure tmux installed
sudo apt-get install -y tmux

# 2. Ensure V2Ray running
ps aux | grep v2ray

# 3. Test robot connectivity (replace with actual values from user)
sshpass -p 'TARGET_PASS' ssh TARGET_USER@TARGET_IP 'hostname'

# Execute evaluation
# Step 1: Create session
tmux kill-session -t lerobot_eval 2>/dev/null
tmux new-session -d -s lerobot_eval -x 240 -y 60

# Step 2: Start robot host (replace TARGET_PASS, TARGET_USER, TARGET_IP)
tmux send-keys -t lerobot_eval:0 "sshpass -p 'TARGET_PASS' ssh -t -o StrictHostKeyChecking=no -X TARGET_USER@TARGET_IP \"source /root/miniconda3/bin/activate && cd /root/workspace/lerobot_ros2 && bash cmd.sh\"" Enter
sleep 5
tmux send-keys -t lerobot_eval:0 "Enter"

# Step 3: Start evaluation (replace TARGET_IP, JUMP_USER paths)
tmux new-window -t lerobot_eval -n evaluate
tmux send-keys -t lerobot_eval:1 "rm -rf /home/JUMP_USER/.cache/huggingface/lerobot/ly/eval_dataset" Enter
sleep 2
tmux send-keys -t lerobot_eval:1 "source /home/JUMP_USER/miniconda3/bin/activate lerobot && export ALL_PROXY=socks5://127.0.0.1:10808 && export DISPLAY=:0 && cd /home/JUMP_USER/ly/lerobot_ros2 && python examples/lekiwi/evaluate.py --id=lekiwi --remote_ip=TARGET_IP --hf_model_id=/home/JUMP_USER/ly/lerobot_ros2/outputs/mylerobot_train/0106_smolvla_000/checkpoints/020000/pretrained_model --hf_dataset_id=ly/eval_dataset --is_headless_flag=False" Enter

# Step 4: Monitor
sleep 20
tmux capture-pane -t lerobot_eval:1 -p | tail -30
```

## Advanced: Automation Script

See `scripts/run_remote_eval.sh` for automated execution.

## Session Management

### Stop All Processes

```bash
# Kill evaluation script
pkill -f "evaluate.py"

# Stop tmux session
tmux kill-session -t lerobot_eval

# Or send Ctrl+C to windows
tmux send-keys -t lerobot_eval:0 "C-c"
tmux send-keys -t lerobot_eval:1 "C-c"
```

### Restart Evaluation

```bash
# Kill old process
pkill -f "evaluate.py"

# Clean cache
rm -rf /home/nice/.cache/huggingface/lerobot/ly/eval_dataset

# Restart in window 1
tmux send-keys -t lerobot_eval:1 "python examples/lekiwi/evaluate.py --id=lekiwi --remote_ip=10.10.10.54 --hf_model_id=/home/nice/ly/lerobot_ros2/outputs/mylerobot_train/0106_smolvla_000/checkpoints/020000/pretrained_model --hf_dataset_id=ly/eval_dataset --is_headless_flag=False" Enter
```

## Expected Behavior

### Normal Execution Flow

1. **Robot Host (Window 0):**
   - Starts cmd.sh
   - Prompts for ENTER to use calibration
   - Shows continuous: `WARNING:root:No command available`

2. **Evaluation Script (Window 1):**
   - Loads SmolVLM2-500M-Video-Instruct weights
   - Reduces VLM layers to 16
   - Loads local model
   - Starts gRPC server on 0.0.0.0:9876
   - Detects GPU adapters
   - Starts evaluate loop
   - Shows visualization UI (if headless_flag=False)

### Performance Indicators

- **CPU**: 200-500% (multi-core usage)
- **Memory**: 2-4 GB
- **GPU**: Active inference on RTX 4080
- **Duration**: Hours (depends on evaluation episodes)

## Notes

- Ensure robot hardware is connected BEFORE starting cmd.sh
- Dataset cache must be cleaned between runs
- tmux session persists even if SSH disconnects
- Use `tmux attach` to reconnect to sessions
- Proxy required for HuggingFace model download
- DISPLAY=:0 for local X11, remove for headless
