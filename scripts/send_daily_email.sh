#!/usr/bin/env bash
# Sends the daily email report (21:00 job).
set -euo pipefail
cd "$(dirname "$0")/.."
exec ./.venv/bin/jobscout report daily-email
