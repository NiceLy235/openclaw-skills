#!/bin/bash
# LeRobot installation script - Enhanced version with dependency conflict resolution
#
# Improvements:
# - Auto-detect CUDA version and install matching PyTorch
# - Resolve dependency version conflicts
# - Configure proxy for HuggingFace access
# - Install all required dependencies including num2words
# - Verify and fix version mismatches

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# Default installation path
INSTALL_PATH="${INSTALL_PATH:-$HOME/opt/lerobot}"

# ============================================================
# Cuda Version Detection
# ============================================================

detect_cuda_version() {
    log INFO "Detecting CUDA version..."
    
    if ! command -v nvidia-smi >/dev/null 2>&1; then
        log WARNING "No NVIDIA GPU detected"
        echo "cpu"
        return 0
    fi
    
    local gpu_info=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    log SUCCESS "GPU detected: $gpu_info"
    
    # Get CUDA version from driver
    local cuda_version=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')
    
    if [ -z "$cuda_version" ]; then
        # Try nvcc
        if command -v nvcc >/dev/null 2>&1; then
            cuda_version=$(nvcc --version | grep "release" | awk '{print $5}' | cut -d',' -f1)
        fi
    fi
    
    if [ -z "$cuda_version" ]; then
        log WARNING "Could not detect CUDA version, defaulting to 12.1"
        cuda_version="12.1"
    fi
    
    log SUCCESS "CUDA version: $cuda_version"
    echo "$cuda_version"
    return 0
}

get_pytorch_cuda_version() {
    local cuda_version="$1"
    
    # Map CUDA version to PyTorch index
    case "$cuda_version" in
        12.8|12.7|12.6)
            echo "cu128"
            ;;
        12.5|12.4|12.3|12.2|12.1)
            echo "cu121"
            ;;
        12.0|11.8)
            echo "cu118"
            ;;
        11.7)
            echo "cu117"
            ;;
        *)
            log WARNING "Unknown CUDA version $cuda_version, using cu121"
            echo "cu121"
            ;;
    esac
}

# ============================================================
# Proxy Configuration
# ============================================================

check_v2ray_proxy() {
    log INFO "Checking for V2Ray proxy..."
    
    # Check if V2Ray is running
    if ss -tlnp 2>/dev/null | grep -q ":10809"; then
        log SUCCESS "V2Ray HTTP proxy detected on port 10809"
        export HTTP_PROXY="http://127.0.0.1:10809"
        export HTTPS_PROXY="http://127.0.0.1:10809"
        export ALL_PROXY="http://127.0.0.1:10809"
        return 0
    elif ss -tlnp 2>/dev/null | grep -q ":10808"; then
        log SUCCESS "V2Ray SOCKS5 proxy detected on port 10808"
        export HTTP_PROXY="socks5://127.0.0.1:10808"
        export HTTPS_PROXY="socks5://127.0.0.1:10808"
        export ALL_PROXY="socks5://127.0.0.1:10808"
        return 0
    fi
    
    log INFO "No V2Ray proxy detected. Will proceed without proxy."
    log INFO "If you have V2Ray, please start it first: systemctl start v2ray"
    return 1
}

test_huggingface_access() {
    log INFO "Testing HuggingFace access..."
    
    if curl -s --connect-timeout 5 -I https://huggingface.co 2>&1 | grep -q "HTTP"; then
        log SUCCESS "HuggingFace is accessible"
        return 0
    else
        log WARNING "Cannot access HuggingFace directly"
        
        if [ -n "$HTTP_PROXY" ]; then
            log INFO "Testing with proxy..."
            if curl -x "$HTTP_PROXY" -s --connect-timeout 5 -I https://huggingface.co 2>&1 | grep -q "HTTP"; then
                log SUCCESS "HuggingFace accessible via proxy"
                return 0
            fi
        fi
        
        log ERROR "Cannot access HuggingFace. Please check your network or proxy configuration."
        log INFO "If you have V2Ray, start it with: systemctl start v2ray"
        return 1
    fi
}

# ============================================================
# Dependency Installation
# ============================================================

