# V2Ray Installation Guide

## Overview

V2Ray is a platform for building proxies to bypass network restrictions. This guide provides detailed information about V2Ray installation and configuration.

## System Requirements

- **Operating System**: Ubuntu 20.04+, Debian 11+, or macOS
- **Architecture**: x86_64 (AMD64) or ARM64
- **Disk Space**: Minimum 100MB
- **Network**: Stable internet connection

## Installation Methods

### Method 1: Automated Installation (Recommended)

Use the provided script:

```bash
bash scripts/install_v2ray.sh
```

### Method 2: Manual Installation

#### Linux (Ubuntu/Debian)

```bash
# Download installation script
curl -L -o install-release.sh https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh

# Run with sudo
sudo bash install-release.sh
```

#### macOS

```bash
# Install via Homebrew
brew install v2ray

# Or use the installation script
bash install-release.sh
```

## Configuration

### Default Configuration Location

- **Linux**: `/usr/local/etc/v2ray/config.json`
- **macOS**: `/usr/local/etc/v2ray/config.json`

### Basic Configuration Template

```json
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
```

### Advanced Configuration Examples

#### With VMess Protocol

```json
{
  "inbounds": [{
    "port": 1080,
    "protocol": "socks",
    "settings": {
      "auth": "noauth",
      "udp": true
    }
  }],
  "outbounds": [{
    "protocol": "vmess",
    "settings": {
      "vnext": [{
        "address": "your.server.com",
        "port": 443,
        "users": [{
          "id": "your-uuid",
          "alterId": 0
        }]
      }]
    },
    "streamSettings": {
      "network": "ws",
      "wsSettings": {
        "path": "/your-path"
      },
      "security": "tls"
    }
  }]
}
```

## Service Management

### Linux (systemd)

```bash
# Start service
sudo systemctl start v2ray

# Stop service
sudo systemctl stop v2ray

# Restart service
sudo systemctl restart v2ray

# Check status
sudo systemctl status v2ray

# Enable auto-start on boot
sudo systemctl enable v2ray

# View logs
sudo journalctl -u v2ray -f
```

### macOS

```bash
# Start manually
v2ray run -c /usr/local/etc/v2ray/config.json

# Or use launchd (if configured)
launchctl load /usr/local/opt/v2ray/homebrew.mxcl.v2ray.plist
```

## Verification

### Check Version

```bash
v2ray version
```

### Test Configuration

```bash
v2ray test -c /usr/local/etc/v2ray/config.json
```

### Test Connectivity

```bash
# Using curl with SOCKS5 proxy
curl --socks5 127.0.0.1:1080 https://www.google.com
```

## Uninstallation

### Linux

```bash
sudo bash /usr/local/lib/v2ray/uninstall.sh
```

### macOS

```bash
# If installed via Homebrew
brew uninstall v2ray

# If installed via script
sudo bash /usr/local/lib/v2ray/uninstall.sh
```

## Security Considerations

1. **Never expose V2Ray directly to the internet** without proper authentication
2. **Use TLS encryption** when connecting to remote servers
3. **Regularly update** to the latest version for security patches
4. **Monitor logs** for suspicious activity
5. **Use UUID authentication** with strong, randomly generated IDs

## Additional Resources

- [Official Documentation](https://www.v2ray.com/)
- [V2Fly GitHub](https://github.com/v2fly/v2ray-core)
- [Configuration Generator](https://www.v2ray.com/en/ui/)
