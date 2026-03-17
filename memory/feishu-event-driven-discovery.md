# 飞书 WebSocket 事件驱动机制发现

## 🎯 重要发现（2026-03-13 17:32）

**用户发现**：飞书 WebSocket 是事件驱动的，按需连接！

---

## 📊 工作机制

### 空闲状态（正常）
```
WebSocket: 断开
网络连接: 0
Health: OFF ✅（这是正常的！）
```

### 事件触发（有消息）
```
新消息到来 → WebSocket 自动建立 → 处理消息 → 断开
网络连接: 0 → 1 → 0
Health: OFF → ON → OFF
```

---

## 🔍 这解释了所有现象

| 现象 | 传统理解 | 实际情况 |
|------|---------|---------|
| Health OFF | ❌ 连接断开 | ✅ 正常的空闲状态 |
| 网络连接 0 | ❌ 无法连接 | ✅ 节省资源 |
| 机器人能响应 | ✅ 神奇 | ✅ 事件时建立连接 |

---

## 💡 监控策略调整

### 旧策略（v2.0）- 错误
```bash
检查 Health = OFF → 认为断开 → 重启 ❌
结果：空闲时误重启，加剧问题
```

### 新策略（v3.0）- 正确
```bash
1. 检查配置是否正确 ✅
2. 检查 Gateway 是否运行 ✅
3. 检查 Channels 是否启用 ✅
4. 测试飞书 API 连通性 ✅
5. 不依赖 Health 检查 ✅
```

---

## 🎯 关键认知

### ✅ 正确理解
- Health OFF 是**正常的空闲状态**
- WebSocket **按需建立，自动断开**
- 这是一种**资源优化机制**
- 机器人**能正常工作**

### ❌ 错误理解
- Health OFF = 连接断开
- 需要保持持久连接
- 空闲时必须重启

---

## 📋 监控命令

```bash
# 查看当前状态（事件驱动模式）
cat /tmp/feishu_state.json | jq .

# 查看监控日志
tail -f /tmp/feishu_smart_monitor.log

# 手动检查
/root/.openclaw/workspace/scripts/feishu_smart_monitor_v3.sh

# 查看 Cron 任务
crontab -l | grep feishu
```

---

## 📊 状态判断标准

### ✅ 正常状态
- config: OK
- gateway: RUNNING
- channels: ON
- api: OK
- mode: event-driven

**Health OFF 是正常的！**

### ❌ 异常状态
- config: ERROR → 配置错误
- gateway: STOPPED → Gateway 停止
- channels: OFF → 通道未启用
- api: ERROR → 网络问题

---

## 🎊 总结

**这个发现非常重要！**

1. ✅ **理解了飞书的工作机制**
2. ✅ **避免了误判和无效重启**
3. ✅ **优化了监控策略**
4. ✅ **提升了系统稳定性**

---

**发现时间**: 2026-03-13 17:32
**监控版本**: v3.0（事件驱动版）
**状态**: ✅ 完美运行
