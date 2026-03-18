#!/bin/bash
# V2Ray installation script with mirror fallback
# Supports: Ubuntu/Debian, macOS
# Enhanced with: mirror sites, progress display, error handling

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# Default installation path
INSTALL_PATH="${INSTALL_PATH:-$HOME/opt/v2ray}"

# Mirror sites for V2Ray downloads
# GitCode mirror is fastest for Chinese users (added 2026-03-18)
GITHUB_MIRRORS=(
    "https://gitcode.com/nicely235/place/-/raw/main"
    "https://github.com"
    "https://hub.fastgit.xyz"
    "https://ghproxy.com/https://github.com"
    "https://mirror.ghproxy.com/https://github.com"
)

# GitCode download URL (complete package with v2ray + geodata)
GITCODE_V2RAY_URL="https://gitcode.com/nicely235/place/-/raw/main/v2ray-linux-64.tar.gz"
GITCODE_GEOIP_URL="https://gitcode.com/nicely235/place/-/raw/main/geoip.dat"
GITCODE_GEOSITE_URL="https://gitcode.com/nicely235/place/-/raw/main/geosite.dat"

# V2Ray version
V2RAY_VERSION="5.44.1"

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

# Download with mirror fallback
download_with_mirror() {
    local url_path="$1"
    local output_file="$2"
    local description="$3"
    
    log INFO "Downloading $description..."
    
    # Try each mirror
    for mirror in "${GITHUB_MIRRORS[@]}"; do
        local full_url="${mirror}${url_path}"
        log INFO "Trying mirror: $mirror"
        
        if curl -L --connect-timeout 10 -m 60 -o "$output_file" "$full_url" 2>&1 | while read line; do
            if echo "$line" | grep -qE "(saved|100%)"; then
                log SUCCESS "Download complete"
            fi
        done; then
            if [ -f "$output_file" ] && [ -s "$output_file" ]; then
                log SUCCESS "Successfully downloaded from $mirror"
                return 0
            fi
        fi
        
        log WARNING "Mirror failed: $mirror"
        rm -f "$output_file"
    done
    
    log ERROR "All mirrors failed"
    return 1
}

# Download V2Ray from GitCode (fastest for Chinese users)
download_from_gitcode() {
    log INFO "Downloading V2Ray from GitCode mirror (optimized for China)..."
    
    # Create installation directory
    check_directory "$INSTALL_PATH" || return 1
    
    # Download complete package (v2ray + geoip.dat + geosite.dat)
    local tar_file="$INSTALL_PATH/v2ray-linux-64.tar.gz"
    
    log INFO "Downloading complete V2Ray package from GitCode..."
    log INFO "URL: $GITCODE_V2RAY_URL"
    
    if curl -L --connect-timeout 10 -m 120 -o "$tar_file" "$GITCODE_V2RAY_URL"; then
        if [ -f "$tar_file" ] && [ -s "$tar_file" ]; then
            log SUCCESS "Downloaded V2Ray package from GitCode ($(du -h "$tar_file" | cut -f1))"
        else
            log ERROR "Downloaded file is empty or missing"
            rm -f "$tar_file"
            return 1
        fi
    else
        log WARNING "Failed to download from GitCode"
        rm -f "$tar_file"
        return 1
    fi
    
    # Extract package
    log INFO "Extracting V2Ray package..."
    tar -xzf "$tar_file" -C "$INSTALL_PATH" || {
        log ERROR "Failed to extract V2Ray package"
        return 1
    }
    
    # Verify extracted files
    if [ ! -f "$INSTALL_PATH/v2ray" ]; then
        log ERROR "v2ray binary not found after extraction"
        return 1
    fi
    
    if [ ! -f "$INSTALL_PATH/geoip.dat" ] || [ ! -f "$INSTALL_PATH/geosite.dat" ]; then
        log ERROR "Geodata files not found after extraction"
        return 1
    fi
    
    log SUCCESS "V2Ray package extracted successfully"
    
    # Install binary
    log STEP "Installing V2Ray binary..."
    
    if [ "$(uname)" = "Darwin" ]; then
        local bin_dir="/usr/local/bin"
        local dat_dir="/usr/local/share/v2ray"
    else
        local bin_dir="/usr/local/bin"
        local dat_dir="/usr/local/share/v2ray"
    fi
    
    sudo mkdir -p "$bin_dir" "$dat_dir"
    
    sudo cp "$INSTALL_PATH/v2ray" "$bin_dir/v2ray" || {
        log ERROR "Failed to copy v2ray binary"
        return 1
    }
    
    sudo chmod +x "$bin_dir/v2ray"
    
    sudo cp "$INSTALL_PATH/geoip.dat" "$INSTALL_PATH/geosite.dat" "$dat_dir/" || {
        log ERROR "Failed to copy geodata files"
        return 1
    }
    
    log SUCCESS "V2Ray binary installed to $bin_dir/v2ray"
    log SUCCESS "Geodata files installed to $dat_dir/"
    
    # Cleanup
    rm -f "$tar_file"
    
    return 0
}

