"""Facebook Groups source — OPTIONAL and disabled by default.

Facebook provides no public API for reading group feeds, and automated
scraping of Facebook while logged in violates Facebook's Terms of Service
and can get an account restricted. This source is therefore:

  * disabled by default in config/jobscout.yaml
  * best-effort only: it fetches the mobile (mbasic) rendering of each
    group using a session cookie you export from your own browser
    (FB_COOKIE in .env, the full `Cookie:` header value)

Use at your own risk, or better: rely on the group's email notifications /
manual review, and let the other four sources do the automated work.
"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup

from ..config import env
from ..models import Job
from ..scoring import matches_keywords
from .base import BaseSource


class FacebookGroupsSource(BaseSource):
    name = "facebook_groups"

    def fetch(self) -> list[Job]:
        cookie = env("FB_COOKIE")
        if not cookie:
            self.log.warning("facebook_groups enabled but FB_COOKIE not set — skipping")
            return []
        self.session.headers["Cookie"] = cookie
        jobs: list[Job] = []
        for group_url in self.cfg.get("groups", []):
            m = re.search(r"groups/(\d+)", group_url)
            if not m:
                continue
            gid = m.group(1)
            url = f"https://mbasic.facebook.com/groups/{gid}"
            try:
                html = self.get(url).text
            except Exception as e:  # noqa: BLE001
                self.log.warning("facebook group %s fetch failed: %s", gid, e)
                continue
            jobs.extend(self._parse(html, gid))
            self.polite_sleep(3, 6)
        return jobs

    def _parse(self, html: str, gid: str) -> list[Job]:
        soup = BeautifulSoup(html, "html.parser")
        out: list[Job] = []
        limit = int(self.cfg.get("max_posts_per_group", 30))
        for div in soup.find_all("div", limit=400):
            text = div.get_text(" ", strip=True)
            if not (40 < len(text) < 600):
                continue
            if not matches_keywords(text, self.global_cfg):
                continue
            link = div.find("a", href=re.compile(r"/(groups/.+/permalink|story\.php)"))
            url = ("https://www.facebook.com" + link["href"].split("&refid")[0]) if link else ""
            title = text[:120]
            out.append(Job(
                title=title,
                description=text[:500],
                url=url,
                source="facebook",
                location="Facebook grupa",
            ))
            if len(out) >= limit:
                break
        return out
