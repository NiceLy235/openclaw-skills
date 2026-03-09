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
    
    # Check if config file exists
    if [ -f "$config_file" ]; then
        log INFO "Configuration file already exists at $config_file"
        log WARNING "Backing up existing configuration..."
        sudo cp "$config_file" "$config_file.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Create complete configuration with proxy
    log INFO "Creating complete configuration with proxy settings..."
    
    sudo mkdir -p "$config_dir"
    
    sudo tee "$config_file" > /dev/null << 'EOF'
{
  "inbounds": [
    {
      "listen": "0.0.0.0",
      "port": 10808,
      "protocol": "socks",
      "settings": {
        "auth": "noauth",
        "udp": true,
        "userLevel": 8
      },
      "sniffing": {
        "destOverride": [
          "http",
          "tls"
        ],
        "enabled": true,
        "routeOnly": false
      },
      "tag": "socks"
    },
    {
      "listen": "0.0.0.0",
      "port": 10809,
      "protocol": "http",
      "settings": {
        "userLevel": 8
      },
      "tag": "http"
    }
  ],
  "log": {
    "loglevel": "warning"
  },
  "outbounds": [
    {
      "protocol": "vmess",
      "settings": {
        "vnext": [
          {
            "address": "gitee.yianchenyianchen.xyz",
            "port": 443,
            "users": [
              {
                "id": "b831381d-6324-4d53-ad4f-8cda48b30811"
              }
            ]
          }
        ]
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls",
        "sockopt": {
          "keepAlive": 30
        }
      }
    },
    {
      "protocol": "freedom",
      "tag": "direct"
    }
  ],
  "routing": {
    "domainStrategy": "IPOnDemand",
    "rules": [
      {
        "type": "field",
        "ip": [
          "geoip:private"
        ],
        "outboundTag": "direct"
      },
      {
        "domain": [
          "geosite:private"
        ],
        "outboundTag": "direct",
        "type": "field"
      },
      {
        "domain": [
          "domain:alidns.com",
          "domain:doh.pub",
          "domain:dot.pub",
          "domain:360.cn",
          "domain:onedns.net"
        ],
        "outboundTag": "direct",
        "type": "field"
      },
      {
        "ip": [
          "geoip:cn"
        ],
        "outboundTag": "direct",
        "type": "field"
      },
      {
        "domain": [
          "geosite:cn"
        ],
        "outboundTag": "direct",
        "type": "field"
      }
    ]
  }
}
EOF
    
    log SUCCESS "Configuration created at $config_file"
    log INFO "  SOCKS5 proxy: 0.0.0.0:10808"
    log INFO "  HTTP proxy:   0.0.0.0:10809"
    
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

# Test proxy connectivity
test_connectivity() {
    log INFO "Testing proxy connectivity..."
    
    # Wait for service to fully start
    sleep 3
    
    # Test SOCKS5 proxy with Google
    log STEP "Testing connection to Google via SOCKS5 proxy..."
    local test_result
    
    if [ "$(uname)" = "Darwin" ]; then
        # macOS doesn't have systemd, assume manual start
        test_result="skip"
    else
        # Test SOCKS5 proxy
        if timeout 10 curl -x socks5://127.0.0.1:10808 -I https://www.google.com 2>&1 | grep -q "HTTP"; then
            log SUCCESS "Google connection via SOCKS5 proxy: OK"
            test_result="success"
        else
            log WARNING "Google connection via SOCKS5 proxy: FAILED"
            test_result="failed"
        fi
    fi
    
    # Test HTTP proxy
    log STEP "Testing connection to GitHub via HTTP proxy..."
    if timeout 10 curl -x http://127.0.0.1:10809 -I https://github.com 2>&1 | grep -q "HTTP"; then
        log SUCCESS "GitHub connection via HTTP proxy: OK"
    else
        log WARNING "GitHub connection via HTTP proxy: FAILED"
    fi
    
    # Display usage information
    echo ""
    log INFO "========================================="
    log INFO "Proxy Configuration"
    log INFO "========================================="
    log INFO "SOCKS5 Proxy: 127.0.0.1:10808"
    log INFO "HTTP Proxy:   127.0.0.1:10809"
    log INFO ""
    log INFO "Usage Examples:"
    log INFO "  curl -x socks5://127.0.0.1:10808 https://www.google.com"
    log INFO "  export ALL_PROXY=socks5://127.0.0.1:10808"
    log INFO ""
    log INFO "Note: ping command does NOT use proxy (ICMP limitation)"
    log INFO "========================================="
    
    if [ "$test_result" = "success" ]; then
        return 0
    elif [ "$test_result" = "skip" ]; then
        return 0
    else
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
    
    # Initialize progress (7 steps)
    init_progress 7
    
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
    
    # Step 7: Test connectivity
    update_progress "Testing Proxy Connectivity" "running"
    if test_connectivity; then
        update_progress "Testing Proxy Connectivity" "success"
    else
        update_progress "Testing Proxy Connectivity" "error"
        log WARNING "Proxy installed but connectivity test failed"
        log WARNING "This might be normal if network is restricted"
        # Don't exit on connectivity failure, just warn
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
