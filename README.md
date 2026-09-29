# Green Card Next Steps Checklist

A simple, mobile-friendly checklist for people who just got a U.S. green card (lawful permanent residence).

**Live page:** https://danpune.github.io/greencard-checklist/ · **Citizenship test practice:** https://danpune.github.io/greencard-checklist/civics.html

## What's inside

- First-week tasks: check your card, make copies, carry your card, USCIS online account
- Work: I-9 update, job-change guidance
- IDs and eligibility: Social Security card, REAL ID, Selective Service, children turning 14, AR-11 address changes, voting warning
- Travel: 6-month and 1-year rules, re-entry permit, Form I-407, travel log, Global Entry
- Money and taxes: resident filing, IRS tax transcripts for the N-400, FBAR and Form 8938
- Road to citizenship (N-400): early-filing date calculator, trip tracker, 2025 civics test, fees
- News & updates: latest USCIS alerts, plus official feeds, YouTube channels, podcasts and Reddit to follow
- Sources: official USCIS, SSA, CBP, TSA, IRS, FinCEN and SSS pages

## Features

- Tick-box progress, saved only in your own browser (no accounts, no server)
- "Skip what doesn't apply to you": hide items for things like Selective Service or foreign accounts, and the counts adjust
- Sticky section bar with per-section progress (e.g. 2/5); ticked items collapse to their title
- "When can I apply?" calculator with a countdown and an add-to-calendar download
- Trip tracker that flags trips of 6+ months and 1+ year
- WhatsApp share, copy link, and print/PDF
- Works in light and dark mode
- Anonymous running totals (free Abacus counting API): visits, where they came from as one of a few fixed buckets, and which sections get used. No cookies, no IDs, nothing about the visitor is stored. Totals are on `stats.html`

## Citizenship test practice (`civics.html`)

- All 128 questions and answers of the 2025 civics test, taken from USCIS form M-1778 (09/25), in `questions.json`
- Practice cards with self-grading and a read-aloud button, a mock test that stops when the result is decided (20 questions, 12 to pass; 65/20: 10 and 6), a list of missed questions, and progress by topic
- Reading and writing practice for the English test: read a sentence aloud, or write one as the page dictates it. The sentences use only words from the official USCIS reading and writing vocabulary lists
- Enter a ZIP code to fill in your own senators, representative, governor and state capital. The ZIP code is matched on the device against `zip.json` (built from the U.S. Census 2020 ZCTA file) and is never sent anywhere
- Progress, ZIP code and state are saved only in the visitor's own browser

## How it stays current

- `update_news.py` pulls the official USCIS Alerts RSS feed into `news.json`. A GitHub Action runs it every day and commits only when something changed.
- `update_officials.py` rebuilds `officials.json` every day from senate.gov, clerk.house.gov, the National Governors Association and the USCIS test updates page. A source that fails or returns an implausible count keeps its previous data.
- `check_links.py` runs every Monday and fails the workflow (GitHub emails the owner) if any link on the page returns 404 or 410.
- All scripts are plain Python 3, standard library only. Run any of them by hand, for example `python3 update_news.py`.

## Disclaimer

This is not legal advice. It's an unofficial, community-made checklist and isn't connected to USCIS or any government agency. Rules and fees change, so always check the official links or talk to an immigration attorney. Last reviewed September 2026.
