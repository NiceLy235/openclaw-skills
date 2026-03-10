# 推送 Skills 到 GitHub - 快速指南

## 📋 准备工作

### 1. 创建 GitHub 仓库

访问：https://github.com/new

**推荐配置**：
- 仓库名: `openclaw-skills` 或 `openclaw-workspace`
- 描述: `OpenClaw AI skills and configurations`
- 可见性: Private（推荐）或 Public
- **不要**勾选 "Add a README file"（已有本地文件）

### 2. 获取仓库 URL

创建后，复制仓库 URL（选择 HTTPS 或 SSH）：

```
HTTPS: https://github.com/YOUR_USERNAME/YOUR_REPO.git
SSH:   git@github.com:YOUR_USERNAME/YOUR_REPO.git
```

---

## 🚀 方式 1: 自动推送（推荐）

### 如果使用 HTTPS + Token

```bash
# 1. 生成 Personal Access Token
# 访问: https://github.com/settings/tokens
# 权限: 勾选 repo (full control)

# 2. 运行推送脚本
cd ~/.openclaw/workspace
bash scripts/setup_and_push_github.sh

# 3. 当提示输入 URL 时，使用带 token 的格式:
# https://YOUR_TOKEN@github.com/YOUR_USERNAME/YOUR_REPO.git
```

### 如果使用 SSH

```bash
# 1. 确保 SSH keys 已配置
ssh -T git@github.com  # 测试连接

# 2. 运行推送脚本
cd ~/.openclaw/workspace
bash scripts/setup_and_push_github.sh

# 3. 当提示输入 URL 时，使用 SSH 格式:
# git@github.com:YOUR_USERNAME/YOUR_REPO.git
```

---

## 🔧 方式 2: 手动推送

```bash
cd ~/.openclaw/workspace

# 1. 添加 remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 2. 配置代理（如果需要）
git config --local http.proxy http://127.0.0.1:10809
git config --local https.proxy http://127.0.0.1:10809

# 3. 推送
git push -u origin master
```

---

## 📦 将推送的内容

### Skills (2个)
```
✅ env-setup (v2.0)
   - 增强版安装脚本
   - 依赖冲突解决工具
   - 详细故障排查指南

✅ lerobot-auto-train
   - 训练自动化流程
   - 后台任务执行
   - 实时进度监控
   - 推理测试
```

### 配置和工具
```
✅ Daily Memory System
   - 自动保存对话
   - 每日总结生成
   - GitHub 同步

✅ 配置文件
   - AGENTS.md (工作规则)
   - HEARTBEAT.md
   - 各种设置和工具
```

---

## 🔐 认证方式对比

### HTTPS + Token（推荐新手）

**优点**：
- ✅ 不需要额外配置
- ✅ 防火墙友好
- ✅ 可以用代理

**步骤**：
1. 创建 Token: https://github.com/settings/tokens
2. 勾选 `repo` 权限
3. 使用格式: `https://TOKEN@github.com/...`

**示例**：
```bash
git remote add origin https://ghp_xxxx@github.com/user/repo.git
git push -u origin master
```

### SSH Keys（推荐长期使用）

**优点**：
- ✅ 更安全
- ✅ 不需要每次输入密码
- ✅ Git 标准方式

**步骤**：
1. 生成密钥：
   ```bash
   ssh-keygen -t ed25519 -C "your@email.com"
   ```

2. 查看公钥：
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

3. 添加到 GitHub: https://github.com/settings/keys

4. 测试：
   ```bash
   ssh -T git@github.com
   ```

---

## 🌐 使用代理推送

如果在中国或需要代理：

### 启动 V2Ray
```bash
sudo systemctl start v2ray
sudo systemctl status v2ray
```

### 配置 Git 代理
```bash
cd ~/.openclaw/workspace

# HTTP 代理
git config --local http.proxy http://127.0.0.1:10809
git config --local https.proxy http://127.0.0.1:10809

# 或 SOCKS5 代理
git config --local http.proxy socks5://127.0.0.1:10808
git config --local https.proxy socks5://127.0.0.1:10808
```

### 推送
```bash
git push -u origin master
```

---

## ❓ 常见问题

### Q1: 推送时要求输入密码

**A**: 使用 Personal Access Token 而不是 GitHub 密码

```bash
# 格式
https://YOUR_TOKEN@github.com/USERNAME/REPO.git

# 或更新 remote
git remote set-url origin https://TOKEN@github.com/USERNAME/REPO.git
```

### Q2: Connection timed out

**A**: 需要配置代理

```bash
# 启动 V2Ray
sudo systemctl start v2ray

# 配置 Git 代理
git config --local http.proxy http://127.0.0.1:10809
git config --local https.proxy http://127.0.0.1:10809
```

### Q3: Repository not found

**A**: 确保仓库已创建

1. 访问 https://github.com/new
2. 创建仓库
3. 确保 URL 拼写正确

### Q4: Permission denied (SSH)

**A**: SSH keys 未配置或未添加到 GitHub

```bash
# 生成密钥
ssh-keygen -t ed25519 -C "your@email.com"

# 查看公钥
cat ~/.ssh/id_ed25519.pub

# 添加到 GitHub
# https://github.com/settings/keys
```

---

## 📝 推送后

### 查看仓库
```bash
# 在浏览器打开
open https://github.com/YOUR_USERNAME/YOUR_REPO
```

### 后续更新
```bash
cd ~/.openclaw/workspace

# 提交更改
git add -A
git commit -m "feat: Your changes"

# 推送
git push
```

---

## 🎯 快速命令参考

```bash
# 一键推送（推荐）
bash scripts/setup_and_push_github.sh

# 查看状态
git status

# 查看日志
git log --oneline -10

# 查看远程
git remote -v

# 推送
git push origin master

# 拉取更新
git pull origin master
```

---

## 📚 相关文件

- `scripts/setup_and_push_github.sh` - 自动设置和推送
- `scripts/push_skills_to_github.sh` - 简单推送脚本

---

**需要帮助？**

如果遇到问题：
1. 查看上面的常见问题
2. 检查网络和代理配置
3. 确认 GitHub 仓库 URL 正确
4. 验证认证方式（Token 或 SSH）

准备好了就运行：
```bash
bash scripts/setup_and_push_github.sh
```