install_system_dependencies() {
    log INFO "Installing system dependencies..."
    
    local deps=("python3" "python3-pip" "python3-venv" "git" "curl")
    
    for dep in "${deps[@]}"; do
        if ! command_exists "$dep"; then
            log STEP "Installing $dep..."
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
        sudo apt-get update -qq
        sudo apt-get install -y -qq \
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

create_venv() {
    log INFO "Creating Python virtual environment..."
    
    check_directory "$INSTALL_PATH" || return 1
    
    local venv_path="$INSTALL_PATH/venv"
    
    if [ -d "$venv_path" ]; then
        log WARNING "Virtual environment already exists at $venv_path"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log INFO "Removing existing virtual environment..."
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

install_pytorch() {
    log INFO "Installing PyTorch with correct CUDA version..."
    
    local venv_path="$INSTALL_PATH/venv"
    source "$venv_path/bin/activate"
    
    # Detect CUDA version
    local cuda_version=$(detect_cuda_version)
    local pytorch_cuda=$(get_pytorch_cuda_version "$cuda_version")
    
    if [ "$cuda_version" == "cpu" ]; then
        log INFO "Installing PyTorch (CPU version)..."
        local pytorch_url="https://download.pytorch.org/whl/cpu"
    else
        log INFO "Installing PyTorch with CUDA $cuda_version support..."
        log INFO "Using PyTorch index: $pytorch_cuda"
        local pytorch_url="https://download.pytorch.org/whl/$pytorch_cuda"
    fi
    
    log STEP "Downloading from: $pytorch_url"
    echo ""
    
    # Install PyTorch with specific versions that work together
    pip install --upgrade pip setuptools wheel -q
    
    if pip install \
        torch==2.5.1 \
        torchvision==0.20.1 \
        torchaudio==2.5.1 \
        --index-url "$pytorch_url" 2>&1 | while read line; do
            if echo "$line" | grep -qE "(Collecting|Downloading|Installing)"; then
                log PROGRESS "$(echo "$line" | cut -c1-80)"
            elif echo "$line" | grep -q "Successfully installed"; then
                log SUCCESS "$line"
            fi
        done; then
        log SUCCESS "PyTorch installed successfully"
    else
        log ERROR "PyTorch installation failed"
        return 1
    fi
    
    # Verify PyTorch
    if python3 -c "import torch; import torchvision; print(f'PyTorch: {torch.__version__}, torchvision: {torchvision.__version__}')" 2>&1 | while read line; do
        log SUCCESS "$line"
    done; then
        :
    else
        log ERROR "PyTorch verification failed"
        return 1
    fi
    
    return 0
}

install_lerobot_with_deps() {
    log INFO "Installing LeRobot with all required dependencies..."
    
    local venv_path="$INSTALL_PATH/venv"
    source "$venv_path/bin/activate"
    
    # Install specific versions of conflicting packages first
    log STEP "Installing dependency packages with compatible versions..."
    
    # These versions are known to work with lerobot 0.4.4
    pip install -q \
        "huggingface-hub>=0.34.2,<0.36.0" \
        "packaging>=24.2,<26.0" \
        "protobuf>=3.19.0,<7" \
        || {
        log WARNING "Some version-constrained packages failed, will try default versions"
    }
    
    # Install LeRobot
    echo ""
    log STEP "Installing LeRobot..."
    
    if pip install lerobot==0.4.4 2>&1 | while read line; do
        if echo "$line" | grep -qE "(Collecting|Downloading|Installing|Successfully)"; then
            log PROGRESS "$(echo "$line" | cut -c1-80)"
        fi
    done; then
        log SUCCESS "LeRobot installed"
    else
        log ERROR "Failed to install lerobot"
        return 1
    fi
    
    # Install additional required packages
    echo ""
    log STEP "Installing additional dependencies..."
    
    pip install -q \
        transformers \
        accelerate \
        sentencepiece \
        num2words \
        datasets \
        wandb \
        tensorboard \
        || {
        log WARNING "Some additional dependencies failed to install"
    }
    
    log SUCCESS "All dependencies installed"
    return 0
}

# ============================================================
# Verification and Fix
# ============================================================

verify_pytorch_torchvision() {
    log INFO "Verifying PyTorch and torchvision compatibility..."
    
    python3 << 'PYEOF'
import sys
try:
    import torch
    import torchvision
    
    # Check versions
    torch_version = torch.__version__
    tv_version = torchvision.__version__
    
    print(f"✓ PyTorch version: {torch_version}")
    print(f"✓ torchvision version: {tv_version}")
    
    # Test basic functionality
    x = torch.randn(3, 3)
    y = torchvision.transforms.functional.to_pil_image(x.unsqueeze(0))
    
    print("✓ PyTorch and torchvision are compatible")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
PYEOF
    
    if [ $? -eq 0 ]; then
        log SUCCESS "PyTorch and torchvision verification passed"
        return 0
    else
        log ERROR "PyTorch and torchvision are incompatible"
        log INFO "This is likely a version mismatch"
        return 1
    fi
}

verify_all_imports() {
    log INFO "Verifying all required imports..."
    
    python3 << 'PYEOF'
import sys

modules = [
    ("torch", "PyTorch"),
    ("torchvision", "torchvision"),
    ("lerobot", "LeRobot"),
    ("transformers", "transformers"),
    ("accelerate", "accelerate"),
    ("num2words", "num2words"),
    ("sentencepiece", "sentencepiece"),
    ("huggingface_hub", "huggingface-hub"),
]

failed = []

for module, name in modules:
    try:
        __import__(module)
        print(f"✓ {name}")
    except ImportError as e:
        print(f"✗ {name}: {e}")
        failed.append(name)

if failed:
    print(f"\n✗ Failed to import: {', '.join(failed)}")
    sys.exit(1)
else:
    print("\n✓ All imports successful")
    sys.exit(0)
PYEOF
    
    if [ $? -eq 0 ]; then
        log SUCCESS "All imports verified"
        return 0
    else
        log ERROR "Some imports failed"
        return 1
    fi
}

verify_cuda() {
    log INFO "Verifying CUDA support..."
    
    python3 << 'PYEOF'
import torch

if torch.cuda.is_available():
    print(f"✓ CUDA is available")
    print(f"✓ CUDA version: {torch.version.cuda}")
    print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✓ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print("⚠ CUDA is not available (CPU mode)")
PYEOF
}

create_activation_script() {
    log INFO "Creating activation script..."
    
    local activate_script="$INSTALL_PATH/activate.sh"
    
    cat > "$activate_script" << 'EOF'
#!/bin/bash
# LeRobot activation script with proxy support

VENV_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/venv"

if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Configure proxy if V2Ray is running
if ss -tlnp 2>/dev/null | grep -q ":10809"; then
    export HTTP_PROXY="http://127.0.0.1:10809"
    export HTTPS_PROXY="http://127.0.0.1:10809"
    export ALL_PROXY="http://127.0.0.1:10809"
    echo "✓ V2Ray proxy configured"
fi

# Show environment info
echo "LeRobot environment activated!"
echo ""
python3 << 'PYINFO'
import torch
try:
    import lerobot
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA: {torch.cuda.is_available()}")
    print(f"LeRobot: {lerobot.__version__}")
except:
    pass
PYINFO
EOF
    
    chmod +x "$activate_script"
    
    log SUCCESS "Activation script created at $activate_script"
    log INFO "To activate: source $activate_script"
    
    return 0
}

# ============================================================
# Main Installation
# ============================================================

main() {
    local log_file=$(init_log "lerobot_enhanced")
    
    # Show installation header
    show_header "LeRobot (Enhanced)" "0.4.4"
    
    log INFO "Enhanced installation with dependency conflict resolution"
    log STEP "Installation log: $log_file"
    echo ""
    
    # Initialize progress (8 steps)
    init_progress 8
    
    # Redirect all output to log file
    exec > >(tee -a "$log_file") 2>&1
    
    # Step 1: Check proxy and network
    update_progress "Checking Network & Proxy" "running"
    if check_v2ray_proxy; then
        :
    fi
    if test_huggingface_access; then
        update_progress "Checking Network & Proxy" "success"
    else
        update_progress "Checking Network & Proxy" "warning"
        log WARNING "Continuing without confirmed HuggingFace access"
    fi
    
    # Step 2: Check environment
    update_progress "Environment Check" "running"
    if "$SCRIPT_DIR/check_environment.sh" lerobot; then
        update_progress "Environment Check" "success"
    else
        update_progress "Environment Check" "warning"
    fi
    
    # Step 3: Install system dependencies
    update_progress "Installing System Dependencies" "running"
    if install_system_dependencies; then
        update_progress "Installing System Dependencies" "success"
    else
        update_progress "Installing System Dependencies" "error"
        exit 1
    fi
    
    # Step 4: Create virtual environment
    update_progress "Creating Virtual Environment" "running"
    if create_venv; then
        update_progress "Creating Virtual Environment" "success"
    else
        update_progress "Creating Virtual Environment" "error"
        exit 1
    fi
    
    # Step 5: Install PyTorch
    update_progress "Installing PyTorch (CUDA-aware)" "running"
    if install_pytorch; then
        update_progress "Installing PyTorch (CUDA-aware)" "success"
    else
        update_progress "Installing PyTorch (CUDA-aware)" "error"
        exit 1
    fi
    
    # Step 6: Install LeRobot with dependencies
    update_progress "Installing LeRobot & Dependencies" "running"
    if install_lerobot_with_deps; then
        update_progress "Installing LeRobot & Dependencies" "success"
    else
        update_progress "Installing LeRobot & Dependencies" "error"
        exit 1
    fi
    
    # Step 7: Verify installation
    update_progress "Verifying Installation" "running"
    local verify_failed=0
    
    source "$INSTALL_PATH/venv/bin/activate"
    
    if ! verify_pytorch_torchvision; then
        verify_failed=1
    fi
    
    if ! verify_all_imports; then
        verify_failed=1
    fi
    
    verify_cuda
    
    if [ $verify_failed -eq 0 ]; then
        update_progress "Verifying Installation" "success"
    else
        update_progress "Verifying Installation" "warning"
        log WARNING "Some verifications failed, but installation may still work"
    fi
    
    # Step 8: Create activation script
    update_progress "Creating Activation Script" "running"
    if create_activation_script; then
        update_progress "Creating Activation Script" "success"
    else
        update_progress "Creating Activation Script" "error"
        exit 1
    fi
    
    # Generate report
    local lerobot_version=$(python3 -c "import lerobot; print(lerobot.__version__)" 2>/dev/null || echo "unknown")
    generate_report "lerobot" "$INSTALL_PATH" "$lerobot_version" "$log_file"
    
    echo ""
    log SUCCESS "════════════════════════════════════════════════════════"
    log SUCCESS "LeRobot installation completed successfully!"
    log SUCCESS "════════════════════════════════════════════════════════"
    log STEP ""
    log STEP "To activate the environment:"
    log STEP "  source $INSTALL_PATH/activate.sh"
    log STEP ""
    log STEP "To test the installation:"
    log STEP "  python3 -c 'import torch; import lerobot; print(\"OK\")'"
    
    return 0
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
