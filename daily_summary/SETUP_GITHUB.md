# GitHub 自动推送设置指南

## 🎯 目标

每天自动运行记忆同步，并推送到 `https://github.com/NiceLy235/training-memories`

---

## 📋 步骤 1: 创建 GitHub Personal Access Token

### 1.1 访问 GitHub

访问：https://github.com/settings/tokens

### 1.2 生成 Token

1. 点击 **"Generate new token"** → **"Generate new token (classic)"**
2. Note: `OpenClaw Daily Memory`
3. Expiration: `No expiration` 或选择一个长期限
4. Select scopes: 勾选 **`repo`** (full control of private repositories)
5. 点击 **"Generate token"**
6. **⚠️ 复制 token**（只显示一次！）

Token 格式类似：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 📋 步骤 2: 配置认证

### 方式 A: 使用脚本（推荐）

```bash
cd /root/.openclaw/workspace
chmod +x daily_summary/scripts/setup_github_auth.sh
./daily_summary/scripts/setup_github_auth.sh YOUR_TOKEN_HERE
```

### 方式 B: 手动配置

```bash
cd /root/.openclaw/memory
git remote set-url origin https://YOUR_TOKEN@github.com/NiceLy235/training-memories.git
git push -u origin main
```

---

## 📋 步骤 3: 测试推送

```bash
python3 daily_summary/scripts/daily_sync.py run
```

查看输出应该包含：
```
✅ Successfully pushed to GitHub
```

---

## 📋 步骤 4: 设置自动运行

### 方式 A: Cron（推荐）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天 23:00 运行）
0 23 * * * cd /root/.openclaw/workspace && /usr/bin/python3 /root/.openclaw/workspace/daily_summary/scripts/daily_sync.py run >> /var/log/openclaw-memory.log 2>&1
```

### 方式 B: Systemd Timer

创建服务文件：
```bash
sudo nano /etc/systemd/system/openclaw-memory.service
```

内容：
```ini
[Unit]
Description=OpenClaw Daily Memory Sync
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /root/.openclaw/workspace/daily_summary/scripts/daily_sync.py run
User=root

[Install]
WantedBy=multi-user.target
```

创建定时器：
```bash
sudo nano /etc/systemd/system/openclaw-memory.timer
```

内容：
```ini
[Unit]
Description=Daily OpenClaw Memory Sync

[Timer]
OnCalendar=*-*-* 23:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

启用：
```bash
sudo systemctl daemon-reload
sudo systemctl enable openclaw-memory.timer
sudo systemctl start openclaw-memory.timer
```

### 方式 C: Heartbeat 集成

在 OpenClaw 的 heartbeat 中添加检查：

编辑 `/root/.openclaw/workspace/HEARTBEAT.md`:
```markdown
# 每日任务
- [ ] 每晚 23:00 运行记忆同步
```

在 heartbeat 处理逻辑中：
```python
from datetime import datetime
import subprocess

current_hour = datetime.now().hour
last_sync_file = Path("/root/.openclaw/memory/.last_sync")

if current_hour == 23:
    if not last_sync_file.exists() or last_sync_file.read_text().strip() != datetime.now().strftime("%Y-%m-%d"):
        # 运行同步
        subprocess.run(["python3", "daily_summary/scripts/daily_sync.py", "run"])
        last_sync_file.write_text(datetime.now().strftime("%Y-%m-%d"))
```

---

## 🧪 验证设置

### 检查状态
```bash
python3 daily_summary/scripts/daily_sync.py status
```

应该看到：
```
📁 Memory Directory Status
============================================================
Location: /root/.openclaw/memory
✅ Git repository initialized
✅ Remote: https://github.com/NiceLy235/training-memories.git
📅 Last commit: ...

📊 Content:
  - Conversations: X
  - Summaries: X
  - Experiences: X
```

### 检查 GitHub
访问：https://github.com/NiceLy235/training-memories

应该看到：
- ✅ README.md
- ✅ conversations/ 目录
- ✅ daily/ 目录
- ✅ experiences/ 目录

---

## 🔧 故障排查

### 问题 1: Push 失败 - 认证错误

```
fatal: Authentication failed
```

**解决**:
1. 检查 token 是否正确
2. 检查 token 是否有 `repo` scope
3. 重新生成 token 并更新

### 问题 2: Push 失败 - 仓库不存在

```
fatal: repository not found
```

**解决**:
1. 确认仓库存在：https://github.com/NiceLy235/training-memories
2. 如果不存在，先创建仓库
3. 确认仓库名称拼写正确

### 问题 3: Push 失败 - 非 fast-forward

```
! [rejected] main -> main (non-fast-forward)
```

**解决**:
```bash
cd /root/.openclaw/memory
git pull origin main --rebase
git push origin main
```

### 问题 4: Cron 不执行

**检查**:
```bash
# 查看 cron 日志
tail -f /var/log/openclaw-memory.log

# 检查 cron 服务
systemctl status cron

# 列出当前 cron 任务
crontab -l
```

---

## 📊 日常操作

### 手动运行
```bash
python3 daily_summary/scripts/daily_sync.py run
```

### 检查状态
```bash
python3 daily_summary/scripts/daily_sync.py status
```

### 查看日志
```bash
# 查看今天的对话
cat /root/.openclaw/memory/conversations/$(date +%Y-%m-%d)-interactions.md

# 查看每日总结
cat /root/.openclaw/memory/daily/$(date +%Y-%m-%d)-summary.md

# 查看经验文档
cat /root/.openclaw/memory/experiences/$(date +%Y-%m-%d)-experience.md
```

### 搜索历史
```bash
cd /root/.openclaw/memory

# 搜索所有关于 CUDA 的经验
grep -r "CUDA" experiences/

# 搜索特定日期的总结
cat daily/2026-03-10-summary.md
```

---

## 🔐 安全注意事项

1. **Token 安全**
   - Token 存储在 git remote URL 中
   - 不要在公开场合分享 token
   - 定期更新 token
   - 如果 token 泄露，立即在 GitHub 撤销

2. **仓库权限**
   - Token 有完整的 repo 权限
   - 确保仓库设置为 Private（如果包含敏感信息）
   - 或只保存不敏感的元数据

3. **.gitignore**
   已自动创建，排除：
   - `*.tmp`
   - `*.log`

---

## 🎉 完成！

设置完成后，系统会：

- ⏰ 每天 23:00 自动运行
- 💾 保存当天所有交互
- 📊 生成每日总结
- 🧠 提取经验教训
- 📤 自动推送到 GitHub
- 🔍 可搜索历史经验

---

## 📝 示例输出

### GitHub 仓库结构

```
training-memories/
├── README.md
├── .gitignore
├── conversations/
│   ├── 2026-03-10-interactions.md
│   ├── 2026-03-11-interactions.md
│   └── ...
├── daily/
│   ├── 2026-03-10-summary.md
│   ├── 2026-03-11-summary.md
│   └── ...
└── experiences/
    ├── 2026-03-10-experience.md
    ├── 2026-03-11-experience.md
    └── ...
```

### Commit 消息

```
chore: Daily memory update - 2026-03-10

- Updated conversations and interactions
- Generated daily summary
- Saved experiences and lessons learned
```

---

## 🆘 需要帮助？

运行：
```bash
python3 daily_summary/scripts/daily_sync.py --help
```

或查看文档：
```bash
cat daily_summary/README.md
```
