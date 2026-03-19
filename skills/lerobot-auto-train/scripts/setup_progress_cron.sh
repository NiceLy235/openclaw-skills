#!/bin/bash
# Setup OpenClaw cron job for training progress reports
# This creates a cron job that runs every 5 minutes and sends progress updates to Feishu

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROGRESS_SCRIPT="$SCRIPT_DIR/check_training_progress.py"

# Check if progress script exists
if [ ! -f "$PROGRESS_SCRIPT" ]; then
    echo "❌ Progress script not found: $PROGRESS_SCRIPT"
    exit 1
fi

echo "🚀 Setting up training progress cron job..."
echo "📄 Progress script: $PROGRESS_SCRIPT"
echo ""

# Create cron job payload
cat > /tmp/training_progress_cron.json <<EOF
{
  "name": "LeRobot Training Progress Report",
  "schedule": {
    "kind": "every",
    "everyMs": 300000
  },
  "payload": {
    "kind": "agentTurn",
    "message": "检查 LeRobot 训练进度并发送更新。运行脚本: python3 $PROGRESS_SCRIPT",
    "model": "glm-5",
    "thinking": "low"
  },
  "delivery": {
    "mode": "announce",
    "channel": "feishu"
  },
  "sessionTarget": "isolated",
  "enabled": true
}
EOF

echo "📋 Cron job configuration:"
cat /tmp/training_progress_cron.json
echo ""

# Add cron job using OpenClaw cron tool
echo "⏳ Adding cron job to OpenClaw..."
if openclaw cron add /tmp/training_progress_cron.json; then
    echo "✅ Cron job added successfully!"
    echo ""
    echo "📊 Training progress will be reported every 5 minutes"
    echo "🔧 To manage cron jobs, use: openclaw cron list"
else
    echo "❌ Failed to add cron job"
    exit 1
fi

# Cleanup
rm -f /tmp/training_progress_cron.json

echo ""
echo "🎉 Setup complete!"
