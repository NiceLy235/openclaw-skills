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
- 🎯 **适用于所有任务**（训练、安装、下载、数据处理等）
- 📊 进度消息必须包含：
  - 当前执行的步骤
  - 已用时间
  - 预计剩余时间（如果可知）
  - 当前状态（运行中/等待中/错误恢复中）

### 进度消息模板
```
📊 进度更新 (5 分钟汇报)
━━━━━━━━━━━━━━━━━━━━━━━━
• 任务类型: [训练/安装/下载/数据处理]
• 当前步骤: Step 3/5 - [具体步骤]
• 已用时间: 10 分钟
• 预计剩余: 约 15 分钟
• 状态: ⏳ 正在执行 (45%)
━━━━━━━━━━━━━━━━━━━━━━━━
```

### 实现方式

**方式 1: 使用 exec + background progress reporter（推荐）**

```python
import subprocess
import threading
import time
from datetime import datetime

class UniversalProgressReporter:
    """Universal progress reporter for any long-running task."""

    def __init__(self, task_name, channel="feishu", interval=300):
        self.task_name = task_name
        self.channel = channel
        self.interval = interval  # 5 minutes
        self.running = False
        self.thread = None
        self.start_time = time.time()

    def start(self):
        """Start progress reporter."""
        self.running = True
        self.thread = threading.Thread(target=self._report_loop, daemon=True)
        self.thread.start()

    def _report_loop(self):
        """Send progress every 5 minutes."""
        while self.running:
            time.sleep(self.interval)
            if self.running:
                self._send_progress()

    def _send_progress(self):
        """Send progress message."""
        elapsed = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed)

        message = f"""📊 进度更新 (5 分钟汇报)
━━━━━━━━━━━━━━━━━━━━━━━━
• 任务类型: {self.task_name}
• 当前步骤: 正在执行...
• 已用时间: {elapsed_str}
• 状态: ⏳ 运行中
━━━━━━━━━━━━━━━━━━━━━━━━"""

        # Send via OpenClaw message tool
        try:
            subprocess.run([
                "openclaw", "message", "send",
                "--channel", self.channel,
                "-m", message
            ], timeout=30)
        except Exception as e:
            print(f"Failed to send progress: {e}")

    def _format_time(self, seconds):
        """Format seconds to human-readable time."""
        minutes = int(seconds // 60)
        hours = minutes // 60
        minutes = minutes % 60

        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        else:
            return f"{minutes}分钟"

    def stop(self):
        """Stop progress reporter."""
        self.running = False

# Usage example
reporter = UniversalProgressReporter(
    task_name="LeRobot 训练",
    channel="feishu",
    interval=300  # 5 minutes
)
reporter.start()

# Execute long-running task
long_running_task()

# Stop reporter
reporter.stop()
```

**方式 2: 在 exec 命令中使用 background yield**

```bash
# Start command
exec(command, { yieldMs: 10000 })  # 10 seconds

# Start background progress reporter
# (使用定时器线程每 5 分钟发送一次)

# Poll frequently
process poll (timeout: 5000)  # Every 5 seconds

# Every 5 minutes, send progress
if elapsed_time % 300 == 0:
    message(action="send", message="📊 进度更新...")
```

**方式 3: Wrapper script with progress reporting**

```bash
#!/bin/bash
# wrapper_with_progress.sh

TASK_NAME="$1"
COMMAND="$2"
INTERVAL=300  # 5 minutes

# Start progress reporter in background
(
    start_time=$(date +%s)
    while kill -0 $$ 2>/dev/null; do
        sleep $INTERVAL
        elapsed=$(($(date +%s) - start_time))
        minutes=$((elapsed / 60))

        # Send progress message
        openclaw message send --channel feishu -m "📊 进度更新: 已运行 ${minutes} 分钟"
    done
) &
REPORTER_PID=$!

# Execute command
eval "$COMMAND"
EXIT_CODE=$?

# Stop reporter
kill $REPORTER_PID 2>/dev/null

exit $EXIT_CODE
```

### 适用于所有场景

| 场景 | 汇报频率 | 汇报内容 | 实现方式 |
|------|---------|---------|---------|
| LeRobot 训练 | 每 5 分钟 | 当前 step、loss、lr | Cron job + 监控脚本 |
| 模型下载 | 每 5 分钟 | 下载进度、已用时间 | Wrapper script |
| 环境安装 | 每 5 分钟 | 当前安装步骤 | Progress reporter 类 |
| 数据处理 | 每 5 分钟 | 处理进度、已用时间 | Wrapper script |
| Git 操作 | 每 5 分钟 | 当前操作、已用时间 | Progress reporter 类 |
| 文件传输 | 每 5 分钟 | 传输进度、速度 | Wrapper script |

### 强制执行规则

**对于 Agent：**
- ✅ **任何任务 > 5 分钟**必须启动进度汇报
- ✅ **每 5 分钟**发送一次进度消息
- ✅ **任务完成后**停止汇报器
- ❌ **禁止**让用户长时间等待无反馈

**对于 Cron Job：**
- ✅ 已部署 LeRobot 训练监控（Cron Job ID: 93385dee）
- ✅ 每 5 分钟自动检查并发送进度
- ✅ 适用于所有正在运行的训练任务

### 检查清单

**在执行任何任务前，确认：**
- [ ] 任务预计时间 > 5 分钟？
- [ ] 已启动进度汇报机制？
- [ ] 汇报间隔设置为 300 秒（5 分钟）？
- [ ] 消息发送到正确的飞书频道？

**任务完成后，确认：**
- [ ] 已停止进度汇报器
- [ ] 发送了任务完成消息

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