# Download V2Ray binary manually
download_v2ray_manual() {
    log INFO "Downloading V2Ray binary manually..."
    
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
    
    # Download V2Ray core
    local download_url="/v2fly/v2ray-core/releases/download/v${V2RAY_VERSION}/v2ray-linux-${v2ray_arch}.zip"
    local zip_file="$INSTALL_PATH/v2ray.zip"
    
    if download_with_mirror "$download_url" "$zip_file" "V2Ray v${V2RAY_VERSION}"; then
        log SUCCESS "V2Ray binary downloaded"
    else
        log ERROR "Failed to download V2Ray binary"
        return 1
    fi
    
    # Download geodata files
    log INFO "Downloading geodata files..."
    
    local geoip_url="/v2fly/geoip/releases/latest/download/geoip.dat"
    local geosite_url="/v2fly/domain-list-community/releases/latest/download/dlc.dat"
    
    if ! download_with_mirror "$geoip_url" "$INSTALL_PATH/geoip.dat" "geoip.dat"; then
        log WARNING "Failed to download geoip.dat, trying SourceForge..."
        wget -O "$INSTALL_PATH/geoip.dat" "https://downloads.sourceforge.net/project/v2ray/geoip.dat" || {
            log ERROR "Failed to download geoip.dat"
            return 1
        }
    fi
    
    if ! download_with_mirror "$geosite_url" "$INSTALL_PATH/geosite.dat" "geosite.dat"; then
        log WARNING "Failed to download geosite.dat, trying SourceForge..."
        wget -O "$INSTALL_PATH/geosite.dat" "https://downloads.sourceforge.net/project/v2ray/geosite.dat" || {
            log ERROR "Failed to download geosite.dat"
            return 1
        }
    fi
    
    # Extract V2Ray
    log INFO "Extracting V2Ray..."
    unzip -o "$zip_file" -d "$INSTALL_PATH/v2ray-extracted" || {
        log ERROR "Failed to extract V2Ray"
        return 1
    }
    
    # Install binary
    log STEP "Installing V2Ray binary..."
    
    if [ "$(uname)" = "Darwin" ]; then
        # macOS
        local bin_dir="/usr/local/bin"
        local dat_dir="/usr/local/share/v2ray"
    else
        # Linux
        local bin_dir="/usr/local/bin"
        local dat_dir="/usr/local/share/v2ray"
    fi
    
    sudo mkdir -p "$bin_dir" "$dat_dir"
    
    sudo cp "$INSTALL_PATH/v2ray-extracted/v2ray" "$bin_dir/v2ray" || {
        log ERROR "Failed to copy v2ray binary"
        return 1
    }
    
    sudo chmod +x "$bin_dir/v2ray"
    
    sudo cp "$INSTALL_PATH/geoip.dat" "$INSTALL_PATH/geosite.dat" "$dat_dir/" || {
        log ERROR "Failed to copy geodata files"
        return 1
    }
    
    log SUCCESS "V2Ray binary installed to $bin_dir/v2ray"
    log SUCCESS "Geodata files installed to $dat_dir/"
    
    # Cleanup
    rm -rf "$INSTALL_PATH/v2ray-extracted" "$zip_file"
    
    return 0
}

