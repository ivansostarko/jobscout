#!/usr/bin/env bash
# Removes JobScout schedule from plain crontab. For OpenClaw jobs use:
#   openclaw cron list   +   openclaw cron rm <job-id>
set -euo pipefail
TMP=$(mktemp)
crontab -l 2>/dev/null | grep -v "JOBSCOUT" > "$TMP" || true
crontab "$TMP" && rm "$TMP"
echo "JobScout crontab entries removed."
