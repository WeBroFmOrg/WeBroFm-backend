#!/bin/bash
# Setup cron job to update trending ranking every 12 hours
# Run: bash deploy/setup_cron.sh

PROJECT_DIR="/var/www/webrofm/WeBroFm-backend"
CRON_LOG="/var/log/webrofm/trending_cron.log"

# Remove old entry if exists
crontab -l 2>/dev/null | grep -v "update_trending" | crontab -

# Add new entry — runs at 6:00 and 18:00 daily
(crontab -l 2>/dev/null; echo "0 6,18 * * * cd $PROJECT_DIR && source venv/bin/activate && python manage.py update_trending >> $CRON_LOG 2>&1") | crontab -

echo "Cron job installed. Runs daily at 06:00 and 18:00."
echo "Logs: $CRON_LOG"

# Run once immediately
cd $PROJECT_DIR && source venv/bin/activate && python manage.py update_trending
echo "Initial run complete."