# Download and install V2Ray (with mirror fallback)
install_v2ray() {
    log INFO "Installing V2Ray..."
    
    # Method 0: Try GitCode first (fastest for Chinese users)
    log STEP "Method 0: Downloading from GitCode mirror (optimized for China)..."
    
    if download_from_gitcode; then
        log SUCCESS "V2Ray installed successfully from GitCode"
        return 0
    fi
    
    log WARNING "GitCode download failed, trying other methods..."
    
    # Method 1: Try official installer
    log STEP "Method 1: Trying official installer..."
    
    local install_script="$INSTALL_PATH/install-release.sh"
    
    if retry_command 1 5 "curl -L --connect-timeout 10 -m 60 -o $install_script https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh"; then
        log SUCCESS "Official installer downloaded"
        
        chmod +x "$install_script"
        
        log STEP "Executing V2Ray installer..."
        
        if [ "$(uname)" = "Darwin" ]; then
            if timeout 300 bash "$install_script" 2>&1 | while read line; do
                log PROGRESS "$line"
            done; then
                log SUCCESS "V2Ray installed successfully via official installer"
                return 0
            fi
        else
            if timeout 300 sudo bash "$install_script" 2>&1 | while read line; do
                log PROGRESS "$line"
            done; then
                log SUCCESS "V2Ray installed successfully via official installer"
                return 0
            fi
        fi
    fi
    
    log WARNING "Official installer failed, trying mirror downloads..."
    
    # Method 2: Manual download with mirror fallback
    log STEP "Method 2: Manual download from mirrors..."
    
    if download_v2ray_manual; then
        log SUCCESS "V2Ray installed successfully via mirror"
    else
        log ERROR "Mirror download failed"
        
        # Method 3: Try apt (last resort, old version)
        log STEP "Method 3: Trying apt (may install old version)..."
        
        if command_exists apt-get; then
            log WARNING "This will install V2Ray from apt repository (version 4.x, may have bugs)"
            read -p "Continue with apt installation? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                sudo apt-get update && sudo apt-get install -y v2ray || {
                    log ERROR "apt installation failed"
                    return 1
                }
                log SUCCESS "V2Ray installed via apt (version 4.x)"
                log WARNING "Consider upgrading to v5+ manually"
                return 0
            fi
        fi
        
        log ERROR "All installation methods failed"
        return 1
    fi
    
    return 0
}

# Configure V2Ray
configure_v2ray() {
    log INFO "Configuring V2Ray..."
    
    local config_dir="/usr/local/etc/v2ray"
    local config_file="$config_dir/config.json"
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local config_save="$script_dir/../config/v2ray_server.json"
    
    # Create config directory
    sudo mkdir -p "$config_dir"
    
    # Check if config file exists
    if [ -f "$config_file" ]; then
        log INFO "Configuration file already exists at $config_file"
        log WARNING "Backing up existing configuration..."
        sudo cp "$config_file" "$config_file.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Try to download config template from GitCode first
    log INFO "Downloading V2Ray config template from GitCode..."
    
    if curl -L --connect-timeout 10 -m 30 -o "$config_file" "$GITCODE_CONFIG_V2RAY_URL" 2>/dev/null; then
        if [ -f "$config_file" ] && [ -s "$config_file" ]; then
            log SUCCESS "Downloaded config template from GitCode"
            log WARNING "Please edit $config_file and update YOUR_SERVER_ADDRESS and YOUR_UUID"
            return 0
        fi
    fi
    
    log WARNING "Failed to download from GitCode, using local template..."
    
    # Check if saved configuration exists
    if [ -f "$config_save" ]; then
        log INFO "Found saved V2Ray server configuration"
        echo ""
        cat "$config_save"
        echo ""
        read -p "Use saved server configuration? (y/n) " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log INFO "Applying saved server configuration..."
            
            # Use configure_v2ray.sh to generate config
            if [ -f "$script_dir/configure_v2ray.sh" ]; then
                bash "$script_dir/configure_v2ray.sh" --apply "$config_file" || {
                    log WARNING "Failed to apply saved config, using template instead"
                    create_default_config "$config_file"
                }
            else
                log WARNING "configure_v2ray.sh not found, using template"
                create_default_config "$config_file"
            fi
        else
            log INFO "Using default template configuration"
            create_default_config "$config_file"
        fi
    else
        log INFO "No saved server configuration found"
        log INFO "Creating default template configuration..."
        create_default_config "$config_file"
    fi
    
    log SUCCESS "Configuration created at $config_file"
    log WARNING "Please edit $config_file and update YOUR_SERVER_ADDRESS and YOUR_UUID"
    
    return 0
}

