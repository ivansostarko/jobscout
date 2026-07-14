<div align="center">

# 🔎 JobScout

**Autonomous job-search agent for [OpenClaw](https://openclaw.ai)**

Scans LinkedIn, MojPosao.hr, Posao.hr and HZZ Burza rada every hour (07–17),
stores every job exactly once in an Excel database, and delivers AI-ranked
daily & weekly reports with *"apply to these"* recommendations to Telegram
and email — powered by a **local Ollama + Qwen** model, so nothing leaves
your machine.

`Python 3.10+` · `OpenClaw` · `Ollama / Qwen` · `MIT`

</div>

---

## Why "JobScout" instead of "JobSeeker"?

A *seeker* wanders. A *scout* goes out on a schedule, covers assigned
territory, comes back with intelligence and a recommendation. That's exactly
what this agent does — hence **JobScout**.

## What it does

| Time (Europe/Zagreb) | Action |
|---|---|
| **07:00–17:00, hourly** | Scan all enabled sources, dedupe, save new jobs to `data/jobs.xlsx` |
| **19:00 daily** | Telegram report: new jobs + AI recommendation *what to apply to* |
| **21:00 daily** | Email report (HTML table + recommendation) |
| **Friday 09:00** | Weekly email digest (Monday → now) |

**Sources** (each individually switchable in one YAML file):

1. **LinkedIn Jobs** — Croatia (Zagreb, Bjelovar, whole country) & Riyadh, Saudi Arabia; onsite / remote / hybrid
2. **MojPosao.hr** — IT & telekomunikacije, Management; Zagreb, Bjelovar, cijela Hrvatska
3. **Posao.hr** — same categories & locations
4. **Burza rada (HZZ)** — Informatički, računalni i stručnjaci za Internet
5. **Facebook groups** *(optional, disabled by default — see [docs/SOURCES.md](docs/SOURCES.md) for the ToS caveat)*

**Roles searched:** CTO, COO, Business Manager, Project Manager, IT Manager,
Program Manager, AI Engineer + Croatian variants (voditelj projekta,
tehnički direktor, …) — all editable in `config/jobscout.yaml`.

## Architecture

```
OpenClaw (gateway + cron + Telegram channel)
   │  scheduled agent turns (Ollama / Qwen)
   ▼
jobscout CLI  ──►  sources/ (LinkedIn, MojPosao, Posao.hr, HZZ, FB)
   │                    │
   │                    ▼
   │              scoring engine (deterministic relevance score)
   ▼
data/jobs.xlsx  (one row per job, ever — SHA-1 dedup on canonical URL)
   │
   ▼
report builder ──► Ollama (qwen2.5) "what should I apply to" suggestion
   │                (graceful fallback to score ranking if Ollama is down)
   ├──► Telegram Bot API   (daily 19:00)
   └──► SMTP email         (daily 21:00, weekly Fri 09:00)
```

Design principle: **the LLM never scrapes and never schedules.** Scraping,
dedup and delivery are deterministic Python; the model only writes the
human recommendation. Reports go out even if Ollama is offline.

## Quick start (5 minutes)

```bash
git clone https://github.com/ivansostarko/jobscout.git ~/jobscout
cd ~/jobscout
./scripts/install.sh              # venv + deps + CLI + pulls qwen2.5

cp .env.example .env && nano .env # Telegram bot token/chat id, SMTP creds

jobscout test ollama              # connectivity checks
jobscout test telegram
jobscout test email

jobscout scan                     # first manual scan → data/jobs.xlsx
jobscout report daily             # try the Telegram report right now

./scripts/setup_cron.sh openclaw  # register the full schedule in OpenClaw
# no OpenClaw? use:  ./scripts/setup_cron.sh crontab
```

Full walkthrough: **[docs/INSTALL.md](docs/INSTALL.md)**.

## Customize everything in one file

`config/jobscout.yaml` controls keywords, locations, sources on/off,
scoring weights, AI model (`qwen2.5:14b` → any Ollama tag), report language,
and the schedule. Secrets live only in `.env`. Details:
**[docs/CONFIGURATION.md](docs/CONFIGURATION.md)**.

## CLI reference

```
jobscout scan                 # scrape all enabled sources, save new jobs
jobscout report daily         # Telegram report + AI suggestion
jobscout report daily-email   # email report
jobscout report weekly        # weekly email digest
jobscout status               # totals, sources, model, store path
jobscout test telegram|email|ollama
```

## Documentation

| Doc | Contents |
|---|---|
| [docs/INSTALL.md](docs/INSTALL.md) | Step-by-step install: Python, Ollama, OpenClaw, Telegram bot, SMTP |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Every YAML option explained |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Components, data flow, dedup, extension guide |
| [docs/SCHEDULING.md](docs/SCHEDULING.md) | OpenClaw cron vs plain crontab, changing times |
| [docs/SOURCES.md](docs/SOURCES.md) | Per-site notes, selectors, legal/ToS considerations |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common failures and fixes |

## Important notes on scraping

- LinkedIn is scraped via its public logged-out job listing endpoint at a
  polite rate. Heavy use may still be rate-limited or against LinkedIn's ToS
  — keep `posted_within_hours: 24` and default limits.
- Facebook group scraping **violates Facebook's ToS** and is disabled by
  default. Enable only if you accept the risk (see docs/SOURCES.md).
- Croatian job boards change their HTML occasionally; each parser keeps its
  selectors at the top of its file for one-line fixes.

## License

MIT © Ivan Šoštarko — part of the open-source tools at
[github.com/ivansostarko](https://github.com/ivansostarko)
