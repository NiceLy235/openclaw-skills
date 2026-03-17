#!/bin/bash

# 飞书 WebSocket 连接监控脚本
# 用途：定期检查飞书连接状态，断开时发送通知

LOG_FILE="/tmp/feishu_monitor.log"
LAST_STATE_FILE="/tmp/feishu_last_state"
NOTIFICATION_FILE="/tmp/feishu_notifications.txt"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查飞书连接状态（检查健康状态）
check_feishu_status() {
    local status_output
    status_output=$(openclaw status --deep 2>&1 | grep -A 3 "│ Feishu")
    
    # 检查 Health 部分的 Feishu 状态
    if echo "$status_output" | grep -q "OFF"; then
        echo "OFF"
    elif echo "$status_output" | grep -q "ON"; then
        echo "ON"
    else
        echo "UNKNOWN"
    fi
}

# 发送通知
send_notification() {
    local message="$1"
    log "发送通知: $message"
    
    # 写入通知文件
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message" >> "$NOTIFICATION_FILE"
    
    # 尝试通过 message 工具发送（如果可用）
    # 这里可以添加发送到其他渠道的逻辑
}

# 自动恢复函数
auto_recover() {
    log "开始自动恢复流程"
    
    # 1. 杀掉旧的 Gateway
    pkill -9 -f openclaw-gateway
    sleep 2
    
    # 2. 启动新的 Gateway
    nohup openclaw-gateway > /tmp/gateway-auto-restart-$(date +%s).log 2>&1 &
    sleep 5
    
    # 3. 再次检查状态
    local new_state
    new_state=$(check_feishu_status)
    
    if [ "$new_state" = "ON" ]; then
        send_notification "✅ Gateway 已自动重启，飞书连接已恢复"
        return 0
    else
        send_notification "❌ Gateway 自动重启失败，连接状态: $new_state，需要手动干预"
        return 1
    fi
}

# 主函数
main() {
    log "====== 开始检查飞书连接状态 ======"
    
    # 获取当前状态
    local current_state
    current_state=$(check_feishu_status)
    log "当前状态: $current_state"
    
    # 读取上次状态
    local last_state="UNKNOWN"
    if [ -f "$LAST_STATE_FILE" ]; then
        last_state=$(cat "$LAST_STATE_FILE")
    fi
    log "上次状态: $last_state"
    
    # 状态变化检测和处理
    if [ "$current_state" = "OFF" ]; then
        log "⚠️ 检测到飞书连接断开"
        
        # 如果之前是 ON 或 UNKNOWN，说明刚刚断开
        if [ "$last_state" = "ON" ] || [ "$last_state" = "UNKNOWN" ]; then
            send_notification "⚠️ 飞书 WebSocket 连接已断开，正在尝试自动恢复..."
        fi
        
        # 尝试自动恢复
        auto_recover
        
    elif [ "$current_state" = "ON" ] && [ "$last_state" = "OFF" ]; then
        # 状态从 OFF -> ON，发送恢复通知
        send_notification "✅ 飞书 WebSocket 连接已自动恢复"
    fi
    
    # 保存当前状态
    echo "$current_state" > "$LAST_STATE_FILE"
    
    log "检查完成"
}

# 执行主函数
main