# Create default V2Ray configuration
create_default_config() {
    local config_file="$1"
    local config_dir="$(dirname "$config_file")"
    
    sudo mkdir -p "$config_dir"
    
    # Create complete configuration with proxy
    log INFO "Creating complete configuration with proxy settings..."
    
    sudo tee "$config_file" > /dev/null << 'EOF'
    
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
      "sniffing": {
        "destOverride": [
          "http",
          "tls"
        ],
        "enabled": true,
        "routeOnly": false
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
            "address": "YOUR_SERVER_ADDRESS",
            "port": 443,
            "users": [
              {
                "id": "YOUR_UUID",
                "alterId": 0,
                "security": "auto",
                "level": 8
              }
            ]
          }
        ]
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls",
        "tlsSettings": {
          "allowInsecure": false,
          "serverName": "YOUR_SERVER_ADDRESS"
        },
        "wsSettings": {
          "headers": {
            "Host": "YOUR_SERVER_ADDRESS"
          },
          "path": "/"
        }
      },
      "tag": "proxy"
    },
    {
      "protocol": "freedom",
      "settings": {},
      "tag": "direct"
    }
  ],
  "routing": {
    "domainStrategy": "IPIfNonMatch",
    "rules": [
      {
        "ip": [
          "geoip:private"
        ],
        "outboundTag": "direct",
        "type": "field"
      }
    ]
  }
}
EOF
    
    log SUCCESS "Configuration created at $config_file"
    log WARNING "Please edit $config_file and update YOUR_SERVER_ADDRESS and YOUR_UUID"
    
    return 0
}

# Start V2Ray service
start_v2ray() {
    log INFO "Starting V2Ray service..."
    
    if [ "$(uname)" = "Darwin" ]; then
        # macOS - manual start
        log INFO "macOS detected, starting V2Ray manually..."
        
        local config_file="/usr/local/etc/v2ray/config.json"
        local log_file="/tmp/v2ray.log"
        
        # Check if already running
        if pgrep -f "v2ray run" > /dev/null; then
            log WARNING "V2Ray is already running"
            return 0
        fi
        
        # Start in background
        nohup /usr/local/bin/v2ray run -config "$config_file" > "$log_file" 2>&1 &
        local pid=$!
        
        sleep 2
        
        if ps -p $pid > /dev/null; then
            log SUCCESS "V2Ray started (PID: $pid)"
            log INFO "Log file: $log_file"
        else
            log ERROR "Failed to start V2Ray"
            cat "$log_file"
            return 1
        fi
    else
        # Linux - use systemd
        if command_exists systemctl; then
            log INFO "Starting V2Ray via systemd..."
            
            # Create systemd service if not exists
            if [ ! -f /etc/systemd/system/v2ray.service ]; then
                log INFO "Creating systemd service..."
                
                sudo tee /etc/systemd/system/v2ray.service > /dev/null << 'EOF'
[Unit]
Description=V2Ray Service
Documentation=https://www.v2fly.org/
After=network.target nss-lookup.target

[Service]
Type=simple
User=root
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ExecStart=/usr/local/bin/v2ray run -config /usr/local/etc/v2ray/config.json
Restart=on-failure
RestartPreventExitStatus=23

[Install]
WantedBy=multi-user.target
EOF
                
                sudo systemctl daemon-reload
            fi
            
            sudo systemctl enable v2ray
            sudo systemctl start v2ray
            
            if sudo systemctl is-active --quiet v2ray; then
                log SUCCESS "V2Ray service started"
            else
                log ERROR "Failed to start V2Ray service"
                sudo journalctl -u v2ray --no-pager -n 20
                return 1
            fi
        else
            log WARNING "systemd not available, starting manually..."
            
            local config_file="/usr/local/etc/v2ray/config.json"
            local log_file="/tmp/v2ray.log"
            
            # Check if already running
            if pgrep -f "v2ray run" > /dev/null; then
                log WARNING "V2Ray is already running"
                return 0
            fi
            
            # Start in background
            nohup /usr/local/bin/v2ray run -config "$config_file" > "$log_file" 2>&1 &
            local pid=$!
            
            sleep 2
            
            if ps -p $pid > /dev/null; then
                log SUCCESS "V2Ray started (PID: $pid)"
                log INFO "Log file: $log_file"
            else
                log ERROR "Failed to start V2Ray"
                cat "$log_file"
                return 1
            fi
        fi
    fi
    
    return 0
}

# Test proxy connection
test_connection() {
    log INFO "Testing proxy connection..."
    
    # Test SOCKS5 proxy
    log INFO "Testing SOCKS5 proxy (127.0.0.1:10808)..."
    
    if curl -x socks5://127.0.0.1:10808 -I -m 10 -s https://www.google.com | grep -q "HTTP"; then
        log SUCCESS "SOCKS5 proxy is working"
    else
        log WARNING "SOCKS5 proxy test failed"
    fi
    
    # Test HTTP proxy
    log INFO "Testing HTTP proxy (127.0.0.1:10809)..."
    
    if curl -x http://127.0.0.1:10809 -I -m 10 -s https://www.google.com | grep -q "HTTP"; then
        log SUCCESS "HTTP proxy is working"
    else
        log WARNING "HTTP proxy test failed"
    fi
    
    # Test HuggingFace access
    log INFO "Testing HuggingFace access..."
    
    if curl -x http://127.0.0.1:10809 -I -m 10 -s https://huggingface.co | grep -q "HTTP/2 200"; then
        log SUCCESS "HuggingFace is accessible"
    else
        log WARNING "HuggingFace access test failed"
    fi
    
    return 0
}

