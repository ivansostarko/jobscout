# Architecture

## Design principles

1. **Deterministic core, AI on top.** Scraping, deduplication, storage and
   delivery are plain Python. The LLM (Ollama/Qwen) only writes the
   recommendation text. If Ollama is down, a score-based fallback keeps
   reports flowing.
2. **One row per job, forever.** `job_id = sha1(canonical URL)` (or a
   content hash when a URL is missing). `ExcelStore.add_jobs()` checks
   existing IDs before appending — a job can never appear twice.
3. **Fail soft.** Every source is wrapped in `safe_fetch()`; one broken
   site never kills a scan.
4. **Config over code.** All behavior lives in `config/jobscout.yaml`.

## Components

```
src/jobscout/
├── cli.py          argparse entry point (scan / report / status / test)
├── config.py       YAML + .env loading
├── models.py       Job dataclass + stable job_id
├── storage.py      ExcelStore (openpyxl): dedup, today/this-week queries
├── scoring.py      keyword matching + relevance score
├── ai.py           Ollama chat call + deterministic fallback
├── report.py       Telegram HTML + email HTML/plain builders
├── notify/
│   ├── telegram.py Bot API sendMessage
│   └── email.py    SMTP (STARTTLS/SSL) multipart
└── sources/
    ├── base.py     session, UA rotation, polite delays, safe_fetch
    ├── linkedin.py guest job-search endpoint
    ├── mojposao.py resilient multi-selector parser
    ├── posao_hr.py link-pattern parser
    ├── burza_hzz.py best-effort ASPX listing parser
    └── facebook_groups.py optional cookie-based mbasic parser
```

## OpenClaw integration

- `workspace/AGENTS.md` + `SOUL.md` — the agent's operating instructions
  (never scrape in chat; always use the CLI; never apply on your behalf).
- `workspace/skills/jobscout/SKILL.md` — teaches the agent the CLI.
- `config/openclaw.jobscout.json` — Ollama provider (Qwen default), agent
  definition, Telegram channel, exec/cron/message tools.
- `scripts/setup_cron.sh openclaw` — four isolated cron jobs that run the
  CLI via exec. Delivery is done by the CLI itself (Bot API / SMTP), so the
  jobs use `--no-deliver` and reply `NO_REPLY` — no duplicate messages.

## Adding a new source

1. Create `src/jobscout/sources/mysite.py`, subclass `BaseSource`,
   implement `fetch() -> list[Job]`.
2. Register it in `sources/__init__.py` (`SOURCES` dict).
3. Add a `sources.mysite` block to `config/jobscout.yaml` with `enabled`.

That's it — scoring, dedup, storage and reporting pick it up automatically.

## Data flow of a report

`ExcelStore.jobs_today()` → sort by score → `ai.suggest()` (Ollama) or
`ai.fallback_suggestion()` → `report.telegram_report()` /
`report.email_report()` → `notify.telegram.send()` / `notify.email.send()`.
