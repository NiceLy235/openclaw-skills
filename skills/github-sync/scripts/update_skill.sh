#!/bin/bash
# Update skill and auto-sync to GitHub
#
# Usage:
#   ./update_skill.sh <skill_name> "commit message"
#   ./update_skill.sh env-setup "Add Python 3.12 support"
#
# This script:
# 1. Commits skill changes
# 2. Syncs to GitHub immediately
# 3. Sends real-time progress updates

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_DIR="$(cd "$SKILL_DIR/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <skill_name> \"commit message\""
    echo ""
    echo "Examples:"
    echo "  $0 env-setup \"Add Python 3.12 support\""
    echo "  $0 lerobot-auto-train \"Fix dependency conflicts\""
    echo "  $0 github-sync \"Add new sync feature\""
    exit 1
fi

SKILL_NAME="$1"
COMMIT_MSG="$2"

# Validate skill exists
if [ ! -d "$WORKSPACE_DIR/skills/$SKILL_NAME" ]; then
    echo -e "${YELLOW}⚠️  Skill not found: $SKILL_NAME${NC}"
    echo "Available skills:"
    ls -1 "$WORKSPACE_DIR/skills/" | grep -v "^\."
    exit 1
fi

# Function to send message
send_message() {
    local msg="$1"
    if command -v openclaw-message &> /dev/null; then
        openclaw-message send "$msg" 2>/dev/null || true
    fi
    echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $msg"
}

# Start
send_message "🔄 开始更新 skill: $SKILL_NAME"

cd "$WORKSPACE_DIR"

# Check for changes
if git diff-index --quiet HEAD -- "skills/$SKILL_NAME" 2>/dev/null; then
    send_message "⚠️  没有检测到 $SKILL_NAME 的更改"
    exit 0
fi

# Show changes
CHANGED_FILES=$(git status --short "skills/$SKILL_NAME" | wc -l)
send_message "📝 检测到 $CHANGED_FILES 个文件更改"

# Commit changes
send_message "💾 正在提交更改..."
git add "skills/$SKILL_NAME"
git commit -m "$COMMIT_MSG" > /dev/null 2>&1
send_message "✅ 已提交: $COMMIT_MSG"

# Sync to GitHub
send_message "🚀 正在同步到 GitHub..."
bash "$SCRIPT_DIR/sync_skills.sh"

# Done
send_message "🎉 Skill 更新并同步完成！"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Skill 更新完成${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Skill: $SKILL_NAME"
echo "  Commit: $COMMIT_MSG"
echo "  Files: $CHANGED_FILES changed"
echo "  Status: Synced to GitHub ✅"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