# Main installation flow
main() {
    log INFO "Starting V2Ray installation..."
    log INFO "Installation log: $LOG_FILE"
    
    # Step 1: Install dependencies
    install_dependencies || {
        log ERROR "Dependency installation failed"
        return 1
    }
    
    # Step 2: Install V2Ray
    install_v2ray || {
        log ERROR "V2Ray installation failed"
        return 1
    }
    
    # Step 3: Configure V2Ray
    configure_v2ray || {
        log ERROR "V2Ray configuration failed"
        return 1
    }
    
    # Step 4: Start V2Ray service
    start_v2ray || {
        log ERROR "Failed to start V2Ray service"
        return 1
    }
    
    # Step 5: Test connection
    test_connection || {
        log WARNING "Connection test failed (may need configuration)"
    }
    
    log SUCCESS "V2Ray installation completed!"
    log INFO "Proxy endpoints:"
    log INFO "  SOCKS5: 127.0.0.1:10808"
    log INFO "  HTTP:   127.0.0.1:10809"
    log INFO ""
    log WARNING "Please edit /usr/local/etc/v2ray/config.json with your server details"
    
    # Step 6: Configure proxy environment variables
    configure_proxy_env || {
        log WARNING "Failed to configure proxy environment variables (optional)"
    }
    
    return 0
}

# Configure proxy environment variables
configure_proxy_env() {
    log INFO "Configuring proxy environment variables..."
    
    local proxy_http="http://127.0.0.1:10809"
    local proxy_https="http://127.0.0.1:10809"
    local proxy_all="socks5://127.0.0.1:10808"
    
    # Check current shell
    local shell_rc=""
    if [ -n "$BASH_VERSION" ]; then
        shell_rc="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        shell_rc="$HOME/.zshrc"
    else
        shell_rc="$HOME/.profile"
    fi
    
    log INFO "Detected shell RC file: $shell_rc"
    
    # Check if proxy is already configured
    if grep -q "HTTP_PROXY.*127.0.0.1:10809" "$shell_rc" 2>/dev/null; then
        log SUCCESS "Proxy environment variables already configured in $shell_rc"
        return 0
    fi
    
    # Ask user if they want to configure
    log INFO "Proxy environment variables are required for:"
    log INFO "  - HuggingFace model downloads"
    log INFO "  - GitHub access"
    log INFO "  - pip/conda package installation"
    echo ""
    read -p "Configure proxy environment variables automatically? (y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log INFO "Skipping proxy environment configuration"
        log INFO "You can manually add these lines to $shell_rc:"
        log INFO "  export HTTP_PROXY=$proxy_http"
        log INFO "  export HTTPS_PROXY=$proxy_https"
        log INFO "  export ALL_PROXY=$proxy_all"
        return 0
    fi
    
    # Backup RC file
    if [ -f "$shell_rc" ]; then
        cp "$shell_rc" "$shell_rc.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Add proxy configuration
    log INFO "Adding proxy configuration to $shell_rc..."
    
    cat >> "$shell_rc" << 'EOF'

# V2Ray Proxy Configuration (added by env-setup skill)
export HTTP_PROXY=http://127.0.0.1:10809
export HTTPS_PROXY=http://127.0.0.1:10809
export ALL_PROXY=socks5://127.0.0.1:10808
export http_proxy=http://127.0.0.1:10809
export https_proxy=http://127.0.0.1:10809
EOF
    
    log SUCCESS "Proxy environment variables added to $shell_rc"
    
    # Set for current session
    export HTTP_PROXY="$proxy_http"
    export HTTPS_PROXY="$proxy_https"
    export ALL_PROXY="$proxy_all"
    export http_proxy="$proxy_http"
    export https_proxy="$proxy_https"
    
    log SUCCESS "Proxy environment variables set for current session"
    log INFO ""
    log INFO "To apply to current terminal, run:"
    log INFO "  source $shell_rc"
    log INFO ""
    log INFO "Or open a new terminal"
    
    return 0
}

# Run main function
main "$@"
