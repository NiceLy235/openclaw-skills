#!/bin/bash
# Setup cron job for daily memory sync
#
# This script adds a cron job to run daily memory sync at 23:00

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SYNC_SCRIPT="${WORKSPACE_DIR}/daily_summary/scripts/daily_sync.py"
LOG_FILE="/var/log/openclaw-memory.log"

echo "⏰ Setting up cron job for daily memory sync..."
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "daily_sync.py"; then
    echo "⚠️  Cron job already exists:"
    crontab -l | grep "daily_sync.py"
    echo ""
    read -p "Do you want to update it? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled"
        exit 0
    fi
    # Remove existing
    crontab -l 2>/dev/null | grep -v "daily_sync.py" | crontab -
fi

# Add new cron job
CRON_JOB="0 23 * * * cd ${WORKSPACE_DIR} && /usr/bin/python3 ${SYNC_SCRIPT} run >> ${LOG_FILE} 2>&1"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job added successfully!"
echo ""
echo "📋 Current crontab:"
crontab -l | grep -A1 -B1 "daily_sync.py" || crontab -l
echo ""
echo "📅 Schedule: Every day at 23:00 (11 PM)"
echo "📝 Log file: ${LOG_FILE}"
echo ""
echo "🧪 To test manually:"
echo "   python3 ${SYNC_SCRIPT} run"
echo ""
echo "📊 To view logs:"
echo "   tail -f ${LOG_FILE}"
echo ""
echo "✅ Setup complete! Daily memory sync will run automatically at 23:00."
