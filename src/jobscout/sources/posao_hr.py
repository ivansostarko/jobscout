"""Posao.hr source (Croatian job board).

Posao.hr's keyword search is form/POST driven, but its public listing page
(/poslovi/) exposes all active ads as /oglasi/<slug>/<id>/ links, so we
fetch the listing (a few pages) and keyword-filter locally — this is far
more robust against redesigns than form scraping.
"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup

from ..models import Job
from ..scoring import matches_keywords
from .base import BaseSource

LISTING_PATH = "/poslovi/"
PAGES = 3                      # how many listing pages to walk
JOB_LINK_RE = re.compile(r"/oglasi/[^\"]+/\d+/?$")
EXPIRES_RE = re.compile(r"(Expires in .*|Isti[čc]e .*)$", re.I)


class PosaoHrSource(BaseSource):
    name = "posao_hr"

    def fetch(self) -> list[Job]:
        base = self.cfg.get("base_url", "https://www.posao.hr").rstrip("/")
        jobs: list[Job] = []
        seen: set[str] = set()
        for page in range(1, PAGES + 1):
            url = base + LISTING_PATH if page == 1 else f"{base}{LISTING_PATH}stranica/{page}/"
            try:
                html = self.get(url).text
            except Exception as e:  # noqa: BLE001
                self.log.warning("posao.hr page %d failed: %s", page, e)
                break
            new = self._parse(html, seen)
            if not new:
                break
            jobs.extend(new)
            self.polite_sleep()
        return jobs

    def _parse(self, html: str, seen: set[str]) -> list[Job]:
        soup = BeautifulSoup(html, "html.parser")
        out: list[Job] = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not JOB_LINK_RE.search(href) or href in seen:
                continue
            seen.add(href)
            text = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
            text = EXPIRES_RE.sub("", text).strip()
            if not text:
                continue
            # anchor text is usually "Title (m/ž) Location"
            m = re.match(r"^(.*?\(m/[žz]\))\s*(.*)$", text, re.I)
            if m:
                title, location = m.group(1).strip(), m.group(2).strip()
            else:
                title, location = text, ""
            if not matches_keywords(title, self.global_cfg):
                continue
            out.append(Job(
                title=title,
                location=location,
                url=href,
                source="posao_hr",
                category="IT / Management",
            ))
        return out
