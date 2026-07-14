#!/usr/bin/env bash
# Manual scan wrapper (used by cron and for testing).
set -euo pipefail
cd "$(dirname "$0")/.."
exec ./.venv/bin/jobscout scan
