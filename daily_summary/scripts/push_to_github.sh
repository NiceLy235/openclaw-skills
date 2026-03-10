#!/bin/bash
# Push memory to GitHub
#
# Usage:
#   ./push_to_github.sh [--date YYYY-MM-DD]

set -e

# Configuration
MEMORY_DIR="${HOME}/.openclaw/memory"
CONFIG_FILE="${MEMORY_DIR}/../daily_summary/config.json"
DATE="${1:-$(date +%Y-%m-%d)}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configure git proxy (uses V2Ray HTTP proxy)
configure_proxy() {
    if ss -tlnp | grep -q ":10809"; then
        log_info "Configuring Git to use V2Ray proxy..."
        git config --local http.proxy http://127.0.0.1:10809
        git config --local https.proxy http://127.0.0.1:10809
    else
        log_warn "V2Ray proxy not detected on port 10809"
        log_warn "If push fails, check V2Ray status: systemctl status v2ray"
    fi
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    log_error "Git is not installed"
    exit 1
fi

# Check if memory directory exists
if [ ! -d "$MEMORY_DIR" ]; then
    log_error "Memory directory does not exist: $MEMORY_DIR"
    exit 1
fi

# Check if already a git repo
if [ ! -d "$MEMORY_DIR/.git" ]; then
    log_info "Initializing git repository..."
    cd "$MEMORY_DIR"
    git init

    # Read config
    if [ -f "$CONFIG_FILE" ]; then
        REPO_URL=$(jq -r '.github.repo_url' "$CONFIG_FILE")
        BRANCH=$(jq -r '.github.branch' "$CONFIG_FILE")

        log_info "Adding remote: $REPO_URL"
        git remote add origin "$REPO_URL"
    else
        log_warn "Config file not found, skipping remote setup"
    fi
fi

cd "$MEMORY_DIR"

# Configure proxy
configure_proxy

# Check if there are changes
if [ -z "$(git status --porcelain)" ]; then
    log_info "No changes to commit"
    exit 0
fi

# Add all changes
log_info "Adding changes..."
git add -A

# Create commit message
COMMIT_MSG="chore: Daily memory update - $DATE

- Updated conversations and interactions
- Generated daily summary
- Saved experiences and lessons learned"

log_info "Creating commit..."
git commit -m "$COMMIT_MSG"

# Push to GitHub
log_info "Pushing to GitHub..."

# Check if remote exists
if git remote | grep -q "origin"; then
    # Get current branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

    # Try to push
    if git push origin "$CURRENT_BRANCH" 2>&1; then
        log_info "✅ Successfully pushed to GitHub"
    else
        log_error "Failed to push. You may need to:"
        log_error "1. Set up SSH keys or credentials"
        log_error "2. Pull first if remote has changes"
        log_error "3. Check repository permissions"

        echo ""
        log_info "Your changes are committed locally. To push manually:"
        log_info "  cd $MEMORY_DIR"
        log_info "  git push origin $CURRENT_BRANCH"

        exit 1
    fi
else
    log_error "No remote configured. Please set up GitHub remote:"
    log_error "  cd $MEMORY_DIR"
    log_error "  git remote add origin <your-repo-url>"
    exit 1
fi

log_info "✅ Memory successfully synced to GitHub!"
