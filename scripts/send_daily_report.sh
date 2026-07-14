#!/usr/bin/env bash
# Sends the daily Telegram report (19:00 job).
set -euo pipefail
cd "$(dirname "$0")/.."
exec ./.venv/bin/jobscout report daily
