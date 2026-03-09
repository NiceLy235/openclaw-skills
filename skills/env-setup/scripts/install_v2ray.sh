#!/bin/bash
# V2Ray installation script for Ubuntu/Debian/macOS

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# Default installation path
INSTALL_PATH="${INSTALL_PATH:-$HOME/opt/v2ray}"

# Install dependencies
install_dependencies() {
    log INFO "Installing required packages..."
    
    local deps=("curl" "wget" "unzip")
    
    for dep in "${deps[@]}"; do
        if ! command_exists "$dep"; then
            log STEP "Installing $dep..."
            install_package "$dep" || {
                log ERROR "Failed to install $dep"
                return 1
            }
        else
            log SUCCESS "$dep is already installed"
        fi
    done
    
    log SUCCESS "All dependencies are ready"
    return 0
}

# Download and install V2Ray
install_v2ray() {
    log INFO "Installing V2Ray..."
    
    # Create installation directory
    check_directory "$INSTALL_PATH" || return 1
    
    # Detect architecture
    local arch=$(detect_arch)
    local v2ray_arch=""
    
    case $arch in
        x86_64)
            v2ray_arch="64"
            log INFO "Detected architecture: x86_64"
            ;;
        aarch64|arm64)
            v2ray_arch="arm64-v8a"
            log INFO "Detected architecture: ARM64"
            ;;
        *)
            log ERROR "Unsupported architecture: $arch"
            return 1
            ;;
    esac
    
    # Download V2Ray installation script
    log STEP "Downloading V2Ray installation script..."
    local install_script="$INSTALL_PATH/install-release.sh"
    
    show_download_progress "https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh" "V2Ray Installer"
    
    if retry_command 3 5 "curl -L -o $install_script https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh"; then
        log SUCCESS "Installation script downloaded"
    else
        log ERROR "Failed to download V2Ray installation script"
        return 1
    fi
    
    # Make executable
    chmod +x "$install_script"
    
    # Run installation
    log STEP "Executing V2Ray installer..."
    log INFO "This will download and install V2Ray to /usr/local/bin/"
    echo ""
    
    if [ "$(uname)" = "Darwin" ]; then
        # macOS doesn't use systemd, manual installation
        if bash "$install_script" 2>&1 | grep -E "(installed|error|V2Ray)" | while read line; do
            log PROGRESS "$line"
        done; then
            log SUCCESS "V2Ray installed successfully"
        else
            log ERROR "V2Ray installation failed"
            return 1
        fi
    else
        # Linux with systemd
        if sudo bash "$install_script" 2>&1 | while read line; do
            if echo "$line" | grep -q "installed:"; then
                log SUCCESS "$(echo "$line" | sed 's/installed:/  ✓/')"
            elif echo "$line" | grep -qE "(info|V2Ray)"; then
                log PROGRESS "$line"
            fi
        done; then
            log SUCCESS "V2Ray core installed"
        else
            log ERROR "V2Ray installation failed"
            return 1
        fi
    fi
    
    return 0
}

# Configure V2Ray
configure_v2ray() {
    log INFO "Configuring V2Ray..."
    
    local config_dir="/usr/local/etc/v2ray"
    local config_file="$config_dir/config.json"
    
    # Create default config if not exists
    if [ ! -f "$config_file" ]; then
        log INFO "Creating default configuration..."
        
        sudo mkdir -p "$config_dir"
        
        sudo tee "$config_file" > /dev/null << 'EOF'
{
  "inbounds": [{
    "port": 1080,
    "listen": "127.0.0.1",
    "protocol": "socks",
    "settings": {
      "udp": true
    }
  }],
  "outbounds": [{
    "protocol": "freedom",
    "settings": {}
  }]
}
EOF
        
        log SUCCESS "Default configuration created at $config_file"
    else
        log INFO "Configuration file already exists at $config_file"
    fi
    
    return 0
}

# Start V2Ray service
start_v2ray() {
    log INFO "Starting V2Ray service..."
    
    if [ "$(uname)" = "Darwin" ]; then
        # macOS - manual start
        log WARNING "On macOS, you need to manually start V2Ray:"
        log WARNING "  v2ray run -c /usr/local/etc/v2ray/config.json"
    else
        # Linux with systemd
        sudo systemctl daemon-reload
        sudo systemctl enable v2ray
        sudo systemctl start v2ray
        
        # Check status
        sleep 2
        if sudo systemctl is-active --quiet v2ray; then
            log SUCCESS "V2Ray service is running"
        else
            log ERROR "V2Ray service failed to start"
            return 1
        fi
    fi
    
    return 0
}

# Verify installation
verify_installation() {
    log INFO "Verifying installation..."
    
    if command_exists v2ray; then
        local version=$(v2ray version | head -1)
        log SUCCESS "V2Ray installed: $version"
        
        # Test basic functionality
        if v2ray help >/dev/null 2>&1; then
            log SUCCESS "V2Ray is functioning correctly"
            return 0
        else
            log WARNING "V2Ray installed but basic test failed"
            return 1
        fi
    else
        log ERROR "V2Ray not found in PATH"
        return 1
    fi
}

# Main installation function
main() {
    local log_file=$(init_log "v2ray")
    
    # Show installation header
    show_header "V2Ray" "5.44.1"
    
    log INFO "Starting V2Ray installation..."
    log STEP "Installation log: $log_file"
    echo ""
    
    # Initialize progress (6 steps)
    init_progress 6
    
    # Redirect all output to log file
    exec > >(tee -a "$log_file") 2>&1
    
    # Step 1: Check environment
    update_progress "Environment Check" "running"
    if "$SCRIPT_DIR/check_environment.sh" v2ray; then
        update_progress "Environment Check" "success"
    else
        update_progress "Environment Check" "error"
        exit 1
    fi
    
    # Step 2: Install dependencies
    update_progress "Installing Dependencies" "running"
    if install_dependencies; then
        update_progress "Installing Dependencies" "success"
    else
        update_progress "Installing Dependencies" "error"
        exit 1
    fi
    
    # Step 3: Install V2Ray
    update_progress "Installing V2Ray Core" "running"
    log INFO "Downloading V2Ray from GitHub..."
    if install_v2ray; then
        update_progress "Installing V2Ray Core" "success"
    else
        update_progress "Installing V2Ray Core" "error"
        exit 1
    fi
    
    # Step 4: Configure V2Ray
    update_progress "Configuring V2Ray" "running"
    if configure_v2ray; then
        update_progress "Configuring V2Ray" "success"
    else
        update_progress "Configuring V2Ray" "error"
        exit 1
    fi
    
    # Step 5: Start service
    update_progress "Starting V2Ray Service" "running"
    if start_v2ray; then
        update_progress "Starting V2Ray Service" "success"
    else
        update_progress "Starting V2Ray Service" "error"
        exit 1
    fi
    
    # Step 6: Verify installation
    update_progress "Verifying Installation" "running"
    if verify_installation; then
        update_progress "Verifying Installation" "success"
    else
        update_progress "Verifying Installation" "error"
        exit 1
    fi
    
    # Generate report
    local version=$(v2ray version | head -1 | awk '{print $2}')
    generate_report "v2ray" "/usr/local/bin/v2ray" "$version" "$log_file"
    
    log SUCCESS "V2Ray installation completed successfully!"
    
    return 0
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
