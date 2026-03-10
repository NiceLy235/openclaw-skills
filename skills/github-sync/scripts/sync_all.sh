#!/bin/bash
# Sync all content (memory + skills) to GitHub

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$HOME/.openclaw/github_sync.log"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] $1" | tee -a "$LOG_FILE"
}

log_info() { log "${GREEN}[INFO]${NC} $1"; }
log_step() { log "${BLUE}[STEP]${NC} $1"; }

main() {
    log ""
    log "🚀 Full Sync - $(date '+%Y-%m-%d %H:%M:%S')"
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Step 1: Sync memory
    log_step "1/2 Syncing memory..."
    if bash "$SCRIPT_DIR/sync_memory.sh"; then
        log_info "✅ Memory sync completed"
    else
        log_info "⚠️  Memory sync had issues"
    fi
    
    echo ""
    
    # Step 2: Sync skills
    log_step "2/2 Syncing skills..."
    if bash "$SCRIPT_DIR/sync_skills.sh"; then
        log_info "✅ Skills sync completed"
    else
        log_info "⚠️  Skills sync had issues"
    fi
    
    log ""
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log "✅ Full sync completed - $(date '+%Y-%m-%d %H:%M:%S')"
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

main "$@"
