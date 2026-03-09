#!/bin/bash
# LeRobot installation script for Ubuntu/Debian/macOS

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# Default installation path
INSTALL_PATH="${INSTALL_PATH:-$HOME/opt/lerobot}"

# Install system dependencies
install_system_dependencies() {
    log INFO "Installing system dependencies..."
    
    local deps=("python3" "python3-pip" "python3-venv" "git")
    
    for dep in "${deps[@]}"; do
        if ! command_exists "$dep"; then
            log INFO "Installing $dep..."
            install_package "$dep" || {
                log ERROR "Failed to install $dep"
                return 1
            }
        else
            log INFO "$dep is already installed"
        fi
    done
    
    # Install additional dependencies for lerobot
    if [ "$(uname)" != "Darwin" ]; then
        log INFO "Installing additional system libraries..."
        sudo apt-get install -y \
            python3-dev \
            libopenblas-dev \
            liblapack-dev \
            gfortran \
            libhdf5-dev \
            >/dev/null 2>&1 || {
            log WARNING "Some optional dependencies failed to install"
        }
    fi
    
    log SUCCESS "System dependencies installed"
    return 0
}

# Check CUDA availability
check_cuda() {
    log INFO "Checking CUDA availability..."
    
    if command -v nvidia-smi >/dev/null 2>&1; then
        local gpu_info=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
        log SUCCESS "NVIDIA GPU detected: $gpu_info"
        
        # Check CUDA version
        if command -v nvcc >/dev/null 2>&1; then
            local cuda_version=$(nvcc --version | grep "release" | awk '{print $5}' | cut -d',' -f1)
            log SUCCESS "CUDA version: $cuda_version"
            return 0
        else
            log WARNING "CUDA toolkit not found. GPU acceleration may not be available"
            return 1
        fi
    else
        log WARNING "No NVIDIA GPU detected. Installation will proceed with CPU-only mode"
        return 1
    fi
}

# Create virtual environment
create_venv() {
    log INFO "Creating Python virtual environment..."
    
    check_directory "$INSTALL_PATH" || return 1
    
    local venv_path="$INSTALL_PATH/venv"
    
    if [ -d "$venv_path" ]; then
        log WARNING "Virtual environment already exists at $venv_path"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$venv_path"
        else
            log INFO "Using existing virtual environment"
            return 0
        fi
    fi
    
    python3 -m venv "$venv_path" || {
        log ERROR "Failed to create virtual environment"
        return 1
    }
    
    log SUCCESS "Virtual environment created at $venv_path"
    return 0
}

# Install LeRobot
install_lerobot() {
    log INFO "Installing LeRobot and PyTorch..."
    
    local venv_path="$INSTALL_PATH/venv"
    
    # Activate virtual environment
    source "$venv_path/bin/activate"
    
    # Upgrade pip
    log STEP "Upgrading pip and build tools..."
    if pip install --upgrade pip setuptools wheel 2>&1 | while read line; do
        if echo "$line" | grep -qE "(Successfully|Requirement already)"; then
            log SUCCESS "$(echo "$line" | cut -c1-80)"
        fi
    done; then
        log SUCCESS "Build tools upgraded"
    else
        log WARNING "Some packages may not have upgraded"
    fi
    
    # Install PyTorch (CPU or GPU version based on CUDA availability)
    echo ""
    log STEP "Installing PyTorch (this may take a few minutes)..."
    
    if check_cuda; then
        log INFO "CUDA detected! Installing PyTorch with GPU support..."
        log STEP "Downloading from: https://download.pytorch.org/whl/cu118"
        echo ""
        
        if pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 2>&1 | while read line; do
            if echo "$line" | grep -qE "(Collecting|Downloading|Installing)"; then
                log PROGRESS "$(echo "$line" | cut -c1-80)"
            elif echo "$line" | grep -q "Successfully installed"; then
                log SUCCESS "$line"
            fi
        done; then
            log SUCCESS "PyTorch (CUDA) installed"
        else
            log WARNING "GPU PyTorch installation failed, falling back to CPU version"
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
        fi
    else
        log INFO "Installing PyTorch (CPU version)..."
        log STEP "Downloading from: https://download.pytorch.org/whl/cpu"
        echo ""
        
        if pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu 2>&1 | while read line; do
            if echo "$line" | grep -qE "(Collecting|Downloading|Installing)"; then
                log PROGRESS "$(echo "$line" | cut -c1-80)"
            elif echo "$line" | grep -q "Successfully installed"; then
                log SUCCESS "$line"
            fi
        done; then
            log SUCCESS "PyTorch (CPU) installed"
        else
            log ERROR "PyTorch installation failed"
            return 1
        fi
    fi
    
    # Install lerobot
    echo ""
    log STEP "Installing LeRobot and dependencies..."
    log INFO "This includes: datasets, diffusers, huggingface-hub, accelerate, etc."
    echo ""
    
    if retry_command 3 10 "pip install lerobot" 2>&1 | while read line; do
        if echo "$line" | grep -qE "(Collecting|Downloading|Installing|Successfully)"; then
            log PROGRESS "$(echo "$line" | cut -c1-80)"
        fi
    done; then
        log SUCCESS "LeRobot and all dependencies installed"
    else
        log ERROR "Failed to install lerobot"
        return 1
    fi
    
    return 0
}

