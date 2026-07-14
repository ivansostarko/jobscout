"""Smoke tests: dedup, scoring, report building (no network)."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jobscout.models import Job
from jobscout.storage import ExcelStore
from jobscout.scoring import score_job, matches_keywords
from jobscout.report import telegram_report, email_report

CFG = {
    "search": {"keywords": ["CTO", "Project Manager"], "keywords_hr": ["voditelj projekta"],
               "exclude_keywords": ["intern"]},
    "scoring": {"title_weights": {"cto": 10, "project manager": 6},
                "seniority_bonus": 3, "remote_bonus": 2,
                "location_bonus": {"zagreb": 2},
                "min_score_to_recommend": 6, "top_n_recommendations": 5},
}


def test_dedup():
    with tempfile.TemporaryDirectory() as d:
        store = ExcelStore(os.path.join(d, "jobs.xlsx"))
        j1 = Job(title="CTO", company="Acme", url="https://x.com/j/1?ref=abc")
        j2 = Job(title="CTO", company="Acme", url="https://x.com/j/1?utm=zzz")  # same canonical URL
        j3 = Job(title="COO", company="Acme", url="https://x.com/j/2")
        added = store.add_jobs([j1, j2, j3])
        assert len(added) == 2, f"expected 2 unique, got {len(added)}"
        added2 = store.add_jobs([j1, j3])
        assert len(added2) == 0, "re-adding must add nothing"
        assert len(store.existing_ids()) == 2
    print("test_dedup OK")


def test_scoring():
    j = Job(title="Senior CTO", location="Zagreb", workplace_type="remote")
    s = score_job(j, CFG)
    assert s == 10 + 3 + 2 + 2, s
    assert matches_keywords("Project Manager (m/f)", CFG)
    assert not matches_keywords("Marketing intern", CFG)
    assert matches_keywords("Voditelj projekta gradnje", CFG)
    print("test_scoring OK")


def test_reports():
    jobs = [Job(title="CTO", company="Acme", location="Zagreb",
                url="https://x.com/1", source="linkedin", score=12).to_dict()]
    msg = telegram_report(jobs, "Apply to Acme CTO.", "daily")
    assert "CTO" in msg and len(msg) <= 4000
    plain, html = email_report(jobs, "Apply to Acme CTO.", "daily")
    assert "Acme" in plain and "<table" in html
    print("test_reports OK")


if __name__ == "__main__":
    test_dedup(); test_scoring(); test_reports()
    print("ALL TESTS PASSED")
