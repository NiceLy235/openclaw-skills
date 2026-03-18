#!/bin/bash
# Check proxy configuration and HuggingFace connectivity
# Usage: bash scripts/check_proxy.sh

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 代理和网络连接检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Step 1: Check environment variables
echo ""
echo "### Step 1: 检查代理环境变量"
echo ""

PROXY_SET=0

if [ -n "$HTTP_PROXY" ]; then
    echo "✅ HTTP_PROXY: $HTTP_PROXY"
    PROXY_SET=1
else
    echo "❌ HTTP_PROXY: 未设置"
fi

if [ -n "$HTTPS_PROXY" ]; then
    echo "✅ HTTPS_PROXY: $HTTPS_PROXY"
    PROXY_SET=1
else
    echo "❌ HTTPS_PROXY: 未设置"
fi

if [ -n "$ALL_PROXY" ]; then
    echo "✅ ALL_PROXY: $ALL_PROXY"
    PROXY_SET=1
else
    echo "❌ ALL_PROXY: 未设置"
fi

if [ $PROXY_SET -eq 0 ]; then
    echo ""
    echo "⚠️  警告：未检测到代理环境变量"
    echo ""
    echo "建议设置："
    echo "  export HTTP_PROXY=http://127.0.0.1:10809"
    echo "  export HTTPS_PROXY=http://127.0.0.1:10809"
    echo ""
    read -p "是否现在设置？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        export HTTP_PROXY=http://127.0.0.1:10809
        export HTTPS_PROXY=http://127.0.0.1:10809
        export ALL_PROXY=socks5://127.0.0.1:10808
        echo "✅ 代理已设置"
    else
        echo "❌ 继续检查（可能无法访问 HuggingFace）"
    fi
fi

# Step 2: Check v2ray service
echo ""
echo "### Step 2: 检查 v2ray 服务"
echo ""

if command -v systemctl &> /dev/null; then
    # Linux with systemd
    if systemctl is-active --quiet v2ray; then
        echo "✅ v2ray 服务运行中"
        systemctl status v2ray --no-pager -l | grep -E "(Active|Main PID)" | head -2
    else
        echo "❌ v2ray 服务未运行"
        echo ""
        read -p "是否启动 v2ray？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo systemctl start v2ray
            echo "✅ v2ray 已启动"
        fi
    fi
else
    # Container or macOS without systemd
    if pgrep -f "v2ray" > /dev/null; then
        echo "✅ v2ray 进程运行中"
        ps aux | grep v2ray | grep -v grep | head -1
    else
        echo "❌ v2ray 进程未运行"
        echo ""
        echo "手动启动命令："
        echo "  nohup /usr/local/bin/v2ray run -c /etc/v2ray/config.json > /tmp/v2ray.log 2>&1 &"
    fi
fi

# Step 3: Test proxy connectivity
echo ""
echo "### Step 3: 测试代理连接"
echo ""

echo "测试 HuggingFace..."
HF_RESULT=$(curl -x http://127.0.0.1:10809 -I -m 10 -s https://huggingface.co | head -1)

if echo "$HF_RESULT" | grep -q "200"; then
    echo "✅ HuggingFace: 可访问"
    echo "   $HF_RESULT"
else
    echo "❌ HuggingFace: 无法访问"
    echo "   $HF_RESULT"
fi

echo ""
echo "测试 Google..."
GOOGLE_RESULT=$(curl -x socks5://127.0.0.1:10808 -I -m 10 -s https://www.google.com | head -1)

if echo "$GOOGLE_RESULT" | grep -q "200"; then
    echo "✅ Google: 可访问"
    echo "   $GOOGLE_RESULT"
else
    echo "❌ Google: 无法访问（但不影响 HuggingFace）"
    echo "   $GOOGLE_RESULT"
fi

# Step 4: Final summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 检查结果总结"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if echo "$HF_RESULT" | grep -q "200"; then
    echo "✅ 网络连接正常，可以开始训练"
    echo ""
    echo "现在可以执行："
    echo "  python scripts/task_manager.py submit ..."
    exit 0
else
    echo "❌ 网络连接失败，无法访问 HuggingFace"
    echo ""
    echo "故障排查步骤："
    echo "1. 检查 v2ray 服务是否运行"
    echo "2. 检查代理环境变量是否设置"
    echo "3. 检查 v2ray 配置文件是否正确"
    echo "4. 检查防火墙是否阻止连接"
    echo ""
    echo "不要开始训练任务，否则会因无法下载模型而失败！"
    exit 1
fi
