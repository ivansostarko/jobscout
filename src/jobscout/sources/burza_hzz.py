"""Burza rada (HZZ) source — Croatian Employment Service job market.

burzarada.hzz.hr is a legacy ASP.NET (WebForms) application driven by
postbacks, which makes deterministic scraping fragile. This source does a
best-effort GET of the public listing page and extracts job links; if HZZ
changes markup, update the selectors below (see docs/SOURCES.md).
"""
from __future__ import annotations

from bs4 import BeautifulSoup

from ..models import Job
from ..scoring import matches_keywords
from .base import BaseSource

LISTING_PATH = "/Posloprimac_RadnaMjesta.aspx"
JOB_LINK_HINTS = ("RadnoMjesto", "Detalji", "oglas")


class BurzaHzzSource(BaseSource):
    name = "burza_hzz"

    def fetch(self) -> list[Job]:
        base = self.cfg.get("base_url", "https://burzarada.hzz.hr").rstrip("/")
        try:
            html = self.get(base + LISTING_PATH).text
        except Exception as e:  # noqa: BLE001
            self.log.warning("burza HZZ fetch failed: %s", e)
            return []
        soup = BeautifulSoup(html, "html.parser")
        out: list[Job] = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            title = a.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            if not any(h.lower() in href.lower() for h in JOB_LINK_HINTS):
                continue
            if not matches_keywords(title, self.global_cfg):
                continue
            if href.startswith("/"):
                href = base + href
            elif not href.startswith("http"):
                href = f"{base}/{href}"
            out.append(Job(
                title=title,
                url=href,
                source="burza_hzz",
                category="Informatički, računalni i stručnjaci za Internet",
                location="Hrvatska",
            ))
        return out
