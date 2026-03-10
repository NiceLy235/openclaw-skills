#!/bin/bash
# Setup GitHub remote and push skills

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  OpenClaw Skills - GitHub 推送工具"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$WORKSPACE_DIR"

# 显示当前 skills
echo "📦 当前 Skills:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "skills" ]; then
    for skill_dir in skills/*/; do
        if [ -f "$skill_dir/SKILL.md" ]; then
            skill_name=$(basename "$skill_dir")
            echo "  ✅ $skill_name"
        fi
    done
else
    echo "  ⚠️  未找到 skills 目录"
    exit 1
fi

echo ""
echo "📊 Git 状态:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git log --oneline -3
echo ""

# 检查 remote
if git remote | grep -q "origin"; then
    echo "✅ 已配置 remote:"
    git remote -v | grep origin
    echo ""
    
    read -p "是否推送到现有的 remote? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        REPO_URL=$(git remote get-url origin)
    else
        read -p "输入新的 GitHub 仓库 URL: " REPO_URL
        if [ -n "$REPO_URL" ]; then
            git remote set-url origin "$REPO_URL"
            echo "✅ Remote 已更新"
        else
            echo "❌ 未提供 URL"
            exit 1
        fi
    fi
else
    echo "⚠️  未配置 remote"
    echo ""
    echo "请提供 GitHub 仓库 URL:"
    echo ""
    echo "方式 1 - HTTPS (推荐，需要 Personal Access Token):"
    echo "  https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo ""
    echo "方式 2 - SSH (需要 SSH keys):"
    echo "  git@github.com:YOUR_USERNAME/YOUR_REPO.git"
    echo ""
    read -p "GitHub 仓库 URL: " REPO_URL
    
    if [ -z "$REPO_URL" ]; then
        echo "❌ 未提供 URL"
        echo ""
        echo "💡 建议:"
        echo "  1. 在 GitHub 创建新仓库: https://github.com/new"
        echo "     仓库名建议: openclaw-skills 或 openclaw-workspace"
        echo "  2. 复制仓库 URL 并重新运行此脚本"
        exit 1
    fi
    
    git remote add origin "$REPO_URL"
    echo "✅ Remote 已添加"
fi

echo ""
echo "🌐 检查网络连接..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查是否需要代理
if ss -tlnp 2>/dev/null | grep -q ":10809"; then
    echo "✅ 检测到 V2Ray HTTP 代理"
    export HTTP_PROXY="http://127.0.0.1:10809"
    export HTTPS_PROXY="http://127.0.0.1:10809"
    
    # 配置 git 使用代理
    git config --local http.proxy http://127.0.0.1:10809
    git config --local https.proxy http://127.0.0.1:10809
    echo "✅ Git 代理已配置"
else
    echo "⚠️  未检测到 V2Ray 代理"
    echo "   如果推送失败，请先启动 V2Ray: systemctl start v2ray"
fi

# 测试连接
echo ""
if [[ "$REPO_URL" == https://* ]]; then
    echo "测试 HTTPS 连接..."
    if curl -x "${HTTPS_PROXY:-}" -s --connect-timeout 5 -I https://github.com 2>&1 | grep -q "HTTP"; then
        echo "✅ GitHub 可访问"
    else
        echo "⚠️  GitHub 连接测试失败"
    fi
elif [[ "$REPO_URL" == git@* ]]; then
    echo "测试 SSH 连接..."
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "✅ SSH 认证成功"
    else
        echo "⚠️  SSH 认证失败，请检查 SSH keys 配置"
    fi
fi

echo ""
echo "🚀 推送到 GitHub..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 获取当前分支
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "分支: $BRANCH"
echo ""

# 推送
if git push -u origin "$BRANCH" 2>&1; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ 推送成功！"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🌐 查看仓库:"
    echo "  $(echo "$REPO_URL" | sed 's/\.git$//' | sed 's/git@github.com:/https:\/\/github.com\//')"
    echo ""
    echo "📚 已推送内容:"
    echo "  - Skills: env-setup (v2.0), lerobot-auto-train"
    echo "  - Daily Memory System"
    echo "  - 所有配置和文档"
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ 推送失败"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "常见问题和解决方案:"
    echo ""
    echo "1. 认证失败 (HTTPS)"
    echo "   解决: 使用 Personal Access Token"
    echo "   URL 格式: https://TOKEN@github.com/USERNAME/REPO.git"
    echo "   创建 Token: https://github.com/settings/tokens"
    echo ""
    echo "2. 认证失败 (SSH)"
    echo "   解决: 配置 SSH keys"
    echo "   ssh-keygen -t ed25519 -C 'your@email.com'"
    echo "   添加到 GitHub: https://github.com/settings/keys"
    echo ""
    echo "3. 网络超时"
    echo "   解决: 启动 V2Ray 代理"
    echo "   systemctl start v2ray"
    echo "   重新运行此脚本"
    echo ""
    echo "4. 仓库不存在"
    echo "   解决: 先在 GitHub 创建仓库"
    echo "   https://github.com/new"
    exit 1
fi
