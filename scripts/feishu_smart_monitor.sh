#!/bin/bash

# ============================================================================
# 飞书 WebSocket 连接智能监控脚本 v2.0
# ============================================================================
# 改进：
# 1. 最多尝试重启1次，避免死循环
# 2. 检查间隔10分钟，减少误判
# 3. 智能判断配置问题 vs 连接问题
# 4. 添加冷却期，避免频繁操作
# 5. 多种通知方式
# 6. 详细的状态跟踪
# ============================================================================

# 配置项
LOG_FILE="/tmp/feishu_smart_monitor.log"
STATE_FILE="/tmp/feishu_state.json"
NOTIFICATION_FILE="/tmp/feishu_notifications.txt"
MAX_RESTART_ATTEMPTS=1           # 最多重启次数
COOLDOWN_MINUTES=30              # 冷却期（分钟）
CHECK_INTERVAL_MINUTES=10        # 检查间隔（分钟）

# 日志函数
log() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

# 发送通知
send_notification() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # 记录到通知文件
    echo "[$timestamp] [$level] $message" >> "$NOTIFICATION_FILE"

    # 可以扩展为其他通知方式
    # 例如：邮件、企业微信、钉钉等

    log "NOTIFY" "$message"
}

# 读取状态
read_state() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE"
    else
        echo '{"restart_attempts":0,"last_restart":0,"last_check":0,"status":"unknown"}'
    fi
}

# 保存状态
save_state() {
    local state="$1"
    echo "$state" > "$STATE_FILE"
}

# 检查飞书连接状态
check_feishu_connection() {
    local status_output
    status_output=$(openclaw status --deep 2>&1 | grep -A 2 "Feishu" | grep -E "ON|OFF")

    if echo "$status_output" | grep -q "ON"; then
        echo "ON"
    else
        echo "OFF"
    fi
}

# 检查配置是否正确
check_feishu_config() {
    local config_ok=true

    # 检查配置文件
    if ! grep -q '"enabled": true' ~/.openclaw/openclaw.json 2>/dev/null; then
        config_ok=false
    fi

    # 检查 AppID
    if ! grep -q 'cli_a9238f9673b99cc1' ~/.openclaw/openclaw.json 2>/dev/null; then
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

# 重启 Gateway
restart_gateway() {
    log "ACTION" "开始重启 Gateway..."

    # 杀掉旧进程
    pkill -9 -f openclaw-gateway
    sleep 2

    # 启动新进程
    nohup openclaw-gateway > /tmp/gateway-restart-$(date +%s).log 2>&1 &
    sleep 10

    # 检查是否成功启动
    if [ "$(check_gateway_process)" = "RUNNING" ]; then
        log "ACTION" "Gateway 重启成功"
        return 0
    else
        log "ERROR" "Gateway 重启失败"
        return 1
    fi
}

# 主监控逻辑
main() {
    log "INFO" "====== 开始智能监控检查 ======"

    # 读取当前状态
    local current_state
    current_state=$(read_state)

    local restart_attempts=$(echo "$current_state" | jq -r '.restart_attempts // 0')
    local last_restart=$(echo "$current_state" | jq -r '.last_restart // 0')
    local current_time=$(date +%s)

    # 检查连接状态
    local connection_status
    connection_status=$(check_feishu_connection)
    log "INFO" "连接状态: $connection_status"

    # 检查配置
    local config_status
    config_status=$(check_feishu_config)
    log "INFO" "配置状态: $config_status"

    # 检查 Gateway 进程
    local gateway_status
    gateway_status=$(check_gateway_process)
    log "INFO" "Gateway 进程: $gateway_status"

    # 更新状态
    local new_state=$(cat <<EOF
{
    "restart_attempts": $restart_attempts,
    "last_restart": $last_restart,
    "last_check": $current_time,
    "status": "$connection_status",
    "config": "$config_status",
    "gateway": "$gateway_status"
}
EOF
)

    # 如果连接正常，重置计数器
    if [ "$connection_status" = "ON" ]; then
        if [ $restart_attempts -gt 0 ]; then
            send_notification "SUCCESS" "✅ 飞书连接已恢复正常"
        fi
        new_state=$(echo "$new_state" | jq '.restart_attempts = 0')
        save_state "$new_state"
        log "INFO" "连接正常，监控结束"
        return 0
    fi

    # 如果连接断开
    if [ "$connection_status" = "OFF" ]; then
        log "WARN" "检测到飞书连接断开"

        # 检查是否在冷却期内
        local cooldown_seconds=$((COOLDOWN_MINUTES * 60))
        local time_since_restart=$((current_time - last_restart))

        if [ $time_since_restart -lt $cooldown_seconds ]; then
            local remaining=$((cooldown_seconds - time_since_restart))
            log "INFO" "在冷却期内，跳过重启（剩余 ${remaining} 秒）"
            save_state "$new_state"
            return 0
        fi

        # 检查是否超过重启次数限制
        if [ $restart_attempts -ge $MAX_RESTART_ATTEMPTS ]; then
            send_notification "ERROR" "❌ 已达到最大重启次数 ($MAX_RESTART_ATTEMPTS)，需要手动干预"
            log "ERROR" "已达到最大重启次数，停止自动重启"
            save_state "$new_state"
            return 1
        fi

        # 检查配置是否正确
        if [ "$config_status" != "OK" ]; then
            send_notification "ERROR" "❌ 飞书配置错误，无法自动修复"
            log "ERROR" "配置错误，请检查飞书应用配置"
            save_state "$new_state"
            return 1
        fi

        # 检查 Gateway 进程
        if [ "$gateway_status" != "RUNNING" ]; then
            log "WARN" "Gateway 进程未运行"
        fi

        # 尝试重启
        send_notification "WARN" "⚠️ 检测到飞书连接断开，尝试自动恢复..."

        if restart_gateway; then
            # 重启成功，更新状态
            new_state=$(echo "$new_state" | jq --arg time "$current_time" '.restart_attempts += 1 | .last_restart = ($time | tonumber)')
            save_state "$new_state"

            # 等待连接恢复
            sleep 15

            # 再次检查
            local new_connection_status
            new_connection_status=$(check_feishu_connection)

            if [ "$new_connection_status" = "ON" ]; then
                send_notification "SUCCESS" "✅ Gateway 重启成功，飞书连接已恢复"
                new_state=$(echo "$new_state" | jq '.restart_attempts = 0 | .status = "ON"')
                save_state "$new_state"
                return 0
            else
                send_notification "WARN" "⚠️ Gateway 已重启，但飞书连接仍未恢复（尝试 $((restart_attempts + 1))/$MAX_RESTART_ATTEMPTS）"
                new_state=$(echo "$new_state" | jq '.status = "OFF"')
                save_state "$new_state"
                return 1
            fi
        else
            send_notification "ERROR" "❌ Gateway 重启失败，需要手动干预"
            new_state=$(echo "$new_state" | jq '.restart_attempts += 1')
            save_state "$new_state"
            return 1
        fi
    fi

    log "INFO" "监控检查完成"
    save_state "$new_state"
}

# 执行主函数
main "$@"
