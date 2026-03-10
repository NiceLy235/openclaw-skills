#!/bin/bash
# Push OpenClaw skills to GitHub

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"

echo "🚀 准备推送 Skills 到 GitHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$WORKSPACE_DIR"

# 检查是否已经有 remote
if git remote | grep -q "origin"; then
    echo "✅ Remote 'origin' 已存在"
    git remote -v | grep origin
else
    echo "❌ 未配置 remote 'origin'"
    echo ""
    echo "请提供 GitHub 仓库 URL："
    echo "  格式: https://github.com/USERNAME/REPO.git"
    echo "  或: git@github.com:USERNAME/REPO.git"
    echo ""
    read -p "GitHub 仓库 URL: " REPO_URL
    
    if [ -z "$REPO_URL" ]; then
        echo "❌ 未提供 URL，退出"
        exit 1
    fi
    
    git remote add origin "$REPO_URL"
    echo "✅ Remote 已添加: $REPO_URL"
fi

echo ""
echo "📊 当前状态:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git log --oneline -5
echo ""
echo "Skills 目录:"
ls -1 skills/
echo ""

# 检查是否有未提交的更改
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  有未提交的更改:"
    git status --short
    echo ""
    read -p "是否先提交这些更改? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add -A
        git commit -m "chore: Auto-commit before push"
    else
        echo "❌ 请先提交更改后再推送"
        exit 1
    fi
fi

echo ""
echo "🚀 开始推送到 GitHub..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 获取当前分支
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "分支: $BRANCH"
echo ""

# 推送
if git push -u origin "$BRANCH"; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ 推送成功！"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📚 已推送的 Skills:"
    echo "  - env-setup (v2.0 - 增强版)"
    echo "  - lerobot-auto-train"
    echo ""
    echo "🌐 GitHub 仓库:"
    git remote get-url origin | sed 's/\.git$//' | sed 's/git@github.com:/https:\/\/github.com\//'
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ 推送失败"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "可能的原因:"
    echo "  1. 需要配置 SSH keys"
    echo "  2. 需要配置 Git 凭据"
    echo "  3. 仓库不存在"
    echo ""
    echo "解决方案:"
    echo "  - HTTPS: 需要 GitHub Personal Access Token"
    echo "  - SSH: 需要配置 SSH keys"
    exit 1
fi
