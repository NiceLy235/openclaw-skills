# Daily Memory System - 每日记忆系统

自动将 OpenClaw 的操作和对话存储到 GitHub，作为历史记忆和经验。

## 🎯 功能

### 1. 自动记录
- ✅ 实时保存对话
- ✅ 记录操作和交互
- ✅ 快速日志记录

### 2. 每日总结
- ✅ 自动生成每日总结
- ✅ 提取关键操作
- ✅ 分析活动分类
- ✅ 提取经验教训

### 3. GitHub 同步
- ✅ 自动 commit 和 push
- ✅ 可配置仓库
- ✅ 定时同步

## 🚀 快速开始

### 1. 设置 GitHub 仓库

```bash
# 创建 GitHub 仓库（例如：openclaw-memory）
# 然后运行设置命令

python scripts/daily_sync.py setup --repo-url https://github.com/YOUR_USERNAME/openclaw-memory.git
```

### 2. 记录对话

在对话中，我会自动使用 `save_conversation.py` 保存重要交互：

```python
# 保存消息
python scripts/save_conversation.py message \
  --user "用户消息" \
  --assistant "助手回复" \
  --tags "training" "cuda" "fix"
```

### 3. 记录操作

```python
# 保存交互操作
python scripts/save_conversation.py interaction \
  --type "error_fix" \
  --details '{"error": "CUDA not available", "fix": "Install driver"}' \
  --outcome "✅ Fixed" \
  --lessons "Always check nvidia-smi before training"
```

### 4. 快速日志

```python
# 快速记录
python scripts/save_conversation.py log "Fixed CUDA issue on 192.168.136.128"
```

### 5. 生成总结

```bash
# 生成今天的总结
python scripts/daily_sync.py run

# 生成指定日期的总结
python scripts/daily_sync.py run --date 2026-03-10

# 只生成本地总结，不推送到 GitHub
python scripts/daily_sync.py run --no-push
```

### 6. 检查状态

```bash
python scripts/daily_sync.py status
```

## ⏰ 自动化

### 方式 1: Heartbeat（推荐）

在 `HEARTBEAT.md` 中添加：

```markdown
# 每日任务
- [ ] 每晚 23:00 运行 daily_sync.py
```

在 heartbeat 检查时：
```python
# 检查时间
if current_time > "23:00" and last_sync_date != today:
    run_daily_sync()
```

### 方式 2: Cron

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天 23:00）
0 23 * * * /usr/bin/python3 /root/.openclaw/workspace/daily_summary/scripts/daily_sync.py run
```

### 方式 3: 手动触发

```bash
# 每天下班前运行
python scripts/daily_sync.py run
```

## 📁 目录结构

```
~/.openclaw/memory/
├── conversations/
│   ├── 2026-03-10.md              # 当天对话
│   ├── 2026-03-10-interactions.md # 当天操作
│   └── 2026-03-10-log.md          # 当天日志
├── daily/
│   └── 2026-03-10-summary.md      # 每日总结
├── experiences/
│   └── 2026-03-10-experience.md   # 经验文档
├── errors/
│   └── 2026-03-10-errors.md       # 错误日志
└── README.md
```

## 📊 每日总结示例

```markdown
# 每日总结 - 2026-03-10

**生成时间**: 2026-03-10T23:00:00

---

## 📊 统计
- 对话次数: 15
- 交互操作: 8
- 日志条目: 12

## 🎯 活动分类
- error_fix: 3
- training: 2
- skill_creation: 1
- environment_setup: 2

## 🔑 关键操作
- 10:15 - training: Started training task train_20260310_101500_abc
- 11:42 - skill_creation: Created lerobot-auto-train skill
- 14:30 - error_fix: Fixed CUDA driver issue on 192.168.136.128

## ❌ 遇到的错误
- **09:58** (error): CUDA not available on 192.168.136.128
  - 原因: nouveau 驱动冲突
  - 修复: 禁用 nouveau，重启系统

