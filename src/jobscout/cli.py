"""JobScout command-line interface.

Commands:
  jobscout scan                 run all enabled sources, dedupe, save to Excel
  jobscout report daily         Telegram + console daily report with AI suggestion
  jobscout report daily-email   email daily report
  jobscout report weekly        email weekly report (Mon–now)
  jobscout status               quick health/status summary
  jobscout test telegram|email|ollama   connectivity tests
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime

from . import __version__
from .ai import fallback_suggestion, suggest
from .config import env, load_config
from .models import Job
from .notify import email as email_notify
from .notify import telegram as tg_notify
from .report import email_report, telegram_report
from .scoring import score_job
from .sources import SOURCES
from .storage import ExcelStore


def _setup_logging(cfg: dict) -> None:
    logging.basicConfig(
        level=getattr(logging, cfg["general"].get("log_level", "INFO")),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )


def cmd_scan(cfg: dict) -> int:
    store = ExcelStore(cfg["general"]["excel_path"])
    all_jobs: list[Job] = []
    for name, cls in SOURCES.items():
        scfg = cfg.get("sources", {}).get(name, {})
        if not scfg.get("enabled", False):
            logging.info("source %s disabled — skipping", name)
            continue
        all_jobs.extend(cls(scfg, cfg).safe_fetch())
    for job in all_jobs:
        job.score = score_job(job, cfg)
    added = store.add_jobs(all_jobs)
    print(f"Scan complete: {len(all_jobs)} scraped, {len(added)} new saved to "
          f"{cfg['general']['excel_path']}")
    return 0


def _get_suggestion(jobs: list[dict], cfg: dict) -> str:
    text = suggest(jobs, cfg)
    return text or fallback_suggestion(jobs, cfg)


def cmd_report_daily_telegram(cfg: dict) -> int:
    store = ExcelStore(cfg["general"]["excel_path"])
    jobs = store.jobs_today()
    suggestion = _get_suggestion(jobs, cfg)
    msg = telegram_report(jobs, suggestion, "daily")
    print(msg)
    if cfg.get("notifications", {}).get("telegram", {}).get("enabled", True):
        return 0 if tg_notify.send(msg, cfg) else 1
    return 0


def cmd_report_daily_email(cfg: dict) -> int:
    store = ExcelStore(cfg["general"]["excel_path"])
    jobs = store.jobs_today()
    suggestion = _get_suggestion(jobs, cfg)
    plain, html = email_report(jobs, suggestion, "daily")
    subject = cfg["notifications"]["email"].get("subject_daily", "JobScout daily report")
    subject += f" — {datetime.now():%d.%m.%Y}"
    if cfg.get("notifications", {}).get("email", {}).get("enabled", True):
        return 0 if email_notify.send(subject, plain, html) else 1
    print(plain)
    return 0


def cmd_report_weekly(cfg: dict) -> int:
    store = ExcelStore(cfg["general"]["excel_path"])
    jobs = store.jobs_this_week()
    suggestion = _get_suggestion(jobs, cfg)
    plain, html = email_report(jobs, suggestion, "weekly")
    subject = cfg["notifications"]["email"].get("subject_weekly", "JobScout weekly report")
    subject += f" — week {datetime.now().isocalendar().week}"
    if cfg.get("notifications", {}).get("email", {}).get("enabled", True):
        return 0 if email_notify.send(subject, plain, html) else 1
    print(plain)
    return 0


def cmd_status(cfg: dict) -> int:
    store = ExcelStore(cfg["general"]["excel_path"])
    total = len(store.existing_ids())
    today = len(store.jobs_today())
    week = len(store.jobs_this_week())
    enabled = [n for n, s in cfg.get("sources", {}).items() if s.get("enabled")]
    print(f"JobScout v{__version__}")
    print(f"Excel store : {cfg['general']['excel_path']}")
    print(f"Jobs total  : {total}  |  today: {today}  |  this week: {week}")
    print(f"Sources on  : {', '.join(enabled) or 'none'}")
    print(f"AI model    : {cfg['ai'].get('provider')}/{cfg['ai'].get('model')} "
          f"@ {cfg['ai'].get('base_url')}")
    return 0


def cmd_test(cfg: dict, what: str) -> int:
    import requests
    if what == "telegram":
        ok = tg_notify.send("✅ JobScout test message — Telegram channel works.", cfg)
    elif what == "email":
        ok = email_notify.send("JobScout test", "Email channel works.",
                               "<p>✅ <b>Email channel works.</b></p>")
    elif what == "ollama":
        try:
            r = requests.get(f"{cfg['ai']['base_url'].rstrip('/')}/api/tags", timeout=10)
            r.raise_for_status()
            models = [m["name"] for m in r.json().get("models", [])]
            print("Ollama reachable. Models:", ", ".join(models) or "(none pulled)")
            ok = cfg["ai"]["model"] in models or any(
                m.startswith(cfg["ai"]["model"].split(":")[0]) for m in models)
            if not ok:
                print(f"⚠ configured model '{cfg['ai']['model']}' not pulled — "
                      f"run: ollama pull {cfg['ai']['model']}")
                ok = True  # server reachable is a pass; missing model is a warning
        except Exception as e:  # noqa: BLE001
            print("Ollama NOT reachable:", e)
            ok = False
    else:
        print("Unknown test target. Use: telegram | email | ollama")
        return 2
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="jobscout", description="JobScout job-search agent")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan")
    rp = sub.add_parser("report")
    rp.add_argument("kind", choices=["daily", "daily-email", "weekly"])
    sub.add_parser("status")
    tp = sub.add_parser("test")
    tp.add_argument("what", choices=["telegram", "email", "ollama"])

    args = p.parse_args(argv)
    cfg = load_config()
    _setup_logging(cfg)

    if args.cmd == "scan":
        return cmd_scan(cfg)
    if args.cmd == "report":
        return {"daily": cmd_report_daily_telegram,
                "daily-email": cmd_report_daily_email,
                "weekly": cmd_report_weekly}[args.kind](cfg)
    if args.cmd == "status":
        return cmd_status(cfg)
    if args.cmd == "test":
        return cmd_test(cfg, args.what)
    return 2


if __name__ == "__main__":
    sys.exit(main())
