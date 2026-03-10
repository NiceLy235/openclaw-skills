#!/bin/bash
# Setup GitHub repositories and configure sync
#
# This script:
# 1. Detects V2Ray proxy
# 2. Configures Git remotes
# 3. Tests GitHub connectivity
# 4. Sets up cron jobs for automatic sync

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
CONFIG_FILE="$SKILL_DIR/config.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# ============================================================
# Proxy Detection
# ============================================================

detect_proxy() {
    log_step "Detecting proxy..."
    
    # Check for V2Ray HTTP proxy
    if ss -tlnp 2>/dev/null | grep -q ":10809"; then
        log_info "V2Ray HTTP proxy detected on port 10809"
        HTTP_PROXY="http://127.0.0.1:10809"
        HTTPS_PROXY="http://127.0.0.1:10809"
        PROXY_DETECTED=true
        return 0
    fi
    
    # Check for V2Ray SOCKS5 proxy
    if ss -tlnp 2>/dev/null | grep -q ":10808"; then
        log_info "V2Ray SOCKS5 proxy detected on port 10808"
        HTTP_PROXY="socks5://127.0.0.1:10808"
        HTTPS_PROXY="socks5://127.0.0.1:10808"
        PROXY_DETECTED=true
        return 0
    fi
    
    log_warn "No V2Ray proxy detected"
    log_info "If you need proxy, start V2Ray: systemctl start v2ray"
    PROXY_DETECTED=false
    return 1
}

configure_git_proxy() {
    log_step "Configuring Git proxy..."
    
    if [ "$PROXY_DETECTED" = true ]; then
        cd "$WORKSPACE_DIR"
        git config --local http.proxy "$HTTP_PROXY"
        git config --local https.proxy "$HTTPS_PROXY"
        log_info "Git proxy configured: $HTTP_PROXY"
    else
        log_warn "Skipping Git proxy configuration (no proxy detected)"
    fi
}

test_github_connection() {
    log_step "Testing GitHub connection..."
    
    if [ "$PROXY_DETECTED" = true ]; then
        if curl -x "$HTTP_PROXY" -s --connect-timeout 5 -I https://github.com 2>&1 | grep -q "HTTP"; then
            log_info "✅ GitHub accessible via proxy"
            return 0
        else
            log_warn "⚠️  GitHub not accessible via proxy"
            return 1
        fi
    else
        if curl -s --connect-timeout 5 -I https://github.com 2>&1 | grep -q "HTTP"; then
            log_info "✅ GitHub accessible (direct connection)"
            return 0
        else
            log_error "❌ GitHub not accessible"
            log_info "Consider starting V2Ray proxy"
            return 1
        fi
    fi
}

# ============================================================
# Repository Setup
# ============================================================

setup_memory_repo() {
    log_step "Setting up memory repository..."
    
    MEMORY_DIR="$HOME/.openclaw/memory"
    
    if [ ! -d "$MEMORY_DIR" ]; then
        log_info "Creating memory directory..."
        mkdir -p "$MEMORY_DIR"
    fi
    
    cd "$MEMORY_DIR"
    
    # Check if already a git repo
    if [ ! -d ".git" ]; then
        log_info "Initializing git repository..."
        git init
        
        # Create .gitignore
        cat > .gitignore << 'EOF'
# Temporary files
*.tmp
*.log
*.swp
*~

# OS files
.DS_Store
Thumbs.db
EOF
        
        git add .gitignore
        git commit -m "chore: Initialize memory repository"
    fi
    
    # Check remote
    if ! git remote | grep -q "origin"; then
        log_info "Memory repository needs to be configured"
        log_info "Using: https://github.com/NiceLy235/training-memories.git"
        
        read -p "Use this URL? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            git remote add origin https://github.com/NiceLy235/training-memories.git
            log_info "✅ Remote added"
        else
            read -p "Enter memory repository URL: " MEM_REPO_URL
            if [ -n "$MEM_REPO_URL" ]; then
                git remote add origin "$MEM_REPO_URL"
                log_info "✅ Remote added"
            else
                log_error "No URL provided, skipping memory repo setup"
                return 1
            fi
        fi
    else
        log_info "✅ Memory remote already configured"
        git remote -v | grep origin
    fi
    
    return 0
}

