# GitHub Sync Skill - 快速开始

## ✨ 一键设置

```bash
cd ~/.openclaw/workspace/skills/github-sync/scripts
./setup_repos.sh
```

这个脚本会：
1. ✅ 检测 V2Ray 代理
2. ✅ 配置 Git 远程仓库
3. ✅ 测试 GitHub 连接
4. ✅ 设置定时任务

---

## 📦 包含的同步任务

### 1. Memory Sync (记忆同步)
- **仓库**: `https://github.com/NiceLy235/training-memories.git`
- **内容**: 对话、每日总结、经验文档
- **时间**: 每天 23:00 自动执行
- **脚本**: `sync_memory.sh`

### 2. Skills Sync (Skill 同步)
- **仓库**: 你配置的 skills 仓库
- **内容**: 所有自定义 skills 和工具
- **时间**: 手动触发 或 配置定时任务
- **脚本**: `sync_skills.sh`

---

## 🚀 使用方法

### 日常操作

```bash
# 查看状态
./sync_status.sh

# 手动同步记忆
./sync_memory.sh

# 手动同步 skills
./sync_skills.sh

# 同步所有内容
./sync_all.sh
```

### 查看日志

```bash
# 实时查看日志
tail -f ~/.openclaw/github_sync.log

# 查看最近 50 行
tail -50 ~/.openclaw/github_sync.log
```

---

## 📋 首次设置步骤

### 1. 准备 GitHub 仓库

你需要两个仓库：

#### Memory 仓库
- 已存在: `https://github.com/NiceLy235/training-memories`
- 无需创建

#### Skills 仓库
- 需要创建: https://github.com/new
- 推荐名称: `openclaw-skills` 或 `openclaw-workspace`

### 2. 运行设置脚本

```bash
cd ~/.openclaw/workspace/skills/github-sync/scripts
./setup_repos.sh
```

按提示输入：
- Memory 仓库 URL（或直接回车使用默认）
- Skills 仓库 URL（需要你提供）

### 3. 测试同步

```bash
# 测试 memory 同步
./sync_memory.sh

# 测试 skills 同步
./sync_skills.sh

# 查看状态
./sync_status.sh
```

---

## 🔐 认证配置

### 方式 1: HTTPS + Token（推荐）

1. 创建 Token: https://github.com/settings/tokens
2. 勾选 `repo` 权限
3. 使用格式: `https://YOUR_TOKEN@github.com/USERNAME/REPO.git`

### 方式 2: SSH Keys

1. 生成密钥: `ssh-keygen -t ed25519 -C "your@email.com"`
2. 添加到 GitHub: https://github.com/settings/keys
3. 测试: `ssh -T git@github.com`

---

## 🌐 代理配置

脚本会自动检测 V2Ray 代理：
- HTTP 代理: `http://127.0.0.1:10809`
- SOCKS5 代理: `socks5://127.0.0.1:10808`

如果需要手动启动：
```bash
sudo systemctl start v2ray
```

---

## ⏰ 定时任务

设置后，定时任务会自动运行：

```
Memory sync: 每天 23:00
Skills sync: 手动触发
```

查看定时任务：
```bash
crontab -l | grep github-sync
```

---

## 📊 同步报告示例

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Memory Sync Report - 2026-03-10 23:00:15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Content Stats:
  Conversations: 3 files
  Daily summaries: 1 file
  Experiences: 1 file

✅ Successfully pushed to GitHub
Repository: https://github.com/NiceLy235/training-memories

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ❓ 常见问题

### Q: 推送失败，提示认证错误

**A**: 使用 Personal Access Token

```bash
# 更新 remote URL
git remote set-url origin https://YOUR_TOKEN@github.com/USERNAME/REPO.git
```

### Q: 推送超时

**A**: 检查 V2Ray 代理

```bash
# 启动 V2Ray
sudo systemctl start v2ray

# 测试代理
curl -x http://127.0.0.1:10809 -I https://github.com
```

### Q: 如何禁用自动同步

**A**: 编辑 crontab

```bash
crontab -e
# 注释掉包含 github-sync 的行
```

---

## 🎯 完整示例

### 设置新环境

```bash
# 1. 进入脚本目录
cd ~/.openclaw/workspace/skills/github-sync/scripts

# 2. 运行设置
./setup_repos.sh

# 3. 输入仓库 URL
# Memory: 直接回车（使用默认）
# Skills: 输入你的仓库 URL

# 4. 测试
./sync_all.sh

# 5. 查看状态
./sync_status.sh
```

---

## 📞 获取帮助

```bash
# 查看详细状态
./sync_status.sh

# 查看日志
tail -100 ~/.openclaw/github_sync.log

# 重新设置
./setup_repos.sh
```

---

**就这么简单！** 🎉

设置完成后，你的记忆和 skills 会自动同步到 GitHub。
