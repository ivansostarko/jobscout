#!/usr/bin/env bash
# JobScout installer — Python venv, dependencies, CLI, config bootstrap.
set -euo pipefail
cd "$(dirname "$0")/.."
JOBSCOUT_HOME="$(pwd)"
echo "==> Installing JobScout into $JOBSCOUT_HOME"

# 1. Python venv + package
if ! command -v python3 >/dev/null; then
  echo "python3 is required (>= 3.10)"; exit 1
fi
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip >/dev/null
./.venv/bin/pip install -e .
echo "==> Python package installed (.venv/bin/jobscout)"

# 2. .env bootstrap
if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> Created .env — EDIT IT with your Telegram/SMTP credentials!"
fi

# 3. Ollama + Qwen (optional but recommended)
if command -v ollama >/dev/null; then
  echo "==> Ollama detected."
  MODEL=$(grep -E '^\s*model:' config/jobscout.yaml | head -1 | awk '{print $2}' | tr -d '"')
  echo "    Pulling model $MODEL (skip with Ctrl+C, reports will fall back to score ranking)"
  ollama pull "$MODEL" || true
else
  echo "==> Ollama not found. Install from https://ollama.com then run:"
  echo "    ollama pull qwen2.5:14b"
fi

# 4. Symlink CLI for convenience
mkdir -p "$HOME/.local/bin"
ln -sf "$JOBSCOUT_HOME/.venv/bin/jobscout" "$HOME/.local/bin/jobscout"
echo "==> CLI linked to ~/.local/bin/jobscout (ensure ~/.local/bin is on PATH)"

echo
echo "Next steps:"
echo "  1. Edit .env (Telegram + SMTP credentials)"
echo "  2. jobscout test ollama && jobscout test telegram && jobscout test email"
echo "  3. jobscout scan            # first manual scan"
echo "  4. ./scripts/setup_cron.sh  # register the schedule (OpenClaw or crontab)"
