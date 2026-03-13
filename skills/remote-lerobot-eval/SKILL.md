---
name: remote-lerobot-eval
description: >
  Remote execution and monitoring of lerobot evaluation tasks via jump server with tmux session management.
  Use when: (1) Running lerobot evaluation on remote machines behind jump server, (2) Need to visualize
  robot evaluation UI and terminal windows, (3) Managing multi-machine workflows with SSH tunneling,
  (4) Setting up persistent terminal sessions for long-running evaluation tasks, (5) User mentions
  "remote evaluation", "jump server", "tmux", "lerobot evaluate", "robot testing".
  Trigger phrases: "remote evaluation", "通过跳板机评估", "远程机器人测试", "tmux session".
---

# Remote Lerobot Evaluation

Execute and monitor lerobot evaluation tasks on remote machines via jump server with persistent terminal sessions.

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

**DO NOT assume any values.** Always ask the user for these required parameters before executing any commands:

**Required questions to ask:**
1. What is the jump server IP address? (e.g., 192.168.136.128)
2. What is the jump server username? (e.g., nice)
3. What is the jump server password? (e.g., NICE)
4. What is the target robot IP address? (e.g., 10.10.10.54)
5. What is the target robot username? (e.g., root)
6. What is the target robot password? (e.g., Nice@123)
7. Is the robot hardware connected and powered? (yes/no)

**Wait for user to confirm hardware is ready before proceeding to Step 2.**

**Only proceed after receiving ALL answers.**

### Prerequisites

Before starting, ensure you have:
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
