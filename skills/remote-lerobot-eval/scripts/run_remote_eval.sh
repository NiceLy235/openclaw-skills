#!/bin/bash
# Automated Remote Lerobot Evaluation Script
# Usage: ./run_remote_eval.sh [--interactive]

set -e

# Default configuration (will be overridden by user input or config file)
JUMP_SERVER_IP="${JUMP_SERVER_IP:-}"
JUMP_USER="${JUMP_USER:-}"
JUMP_PASS="${JUMP_PASS:-}"

TARGET_IP="${TARGET_IP:-}"
TARGET_USER="${TARGET_USER:-}"
TARGET_PASS="${TARGET_PASS:-}"

MODEL_PATH="${MODEL_PATH:-/home/nice/ly/lerobot_ros2/outputs/mylerobot_train/0106_smolvla_000/checkpoints/020000/pretrained_model}"
DATASET_ID="${DATASET_ID:-ly/eval_dataset}"

PROXY_PORT="${PROXY_PORT:-10808}"
TMUX_SESSION="${TMUX_SESSION:-lerobot_eval}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_prompt() {
    echo -e "${BLUE}[?]${NC} $1"
}

# Function to get user input
get_input() {
    local prompt="$1"
    local var_name="$2"
    local default="$3"
    local is_password="$4"
    
    if [ -n "${!var_name}" ]; then
        log_info "$var_name already set: ${!var_name}"
        return
    fi
    
    if [ -n "$default" ]; then
        prompt="$prompt (default: $default)"
    fi
    
    log_prompt "$prompt"
    read -r value
    
    if [ -z "$value" ] && [ -n "$default" ]; then
        value="$default"
    fi
    
    if [ -z "$value" ]; then
        log_error "Value is required for $var_name"
        exit 1
    fi
    
    eval "$var_name='$value'"
}

# Function to execute command on jump server
jump_exec() {
    sshpass -p "$JUMP_PASS" ssh -o StrictHostKeyChecking=no "$JUMP_USER@$JUMP_SERVER_IP" "$1"
}

# Function to execute command on target machine
target_exec() {
    jump_exec "sshpass -p '$TARGET_PASS' ssh -o StrictHostKeyChecking=no '$TARGET_USER@$TARGET_IP' \"$1\""
}

