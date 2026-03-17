#!/bin/bash

# ============================================================================
# 飞书连接智能监控脚本 v3.0（事件驱动版）
# ============================================================================
# 改进：
# 1. 理解飞书 WebSocket 的事件驱动特性
# 2. 不在空闲时误判为断开
# 3. 只在配置错误或真正无法响应时报警
# 4. 记录连接模式为"事件驱动"
# ============================================================================

LOG_FILE="/tmp/feishu_smart_monitor.log"
STATE_FILE="/tmp/feishu_state.json"
NOTIFICATION_FILE="/tmp/feishu_notifications.txt"

log() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

send_notification() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$NOTIFICATION_FILE"
    log "NOTIFY" "$message"
}

read_state() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE"
    else
        echo '{"restart_attempts":0,"last_restart":0,"last_check":0,"config":"unknown","mode":"event-driven"}'
    fi
}

save_state() {
    local state="$1"
    echo "$state" > "$STATE_FILE"
}

# 检查配置是否正确
check_feishu_config() {
    local config_ok=true

    # 检查是否启用
    if ! grep -q '"enabled": true' ~/.openclaw/openclaw.json 2>/dev/null; then
        config_ok=false
    fi

    # 检查 AppID
    if ! grep -q 'cli_a9238f9673b99cc1' ~/.openclaw/openclaw.json 2>/dev/null; then
        config_ok=false
    fi

    # 检查 AppSecret
    if ! grep -q 'appSecret' ~/.openclaw/openclaw.json 2>/dev/null; then
        config_ok=false
    fi

    if [ "$config_ok" = true ]; then
        echo "OK"
    else
        echo "ERROR"
    fi
}

# 检查 Gateway 进程
check_gateway_process() {
    if pgrep -f "openclaw-gateway" > /dev/null; then
        echo "RUNNING"
    else
        echo "STOPPED"
    fi
}

# 检查 Channels 状态
check_channels_status() {
    local status_output
    status_output=$(openclaw status 2>&1 | grep -A 2 "│ Feishu" | head -3)

    if echo "$status_output" | grep -q "ON"; then
        echo "ON"
    else
        echo "OFF"
    fi
}

# 测试飞书 API 连通性
test_feishu_api() {
    local response
    response=$(curl -s https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
        -H "Content-Type: application/json" \
        -d '{"app_id":"cli_a9238f9673b99cc1","app_secret":"JIbTScQNcCntGZXC226mOfiMbMJlbinf"}' 2>/dev/null)

    if echo "$response" | grep -q '"code":0'; then
        echo "OK"
    else
        echo "ERROR"
    fi
}

# 主监控逻辑
main() {
    log "INFO" "====== 开始智能监控检查（事件驱动模式） ======"

    # 读取当前状态
    local current_state
    current_state=$(read_state)

    local restart_attempts=$(echo "$current_state" | jq -r '.restart_attempts // 0')
    local last_restart=$(echo "$current_state" | jq -r '.last_restart // 0')
    local current_time=$(date +%s)

    # 检查各项状态
    local config_status
    config_status=$(check_feishu_config)
    log "INFO" "配置状态: $config_status"

    local gateway_status
    gateway_status=$(check_gateway_process)
    log "INFO" "Gateway 进程: $gateway_status"

    local channels_status
    channels_status=$(check_channels_status)
    log "INFO" "Channels 状态: $channels_status"

    local api_status
    api_status=$(test_feishu_api)
    log "INFO" "飞书 API: $api_status"

    # 更新状态
    local new_state=$(cat <<EOF
{
    "restart_attempts": $restart_attempts,
    "last_restart": $last_restart,
    "last_check": $current_time,
    "config": "$config_status",
    "gateway": "$gateway_status",
    "channels": "$channels_status",
    "api": "$api_status",
    "mode": "event-driven",
    "note": "飞书 WebSocket 是事件驱动的，空闲时断开是正常行为"
}
EOF
)

    # 判断逻辑（基于事件驱动模式）
    local overall_status="OK"

    # 1. 检查配置
    if [ "$config_status" != "OK" ]; then
        overall_status="ERROR"
        send_notification "ERROR" "❌ 飞书配置错误，请检查 AppID 和 AppSecret"
    fi

    # 2. 检查 Gateway 进程
    if [ "$gateway_status" != "RUNNING" ]; then
        overall_status="ERROR"
        send_notification "ERROR" "❌ Gateway 进程未运行，尝试启动..."

        # 启动 Gateway
        nohup openclaw-gateway > /tmp/gateway-auto-start-$(date +%s).log 2>&1 &
        sleep 5

        if [ "$(check_gateway_process)" = "RUNNING" ]; then
            send_notification "SUCCESS" "✅ Gateway 已自动启动"
        else
            send_notification "ERROR" "❌ Gateway 启动失败，需要手动干预"
        fi
    fi

    # 3. 检查飞书 API 连通性
    if [ "$api_status" != "OK" ]; then
        overall_status="WARN"
        send_notification "WARN" "⚠️ 飞书 API 连接失败，可能是网络问题"
    fi

    # 4. 检查 Channels 状态（不是 Health，因为 Health 是事件驱动的）
    if [ "$channels_status" != "ON" ]; then
        overall_status="ERROR"
        send_notification "ERROR" "❌ Channels 配置错误，飞书通道未启用"
    fi

    # 总结
    if [ "$overall_status" = "OK" ]; then
        log "INFO" "✅ 所有检查通过（事件驱动模式）"
        log "INFO" "💡 提示：Health 显示 OFF 是正常的，因为 WebSocket 是事件驱动的"
    else
        log "WARN" "⚠️ 发现问题：$overall_status"
    fi

    # 保存状态
    save_state "$new_state"
    log "INFO" "检查完成"
}

# 执行主函数
main "$@"