setup_skills_repo() {
    log_step "Setting up skills repository..."
    
    cd "$WORKSPACE_DIR"
    
    # Check if already a git repo
    if [ ! -d ".git" ]; then
        log_error "Workspace is not a git repository"
        return 1
    fi
    
    # Check remote
    if git remote | grep -q "origin"; then
        log_info "✅ Workspace remote already configured"
        git remote -v | grep origin
        return 0
    fi
    
    log_info "Skills repository needs to be configured"
    echo ""
    echo "Please provide GitHub repository URL for skills:"
    echo "  Example: https://github.com/USERNAME/openclaw-skills.git"
    echo ""
    read -p "Skills repository URL: " SKILLS_REPO_URL
    
    if [ -z "$SKILLS_REPO_URL" ]; then
        log_warn "No URL provided, skipping skills repo setup"
        log_info "You can add it later:"
        log_info "  git remote add origin YOUR_URL"
        return 1
    fi
    
    git remote add origin "$SKILLS_REPO_URL"
    log_info "✅ Remote added"
    
    return 0
}

# ============================================================
# Cron Setup
# ============================================================

setup_cron_jobs() {
    log_step "Setting up cron jobs..."
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "github-sync"; then
        log_info "Cron jobs already configured"
        crontab -l | grep "github-sync"
        
        read -p "Update cron jobs? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 0
        fi
        
        # Remove existing
        crontab -l 2>/dev/null | grep -v "github-sync" | crontab -
    fi
    
    # Add memory sync cron job (daily at 23:00)
    MEMORY_SYNC_CMD="0 23 * * * $SKILL_DIR/scripts/sync_memory.sh >> ~/.openclaw/github_sync.log 2>&1"
    
    (crontab -l 2>/dev/null; echo "$MEMORY_SYNC_CMD") | crontab -
    
    log_info "✅ Cron jobs configured:"
    log_info "  Memory sync: Daily at 23:00"
    log_info "  Skills sync: On demand (manual)"
    
    return 0
}

# ============================================================
# Main Setup
# ============================================================

main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  GitHub Sync - Repository Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Step 1: Detect proxy
    detect_proxy
    echo ""
    
    # Step 2: Configure Git proxy
    configure_git_proxy
    echo ""
    
    # Step 3: Test GitHub connection
    test_github_connection
    echo ""
    
    # Step 4: Setup memory repository
    setup_memory_repo
    echo ""
    
    # Step 5: Setup skills repository
    setup_skills_repo
    echo ""
    
    # Step 6: Setup cron jobs
    setup_cron_jobs
    echo ""
    
    # Summary
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Setup Complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📦 Repositories:"
    echo "  Memory:  $(cd ~/.openclaw/memory && git remote get-url origin 2>/dev/null || echo 'Not configured')"
    echo "  Skills:  $(cd $WORKSPACE_DIR && git remote get-url origin 2>/dev/null || echo 'Not configured')"
    echo ""
    echo "⏰ Schedule:"
    echo "  Memory sync: Daily at 23:00"
    echo "  Skills sync: Manual (run: $SKILL_DIR/scripts/sync_skills.sh)"
    echo ""
    echo "🚀 Next steps:"
    echo "  1. Test memory sync: $SKILL_DIR/scripts/sync_memory.sh"
    echo "  2. Test skills sync: $SKILL_DIR/scripts/sync_skills.sh"
    echo "  3. Check status: $SKILL_DIR/scripts/sync_status.sh"
    echo ""
}

# Run
main "$@"
