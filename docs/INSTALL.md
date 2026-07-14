# Installation guide

JobScout runs anywhere Python 3.10+ runs (Linux, macOS, WSL). Recommended:
the same machine that runs your OpenClaw gateway and Ollama.

## 1. Prerequisites

| Component | Why | Install |
|---|---|---|
| Python ≥ 3.10 | JobScout CLI | `sudo apt install python3 python3-venv` |
| Ollama | local LLM for recommendations | https://ollama.com/download |
| Qwen model | default model | `ollama pull qwen2.5:14b` (or `qwen2.5:7b` on 8–16 GB RAM) |
| OpenClaw | agent runtime, cron, Telegram channel | https://docs.openclaw.ai — `npm i -g openclaw` (or the official installer), then `openclaw onboard` |
| Telegram bot | delivery channel | talk to **@BotFather** → `/newbot` → copy token; get your chat id from **@userinfobot** |
| SMTP account | email reports | e.g. Gmail App Password (Account → Security → App passwords) |

JobScout also works **without OpenClaw** in standalone mode (plain crontab)
— see step 6.

## 2. Get the code

```bash
git clone https://github.com/ivansostarko/jobscout.git ~/jobscout
cd ~/jobscout
```

## 3. Install

```bash
./scripts/install.sh
```

This creates `.venv`, installs the `jobscout` CLI, copies `.env.example`
to `.env`, and pulls the Qwen model if Ollama is present.

## 4. Configure secrets

```bash
nano .env
```

Fill in `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, and the `SMTP_*` /
`EMAIL_*` values. **Important:** send your bot one message first ("/start"),
otherwise Telegram will not let it message you.

## 5. Verify

```bash
jobscout test ollama     # Ollama reachable? model pulled?
jobscout test telegram   # you should receive a test message
jobscout test email      # you should receive a test email
jobscout scan            # first scan — creates data/jobs.xlsx
jobscout status
jobscout report daily    # full daily report to Telegram, right now
```

## 6. Register the schedule

### Option A — OpenClaw (recommended)

Merge `config/openclaw.jobscout.json` into your `~/.openclaw/openclaw.json`
(Ollama provider with Qwen, the `jobscout` agent pointing at
`~/jobscout/workspace`, Telegram channel, exec/cron/message tools), copy the
skill so the agent knows the CLI:

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -r workspace/skills/jobscout ~/.openclaw/workspace/skills/
openclaw gateway restart
```

Then register the four cron jobs:

```bash
./scripts/setup_cron.sh openclaw
openclaw cron list
```

### Option B — standalone (no OpenClaw)

```bash
./scripts/setup_cron.sh crontab
crontab -l
```

Same schedule, driven by the system cron; the AI suggestion still uses your
local Ollama.

## 7. Done

The schedule (Europe/Zagreb):

- hourly scans 07:00–17:00
- 19:00 Telegram daily report
- 21:00 email daily report
- Friday 09:00 weekly email digest

Change any of it in `config/jobscout.yaml` + rerun `setup_cron.sh`
(see docs/SCHEDULING.md).
