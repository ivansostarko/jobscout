"""MojPosao.hr source (Croatian job board).

Uses the public keyword search and parses result cards. Croatian boards
change markup occasionally — all selectors live at the top of this file.
"""
from __future__ import annotations

import urllib.parse

from bs4 import BeautifulSoup

from ..models import Job
from ..scoring import matches_keywords
from .base import BaseSource

SEARCH_PATH = "/pretraga-poslova/"
# Candidate selectors, tried in order (site markup varies between releases)
CARD_SELECTORS = ["article", "div.job-item", "li.job", "div[class*='JobCard']"]
TITLE_SELECTORS = ["h2 a", "h3 a", "a[class*='title']", "a[href*='/posao/']", "a[href*='/radno-mjesto/']"]


class MojPosaoSource(BaseSource):
    name = "mojposao"

    def fetch(self) -> list[Job]:
        base = self.cfg.get("base_url", "https://www.mojposao.hr").rstrip("/")
        keywords = (self.global_cfg["search"].get("keywords", [])
                    + self.global_cfg["search"].get("keywords_hr", []))
        jobs: list[Job] = []
        for kw in keywords:
            url = f"{base}{SEARCH_PATH}?{urllib.parse.urlencode({'q': kw})}"
            try:
                html = self.get(url).text
            except Exception as e:  # noqa: BLE001
                if "403" in str(e):
                    self.log.warning(
                        "mojposao returned 403 — the site sits behind CloudFront bot "
                        "protection and blocks datacenter/foreign IPs. Run JobScout "
                        "from a Croatian residential connection (see docs/SOURCES.md)."
                    )
                    return []
                self.log.warning("mojposao query failed (%s): %s", kw, e)
                continue
            jobs.extend(self._parse(html, base))
            self.polite_sleep()
        return self._filter_locations(jobs)

    def _parse(self, html: str, base: str) -> list[Job]:
        soup = BeautifulSoup(html, "html.parser")
        out: list[Job] = []
        cards = []
        for sel in CARD_SELECTORS:
            cards = soup.select(sel)
            if cards:
                break
        for card in cards:
            a = None
            for tsel in TITLE_SELECTORS:
                a = card.select_one(tsel)
                if a:
                    break
            if not a:
                continue
            title = a.get_text(strip=True)
            if not title or not matches_keywords(title, self.global_cfg):
                continue
            href = a.get("href") or ""
            if href.startswith("/"):
                href = base + href
            text = card.get_text(" ", strip=True)
            out.append(Job(
                title=title,
                company=self._guess_company(card),
                location=self._guess_location(text),
                url=href,
                source="mojposao",
                category="IT / Management",
            ))
        return out

    @staticmethod
    def _guess_company(card) -> str:
        for sel in ["h3", ".company", "[class*='company']", "h4"]:
            el = card.select_one(sel)
            if el and el.get_text(strip=True):
                return el.get_text(strip=True)
        return ""

    @staticmethod
    def _guess_location(text: str) -> str:
        for city in ("Zagreb", "Bjelovar", "Split", "Rijeka", "Osijek", "Remote", "Hrvatska"):
            if city.lower() in text.lower():
                return city
        return ""

    def _filter_locations(self, jobs: list[Job]) -> list[Job]:
        wanted = [l.lower() for l in self.cfg.get("locations", [])]
        if not wanted or any("cijela" in w for w in wanted):
            return jobs
        return [j for j in jobs if not j.location or j.location.lower() in wanted]
