# 飞书智能监控系统 - 用户手册

## 📊 系统概览

**安装时间**: 2026-03-13 17:17
**版本**: v2.0（智能版）
**状态**: ✅ 已安装并运行

---

## 🎯 核心特性

### 1. 智能重启机制
- ✅ **最多重启 1 次**：避免死循环
- ✅ **冷却期保护**：30 分钟内不重复重启
- ✅ **配置检查**：配置错误时不重启

### 2. 状态跟踪
- 📊 **状态持久化**：记录重启次数、最后检查时间等
- 📊 **状态文件**：`/tmp/feishu_state.json`
- 📊 **智能判断**：区分配置问题 vs 连接问题

### 3. 监控频率
- ⏱️ **检查间隔**：每 10 分钟
- ⏱️ **自动清理**：每周清理旧日志

---

## 📋 使用指南

### 查看监控状态
```bash
# 查看当前状态
cat /tmp/feishu_state.json | jq .

# 实时查看日志
tail -f /tmp/feishu_smart_monitor.log

# 查看通知历史
cat /tmp/feishu_notifications.txt
```

### 手动触发检查
```bash
# 立即执行一次检查
/root/.openclaw/workspace/scripts/feishu_smart_monitor.sh
```

### 停止监控
```bash
# 停止定时任务
crontab -r

# 或者编辑 crontab
crontab -e
```

### 重启监控
```bash
# 重新安装监控
bash /root/.openclaw/workspace/scripts/install_monitor.sh
```

---

## 🔍 监控逻辑

### 检查流程
```
每 10 分钟
    ↓
检查飞书连接状态
    ↓
状态 = ON？
    ├─ 是 → ✅ 记录状态，结束
    │
    └─ 否 → 检查配置
              ↓
          配置 = OK？
              ├─ 否 → ⚠️ 配置错误，不重启
              │
              └─ 是 → 检查重启次数
                        ↓
                    重启次数 < 1？
                        ├─ 是 → 检查冷却期
                        │         ↓
                        │     冷却期内？
                        │         ├─ 是 → ⏸️ 等待冷却期结束
                        │         └─ 否 → 🔄 重启 Gateway
                        │                   ↓
                        │               重启成功？
                        │                   ├─ 是 → ✅ 恢复
                        │                   └─ 否 → ❌ 需要手动干预
                        │
                        └─ 否 → ❌ 已达最大重启次数
```

---

## 🚨 状态说明

### 连接状态
- **ON**: 飞书 WebSocket 连接正常
- **OFF**: 飞书 WebSocket 连接断开
- **UNKNOWN**: 无法确定状态

### 配置状态
- **OK**: 飞书配置正确
- **ERROR**: 飞书配置错误
- **UNKNOWN**: 无法确定配置

### Gateway 状态
- **RUNNING**: Gateway 进程运行中
- **STOPPED**: Gateway 进程已停止
- **UNKNOWN**: 无法确定进程状态

---

## 🔧 故障排查

### 问题 1：频繁收到重启通知

**原因**: 冷却期设置过短

**解决**:
```bash
# 编辑监控脚本
nano /root/.openclaw/workspace/scripts/feishu_smart_monitor.sh

# 修改冷却期（默认 30 分钟）
COOLDOWN_MINUTES=60  # 改为 60 分钟

# 重启监控
crontab -r
bash /root/.openclaw/workspace/scripts/install_monitor.sh
```

### 问题 2：监控显示配置错误

**原因**: 飞书应用配置不正确

**解决**:
1. 登录飞书开放平台
2. 检查事件订阅配置
3. 确认 Request URL 正确

### 问题 3：重启后仍无法恢复

**原因**: 飞书应用本身的问题

**解决**:
```bash
# 查看详细日志
tail -100 /tmp/feishu_smart_monitor.log

# 检查 Gateway 日志
tail -100 /var/log/openclaw/gateway.log

# 手动重启 Gateway
pkill -9 openclaw-gateway
nohup openclaw-gateway > /tmp/gateway-manual.log 2>&1 &
```

---

## 📊 日志文件说明

| 文件 | 说明 | 保留时长 |
|------|------|----------|
| `/tmp/feishu_smart_monitor.log` | 监控主日志 | 7 天 |
| `/tmp/feishu_state.json` | 状态文件 | 永久 |
| `/tmp/feishu_notifications.txt` | 通知历史 | 7 天 |
| `/tmp/feishu_monitor_logs/cron.log` | Cron 日志 | 7 天 |
| `/tmp/gateway-*.log` | Gateway 日志 | 7 天 |

---

## ⚙️ 高级配置

### 修改检查间隔

```bash
# 编辑 crontab
crontab -e

# 修改为每 5 分钟检查一次
*/5 * * * * /root/.openclaw/workspace/scripts/feishu_smart_monitor.sh

# 修改为每 15 分钟检查一次
*/15 * * * * /root/.openclaw/workspace/scripts/feishu_smart_monitor.sh
```

### 修改重启策略

```bash
# 编辑监控脚本
nano /root/.openclaw/workspace/scripts/feishu_smart_monitor.sh

# 修改参数
MAX_RESTART_ATTEMPTS=2      # 最多重启 2 次
COOLDOWN_MINUTES=60         # 冷却期 60 分钟
```

### 添加邮件通知

```bash
# 编辑监控脚本，修改 send_notification 函数
send_notification() {
    local level="$1"
    local message="$2"

    # 记录日志
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$NOTIFICATION_FILE"

    # 发送邮件
    echo "$message" | mail -s "飞书机器人状态" your@email.com
}
```

---

## 📞 技术支持

### 获取帮助
- **查看日志**: `tail -f /tmp/feishu_smart_monitor.log`
- **检查状态**: `cat /tmp/feishu_state.json | jq .`
- **手动检查**: `/root/.openclaw/workspace/scripts/feishu_smart_monitor.sh`

### 常见问题
1. **监控不工作** → 检查 crontab 配置
2. **频繁重启** → 检查飞书应用配置
3. **日志过大** → 手动清理或调整保留时长

---

## ✅ 安装验证

```bash
# 验证监控已安装
crontab -l | grep feishu

# 验证脚本存在
ls -l /root/.openclaw/workspace/scripts/feishu_smart_monitor.sh

# 验证状态文件
cat /tmp/feishu_state.json | jq .

# 验证首次运行
tail -20 /tmp/feishu_smart_monitor.log
```

---

**更新时间**: 2026-03-13 17:17
**下次检查**: 2026-03-13 17:27（10 分钟后）
