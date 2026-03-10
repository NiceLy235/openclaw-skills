# GitHub 自动推送设置 - 快速开始

## ✅ 已完成配置

1. ✅ Git 仓库已初始化
2. ✅ Remote 已设置为: `https://github.com/NiceLy235/training-memories.git`
3. ✅ 初始 commit 已创建

---

## 🔐 需要你的操作：创建 GitHub Token

### 步骤 1: 访问 GitHub

👉 点击这里：https://github.com/settings/tokens

### 步骤 2: 生成 Token

1. 点击 **"Generate new token"** → **"Generate new token (classic)"**
2. Note: 输入 `OpenClaw Daily Memory`
3. Expiration: 选择 `No expiration` 或 `90 days`
4. Select scopes: **勾选 `repo`**（完整控制私有仓库）
5. 点击绿色按钮 **"Generate token"**
6. **⚠️ 复制生成的 token**（类似 `ghp_xxxxxxxxxxxx`）

### 步骤 3: 运行设置脚本

```bash
cd /root/.openclaw/workspace
./daily_summary/scripts/setup_github_auth.sh YOUR_TOKEN_HERE
```

**替换 `YOUR_TOKEN_HERE` 为你刚才复制的 token！**

### 步骤 4: 设置自动运行（Cron）

```bash
# 编辑 crontab
crontab -e

# 添加这一行（每天 23:00 自动运行）
0 23 * * * cd /root/.openclaw/workspace && /usr/bin/python3 /root/.openclaw/workspace/daily_summary/scripts/daily_sync.py run >> /var/log/openclaw-memory.log 2>&1
```

---

## 🧪 测试

```bash
# 手动运行一次测试
python3 daily_summary/scripts/daily_sync.py run

# 检查状态
python3 daily_summary/scripts/daily_sync.py status
```

---

## 📊 完成后效果

### 每天自动执行

```
23:00 → 生成每日总结
     → 提取经验教训
     → 推送到 GitHub
     → ✅ 完成
```

### GitHub 仓库内容

```
https://github.com/NiceLy235/training-memories
├── conversations/      # 对话记录
├── daily/             # 每日总结
├── experiences/       # 经验文档
└── README.md
```

---

## 🆘 需要详细说明？

查看完整文档：
```bash
cat daily_summary/SETUP_GITHUB.md
```

---

## 📝 快速命令参考

```bash
# 手动运行
python3 daily_summary/scripts/daily_sync.py run

# 检查状态
python3 daily_summary/scripts/daily_sync.py status

# 查看今天的总结
cat ~/.openclaw/memory/daily/$(date +%Y-%m-%d)-summary.md

# 搜索历史
cd ~/.openclaw/memory
grep -r "CUDA" experiences/
```

---

**现在请按照步骤 1-4 完成设置！** 🚀
