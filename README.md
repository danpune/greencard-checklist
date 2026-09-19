# Green Card Next Steps Checklist

A simple, mobile-friendly checklist for people who just got a U.S. green card (lawful permanent residence).

**Live page:** https://danpune.github.io/greencard-checklist/

## What's inside

- First-week tasks: check your card, make copies, carry your card, USCIS online account
- Work: I-9 update, job-change guidance
- IDs and eligibility: Social Security card, REAL ID, Selective Service, AR-11 address changes, voting warning
- Travel: 6-month and 1-year rules, re-entry permit, Form I-407, travel log, Global Entry
- Money and taxes: resident filing, IRS tax transcripts for the N-400, FBAR and Form 8938
- Road to citizenship (N-400): early-filing date calculator, trip tracker, 2025 civics test, fees
- News & updates: latest USCIS alerts, plus official feeds, YouTube channels, podcasts and Reddit to follow
- Sources: official USCIS, SSA, CBP, TSA, IRS, FinCEN and SSS pages

## Features

- Tick-box progress, saved only in your own browser (no accounts, no server)
- Sticky section bar with per-section progress (e.g. 2/5); ticked items collapse to their title
- "When can I apply?" calculator with a countdown and an add-to-calendar download
- Trip tracker that flags trips of 6+ months and 1+ year
- WhatsApp share, copy link, and print/PDF
- Works in light and dark mode
- Public visit counter in the footer (free Abacus counting API: no cookies, counts once per browser session)

## How it stays current

- `update_news.py` pulls the official USCIS Alerts RSS feed into `news.json`. A GitHub Action runs it every day and commits only when something changed.
- `check_links.py` runs every Monday and fails the workflow (GitHub emails the owner) if any link on the page returns 404 or 410.
- Both scripts are plain Python 3, standard library only. Run either by hand with `python3 update_news.py`.

## Disclaimer

This is not legal advice. It's an unofficial, community-made checklist and isn't connected to USCIS or any government agency. Rules and fees change, so always check the official links or talk to an immigration attorney. Last reviewed September 2026.
