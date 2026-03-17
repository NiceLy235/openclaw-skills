# env-setup Skill 执行指南

## 问题诊断和解决方案

### 问题 1：执行时跳步骤

#### 原因
OpenClaw 的 skills 是通过 SKILL.md 文件中的说明注入到 system prompt 中的。AI 模型根据这些文本指令决定如何执行，可能：
- 认为某些步骤可以跳过
- 没有理解步骤之间的依赖关系
- 优化执行路径

#### 解决方案

**方案 A：改进 SKILL.md 结构**（已实施）

SKILL.md 已更新为包含：
1. **强制执行规则**：明确要求按顺序执行
2. **分步模板**：每个步骤都有明确的命令和预期输出
3. **进度报告规则**：要求 AI 报告每个步骤的完成情况

**方案 B：使用明确的分步指令**

当使用 skill 时，在提示词中明确要求：
```
请严格按照以下步骤执行 env-setup：
1. Step 1: [具体任务] - 执行后报告结果
2. Step 2: [验证] - 执行后报告结果
3. Step 3: [下一步] - ...

每完成一个步骤，请先报告结果再继续下一步。
```

**方案 C：使用 process poll 监控长耗时操作**

```bash
# 启动后台进程
bash scripts/install_lerobot_enhanced.sh &

# 使用 process poll 监控输出
# 每 30 秒检查一次进度，报告给用户
```

### 问题 2：不及时返回执行结果

#### 原因
1. **命令执行阻塞**：AI 等待命令完成才返回
2. **缺少进度监控**：长耗时命令没有实时输出
3. **配置不当**：没有启用进度报告

#### 解决方案

**方案 A：启用进度报告**（已实施）

在 `openclaw.json` 中添加了：
```json
"exec": {
  "reportProgress": true,
  "progressIntervalMs": 5000
}
```

**方案 B：使用 run_with_progress.sh**

新创建的 `scripts/run_with_progress.sh` 脚本提供：
- 实时进度文件更新
- 明确的状态报告
- 错误捕获和日志记录

使用方法：
```bash
# 在 AI 指令中指定
bash scripts/run_with_progress.sh \
  "bash scripts/install_lerobot_enhanced.sh" \
  "Installing LeRobot with dependency resolution" \
  /tmp/lerobot_install.log
```

**方案 C：使用 process poll（推荐用于长耗时操作）**

```bash
# 启动命令
exec(command="bash scripts/install_lerobot_enhanced.sh", runInBackground=true)

# 监控进度
while true; do
  # 读取输出
  output = exec(command="tail -100 /tmp/install.log")

  # 发送进度更新
  message(content=f"📊 进度: {output}")

  # 检查是否完成
  if is_process_running():
    sleep(30)
  else:
    break
done

# 发送完成消息
message(content="✅ 安装完成！")
```

**方案 D：分步验证和报告**

```bash
# Step 1: 检查环境
message(content="🔍 Step 1: 检查系统环境...")
result = exec(command="bash scripts/check_environment.sh lerobot")
message(content=f"✅ Step 1 完成: {result}")

# Step 2: 安装依赖
message(content="📦 Step 2: 安装 PyTorch 和依赖...")
result = exec(command="pip3 install torch torchvision --index-url ...")
message(content=f"✅ Step 2 完成: {result}")

# 继续后续步骤...
```

## 最佳实践

### 对于用户

1. **明确要求分步执行**：在提示词中说明"按步骤执行"
2. **要求进度报告**：要求 AI 每 30 秒报告一次进度
3. **使用独立终端监控**：可以另开终端 `tail -f /tmp/install.log`

### 对于技能开发者

1. **添加进度钩子**：脚本中输出明确的进度标记
2. **使用进度文件**：写入 `.progress` 文件供外部监控
3. **合理设置 yieldMs**：在调用长耗时命令时设置合理的 yield 值
4. **添加验证步骤**：每个主要操作后添加验证命令

### 对于 OpenClaw 配置

```json5
{
  agents: {
    defaults: {
      exec: {
        reportProgress: true,        // 启用进度报告
        progressIntervalMs: 5000,   // 每 5 秒报告一次
        yieldAfterMs: 30000,        // 30 秒后返回结果
        streamOutput: true,           // 流式输出
      },
    },
  },
}
```

## 测试改进效果

测试以下场景验证改进：

### 场景 1：安装 LeRobot

**指令**：
```
请使用 env-setup skill 安装 LeRobot。
要求：1) 严格按照步骤执行 2) 每步完成后报告结果 3) 每 30 秒报告一次进度
```

**预期行为**：
- Step 1: 检查环境 → 报告结果
- Step 2: 检测 CUDA → 报告结果
- Step 3: 安装依赖 → 定期报告进度
- Step 4: 安装主程序 → 定期报告进度
- Step 5: 验证 → 报告最终结果

### 场景 2：安装 V2Ray

**指令**：
```
请使用 env-setup skill 安装 V2Ray。
要求完成后执行 test_proxy.sh 测试连接。
```

**预期行为**：
- 报告安装进度
- 安装完成后自动执行测试
- 报告测试结果（成功或失败）

## 调试技巧

### 查看执行日志

```bash
# 查看最近的会话
cat /root/.openclaw/agents/main/sessions/*.jsonl | jq '.content'

# 查看特定技能的执行
grep -i "env-setup" /root/.openclaw/agents/main/sessions/*.jsonl
```

### 检查进度文件

```bash
# 监控实时进度
watch -n 1 cat /tmp/*.progress

# 查看安装日志
tail -f /tmp/install_*.log
```

### 重启 OpenClaw

修改配置后需要重启服务：

```bash
# 如果是 systemd 服务
sudo systemctl restart openclaw

# 或者直接重启 openclaw 进程
openclaw restart
```

## 配置文件位置

- OpenClaw 配置：`/root/.openclaw/openclaw.json`
- Skills 目录：`/root/.openclaw/workspace/skills/`
- 会话日志：`/root/.openclaw/agents/main/sessions/`
- 临时日志：`/tmp/`