# Create activation script
create_activation_script() {
    log INFO "Creating activation script..."
    
    local activate_script="$INSTALL_PATH/activate.sh"
    
    cat > "$activate_script" << 'EOF'
#!/bin/bash
# LeRobot activation script

VENV_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/venv"

if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

source "$VENV_PATH/bin/activate"
echo "LeRobot environment activated!"
echo "Python: $(which python3)"
echo "LeRobot: $(python3 -c 'import lerobot; print(lerobot.__version__)')"
EOF
    
    chmod +x "$activate_script"
    
    log SUCCESS "Activation script created at $activate_script"
    log INFO "To activate the environment, run: source $activate_script"
    
    return 0
}

# Verify installation
verify_installation() {
    log INFO "Verifying installation..."
    
    local venv_path="$INSTALL_PATH/venv"
    source "$venv_path/bin/activate"
    
    # Check Python version
    local python_version=$(python3 --version)
    log SUCCESS "Python: $python_version"
    
    # Check PyTorch
    if python3 -c "import torch; print(f'PyTorch: {torch.__version__}')" 2>/dev/null; then
        log SUCCESS "PyTorch is installed"
        
        # Check if CUDA is available
        if python3 -c "import torch; assert torch.cuda.is_available()" 2>/dev/null; then
            log SUCCESS "CUDA is available in PyTorch"
        else
            log INFO "PyTorch is running in CPU mode"
        fi
    else
        log ERROR "PyTorch installation verification failed"
        return 1
    fi
    
    # Check lerobot
    if python3 -c "import lerobot" 2>/dev/null; then
        local lerobot_version=$(python3 -c "import lerobot; print(lerobot.__version__)" 2>/dev/null || echo "unknown")
        log SUCCESS "LeRobot version: $lerobot_version"
    else
        log ERROR "LeRobot installation verification failed"
        return 1
    fi
    
    return 0
}

# Main installation function
main() {
    local log_file=$(init_log "lerobot")
    
    # Show installation header
    show_header "LeRobot" "0.4.4"
    
    log INFO "Starting LeRobot installation..."
    log STEP "Installation log: $log_file"
    echo ""
    
    # Initialize progress (6 steps)
    init_progress 6
    
    # Redirect all output to log file
    exec > >(tee -a "$log_file") 2>&1
    
    # Step 1: Check environment
    update_progress "Environment Check" "running"
    if "$SCRIPT_DIR/check_environment.sh" lerobot; then
        update_progress "Environment Check" "success"
    else
        update_progress "Environment Check" "error"
        exit 1
    fi
    
    # Step 2: Install system dependencies
    update_progress "Installing System Dependencies" "running"
    log INFO "Installing Python, pip, git and build tools..."
    if install_system_dependencies; then
        update_progress "Installing System Dependencies" "success"
    else
        update_progress "Installing System Dependencies" "error"
        exit 1
    fi
    
    # Step 3: Create virtual environment
    update_progress "Creating Virtual Environment" "running"
    log INFO "Setting up Python virtual environment at $INSTALL_PATH/venv"
    if create_venv; then
        update_progress "Creating Virtual Environment" "success"
    else
        update_progress "Creating Virtual Environment" "error"
        exit 1
    fi
    
    # Step 4: Install LeRobot and dependencies
    update_progress "Installing LeRobot & PyTorch" "running"
    log INFO "This may take several minutes depending on your network speed..."
    if install_lerobot; then
        update_progress "Installing LeRobot & PyTorch" "success"
    else
        update_progress "Installing LeRobot & PyTorch" "error"
        exit 1
    fi
    
    # Step 5: Create activation script
    update_progress "Creating Activation Script" "running"
    if create_activation_script; then
        update_progress "Creating Activation Script" "success"
    else
        update_progress "Creating Activation Script" "error"
        exit 1
    fi
    
    # Step 6: Verify installation
    update_progress "Verifying Installation" "running"
    log INFO "Testing imports and checking CUDA availability..."
    if verify_installation; then
        update_progress "Verifying Installation" "success"
    else
        update_progress "Verifying Installation" "error"
        exit 1
    fi
    
    # Generate report
    source "$INSTALL_PATH/venv/bin/activate"
    local lerobot_version=$(python3 -c "import lerobot; print(lerobot.__version__)" 2>/dev/null || echo "unknown")
    generate_report "lerobot" "$INSTALL_PATH" "$lerobot_version" "$log_file"
    
    log SUCCESS "LeRobot installation completed successfully!"
    log STEP "To activate the environment: source $INSTALL_PATH/activate.sh"
    
    return 0
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
