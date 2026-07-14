"""Telegram delivery via Bot API (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID in .env)."""
from __future__ import annotations

import logging

import requests

from ..config import env

log = logging.getLogger("jobscout.telegram")


def send(text: str, cfg: dict) -> bool:
    token = env("TELEGRAM_BOT_TOKEN")
    chat_id = env("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log.error("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID missing in .env")
        return False
    parse_mode = cfg.get("notifications", {}).get("telegram", {}).get("parse_mode", "HTML")
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode,
              "disable_web_page_preview": True},
        timeout=30,
    )
    if r.status_code != 200:
        log.error("Telegram send failed: %s %s", r.status_code, r.text[:300])
        return False
    log.info("Telegram report delivered")
    return True
