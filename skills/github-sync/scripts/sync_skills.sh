#!/bin/bash
# Sync skills to GitHub
#
# This script:
# 1. Commits skill changes
# 2. Pushes to GitHub

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
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
        cd "$WORKSPACE_DIR"
        git config --local http.proxy http://127.0.0.1:10809
        git config --local https.proxy http://127.0.0.1:10809
        log_info "Proxy configured: http://127.0.0.1:10809"
        return 0
    elif ss -tlnp 2>/dev/null | grep -q ":10808"; then
        export HTTP_PROXY="socks5://127.0.0.1:10808"
        export HTTPS_PROXY="socks5://127.0.0.1:10808"
        export ALL_PROXY="socks5://127.0.0.1:10808"
        cd "$WORKSPACE_DIR"
        git config --local http.proxy socks5://127.0.0.1:10808
        git config --local https.proxy socks5://127.0.0.1:10808
        log_info "Proxy configured: socks5://127.0.0.1:10808"
        return 0
    fi
    
    log_warn "No proxy detected"
    return 1
}

# ============================================================
# Sync Process
# ============================================================

sync_skills() {
    log_step "Starting skills sync..."
    
    cd "$WORKSPACE_DIR"
    
    # Check if git repo
    if [ ! -d ".git" ]; then
        log_error "Workspace is not a git repository"
        return 1
    fi
    
    # Check for changes
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        log_info "No changes to sync"
        return 0
    fi
    
    # Get stats
    local files_changed=$(git status --short | wc -l)
    local skills_changed=$(git status --short skills/ 2>/dev/null | wc -l)
    
    log_info "Total files to sync: $files_changed"
    log_info "Skills files changed: $skills_changed"
    
    # Show changed skills
    if [ $skills_changed -gt 0 ]; then
        log_info "Changed skills:"
        git status --short skills/ | head -10 | while read line; do
            log_info "  $line"
        done
    fi
    
    # Add all changes
    git add -A
    
    # Create commit
    local date=$(date '+%Y-%m-%d')
    local commit_msg="feat: Skills and workspace update - $date

Skills updated:
$(git diff --cached --name-only skills/ | sed 's/^/  - /' | head -20)

Other changes:
$(git diff --cached --name-only | grep -v '^skills/' | sed 's/^/  - /' | head -10)"
    
    git commit -m "$commit_msg" >> "$LOG_FILE" 2>&1
    log_info "✅ Changes committed"
    
    # Configure proxy
    configure_proxy
    
    # Check if remote exists
    if ! git remote | grep -q "origin"; then
        log_error "No remote 'origin' configured"
        log_info "Run setup script: $SKILL_DIR/scripts/setup_repos.sh"
        return 1
    fi
    
    # Push to GitHub
    log_step "Pushing to GitHub..."
    
    local branch=$(git rev-parse --abbrev-ref HEAD)
    
    if git push -u origin "$branch" >> "$LOG_FILE" 2>&1; then
        log_info "✅ Successfully pushed to GitHub"
        
        # Get remote URL
        local remote_url=$(git remote get-url origin 2>/dev/null | sed 's/\.git$//' | sed 's/https:\/\/[^@]*@/https:\/\//')
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
    log "  Skills Sync Report - $(date '+%Y-%m-%d %H:%M:%S')"
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ -d "$WORKSPACE_DIR/skills" ]; then
        local skill_count=$(find "$WORKSPACE_DIR/skills" -maxdepth 1 -type d | tail -n +2 | wc -l)
        
        log ""
        log "📚 Skills Available:"
        for skill_path in "$WORKSPACE_DIR/skills"/*/; do
            if [ -f "$skill_path/SKILL.md" ]; then
                local skill_name=$(basename "$skill_path")
                log "  ✅ $skill_name"
            fi
        done
        
        log ""
        log "Total: $skill_count skills"
    fi
    
    log ""
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ============================================================
# Main
# ============================================================

main() {
    log ""
    log "🚀 Skills Sync - $(date '+%Y-%m-%d %H:%M:%S')"
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Sync to GitHub
    sync_skills
    
    # Generate report
    generate_report
}

# Run
main "$@"
