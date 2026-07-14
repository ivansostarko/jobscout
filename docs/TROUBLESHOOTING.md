# Troubleshooting

## Reports don't arrive

**Telegram**
- `jobscout test telegram` — most common cause: you never messaged the bot.
  Open the bot in Telegram, press **Start**, retry.
- `TELEGRAM_CHAT_ID` must be *your* numeric id (@userinfobot), or a group id
  (negative number, bot must be a member).

**Email**
- `jobscout test email`. Gmail: you need an **App Password** (2FA required),
  not your normal password. Port 587 = STARTTLS, 465 = SSL (both supported).
- Corporate SMTP may require the From address to equal SMTP_USER.

## `jobscout scan` finds 0 jobs

- Run with `log_level: DEBUG` in the YAML and read which source failed.
- LinkedIn HTTP 429/999 → rate-limited; wait, reduce keyword×location
  combinations, or raise delays.
- MojPosao/Posao.hr zero results → site redesign; update selectors at the
  top of the source file (docs/SOURCES.md).
- MojPosao HTTP 403 / HZZ HTTP 503 → CloudFront/geo blocking of
  datacenter or foreign IPs. Run JobScout from a Croatian residential
  connection (home server, Raspberry Pi, laptop) or a Croatian VPN exit.
- Genuinely quiet day for executive roles is normal — check
  `posted_within_hours` (LinkedIn) isn't too tight.

## Ollama problems

- `jobscout test ollama` — is the server up? `systemctl status ollama` or
  just run `ollama serve`.
- Model missing → `ollama pull qwen2.5:14b`.
- 14B too heavy (needs ~10 GB RAM/VRAM)? switch `ai.model` to `qwen2.5:7b`.
- Remember: reports still go out without Ollama (score-ranking fallback).

## OpenClaw cron jobs don't fire

- `openclaw cron list` — enabled? next-run time sane? correct timezone?
- `openclaw cron run <job-id>` to force a run and read the error.
- `openclaw logs --follow` while a job is due.
- Isolated jobs preflight the local Ollama endpoint; if it's down the run is
  recorded as **skipped**, not failed — start Ollama.

## Excel file issues

- Locked file (open in Excel/LibreOffice while a scan writes) → close it;
  scans that can't save will error but the next hourly scan recovers.
- Want a fresh start? Delete `data/jobs.xlsx` — it's recreated on next scan
  (history is lost; back it up first).

## Duplicate jobs anyway?

Dedup is by canonical URL. The same job posted on two boards (LinkedIn +
MojPosao) is intentionally kept as two rows — different sources, different
URLs. Same-board duplicates should never happen; if they do, open an issue
with both URLs.
