# FAQ

**Can I change the model?** Yes — `ai.model` in `config/jobscout.yaml`
accepts any Ollama tag. Qwen 2.5 is the default; 7B works fine on modest
hardware.

**Can I add locations (e.g. Dubai, remote-EU)?** Add entries to
`sources.linkedin.locations`. HR boards are country-specific.

**Can I add another job board?** Yes — ~50 lines. See "Adding a new source"
in docs/ARCHITECTURE.md.

**Does it apply for me?** No, by design. It finds, ranks, and recommends;
you apply. (See workspace/AGENTS.md rule 2.)

**Where is my data?** Everything is local: `data/jobs.xlsx`, local Ollama,
your own Telegram bot and SMTP account. Nothing is sent to third-party AI
APIs.

**Can I run it without OpenClaw?** Yes — `./scripts/setup_cron.sh crontab`
gives you the identical behavior via system cron.

**How do I get the weekly report on a different day?** Change `0 9 * * 5`
(5 = Friday) in the cron registration; see docs/SCHEDULING.md.

**Croatian reports?** Set `general.language: hr` and translate the strings
in `src/jobscout/report.py` (PRs welcome) — the AI suggestion will follow
whatever language you use in `ai.profile`.
