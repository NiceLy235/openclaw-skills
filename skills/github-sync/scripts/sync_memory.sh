#!/bin/bash
# Sync memory to GitHub
#
# This script:
# 1. Generates daily summary
# 2. Commits memory changes
# 3. Pushes to GitHub

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
MEMORY_DIR="$HOME/.openclaw/memory"
LOG_FILE="$HOME/.openclaw/github_sync.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] $1" | tee -a "$LOG_FILE"
}

log_info() { log "${GREEN}[INFO]${NC} $1"; }
log_warn() { log "${YELLOW}[WARN]${NC} $1"; }
log_error() { log "${RED}[ERROR]${NC} $1"; }
log_step() { log "${BLUE}[STEP]${NC} $1"; }

# ============================================================
# Proxy Configuration
# ============================================================

configure_proxy() {
    if ss -tlnp 2>/dev/null | grep -q ":10809"; then
        export HTTP_PROXY="http://127.0.0.1:10809"
        export HTTPS_PROXY="http://127.0.0.1:10809"
        export ALL_PROXY="http://127.0.0.1:10809"
        cd "$MEMORY_DIR"
        git config --local http.proxy http://127.0.0.1:10809
        git config --local https.proxy http://127.0.0.1:10809
        log_info "Proxy configured: http://127.0.0.1:10809"
        return 0
    elif ss -tlnp 2>/dev/null | grep -q ":10808"; then
        export HTTP_PROXY="socks5://127.0.0.1:10808"
        export HTTPS_PROXY="socks5://127.0.0.1:10808"
        export ALL_PROXY="socks5://127.0.0.1:10808"
        cd "$MEMORY_DIR"
        git config --local http.proxy socks5://127.0.0.1:10808
        git config --local https.proxy socks5://127.0.0.1:10808
        log_info "Proxy configured: socks5://127.0.0.1:10808"
        return 0
    fi
    
    log_warn "No proxy detected"
    return 1
}

# ============================================================
# Generate Summary
# ============================================================

generate_summary() {
    log_step "Generating daily summary..."
    
    if [ -f "$WORKSPACE_DIR/daily_summary/scripts/daily_sync.py" ]; then
        python3 "$WORKSPACE_DIR/daily_summary/scripts/daily_sync.py" --no-push >> "$LOG_FILE" 2>&1
        log_info "✅ Daily summary generated"
    else
        log_warn "Daily summary script not found, skipping"
    fi
}

# ============================================================
# Sync Process
# ============================================================

sync_memory() {
    log_step "Starting memory sync..."
    
    cd "$MEMORY_DIR"
    
    # Check if git repo
    if [ ! -d ".git" ]; then
        log_error "Memory directory is not a git repository"
        return 1
    fi
    
    # Check for changes
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        log_info "No changes to sync"
        return 0
    fi
    
    # Get stats
    local files_changed=$(git status --short | wc -l)
    log_info "Files to sync: $files_changed"
    
    # Add all changes
    git add -A
    
    # Create commit
    local date=$(date '+%Y-%m-%d')
    local commit_msg="chore: Daily memory update - $date

- Updated conversations and interactions
- Generated daily summary
- Saved experiences and lessons learned"
    
    git commit -m "$commit_msg" >> "$LOG_FILE" 2>&1
    log_info "✅ Changes committed"
    
    # Configure proxy
    configure_proxy
    
    # Push to GitHub
    log_step "Pushing to GitHub..."
    
    local branch=$(git rev-parse --abbrev-ref HEAD)
    
    if git push origin "$branch" >> "$LOG_FILE" 2>&1; then
        log_info "✅ Successfully pushed to GitHub"
        
        # Get remote URL
        local remote_url=$(git remote get-url origin 2>/dev/null | sed 's/\.git$//')
        log_info "Repository: $remote_url"
        
        return 0
    else
        log_error "Failed to push to GitHub"
        log_info "Check log: $LOG_FILE"
        return 1
    fi
}

# ============================================================
# Generate Report
# ============================================================

generate_report() {
    log ""
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log "  Memory Sync Report - $(date '+%Y-%m-%d %H:%M:%S')"
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ -d "$MEMORY_DIR" ]; then
        local conv_count=$(find "$MEMORY_DIR/conversations" -name "*.md" 2>/dev/null | wc -l)
        local summary_count=$(find "$MEMORY_DIR/daily" -name "*-summary.md" 2>/dev/null | wc -l)
        local exp_count=$(find "$MEMORY_DIR/experiences" -name "*.md" 2>/dev/null | wc -l)
        
        log ""
        log "📊 Content Stats:"
        log "  Conversations: $conv_count files"
        log "  Daily summaries: $summary_count files"
        log "  Experiences: $exp_count files"
    fi
    
    log ""
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ============================================================
# Main
# ============================================================

main() {
    log ""
    log "🚀 Memory Sync - $(date '+%Y-%m-%d %H:%M:%S')"
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Step 1: Generate summary
    generate_summary
    
    # Step 2: Sync to GitHub
    sync_memory
    
    # Step 3: Generate report
    generate_report
}

# Run
main "$@"
