"""AI layer — talks to a local Ollama server (default model: qwen2.5).

Used to turn the day's job list into a short, human "what should I apply
to and why" recommendation. If Ollama is unreachable the pipeline degrades
gracefully to the deterministic score-based ranking, so reports always go out.
"""
from __future__ import annotations

import json
import logging

import requests

log = logging.getLogger("jobscout.ai")

SYSTEM_PROMPT = (
    "You are JobScout, a career assistant for a senior technology executive. "
    "Given a list of job postings (title, company, location, source, score, url), "
    "pick the best matches and explain briefly why the candidate should apply. "
    "Be concrete and concise. Answer with: (1) 'Apply today' — max 5 jobs with a "
    "one-line reason each, (2) 'Worth watching' — max 3 jobs, (3) one sentence of "
    "overall market observation. Plain text only, no markdown tables."
)


def suggest(jobs: list[dict], cfg: dict) -> str:
    ai = cfg.get("ai", {})
    if not ai.get("enabled", True) or not jobs:
        return ""
    top = sorted(jobs, key=lambda j: float(j.get("score") or 0), reverse=True)
    top = top[: int(ai.get("max_jobs_in_prompt", 40))]
    lines = [
        f"- {j['title']} | {j.get('company','')} | {j.get('location','')} | "
        f"{j.get('source','')} | score={j.get('score','')} | {j.get('url','')}"
        for j in top
    ]
    profile = ai.get("profile", "")
    prompt = (
        f"Candidate profile: {profile}\n\n"
        f"Today's job postings:\n" + "\n".join(lines) +
        "\n\nWhich should the candidate apply to and why?"
    )
    try:
        r = requests.post(
            f"{ai.get('base_url', 'http://localhost:11434').rstrip('/')}/api/chat",
            json={
                "model": ai.get("model", "qwen2.5:14b"),
                "stream": False,
                "options": {"temperature": float(ai.get("temperature", 0.3))},
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=180,
        )
        r.raise_for_status()
        return (r.json().get("message") or {}).get("content", "").strip()
    except Exception as e:  # noqa: BLE001
        log.warning("Ollama unavailable (%s) — falling back to score ranking", e)
        return ""


def fallback_suggestion(jobs: list[dict], cfg: dict) -> str:
    """Deterministic recommendation used when the LLM is unavailable."""
    sc = cfg.get("scoring", {})
    min_score = float(sc.get("min_score_to_recommend", 6))
    top_n = int(sc.get("top_n_recommendations", 5))
    ranked = sorted(jobs, key=lambda j: float(j.get("score") or 0), reverse=True)
    picks = [j for j in ranked if float(j.get("score") or 0) >= min_score][:top_n]
    if not picks:
        return "No postings crossed the recommendation threshold today."
    lines = ["Top matches by relevance score:"]
    for j in picks:
        lines.append(f"• {j['title']} — {j.get('company','?')} ({j.get('location','')}) "
                     f"[score {j.get('score')}] {j.get('url','')}")
    return "\n".join(lines)