## 💡 经验教训
1. 安装 NVIDIA 驱动后必须禁用 nouveau 并重启
2. 长时间任务应该使用实时反馈机制
3. Skill 创建应遵循 skill-creator 最佳实践

## 📝 讨论主题
CUDA, GPU, skill, 训练, 环境配置, 错误修复
```

## 💡 使用场景

### 1. 在对话中自动保存

我会在以下情况自动保存：

- **完成重要任务** → 保存为 interaction
- **修复错误** → 保存错误 + 解决方案 + 经验
- **创建/修改 skill** → 保存操作记录
- **用户说 "记住这个"** → 保存为经验

### 2. 避免重复错误

```python
# 在 memory/experiences/ 中查找历史经验
# 每次遇到问题时，先搜索历史经验
search_memory("CUDA 问题")
# → 找到 2026-03-10 的经验：需要禁用 nouveau
```

### 3. 学习和改进

- 每周回顾 daily summary
- 分析常见错误模式
- 改进工作流程

## 🔧 配置

编辑 `daily_summary/config.json`:

```json
{
  "github": {
    "repo_url": "https://github.com/YOUR_USERNAME/openclaw-memory.git",
    "branch": "main"
  },
  "schedule": {
    "summary_time": "23:00",
    "push_time": "23:30",
    "timezone": "Asia/Shanghai"
  },
  "retention": {
    "keep_conversations_days": 30,
    "keep_summaries_days": 365,
    "keep_experiences_days": 365
  }
}
```

## 🚨 隐私和安全

**重要**：
- ✅ 不会保存密码、密钥等敏感信息
- ✅ 可以在 `.gitignore` 中排除敏感文件
- ✅ 建议使用私有 GitHub 仓库
- ✅ 可以配置只保存元数据，不保存完整对话

## 🎯 最佳实践

1. **设置自动同步**
   - 使用 heartbeat 或 cron 自动运行
   - 避免忘记手动同步

2. **及时记录**
   - 完成重要任务后立即记录
   - 遇到错误时保存详细信息和解决方案

3. **定期回顾**
   - 每周查看 experiences/
   - 学习过去的经验
   - 避免重复错误

4. **配置 GitHub**
   - 使用 SSH keys 避免输入密码
   - 使用私有仓库保护隐私
   - 设置 branch protection

## 📝 示例工作流程

```bash
# 1. 早上开始工作
# (我会自动开始记录对话)

# 2. 工作中
# - 修复了一个 CUDA 问题 → 自动保存
# - 创建了一个 skill → 自动保存
# - 用户说 "记住这个" → 手动保存经验

# 3. 晚上 23:00
# (heartbeat 触发)
$ python scripts/daily_sync.py run

# 4. 自动执行
# - 生成每日总结
# - 提取经验教训
# - Commit + Push 到 GitHub

# 5. 第二天
# - 查看 GitHub 上的每日总结
# - 回顾昨天的经验
# - 搜索历史记录避免重复错误
```

## 🔄 与 AGENTS.md 集成

在 AGENTS.md 中添加：

```markdown
## Daily Memory

- Automatically save important interactions
- Generate daily summary at 23:00
- Push to GitHub for persistence
- Search memory before attempting solutions
```

## 🎉 开始使用

```bash
# 1. 设置仓库
python scripts/daily_sync.py setup --repo-url <your-repo-url>

# 2. 检查状态
python scripts/daily_sync.py status

# 3. 运行同步
python scripts/daily_sync.py run

# 4. 设置自动同步（可选）
# - 编辑 HEARTBEAT.md
# - 或设置 cron job
```

## 📚 相关文档

- `save_conversation.py --help` - 对话保存帮助
- `summarize_day.py --help` - 总结生成帮助
- `daily_sync.py --help` - 同步命令帮助

## 🤝 贡献

发现 bug 或有改进建议？欢迎：
1. 提交 issue
2. 创建 PR
3. 更新文档

---

**让 OpenClaw 拥有持久记忆，不断学习和成长！** 🧠✨
