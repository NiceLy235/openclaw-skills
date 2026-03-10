#!/bin/bash
# Check GitHub sync status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
MEMORY_DIR="$HOME/.openclaw/memory"
LOG_FILE="$HOME/.openclaw/github_sync.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  GitHub Sync Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Proxy status
echo -e "${BLUE}🌐 Proxy Status:${NC}"
if ss -tlnp 2>/dev/null | grep -q ":10809"; then
    echo -e "  ✅ V2Ray HTTP proxy: Running (port 10809)"
elif ss -tlnp 2>/dev/null | grep -q ":10808"; then
    echo -e "  ✅ V2Ray SOCKS5 proxy: Running (port 10808)"
else
    echo -e "  ⚠️  V2Ray proxy: Not running"
fi
echo ""

# Memory repository status
echo -e "${BLUE}📦 Memory Repository:${NC}"
if [ -d "$MEMORY_DIR/.git" ]; then
    cd "$MEMORY_DIR"
    echo -e "  ✅ Location: $MEMORY_DIR"
    
    if git remote | grep -q "origin"; then
        local remote_url=$(git remote get-url origin 2>/dev/null)
        echo -e "  ✅ Remote: $remote_url"
        
        # Check for uncommitted changes
        if ! git diff-index --quiet HEAD -- 2>/dev/null; then
            local files=$(git status --short | wc -l)
            echo -e "  ⚠️  Uncommitted changes: $files files"
        else
            echo -e "  ✅ No uncommitted changes"
        fi
        
        # Last commit
        local last_commit=$(git log -1 --format="%h - %s (%ar)" 2>/dev/null)
        echo -e "  📅 Last commit: $last_commit"
    else
        echo -e "  ⚠️  Remote: Not configured"
    fi
else
    echo -e "  ⚠️  Not a git repository"
fi
echo ""

# Skills repository status
echo -e "${BLUE}📚 Skills Repository:${NC}"
cd "$WORKSPACE_DIR"
echo -e "  ✅ Location: $WORKSPACE_DIR"

if git remote | grep -q "origin"; then
    local remote_url=$(git remote get-url origin 2>/dev/null | sed 's/https:\/\/[^@]*@/https:\/\//')
    echo -e "  ✅ Remote: $remote_url"
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        local files=$(git status --short | wc -l)
        local skill_files=$(git status --short skills/ 2>/dev/null | wc -l)
        echo -e "  ⚠️  Uncommitted changes: $files files ($skill_files in skills)"
    else
        echo -e "  ✅ No uncommitted changes"
    fi
    
    # Last commit
    local last_commit=$(git log -1 --format="%h - %s (%ar)" 2>/dev/null)
    echo -e "  📅 Last commit: $last_commit"
else
    echo -e "  ⚠️  Remote: Not configured"
fi
echo ""

# Skills list
echo -e "${BLUE}📖 Available Skills:${NC}"
if [ -d "$WORKSPACE_DIR/skills" ]; then
    for skill_path in "$WORKSPACE_DIR/skills"/*/; do
        if [ -f "$skill_path/SKILL.md" ]; then
            local skill_name=$(basename "$skill_path")
            echo -e "  ✅ $skill_name"
        fi
    done
else
    echo -e "  ⚠️  No skills directory"
fi
echo ""

# Cron status
echo -e "${BLUE}⏰ Scheduled Tasks:${NC}"
if crontab -l 2>/dev/null | grep -q "github-sync"; then
    echo -e "  ✅ Cron jobs configured:"
    crontab -l 2>/dev/null | grep "github-sync" | while read line; do
        echo -e "    $line"
    done
else
    echo -e "  ⚠️  No cron jobs configured"
    echo -e "  Run setup: $SKILL_DIR/scripts/setup_repos.sh"
fi
echo ""

# Log file
echo -e "${BLUE}📝 Log File:${NC}"
if [ -f "$LOG_FILE" ]; then
    local log_size=$(du -h "$LOG_FILE" | cut -f1)
    local log_lines=$(wc -l < "$LOG_FILE")
    echo -e "  ✅ Location: $LOG_FILE"
    echo -e "  📊 Size: $log_size ($log_lines lines)"
    echo -e "  📅 Last 3 entries:"
    tail -3 "$LOG_FILE" | sed 's/^/    /'
else
    echo -e "  ⚠️  No log file yet"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Quick actions
echo -e "${BLUE}🚀 Quick Actions:${NC}"
echo "  Sync memory:  $SKILL_DIR/scripts/sync_memory.sh"
echo "  Sync skills:  $SKILL_DIR/scripts/sync_skills.sh"
echo "  Sync all:     $SKILL_DIR/scripts/sync_all.sh"
echo "  View logs:    tail -f $LOG_FILE"
echo ""
