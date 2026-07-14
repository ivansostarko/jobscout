# Scheduling

Default schedule (timezone **Europe/Zagreb**):

| Cron | Job | Delivery |
|---|---|---|
| `0 7-17 * * *` | `jobscout scan` | none (writes to Excel) |
| `0 19 * * *` | `jobscout report daily` | Telegram |
| `0 21 * * *` | `jobscout report daily-email` | Email |
| `0 9 * * 5` | `jobscout report weekly` | Email (Mon→Fri digest) |

## OpenClaw mode (recommended)

```bash
./scripts/setup_cron.sh openclaw
openclaw cron list                # verify
openclaw cron run <job-id>        # test any job immediately
openclaw cron edit <job-id> --cron "30 18 * * *"   # change a time
openclaw cron rm <job-id>         # remove
```

Notes:
- Jobs run as **isolated sessions** with `--no-deliver`; the jobscout CLI
  performs the actual Telegram/email delivery, and the agent replies
  `NO_REPLY` so OpenClaw doesn't post duplicate announcements.
- OpenClaw preflights the local Ollama endpoint before isolated runs; if
  Ollama is down the run is recorded as *skipped* and retried on the next
  schedule.
- Cron expressions use the `--tz Europe/Zagreb` passed by the script;
  without `--tz` OpenClaw uses the gateway host timezone.

## Standalone mode (plain crontab)

```bash
./scripts/setup_cron.sh crontab   # install
crontab -l                        # verify
./scripts/uninstall_cron.sh       # remove
```

Logs go to `data/scan.log` and `data/report.log`.

## Changing the schedule

1. Edit the `schedule:` block in `config/jobscout.yaml` (documentation) and
2. re-register: for crontab mode just rerun the script; for OpenClaw mode
   either rerun the script (after removing old jobs) or use
   `openclaw cron edit`.

Tip: to scan every 30 minutes during work hours use `*/30 7-17 * * *`.
