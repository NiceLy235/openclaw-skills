#!/bin/bash

# 飞书智能监控安装脚本

echo "🚀 安装飞书智能监控系统..."

# 1. 检查依赖
echo "检查依赖..."
if ! command -v jq &> /dev/null; then
    echo "安装 jq..."
    apt-get update && apt-get install -y jq
fi

# 2. 创建日志目录
mkdir -p /tmp/feishu_monitor_logs

# 3. 安装 Cron 任务（每 10 分钟检查一次）
echo "配置定时任务..."
cat > /tmp/feishu_monitor_cron <<EOF
# 飞书智能监控（每 10 分钟检查一次）
*/10 * * * * /root/.openclaw/workspace/scripts/feishu_smart_monitor.sh >> /tmp/feishu_monitor_logs/cron.log 2>&1

# 每周清理日志（周日凌晨 2 点）
0 2 * * 0 find /tmp -name "feishu_*.log" -mtime +7 -delete >> /tmp/feishu_monitor_logs/cleanup.log 2>&1
0 2 * * 0 find /tmp -name "gateway-*.log" -mtime +7 -delete >> /tmp/feishu_monitor_logs/cleanup.log 2>&1
EOF

crontab /tmp/feishu_monitor_cron
echo "✅ Cron 任务已配置"

# 4. 首次运行
echo "执行首次检查..."
/root/.openclaw/workspace/scripts/feishu_smart_monitor.sh

# 5. 显示配置
cat <<EOF

✅ 安装完成！

📊 监控配置：
  - 检查间隔：每 10 分钟
  - 最大重启次数：1 次
  - 冷却期：30 分钟
  - 日志文件：/tmp/feishu_smart_monitor.log
  - 状态文件：/tmp/feishu_state.json
  - 通知文件：/tmp/feishu_notifications.txt

📋 管理命令：
  - 查看日志：tail -f /tmp/feishu_smart_monitor.log
  - 查看状态：cat /tmp/feishu_state.json | jq .
  - 查看通知：cat /tmp/feishu_notifications.txt
  - 手动检查：/root/.openclaw/workspace/scripts/feishu_smart_monitor.sh
  - 停止监控：crontab -r

🔄 智能特性：
  ✅ 自动检测连接断开
  ✅ 智能重启（最多 1 次）
  ✅ 冷却期保护（30 分钟内不重复重启）
  ✅ 配置检查（配置错误不重启）
  ✅ 状态持久化
  ✅ 详细日志记录

EOF
