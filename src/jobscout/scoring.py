"""Deterministic relevance scoring used for ranking and recommendations."""
from __future__ import annotations

from .models import Job

SENIORITY_WORDS = ("senior", "lead", "executive", "chief", "principal")


def score_job(job: Job, cfg: dict) -> float:
    sc = cfg.get("scoring", {})
    title = (job.title or "").lower()
    loc = f"{job.location} {job.workplace_type}".lower()
    score = 0.0
    for kw, w in (sc.get("title_weights") or {}).items():
        if kw.lower() in title:
            score += float(w)
    if any(w in title for w in SENIORITY_WORDS):
        score += float(sc.get("seniority_bonus", 0))
    if "remote" in loc or job.workplace_type == "remote":
        score += float(sc.get("remote_bonus", 0))
    for kw, w in (sc.get("location_bonus") or {}).items():
        if kw.lower() in loc:
            score += float(w)
    return round(score, 1)


def matches_keywords(title: str, cfg: dict) -> bool:
    s = cfg.get("search", {})
    t = (title or "").lower()
    if any(x.lower() in t for x in s.get("exclude_keywords", [])):
        return False
    kws = [k.lower() for k in s.get("keywords", [])] + [k.lower() for k in s.get("keywords_hr", [])]
    # also match broad managerial patterns
    extras = ["manager", "director", "voditelj", "direktor", "head of", "engineer"]
    return any(k in t for k in kws) or any(k in t for k in extras)
