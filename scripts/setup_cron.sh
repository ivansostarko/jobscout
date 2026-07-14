#!/usr/bin/env bash
# Registers the JobScout schedule.
#   ./scripts/setup_cron.sh openclaw   -> OpenClaw cron jobs (recommended)
#   ./scripts/setup_cron.sh crontab    -> plain system crontab (no OpenClaw needed)
set -euo pipefail
cd "$(dirname "$0")/.."
JOBSCOUT_HOME="$(pwd)"
BIN="$JOBSCOUT_HOME/.venv/bin/jobscout"
MODE="${1:-openclaw}"
TZ_NAME="Europe/Zagreb"

if [ "$MODE" = "openclaw" ]; then
  command -v openclaw >/dev/null || { echo "openclaw CLI not found — run with 'crontab' mode instead"; exit 1; }
  echo "==> Registering OpenClaw cron jobs (agent runs the jobscout CLI via exec)"

  openclaw cron add --name "jobscout-scan" \
    --cron "0 7-17 * * *" --tz "$TZ_NAME" --session isolated --no-deliver \
    --message "Run the shell command: cd $JOBSCOUT_HOME && $BIN scan — then reply NO_REPLY unless it failed."

  openclaw cron add --name "jobscout-daily-telegram" \
    --cron "0 19 * * *" --tz "$TZ_NAME" --session isolated --no-deliver \
    --message "Run: cd $JOBSCOUT_HOME && $BIN report daily — the CLI sends the Telegram report itself. Reply NO_REPLY unless it failed."

  openclaw cron add --name "jobscout-daily-email" \
    --cron "0 21 * * *" --tz "$TZ_NAME" --session isolated --no-deliver \
    --message "Run: cd $JOBSCOUT_HOME && $BIN report daily-email — the CLI sends the email itself. Reply NO_REPLY unless it failed."

  openclaw cron add --name "jobscout-weekly-email" \
    --cron "0 9 * * 5" --tz "$TZ_NAME" --session isolated --no-deliver \
    --message "Run: cd $JOBSCOUT_HOME && $BIN report weekly — the CLI sends the weekly email itself. Reply NO_REPLY unless it failed."

  openclaw cron list
  echo "==> Done. Inspect with: openclaw cron list | edit with: openclaw cron edit <id>"

elif [ "$MODE" = "crontab" ]; then
  echo "==> Installing plain crontab entries (standalone mode, no OpenClaw)"
  TMP=$(mktemp)
  crontab -l 2>/dev/null | grep -v "JOBSCOUT" > "$TMP" || true
  cat >> "$TMP" <<CRON
# JOBSCOUT begin (managed by setup_cron.sh)
CRON_TZ=$TZ_NAME
0 7-17 * * * cd $JOBSCOUT_HOME && $BIN scan >> data/scan.log 2>&1               # JOBSCOUT scan
0 19 * * *  cd $JOBSCOUT_HOME && $BIN report daily >> data/report.log 2>&1      # JOBSCOUT telegram
0 21 * * *  cd $JOBSCOUT_HOME && $BIN report daily-email >> data/report.log 2>&1 # JOBSCOUT email
0 9 * * 5   cd $JOBSCOUT_HOME && $BIN report weekly >> data/report.log 2>&1     # JOBSCOUT weekly
# JOBSCOUT end
CRON
  crontab "$TMP" && rm "$TMP"
  crontab -l | grep JOBSCOUT
  echo "==> Done."
else
  echo "Usage: $0 [openclaw|crontab]"; exit 2
fi
