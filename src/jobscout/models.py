"""Data model for a job posting."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


@dataclass
class Job:
    title: str
    company: str = ""
    location: str = ""
    source: str = ""                 # linkedin | mojposao | posao_hr | burza_hzz | facebook
    url: str = ""
    workplace_type: str = ""         # onsite | remote | hybrid | ""
    posted_at: str = ""              # as reported by the site
    description: str = ""
    salary: str = ""
    category: str = ""
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    score: float = 0.0

    @property
    def job_id(self) -> str:
        """Stable dedup key. Prefer the canonical URL; fall back to content hash."""
        if self.url:
            base = re.sub(r"[?#].*$", "", self.url.strip().lower())
        else:
            base = f"{_norm(self.source)}|{_norm(self.title)}|{_norm(self.company)}|{_norm(self.location)}"
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["job_id"] = self.job_id
        return d
