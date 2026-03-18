#!/bin/bash
# V2Ray Configuration Manager
# Extract and apply V2Ray server configuration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")/config"

# Extract server configuration from local V2Ray config
extract_server_config() {
    local config_file="$1"
    
    if [ ! -f "$config_file" ]; then
        echo "❌ Configuration file not found: $config_file"
        return 1
    fi
    
    echo "📖 Extracting server configuration from: $config_file"
    
    # Use Python to extract config
    python3 - "$config_file" "$CONFIG_DIR/v2ray_server.json" << 'PYTHON'
import json
import sys

config_file = sys.argv[1]
output_file = sys.argv[2]

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    outbound = config['outbounds'][0]
    vnext = outbound['settings']['vnext'][0]
    user = vnext['users'][0]
    ws = outbound['streamSettings']['wsSettings']
    
    server_config = {
        'address': vnext['address'],
        'port': vnext['port'],
        'uuid': user['id'],
        'path': ws.get('path', '/'),
        'network': 'ws',
        'security': 'tls'
    }
    
    print(f"  Server: {server_config['address']}:{server_config['port']}")
    print(f"  UUID: {server_config['uuid']}")
    print(f"  Path: {server_config['path']}")
    
    with open(output_file, 'w') as f:
        json.dump(server_config, f, indent=2)
    
    print(f"✅ Server configuration saved to: {output_file}")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Failed to extract config: {e}")
    sys.exit(1)
PYTHON
    
    return $?
}

# Apply server configuration to template
apply_server_config() {
    local server_config="$CONFIG_DIR/v2ray_server.json"
    local template="$CONFIG_DIR/v2ray_template.json"
    local output="$1"
    
    if [ ! -f "$server_config" ]; then
        echo "❌ Server configuration not found: $server_config"
        echo "   Run: $0 --extract <config_file>"
        return 1
    fi
    
    if [ ! -f "$template" ]; then
        echo "❌ Template not found: $template"
        return 1
    fi
    
    echo "🔧 Applying server configuration to template..."
    
    # Use Python to merge configurations
    python3 - "$server_config" "$template" "$output" << 'PYTHON'
import json
import sys

server_file = sys.argv[1]
template_file = sys.argv[2]
output_file = sys.argv[3]

try:
    # Load server config
    with open(server_file, 'r') as f:
        server = json.load(f)
    
    # Load template
    with open(template_file, 'r') as f:
        config = json.load(f)
    
    # Apply server configuration
    vnext = config['outbounds'][0]['settings']['vnext'][0]
    vnext['address'] = server['address']
    vnext['port'] = server['port']
    vnext['users'][0]['id'] = server['uuid']
    
    stream = config['outbounds'][0]['streamSettings']
    stream['wsSettings']['path'] = server['path']
    stream['wsSettings']['headers']['Host'] = server['address']
    stream['tlsSettings']['serverName'] = server['address']
    
    # Save output
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration generated: {output_file}")
    print(f"   Server: {server['address']}:{server['port']}")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Failed to apply config: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON
    
    return $?
}

# Show usage
show_usage() {
    cat << 'EOF'
V2Ray Configuration Manager

Usage:
  $0 --extract <config_file>     Extract server config from local V2Ray config
  $0 --apply <output_file>       Apply server config to template and generate output
  $0 --show                      Show current server configuration

Examples:
  # Extract from local machine
  $0 --extract /usr/local/etc/v2ray/config.json

  # Generate config for remote server
  $0 --apply /tmp/v2ray_config.json

  # Show current configuration
  $0 --show
EOF
}

# Main
case "${1:-}" in
    --extract)
        extract_server_config "${2:-/usr/local/etc/v2ray/config.json}"
        ;;
    --apply)
        apply_server_config "${2:-/tmp/v2ray_config.json}"
        ;;
    --show)
        if [ -f "$CONFIG_DIR/v2ray_server.json" ]; then
            echo "📋 Current V2Ray Server Configuration:"
            cat "$CONFIG_DIR/v2ray_server.json"
        else
            echo "❌ No server configuration saved"
            echo "   Run: $0 --extract <config_file>"
        fi
        ;;
    *)
        show_usage
        ;;
esac
