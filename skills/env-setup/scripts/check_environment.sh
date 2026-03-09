#!/bin/bash
# Environment detection and validation script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# Check if a component is already installed
check_installed() {
    local component=$1
    local check_command=$2
    
    if eval "$check_command" >/dev/null 2>&1; then
        log WARNING "$component is already installed"
        return 0
    else
        log INFO "$component is not installed"
        return 1
    fi
}

# Main environment check function
main() {
    local env_type=$1
    
    log INFO "Starting environment check for: $env_type"
    echo "========================================="
    
    # Check 1: Operating System
    log INFO "Check 1: Operating System"
    local os_info=$(detect_os)
    log INFO "Detected OS: $os_info"
    
    # Check 2: Architecture
    log INFO "Check 2: System Architecture"
    local arch=$(detect_arch)
    log INFO "Architecture: $arch"
    
    # Check 3: Disk Space
    log INFO "Check 3: Disk Space"
    check_disk_space "$HOME" || exit 1
    
    # Check 4: Network Connectivity
    log INFO "Check 4: Network Connectivity"
    check_network || exit 1
    
    # Check 5: Sudo Access (for Linux)
    if [ "$(uname)" != "Darwin" ]; then
        log INFO "Check 5: Sudo Access"
        if sudo -n true 2>/dev/null; then
            log SUCCESS "Sudo access available"
        else
            log WARNING "Sudo access may require password"
        fi
    fi
    
    # Check 6: Existing Components
    log INFO "Check 6: Existing Components"
    
    case $env_type in
        v2ray)
            check_installed "v2ray" "command -v v2ray"
            check_installed "systemd" "pidof systemd"
            ;;
        lerobot)
            check_installed "Python 3" "python3 --version"
            check_installed "pip" "pip3 --version"
            check_installed "git" "git --version"
            # Check for CUDA (optional)
            if command -v nvidia-smi >/dev/null 2>&1; then
                log SUCCESS "CUDA available: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
            else
                log WARNING "CUDA not detected (optional for lerobot)"
            fi
            ;;
        *)
            log ERROR "Unknown environment type: $env_type"
            exit 1
            ;;
    esac
    
    echo "========================================="
    log SUCCESS "Environment check completed successfully"
    
    return 0
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    if [ -z "$1" ]; then
        echo "Usage: $0 <env_type>"
        echo "  env_type: v2ray | lerobot"
        exit 1
    fi
    
    main "$1"
fi
