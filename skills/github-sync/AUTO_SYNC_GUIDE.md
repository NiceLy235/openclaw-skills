# Skill 更新后自动同步 - 快速指南

## ✅ 新规则

**每次更新 skill 后，必须立即同步到 GitHub。**

---

## 🚀 一键更新 + 同步

```bash
cd ~/.openclaw/workspace/skills/github-sync/scripts

# 更新 skill 并自动同步
./update_skill.sh <skill_name> "你的提交信息"

# 示例
./update_skill.sh env-setup "Add Python 3.12 support"
./update_skill.sh lerobot-auto-train "Fix dependency conflicts"
```

---

## 📋 工作流程

### 方式 1: 使用自动化脚本（推荐）

```bash
# 1. 编辑 skill
cd ~/.openclaw/workspace/skills/env-setup
vim scripts/install_lerobot_enhanced.sh

# 2. 一键更新 + 同步
cd ../github-sync/scripts
./update_skill.sh env-setup "Add new installation feature"

# ✅ 完成！自动：
# - 提交更改
# - 同步到 GitHub
# - 发送实时进度
```

### 方式 2: 手动步骤

```bash
# 1. 编辑 skill
cd ~/.openclaw/workspace/skills/YOUR_SKILL
# Make changes...

# 2. 提交更改
cd ~/.openclaw/workspace
git add skills/YOUR_SKILL/
git commit -m "feat: Your changes"

# 3. 同步到 GitHub (必需)
cd skills/github-sync/scripts
./sync_skills.sh
```

---

## 🎯 什么时候需要同步

- ✅ **创建新 skill**
- ✅ **更新现有 skill**
- ✅ **修复 skill bug**
- ✅ **添加新功能**
- ✅ **更新文档**

**规则：任何 skill 文件的更改 → 立即同步**

---

## 📊 实时反馈

更新脚本会发送实时进度：

```
🔄 开始更新 skill: env-setup
📝 检测到 3 个文件更改
💾 正在提交更改...
✅ 已提交: Add Python 3.12 support
🚀 正在同步到 GitHub...
✅ Skills synced to GitHub
🎉 Skill 更新并同步完成！
```

---

## 🔧 示例会话

### 创建新 skill

```bash
# 1. 创建 skill
cd ~/.openclaw/workspace/skills
mkdir my-new-skill
# Create SKILL.md, scripts, etc...

# 2. 提交并同步
cd github-sync/scripts
./update_skill.sh my-new-skill "feat: Add new skill"

# ✅ 新 skill 已在 GitHub
```

### 修复 bug

```bash
# 1. 修复 bug
cd ~/.openclaw/workspace/skills/lerobot-auto-train
vim scripts/train.py
# Fix the bug...

# 2. 提交并同步
cd ../github-sync/scripts
./update_skill.sh lerobot-auto-train "fix: Resolve training timeout issue"

# ✅ 修复已同步到 GitHub
```

---

## 💡 为什么自动同步

### 1. 备份
- Skills 是宝贵的工作成果
- GitHub 提供安全的远程备份
- 不会因为本地问题丢失工作

### 2. 版本控制
- 跟踪所有更改历史
- 可以回退到任何版本
- 清楚地看到演进过程

### 3. 分享
- 跨机器使用相同的 skills
- 团队协作
- 知识共享

### 4. 恢复
- 如果本地文件损坏
- 可以从 GitHub 恢复
- 保障数据安全

---

## 📝 Git 提交信息规范

使用规范的提交信息：

```bash
# 新功能
./update_skill.sh env-setup "feat: Add Python 3.12 support"

# Bug 修复
./update_skill.sh lerobot-auto-train "fix: Resolve memory leak"

# 文档更新
./update_skill.sh github-sync "docs: Update sync guide"

# 重构
./update_skill.sh env-setup "refactor: Simplify installation flow"

# 性能优化
./update_skill.sh lerobot-auto-train "perf: Improve training speed"
```

---

## ⚠️ 注意事项

### 检查 V2Ray

```bash
# 确保 V2Ray 运行
systemctl status v2ray

# 如果未运行
sudo systemctl start v2ray
```

### 检查 Remote

```bash
# 确认 remote 已配置
cd ~/.openclaw/workspace
git remote -v

# 如果没有，运行设置脚本
cd skills/github-sync/scripts
./setup_repos.sh
```

---

## 🎁 自动化的好处

### 之前
```
1. 编辑 skill
2. 测试
3. git add
4. git commit
5. git push
6. 记得做第 5 步吗？❌ 经常忘记
```

### 现在
```
1. 编辑 skill
2. 测试
3. ./update_skill.sh skill "message"
4. ✅ 完成！自动提交 + 同步
```

---

## 📞 需要帮助？

```bash
# 查看用法
./update_skill.sh

# 查看 sync 状态
./sync_status.sh

# 查看日志
tail -f ~/.openclaw/github_sync.log
```

---

## ✨ 总结

**一个命令完成所有操作：**

```bash
./update_skill.sh <skill_name> "your message"
```

✅ 提交更改
✅ 同步 GitHub
✅ 实时反馈
✅ 备份完成

**不再需要记住手动推送！** 🚀
