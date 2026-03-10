#!/bin/bash
# Setup GitHub authentication for daily memory sync
#
# This script helps configure GitHub authentication for automatic pushes.

set -e

MEMORY_DIR="${HOME}/.openclaw/memory"
CONFIG_FILE="${MEMORY_DIR}/../workspace/daily_summary/config.json"

echo "🔐 GitHub Authentication Setup"
echo "================================"
echo ""
echo "This script will help you configure GitHub authentication for automatic pushes."
echo ""

# Check if token is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <GITHUB_TOKEN>"
    echo ""
    echo "To get your GitHub Personal Access Token:"
    echo "1. Go to https://github.com/settings/tokens"
    echo "2. Click 'Generate new token (classic)'"
    echo "3. Select scopes: repo (full control)"
    echo "4. Generate and copy the token"
    echo ""
    echo "Then run:"
    echo "  $0 YOUR_TOKEN_HERE"
    exit 1
fi

TOKEN="$1"
REPO_OWNER="NiceLy235"
REPO_NAME="training-memories"

echo "📦 Configuring repository..."
cd "$MEMORY_DIR"

# Update remote URL with token
REMOTE_URL="https://${TOKEN}@github.com/${REPO_OWNER}/${REPO_NAME}.git"
git remote set-url origin "$REMOTE_URL"

echo "✅ Remote URL updated with authentication"
echo ""

# Test push
echo "🧪 Testing push..."
if git push -u origin main; then
    echo ""
    echo "✅ SUCCESS! Authentication configured successfully."
    echo ""
    echo "📝 Your token is stored in the git remote URL."
    echo "   It will be used for all future pushes."
    echo ""
    echo "🚀 You can now run:"
    echo "   python3 daily_summary/scripts/daily_sync.py run"
    echo ""
    echo "⏰ To set up automatic daily sync, add to crontab:"
    echo "   0 23 * * * cd /root/.openclaw/workspace && /usr/bin/python3 daily_summary/scripts/daily_sync.py run"
else
    echo ""
    echo "❌ Push failed. Please check:"
    echo "   1. Your token is correct"
    echo "   2. Token has 'repo' scope"
    echo "   3. Repository exists: https://github.com/${REPO_OWNER}/${REPO_NAME}"
    echo ""
    echo "You can regenerate the token at:"
    echo "   https://github.com/settings/tokens"
    exit 1
fi
