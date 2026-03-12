#!/bin/bash
# V2Ray proxy connectivity test script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# Test targets
GOOGLE_URL="https://www.google.com"
HUGGINGFACE_URL="https://huggingface.co"
GITHUB_URL="https://github.com"

# Proxy settings
SOCKS5_PROXY="socks5://127.0.0.1:10808"
HTTP_PROXY="http://127.0.0.1:10809"

# Test single URL
test_url() {
    local url=$1
    local proxy=$2
    local name=$3
    local timeout=15
    
    log STEP "Testing $name..."
    
    if timeout $timeout curl -x "$proxy" -sS -I "$url" 2>&1 | grep -q "HTTP"; then
        log SUCCESS "✓ $name: Connection successful"
        return 0
    else
        log ERROR "✗ $name: Connection failed"
        return 1
    fi
}

# Check if V2Ray is running
check_v2ray_running() {
    log INFO "Checking if V2Ray is running..."
    
    if ps aux | grep -v grep | grep -q "v2ray"; then
        log SUCCESS "V2Ray process is running"
        return 0
    else
        log ERROR "V2Ray process is NOT running"
        log INFO "Please start V2Ray first:"
        log INFO "  sudo systemctl start v2ray  # Linux"
        log INFO "  v2ray run -c /usr/local/etc/v2ray/config.json  # macOS"
        return 1
    fi
}

# Main test function
main() {
    local log_file=$(init_log "proxy_test")
    
    show_header "Proxy Connectivity Test" "1.0"
    
    log INFO "Starting proxy connectivity tests..."
    log STEP "Test log: $log_file"
    echo ""
    
    # Redirect output to log
    exec > >(tee -a "$log_file") 2>&1
    
    # Step 1: Check if V2Ray is running
    log INFO "========================================="
    log INFO "Step 1: Check V2Ray Service"
    log INFO "========================================="
    
    if ! check_v2ray_running; then
        log ERROR "V2Ray is not running. Please start it first."
        exit 1
    fi
    
    echo ""
    
    # Step 2: Test Google via SOCKS5
    log INFO "========================================="
    log INFO "Step 2: Test Google Connectivity"
    log INFO "========================================="
    
    local google_ok=false
    if test_url "$GOOGLE_URL" "$SOCKS5_PROXY" "Google (SOCKS5)"; then
        google_ok=true
    fi
    
    echo ""
    
    # Step 3: Test HuggingFace via HTTP
    log INFO "========================================="
    log INFO "Step 3: Test HuggingFace Connectivity"
    log INFO "========================================="
    
    local hf_ok=false
    if test_url "$HUGGINGFACE_URL" "$HTTP_PROXY" "HuggingFace (HTTP)"; then
        hf_ok=true
    fi
    
    echo ""
    
    # Step 4: Test GitHub via HTTP
    log INFO "========================================="
    log INFO "Step 4: Test GitHub Connectivity"
    log INFO "========================================="
    
    local github_ok=false
    if test_url "$GITHUB_URL" "$HTTP_PROXY" "GitHub (HTTP)"; then
        github_ok=true
    fi
    
    echo ""
    
    # Summary
    log INFO "========================================="
    log INFO "Test Summary"
    log INFO "========================================="
    
    if [ "$google_ok" = true ]; then
        log SUCCESS "✓ Google:      PASSED"
    else
        log ERROR "✗ Google:      FAILED"
    fi
    
    if [ "$hf_ok" = true ]; then
        log SUCCESS "✓ HuggingFace: PASSED"
    else
        log ERROR "✗ HuggingFace: FAILED"
    fi
    
    if [ "$github_ok" = true ]; then
        log SUCCESS "✓ GitHub:      PASSED"
    else
        log ERROR "✗ GitHub:      FAILED"
    fi
    
    echo ""
    
    # Overall result
    if [ "$google_ok" = true ] && [ "$hf_ok" = true ]; then
        log SUCCESS "========================================="
        log SUCCESS "✅ ALL CRITICAL TESTS PASSED!"
        log SUCCESS "========================================="
        log SUCCESS "Proxy is working correctly."
        log SUCCESS "You can now proceed with other installations."
        log INFO ""
        log INFO "To use proxy in your environment:"
        log INFO "  export ALL_PROXY=socks5://127.0.0.1:10808"
        log INFO "  export HTTPS_PROXY=http://127.0.0.1:10809"
        return 0
    else
        log ERROR "========================================="
        log ERROR "❌ CRITICAL TESTS FAILED!"
        log ERROR "========================================="
        log ERROR "Proxy is not working correctly."
        log ERROR "Please check V2Ray configuration before proceeding."
        log INFO ""
        log INFO "Troubleshooting:"
        log INFO "1. Check V2Ray config: /usr/local/etc/v2ray/config.json"
        log INFO "2. Check V2Ray logs: journalctl -u v2ray -n 50"
        log INFO "3. Verify server address and credentials"
        return 1
    fi
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
