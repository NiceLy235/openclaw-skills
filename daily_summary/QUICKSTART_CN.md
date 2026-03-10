# 每日记忆系统 - 快速开始

## ✅ 系统已就绪！

已创建完整的每日记忆系统，自动保存对话和经验到 GitHub。

## 📦 已创建的组件

### 1. 脚本 (4个)
- `save_conversation.py` - 保存对话和交互
- `summarize_day.py` - 生成每日总结
- `push_to_github.sh` - 推送到 GitHub
- `daily_sync.py` - 主控脚本

### 2. 配置
- `config.json` - GitHub 配置和调度设置
- `README.md` - 完整文档

### 3. 示例输出
今天的记忆已生成：
- ✅ 3 个交互记录
- ✅ 每日总结
- ✅ 经验文档

## 🚀 立即使用

### 方式 1: 手动运行

```bash
# 每天下班前运行
cd /root/.openclaw/workspace
python3 daily_summary/scripts/daily_sync.py run
```

### 方式 2: 自动运行（Heartbeat）

**步骤 1**: 设置 GitHub 仓库

```bash
# 创建 GitHub 仓库（如 openclaw-memory）
# 然后运行
python3 daily_summary/scripts/daily_sync.py setup \
  --repo-url https://github.com/YOUR_USERNAME/openclaw-memory.git
```

**步骤 2**: 添加到 HEARTBEAT.md

```markdown
# 每日任务
- [ ] 23:00 生成每日总结并推送到 GitHub
```

**步骤 3**: 在 heartbeat 检查中

系统会自动在 23:00 运行总结和推送。

### 方式 3: Cron 定时任务

```bash
# 编辑 crontab
crontab -e

# 添加（每天 23:00）
0 23 * * * cd /root/.openclaw/workspace && /usr/bin/python3 daily_summary/scripts/daily_sync.py run
```

## 📊 今天的示例

### 已保存的交互

1. **Skill 创建** (lerobot-auto-train)
   - 经验: 遵循 skill-creator 最佳实践

2. **CUDA 修复** (192.168.136.128)
   - 错误: nouveau 驱动冲突
   - 解决: 禁用 nouveau + 重启
   - 经验: 安装 NVIDIA 驱动后必须重启

3. **工作流改进** (实时反馈)
   - 问题: 长时间命令无反馈
   - 解决: 短 poll 间隔 + 持续报告

### 生成的总结

```
📊 统计
- 交互操作: 3
- 活动分类: skill_creation, error_fix, workflow_improvement

💡 经验教训
1. Skill 创建最佳实践
2. NVIDIA 驱动安装流程
3. 实时反馈重要性
```

## 💾 存储位置

```
~/.openclaw/memory/          # 独立的 git 仓库
├── conversations/           # 对话记录
│   └── 2026-03-10-interactions.md
├── daily/                  # 每日总结
│   └── 2026-03-10-summary.md
└── experiences/            # 经验文档
    └── 2026-03-10-experience.md
```

## 🔧 在对话中使用

### 我会自动保存

- ✅ 完成重要任务 → 保存为 interaction
- ✅ 修复错误 → 保存错误 + 解决方案 + 经验
- ✅ 创建 skill → 保存操作记录
- ✅ 你说 "记住这个" → 保存为经验

### 手动保存

```bash
# 快速日志
python3 daily_summary/scripts/save_conversation.py log "今天的进度"

# 保存交互
python3 daily_summary/scripts/save_conversation.py interaction \
  --type "training" \
  --details '{"task_id": "xxx", "epochs": 100}' \
  --outcome "✅ Completed" \
  --lessons "Batch size 32 works well for RTX 4080"
```

## 📈 每日流程

```
早上
 └─> 开始工作
      └─> 自动记录对话和操作

工作中
 ├─> 完成任务 → 自动保存
 ├─> 修复错误 → 自动保存
 └─> 学习经验 → 自动保存

晚上 23:00
 └─> Heartbeat 触发
      ├─> 生成每日总结
      ├─> 提取经验教训
      └─> 推送到 GitHub ✅

第二天
 └─> 查看 GitHub
      ├─> 回顾昨天总结
      └─> 搜索历史经验
```

## 🎯 下一步

### 1. 设置 GitHub 仓库（一次性）

```bash
python3 daily_summary/scripts/daily_sync.py setup \
  --repo-url https://github.com/YOUR_USERNAME/openclaw-memory.git
```

### 2. 配置自动同步

选择一种方式：
- [ ] Heartbeat（推荐）
- [ ] Cron 定时任务
- [ ] 手动运行

### 3. 测试

```bash
# 检查状态
python3 daily_summary/scripts/daily_sync.py status

# 手动运行一次
python3 daily_summary/scripts/daily_sync.py run --no-push

# 推送到 GitHub
python3 daily_summary/scripts/daily_sync.py run
```

## 📚 文档

- `daily_summary/README.md` - 完整文档
- `daily_summary/config.json` - 配置文件
- `AGENTS.md` - 已集成每日记忆规则

## ✨ 好处

1. **持久记忆** - 不会忘记过去的经验
2. **避免重复** - 搜索历史解决方案
3. **持续学习** - 分析模式并改进
4. **知识传承** - GitHub 上的持久存储

## 🎉 示例：搜索历史

明天遇到 CUDA 问题时：

```bash
# 在 memory 目录搜索
cd ~/.openclaw/memory
grep -r "CUDA" experiences/

# 找到 2026-03-10 的经验：
# "CRITICAL: After installing NVIDIA driver, must disable nouveau and reboot"
```

---

**系统已就绪！开始记录你的经验吧！** 🧠✨

需要帮助？
```bash
python3 daily_summary/scripts/daily_sync.py --help
```
