# Configuration reference

Everything is customized in **`config/jobscout.yaml`**. Secrets go in
**`.env`**. Never edit source code for configuration.

## general
| Key | Default | Meaning |
|---|---|---|
| `timezone` | Europe/Zagreb | used by the schedule scripts |
| `language` | en | report language (en / hr) |
| `data_dir` | ./data | where the Excel DB and logs live |
| `excel_file` | jobs.xlsx | database file name |
| `log_level` | INFO | DEBUG for verbose scraping logs |

## search
- `keywords` / `keywords_hr` — titles to look for (English + Croatian).
  Matching is substring-based and case-insensitive; broad managerial words
  (manager, director, voditelj, head of, engineer) are matched too.
- `exclude_keywords` — drop titles containing these (intern, junior…).
- `workplace_types` — informational; LinkedIn filtering is per-source below.

## sources
Each source has `enabled: true|false`. Specific options:

- **linkedin** — `locations` (add/remove freely, e.g. add Dubai),
  `workplace_filters` (`1`=onsite, `2`=remote, `3`=hybrid, empty = all),
  `posted_within_hours` (24 keeps daily scans tight), `max_results_per_query`.
- **mojposao / posao_hr** — `base_url`, `locations`, `categories`
  (categories are informational; matching is keyword-driven).
- **burza_hzz** — `base_url`, `categories`.
- **facebook_groups** — `groups` list; requires `FB_COOKIE` in `.env`.
  Disabled by default (ToS risk — see SOURCES.md).

## scoring
Deterministic relevance score used for ranking and the fallback
recommendation:

- `title_weights` — points per keyword found in the title
- `seniority_bonus`, `remote_bonus`, `location_bonus`
- `min_score_to_recommend`, `top_n_recommendations`

Tune these to change what "Apply today" surfaces.

## ai
- `model` — any Ollama tag: `qwen2.5:14b` (default), `qwen2.5:7b`,
  `llama3.1:8b`, `mistral`, …
- `base_url` — remote Ollama works too (`http://server:11434`)
- `profile` — one paragraph describing you; this is what the model uses to
  judge fit. **Update it to match your CV.**
- `enabled: false` — skip the LLM entirely; reports use score ranking.

## notifications
Toggle Telegram/email independently; subjects are configurable. Credentials
come from `.env`:

```
TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO
```

`EMAIL_TO` accepts a comma-separated list.

## schedule
The cron expressions here are read by `scripts/setup_cron.sh` documentation
purposes; after changing them, rerun the script to re-register jobs.
