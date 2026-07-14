#!/usr/bin/env bash
# Verifies all moving parts: Ollama, Telegram, email, Excel store.
set -uo pipefail
cd "$(dirname "$0")/.."
BIN=./.venv/bin/jobscout
echo "== JobScout healthcheck =="
$BIN status
echo "-- Ollama --";  $BIN test ollama
echo "-- Telegram --"; $BIN test telegram
echo "-- Email --";   $BIN test email
