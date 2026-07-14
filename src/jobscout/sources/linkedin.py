"""LinkedIn Jobs source.

Uses LinkedIn's public "guest" job-search endpoint (the same one the
logged-out jobs page uses). No login required. Selectors are kept at the
top of the file so they are easy to update if LinkedIn changes markup.
"""
from __future__ import annotations

import urllib.parse

from bs4 import BeautifulSoup

from ..models import Job
from ..scoring import matches_keywords
from .base import BaseSource

GUEST_API = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

SEL_CARD = "li"
SEL_TITLE = "h3.base-search-card__title"
SEL_COMPANY = "h4.base-search-card__subtitle"
SEL_LOCATION = "span.job-search-card__location"
SEL_LINK = "a.base-card__full-link"
SEL_DATE = "time"


class LinkedInSource(BaseSource):
    name = "linkedin"

    def fetch(self) -> list[Job]:
        jobs: list[Job] = []
        hours = int(self.cfg.get("posted_within_hours", 24))
        tpr = f"r{hours * 3600}"
        keywords = self.global_cfg["search"]["keywords"]
        max_results = int(self.cfg.get("max_results_per_query", 25))
        wt_filters = self.cfg.get("workplace_filters") or [""]

        for loc in self.cfg.get("locations", []):
            for kw in keywords:
                for wt in wt_filters:
                    params = {
                        "keywords": kw,
                        "location": loc["geo"],
                        "f_TPR": tpr,
                        "start": 0,
                    }
                    if wt:
                        params["f_WT"] = wt
                    url = f"{GUEST_API}?{urllib.parse.urlencode(params)}"
                    try:
                        html = self.get(url).text
                    except Exception as e:  # noqa: BLE001
                        self.log.warning("linkedin query failed (%s @ %s): %s", kw, loc["name"], e)
                        continue
                    jobs.extend(self._parse(html, max_results))
                    self.polite_sleep(1.5, 3.5)
        return jobs

    def _parse(self, html: str, limit: int) -> list[Job]:
        soup = BeautifulSoup(html, "html.parser")
        out: list[Job] = []
        for card in soup.select(SEL_CARD)[:limit]:
            title_el = card.select_one(SEL_TITLE)
            link_el = card.select_one(SEL_LINK)
            if not title_el or not link_el:
                continue
            title = title_el.get_text(strip=True)
            if not matches_keywords(title, self.global_cfg):
                continue
            company_el = card.select_one(SEL_COMPANY)
            loc_el = card.select_one(SEL_LOCATION)
            date_el = card.select_one(SEL_DATE)
            out.append(Job(
                title=title,
                company=company_el.get_text(strip=True) if company_el else "",
                location=loc_el.get_text(strip=True) if loc_el else "",
                url=(link_el.get("href") or "").split("?")[0],
                posted_at=date_el.get("datetime", "") if date_el else "",
                source="linkedin",
            ))
        return out
