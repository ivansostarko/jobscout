#!/usr/bin/env bash
# Sends the weekly email report (Friday 09:00 job).
set -euo pipefail
cd "$(dirname "$0")/.."
exec ./.venv/bin/jobscout report weekly
