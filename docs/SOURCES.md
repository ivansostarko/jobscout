# Source notes & legal considerations

## 1. LinkedIn (`sources.linkedin`)

Uses the public logged-out endpoint
`linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search` — the same one
the anonymous jobs page calls. No credentials are used or stored.

- Filters: keywords × locations (Zagreb, Bjelovar, Croatia, Riyadh) ×
  optional `f_WT` workplace type (1 onsite / 2 remote / 3 hybrid), limited
  to postings from the last `posted_within_hours` (default 24 h).
- Rate limiting: random 1.5–3.5 s delay between queries, rotating desktop
  user agents. Keep the defaults — LinkedIn aggressively blocks abusive
  clients, and heavy automated access may breach LinkedIn's User Agreement.
- If you start receiving HTTP 429/999, reduce keywords/locations or increase
  delays in `sources/base.py`.

## 2. MojPosao.hr (`sources.mojposao`)

Public keyword search (`/pretraga-poslova/?q=`).

> **Geo/bot blocking:** MojPosao sits behind CloudFront bot protection and
> returns **HTTP 403** to datacenter and many foreign IPs. Run JobScout from
> a normal Croatian residential connection (which is the typical setup) and
> it works; from a VPS abroad it will likely be blocked — the source fails
> soft and the rest of the scan continues. The parser tries several
card/title selector candidates (top of `sources/mojposao.py`) because the
site redesigns periodically. If results drop to zero, open the search page
in a browser, inspect the job card markup, and update `CARD_SELECTORS` /
`TITLE_SELECTORS`.

## 3. Posao.hr (`sources.posao_hr`)

Public keyword search (`/pretraga/?q=`). Parsing is link-pattern based
(`a[href*='/posao/']`), which survives most redesigns.

## 4. Burza rada — HZZ (`sources.burza_hzz`)

> **Geo blocking:** like many Croatian government services, HZZ may return
> **503** to foreign/datacenter IPs. Works from Croatian connections.

`burzarada.hzz.hr` is a legacy ASP.NET WebForms app driven by postbacks, so
deep filtered scraping is fragile. JobScout does a best-effort parse of the
public listing page and keyword-filters the anchors. HZZ also offers job
mediation services — for the most reliable HZZ coverage consider their
email alerts as a complement.

## 5. Facebook groups (`sources.facebook_groups`) — read this before enabling

Facebook **does not provide any API** for reading group feeds, and
automating a logged-in account (even read-only) **violates Facebook's Terms
of Service** and risks account restriction or ban. That's why this source is
`enabled: false` by default.

If you still want it:
1. Log into Facebook in your browser, open DevTools → Network → any request
   → copy the full `Cookie:` request header value.
2. Put it in `.env` as `FB_COOKIE=...`
3. Set `sources.facebook_groups.enabled: true`.

JobScout will fetch the lightweight `mbasic.facebook.com` rendering of each
group at a slow rate (3–6 s between groups) and keyword-match post texts.
Safer alternatives: turn on group notifications in Facebook and review
manually, or ask group admins about email digests.

## General etiquette

- One scan per hour, small result caps, randomized delays — the defaults are
  deliberately polite. Don't turn JobScout into a hammering crawler.
- All parsers fail soft: a broken/blocked source logs an error and returns
  an empty list; the scan and the reports continue.