# Step 0: Collect configuration
collect_config() {
    log_info "=========================================="
    log_info "Remote Lerobot Evaluation Configuration"
    log_info "=========================================="
    echo ""
    
    get_input "Jump server IP address" JUMP_SERVER_IP
    get_input "Jump server username" JUMP_USER
    get_input "Jump server password" JUMP_PASS "" "password"
    
    echo ""
    get_input "Target robot IP address" TARGET_IP
    get_input "Target robot username" TARGET_USER
    get_input "Target robot password" TARGET_PASS "" "password"
    
    echo ""
    get_input "Pretrained model path" MODEL_PATH "$MODEL_PATH"
    get_input "Dataset ID" DATASET_ID "$DATASET_ID"
    
    echo ""
    log_prompt "Is robot hardware connected and powered? (yes/no)"
    read -r hardware_ready
    
    if [[ ! "$hardware_ready" =~ ^[Yy][Ee][Ss]$ ]]; then
        log_error "Please connect and power on robot hardware before continuing."
        log_info "Run this script again after hardware is ready."
        exit 1
    fi
    
    log_info "Configuration collected ✓"
    echo ""
    log_info "Summary:"
    echo "  Jump Server: $JUMP_USER@$JUMP_SERVER_IP"
    echo "  Target Robot: $TARGET_USER@$TARGET_IP"
    echo "  Model: $MODEL_PATH"
    echo "  Dataset: $DATASET_ID"
    echo ""
    
    log_prompt "Continue with execution? (yes/no)"
    read -r confirm
    
    if [[ ! "$confirm" =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Execution cancelled."
        exit 0
    fi
}

# Step 1: Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if sshpass is installed
    if ! command -v sshpass &> /dev/null; then
        log_error "sshpass not found. Please install: apt-get install sshpass"
        exit 1
    fi
    
    # Check jump server connectivity
    log_info "Testing jump server connectivity..."
    if ! jump_exec "echo 'Jump server OK'" &> /dev/null; then
        log_error "Cannot connect to jump server $JUMP_SERVER_IP"
        exit 1
    fi
    
    # Check target machine connectivity
    log_info "Testing target machine connectivity..."
    if ! target_exec "echo 'Target machine OK'" &> /dev/null; then
        log_error "Cannot connect to target machine $TARGET_IP"
        exit 1
    fi
    
    log_info "Prerequisites check passed ✓"
}

# Step 2: Initialize tmux session
init_tmux() {
    log_info "Initializing tmux session..."
    
    jump_exec "tmux kill-session -t $TMUX_SESSION 2>/dev/null || true"
    jump_exec "tmux new-session -d -s $TMUX_SESSION -x 240 -y 60"
    
    log_info "tmux session '$TMUX_SESSION' created ✓"
}

# Step 3: Start robot host
start_robot_host() {
    log_info "Starting robot host on target machine..."
    
    # Start cmd.sh in window 0
    jump_exec "tmux send-keys -t $TMUX_SESSION:0 \"sshpass -p '$TARGET_PASS' ssh -t -o StrictHostKeyChecking=no -X $TARGET_USER@$TARGET_IP \\\"source /root/miniconda3/bin/activate && cd /root/workspace/lerobot_ros2 && bash cmd.sh\\\"\" Enter"
    
    # Wait for prompt
    log_info "Waiting for robot initialization..."
    sleep 5
    
    # Send ENTER to continue calibration
    jump_exec "tmux send-keys -t $TMUX_SESSION:0 'Enter'"
    
    # Verify robot is running
    sleep 3
    local status=$(jump_exec "tmux capture-pane -t $TMUX_SESSION:0 -p | grep 'No command available' | wc -l")
    
    if [ "$status" -gt 0 ]; then
        log_info "Robot host started successfully ✓"
    else
        log_warn "Robot host may not be running properly. Check window 0."
    fi
}

# Step 4: Start evaluation script
start_evaluation() {
    log_info "Starting evaluation script..."
    
    # Create window 1
    jump_exec "tmux new-window -t $TMUX_SESSION -n evaluate"
    
    # Clean old dataset cache
    jump_exec "tmux send-keys -t $TMUX_SESSION:1 'rm -rf /home/nice/.cache/huggingface/lerobot/ly/eval_dataset' Enter"
    sleep 2
    
    # Start evaluation
    local eval_cmd="source /home/nice/miniconda3/bin/activate lerobot && export ALL_PROXY=socks5://127.0.0.1:$PROXY_PORT && export DISPLAY=:0 && cd /home/nice/ly/lerobot_ros2 && python examples/lekiwi/evaluate.py --id=lekiwi --remote_ip=$TARGET_IP --hf_model_id=$MODEL_PATH --hf_dataset_id=$DATASET_ID --is_headless_flag=False"
    
    jump_exec "tmux send-keys -t $TMUX_SESSION:1 \"$eval_cmd\" Enter"
    
    log_info "Evaluation script started ✓"
}

# Step 5: Monitor progress
monitor_progress() {
    log_info "Monitoring evaluation progress..."
    log_info "Press Ctrl+C to stop monitoring (evaluation will continue)"
    
    while true; do
        echo "========================================"
        echo "Evaluation Window (last 20 lines):"
        echo "========================================"
        jump_exec "tmux capture-pane -t $TMUX_SESSION:1 -p | tail -20"
        echo ""
        echo "========================================"
        echo "Robot Host Window (last 5 lines):"
        echo "========================================"
        jump_exec "tmux capture-pane -t $TMUX_SESSION:0 -p | tail -5"
        echo ""
        
        # Check if evaluation is still running
        local pid=$(jump_exec "ps aux | grep 'evaluate.py' | grep -v grep | awk '{print \$2}'")
        if [ -z "$pid" ]; then
            log_warn "Evaluation process not found. It may have finished or crashed."
            break
        fi
        
        sleep 10
    done
}

# Display usage instructions
show_usage() {
    echo ""
    echo "========================================"
    echo "How to Access Terminal Windows"
    echo "========================================"
    echo ""
    echo "1. Attach to tmux session:"
    echo "   ssh $JUMP_USER@$JUMP_SERVER_IP"
    echo "   tmux attach-session -t $TMUX_SESSION"
    echo ""
    echo "2. Switch windows:"
    echo "   Ctrl+B, 0  → Robot host"
    echo "   Ctrl+B, 1  → Evaluation script"
    echo ""
    echo "3. Detach (keep running):"
    echo "   Ctrl+B, D"
    echo ""
    echo "4. View without attaching:"
    echo "   tmux capture-pane -t $TMUX_SESSION:1 -p | tail -30"
    echo ""
    echo "========================================"
    echo "Visualization UI Access"
    echo "========================================"
    echo ""
    echo "1. Physical access: View monitor on jump server"
    echo "2. VNC: Connect to $JUMP_SERVER_IP:5901"
    echo "3. Rerun: rerun --connect rerun+http://$JUMP_SERVER_IP:9876/proxy"
    echo ""
}

# Main execution
main() {
    if [ -f "$1" ]; then
        log_info "Loading configuration from $1"
        source "$1"
    fi
    
    log_info "Starting Remote Lerobot Evaluation..."
    log_info "Jump Server: $JUMP_SERVER_IP"
    log_info "Target Machine: $TARGET_IP"
    log_info "Model: $MODEL_PATH"
    log_info "Dataset: $DATASET_ID"
    echo ""
    
    check_prerequisites
    init_tmux
    start_robot_host
    start_evaluation
    
    log_info "Evaluation started successfully!"
    show_usage
    
    read -p "Monitor progress in real-time? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        monitor_progress
    else
        log_info "Evaluation is running in background."
        log_info "Use 'tmux attach-session -t $TMUX_SESSION' to view."
    fi
}

# Run main function
main "$@"
