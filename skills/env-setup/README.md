# Env-Setup Skill - 使用说明

## 简介

env-setup 是一个自动搭建开发环境的 skill，支持在新电脑上快速安装和配置开发工具。

## 支持的环境

1. **v2ray** - 网络代理工具
2. **lerobot** - 机器人学习和强化学习框架

## 安装 Skill

将 `env-setup.skill` 文件导入到 OpenClaw:

```bash
# 方法 1: 复制到 skills 目录
cp env-setup.skill ~/.openclaw/skills/

# 方法 2: 通过 OpenClaw CLI 导入
openclaw skills import env-setup.skill
```

## 使用方法

### 1. 安装 v2ray

```bash
# 直接询问 AI
"帮我安装 v2ray"

# 或者更具体地说明
"我想在我的 Ubuntu 系统上安装 v2ray 代理工具"
```

AI 会自动：
- 检测系统环境
- 安装必要依赖
- 下载并安装 v2ray
- 生成默认配置
- 启动服务

### 2. 安装 lerobot

```bash
# 直接询问 AI
"帮我安装 lerobot"

# 或者指定路径
"在 ~/my_tools 目录下安装 lerobot"
```

AI 会自动：
- 检测系统环境和 GPU
- 安装 Python 依赖
- 创建虚拟环境
- 安装 PyTorch (GPU 或 CPU 版本)
- 安装 lerobot
- 创建激活脚本

### 3. 检查环境

```bash
"检查我的系统是否可以安装 v2ray"
"检查 lerobot 的安装要求"
```

## 功能特性

### ✅ 自动化安装
- 一键完成所有安装步骤
- 自动处理依赖关系
- 支持自定义安装路径

### ✅ 智能检测
- 自动检测操作系统和架构
- 检查磁盘空间和网络
- 检测已安装组件
- GPU 自动识别 (lerobot)

### ✅ 完整日志
- 所有操作记录到日志文件
- 日志位置: `~/.openclaw/install_<env>_<date>.log`

### ✅ 错误处理
- 网络失败自动重试
- 清晰的错误提示
- 完整的故障排查指南

### ✅ 安装报告
- 安装完成后生成详细报告
- 包含版本、路径、系统信息

## 系统要求

### 最低要求
- Ubuntu 20.04+ / Debian 11+ / macOS
- 2GB 可用磁盘空间
- 稳定的网络连接
- sudo 权限（系统级安装）

### 推荐配置 (lerobot)
- 8GB RAM
- NVIDIA GPU + CUDA
- 5GB 磁盘空间

## 高级用法

### 自定义安装路径

```bash
# 在对话中告诉 AI
"把 v2ray 安装到 /opt/tools/v2ray"
"在 ~/.local 目录下安装 lerobot"
```

### 查看详细文档

AI 可以访问完整的参考文档：
- v2ray 详细配置指南
- lerobot 使用教程
- 故障排查指南

只需询问：
```bash
"v2ray 如何配置代理？"
"lerobot 支持哪些功能？"
"安装失败了怎么办？"
```

## 示例对话

**用户**: 帮我安装 v2ray

**AI**: 好的，我来帮你安装 v2ray。首先检查一下系统环境...
[执行 check_environment.sh]
系统检查通过！现在开始安装...
[执行 install_v2ray.sh]
✅ v2ray 安装成功！
- 版本: v5.x.x
- 安装路径: /usr/local/bin/v2ray
- 配置文件: /usr/local/etc/v2ray/config.json
- 服务状态: 运行中

你可以使用以下命令管理 v2ray:
- 查看状态: `sudo systemctl status v2ray`
- 重启服务: `sudo systemctl restart v2ray`
- 查看日志: `sudo journalctl -u v2ray -f`

## 文件结构

```
env-setup/
├── SKILL.md                    # Skill 主文件
├── scripts/                    # 安装脚本
│   ├── common_utils.sh         # 通用工具函数
│   ├── check_environment.sh    # 环境检测
│   ├── install_v2ray.sh        # v2ray 安装
│   └── install_lerobot.sh      # lerobot 安装
└── references/                 # 参考文档
    ├── v2ray_guide.md          # v2ray 详细指南
    ├── lerobot_guide.md        # lerobot 详细指南
    └── troubleshooting.md      # 故障排查
```

## 扩展 Skill

要添加对新环境的支持：

1. 创建 `scripts/install_<env>.sh`
2. 更新 `check_environment.sh`
3. 创建 `references/<env>_guide.md`
4. 更新 `SKILL.md`

## 技术支持

遇到问题？查看：
1. 日志文件: `~/.openclaw/install_*.log`
2. 故障排查指南: 询问 AI "安装失败怎么办"
3. 详细文档: 询问 AI "查看 <env> 详细配置"

## 版本历史

- **v1.0** (2026-03-06)
  - 初始版本
  - 支持 v2ray 和 lerobot
  - 完整的自动化安装流程
  - 详细的参考文档
