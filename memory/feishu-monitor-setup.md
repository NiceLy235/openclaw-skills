# 飞书 WebSocket 连接监控设置

## 📋 监控配置

### 1. 监控脚本
- **位置**: `/root/.openclaw/workspace/scripts/monitor_feishu_connection.sh`
- **功能**:
  - 检查飞书连接状态
  - 自动检测连接断开
  - 自动重启 Gateway
  - 记录状态变化
  - 发送通知

### 2. 定时任务
- **方式 1**: Cron 任务（每 3 分钟）
  ```bash
  */3 * * * * /root/.openclaw/workspace/scripts/monitor_feishu_connection.sh
  ```

- **方式 2**: OpenClaw Cron（每 5 分钟）
  - 任务 ID: `3aff9160-3af5-4267-9440-68e80ca850d8`
  - 名称: `monitor-feishu-connection`

### 3. 日志文件
- **监控日志**: `/tmp/feishu_monitor.log`
- **通知记录**: `/tmp/feishu_notifications.txt`
- **状态文件**: `/tmp/feishu_last_state`

---

## 🎯 监控流程

```
每 3 分钟执行一次
    ↓
检查飞书连接状态 (Health: ON/OFF)
    ↓
状态变化？
    ├─ OFF → 发送通知 "⚠️ 连接断开"
    │         ↓
    │       自动重启 Gateway
    │         ↓
    │       再次检查状态
    │         ├─ ON → 发送 "✅ 已恢复"
    │         └─ OFF → 发送 "❌ 需要手动干预"
    │
    └─ ON (之前是 OFF) → 发送 "✅ 已恢复"
```

---

## 📊 查看监控状态

### 查看日志
```bash
tail -f /tmp/feishu_monitor.log
```

### 查看通知
```bash
cat /tmp/feishu_notifications.txt
```

### 查看当前状态
```bash
cat /tmp/feishu_last_state
```

### 手动执行检查
```bash
bash /root/.openclaw/workspace/scripts/monitor_feishu_connection.sh
```

---

## 🔧 配置调整

### 修改检查频率
```bash
# 每 1 分钟检查一次
* * * * * /root/.openclaw/workspace/scripts/monitor_feishu_connection.sh

# 每 5 分钟检查一次
*/5 * * * * /root/.openclaw/workspace/scripts/monitor_feishu_connection.sh
```

### 禁用自动重启
编辑脚本，注释掉 `auto_recover` 函数调用。

---

## ⚠️ 注意事项

1. **首次运行**: 会创建状态文件，不会触发通知
2. **自动重启**: 最多尝试 1 次，失败后需要手动干预
3. **通知方式**: 当前写入文件，可以扩展为发送到其他渠道
4. **日志轮转**: 需要定期清理日志文件

---

## 🚀 扩展建议

### 添加邮件通知
```bash
send_notification() {
    local message="$1"
    echo "$message" | mail -s "飞书机器人状态" your@email.com
}
```

### 添加飞书通知
```bash
send_notification() {
    local message="$1"
    curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK" \
         -H "Content-Type: application/json" \
         -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"$message\"}}"
}
```

### 添加企业微信通知
```bash
send_notification() {
    local message="$1"
    curl -X POST "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY" \
         -H "Content-Type: application/json" \
         -d "{\"msgtype\":\"text\",\"text\":{\"content\":\"$message\"}}"
}
```

---

**设置时间**: 2026-03-13 16:56
**下次检查**: 2026-03-13 16:59 (3 分钟后)
