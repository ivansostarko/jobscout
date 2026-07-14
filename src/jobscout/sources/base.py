"""Base class for all job sources."""
from __future__ import annotations

import logging
import random
import time

import requests

from ..models import Job

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]


class BaseSource:
    name = "base"

    def __init__(self, source_cfg: dict, global_cfg: dict):
        self.cfg = source_cfg
        self.global_cfg = global_cfg
        self.log = logging.getLogger(f"jobscout.{self.name}")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "hr,en;q=0.8",
        })

    def polite_sleep(self, lo: float = 1.0, hi: float = 3.0) -> None:
        time.sleep(random.uniform(lo, hi))

    def get(self, url: str, **kw) -> requests.Response:
        r = self.session.get(url, timeout=30, **kw)
        r.raise_for_status()
        return r

    def fetch(self) -> list[Job]:
        """Return a list of Job objects. Must be overridden."""
        raise NotImplementedError

    def safe_fetch(self) -> list[Job]:
        try:
            jobs = self.fetch()
            self.log.info("%s: fetched %d jobs", self.name, len(jobs))
            return jobs
        except Exception as e:  # noqa: BLE001 — a broken source must not kill the scan
            self.log.error("%s: fetch failed: %s", self.name, e)
            return []
