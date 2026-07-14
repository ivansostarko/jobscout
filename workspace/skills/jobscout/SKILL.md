---
name: jobscout
description: >
  Search job boards (LinkedIn, MojPosao.hr, Posao.hr, HZZ Burza rada,
  optional Facebook groups) for executive/IT roles, store them deduplicated
  in an Excel database, and send daily Telegram / email and weekly email
  reports with AI-ranked apply recommendations. Use this skill whenever the
  user asks about jobs, job reports, the job market, scanning job boards,
  or "what should I apply to".
---

# JobScout skill

All operations go through the `jobscout` CLI (installed via
`scripts/install.sh`; available on PATH inside the project venv at
`{{JOBSCOUT_HOME}}/.venv/bin/jobscout`).

## Commands

| Task | Command |
|---|---|
| Scan all job boards now | `jobscout scan` |
| Daily Telegram report + AI suggestion | `jobscout report daily` |
| Daily email report | `jobscout report daily-email` |
| Weekly email report (Mon–now) | `jobscout report weekly` |
| Status / health | `jobscout status` |
| Test channels | `jobscout test telegram` / `jobscout test email` / `jobscout test ollama` |

## Conventions
- Run commands with the `exec` tool from the project directory
  (`JOBSCOUT_HOME`, default `~/jobscout`).
- Jobs database: `data/jobs.xlsx` (one row per job, deduplicated by job_id).
- Configuration: `config/jobscout.yaml` — if the user wants different
  keywords, locations, sources or schedules, edit that file, never the code.
- Secrets are in `.env`; never print token or password values to chat.
- If a scan or send fails, report the exact CLI error output.
