# FEISHU_RULES.md - 飞书实时反馈规则（强制）

⚠️ **此文件适用于所有飞书会话（包括隔离会话）**

---

## 🚨 强制执行规则

**所有飞书机器人执行的多步骤任务，必须：**

1. ✅ **每个步骤开始前**：发送 "🚀 开始执行步骤 X/Y"
2. ✅ **每个步骤完成后**：发送 "✅ 步骤 X/Y 完成：[摘要]"
3. ✅ **遇到错误时**：立即发送 "❌ 步骤 X 失败：[错误]" 并停止
4. ✅ **任务完成时**：发送 "🎉 全部完成！[结果摘要]"

---

## ⚡ 实时反馈要求

### 禁止行为
- ❌ 执行 >3 个 API 调用而不发送进度消息
- ❌ 等待整个任务完成才返回结果
- ❌ 遇到错误不立即报告
- ❌ 让用户长时间等待无反馈
- ❌ 超过 5 分钟不发送任何进度更新

### 必须行为
- ✅ 在第一个 API 调用前发送开始消息
- ✅ 在每个主要步骤后发送进度
- ✅ 在最后一个 API 调用后发送完成消息
- ✅ 遇到错误立即报告并尝试恢复
- ✅ **每 5 分钟发送一次进度更新**（即使任务还在执行中）⭐ **NEW**

---

## ⏰ 五分钟汇报规则（强制）

**适用于所有长时间运行的任务（>5 分钟）：**

### 规则说明
- ⏰ **每 5 分钟**必须发送一次进度消息
- 📊 进度消息必须包含：
  - 当前执行的步骤
  - 已用时间
  - 预计剩余时间（如果可知）
  - 当前状态（运行中/等待中/错误恢复中）

### 进度消息模板
```
📊 进度更新 (5 分钟汇报)
━━━━━━━━━━━━━━━━━━━━━━━━
• 当前步骤: Step 3/5 - 下载模型
• 已用时间: 10 分钟
• 预计剩余: 约 15 分钟
• 状态: ⏳ 正在下载 (45%)
━━━━━━━━━━━━━━━━━━━━━━━━
```

### 实现方式

**方式 1: 使用后台定时器（推荐）**
```python
import threading
import time

class ProgressReporter:
    def __init__(self, channel="feishu"):
        self.channel = channel
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._report_loop)
        self.thread.daemon = True
        self.thread.start()

    def _report_loop(self):
        while self.running:
            time.sleep(300)  # 5 分钟
            if self.running:
                self._send_progress()

    def _send_progress(self):
        # 发送进度消息到飞书
        message(action="send", message="📊 进度更新...")

    def stop(self):
        self.running = False

# 使用
reporter = ProgressReporter()
reporter.start()

# 执行长时间任务
long_running_task()

# 停止汇报
reporter.stop()
```

**方式 2: 在长时间命令中定期检查**
```bash
# 在训练循环中每 5 分钟发送进度
start_time=$(date +%s)
while true; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))

    if [ $((elapsed % 300)) -eq 0 ]; then
        echo "📊 进度更新: 已运行 $((elapsed / 60)) 分钟"
        # 发送消息到飞书
    fi

    # 执行任务...
    sleep 10
done
```

### 适用于所有场景

| 场景 | 汇报频率 | 汇报内容 |
|------|---------|---------|
| 模型下载 | 每 5 分钟 | 下载进度、已用时间、剩余时间 |
| 训练任务 | 每 5 分钟 | 当前 step、loss、lr、预计完成时间 |
| 环境安装 | 每 5 分钟 | 当前安装步骤、已用时间 |
| 数据处理 | 每 5 分钟 | 处理进度、已用时间 |
| Git 操作 | 每 5 分钟 | 当前操作、已用时间 |

---

## 📋 标准工作流模板

```
1. 🚀 开始执行任务：[任务名称]

2. 执行步骤 1
   → ✅ 步骤 1/N 完成：[摘要]

3. 执行步骤 2
   → ✅ 步骤 2/N 完成：[摘要]

4. ...

5. 🎉 全部完成！[结果摘要]
```

---

## 🎯 适用于所有技能

此规则覆盖所有技能，包括但不限于：
- `lerobot-auto-train` - 训练任务
- `feishu-doc` - 文档操作
- `feishu-wiki` - Wiki 导航
- `feishu-drive` - 云盘管理
- `env-setup` - 环境安装

---

## 💡 为什么重要

- 用户体验第一：不让用户在沉默中等待
- 透明性：用户知道每个步骤在执行什么
- 快速定位问题：如果某个步骤失败，立即知道是哪一步

---

## 🔧 执行示例

### ❌ 错误（无反馈）
```python
# 执行训练任务
result = submit_training_task()
# 用户等待 5 分钟无消息...
return "训练完成"
```

### ✅ 正确（实时反馈）
```python
# 1. 发送开始消息
message("🚀 开始提交训练任务...")

# 2. 执行步骤 1
message("### Step 1: 检查环境")
check_environment()
message("✅ 步骤 1/5 完成：环境检查通过")

# 3. 执行步骤 2
message("### Step 2: 准备数据集")
prepare_dataset()
message("✅ 步骤 2/5 完成：数据集已准备")

# 4. 执行步骤 3
message("### Step 3: 生成配置")
config = generate_config()
message("✅ 步骤 3/5 完成：配置已生成")

# 5. 执行步骤 4
message("### Step 4: 等待用户确认")
# 等待确认...

# 6. 执行步骤 5
message("### Step 5: 提交训练任务")
task_id = submit_task()
message("✅ 步骤 5/5 完成：任务已提交")

# 7. 发送完成消息
message("🎉 训练任务已提交！Task ID: " + task_id)
```

---

## 🚨 特别说明

**此文件必须在飞书会话启动时加载，即使是隔离会话！**

---

**创建日期**: 2026-03-17
**原因**: 解决飞书机器人在执行训练任务时不发送进度反馈的问题
**适用范围**: 所有飞书会话（包括隔离会话）
