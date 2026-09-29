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

- Checkbox progress, saved only in your own browser (no accounts, no server)
- "Skip what doesn't apply to you": hide items for things like Selective Service or foreign accounts, and the counts adjust
- Sticky section bar with per-section progress (e.g. 2/5); checked items collapse to their title
- "When can I apply?" calculator with a countdown and an add-to-calendar download
- Trip tracker that flags trips of 6+ months and 1+ year
- WhatsApp share, copy link, and print/PDF
- Works in light and dark mode
- Anonymous running totals (free Abacus counting API): visits, where they came from as one of a few fixed buckets, and which sections get used. No cookies, no IDs. The page sends nothing that identifies the visitor. As with any web server, GitHub Pages and Abacus see the visitor's IP address. Totals are on `stats.html`

## Citizenship test practice (`civics.html`)

- All 128 questions and answers of the 2025 civics test, taken from USCIS form M-1778 (09/25), in `questions.json`
- Practice cards with self-grading and a read-aloud button, a mock test that stops when the result is decided (20 questions, 12 to pass; 65/20: 10 and 6), a list of missed questions, and progress by topic
- Flash cards that turn over, a full-screen view, and an auto-play mode that goes through the questions on its own and keeps the screen awake
- Previous and Next on every card, a card you miss comes back a few cards later, and you can hear the question or the answer, at normal or slow speed
- A searchable list of all 128 questions with your own answers filled in, which prints cleanly
- Learn mode: twelve chapters matching the official study guide, with a short "why" for each of the 128 answers in `why.json`. The notes are based on the USCIS 2025 Civics Test Study Guide and were checked against it by a second reader
- Reading and writing practice for the English test: read a sentence aloud, or write one as the page dictates it. The sentences use only words from the official USCIS reading and writing vocabulary lists
- Enter a ZIP code to fill in your own senators, representative, governor and state capital. The ZIP code is matched on the device against `zip.json` and `zipcd.json` (built from U.S. Census Bureau files for the 119th Congress) and is never sent anywhere. A ZIP code in one congressional district picks it for you; one that crosses a line offers only the districts it touches; one that is not in the Census table, such as a PO box, shows every district in the state. `build_zip.py` rebuilds both files after each redistricting. The page compares the Congress number of `zipcd.json` with that of the House member list in `officials.json`, and stops picking a district when they differ
- Interview practice: every yes-or-no question in Part 9 of Form N-400 (edition 01/20/25) in the form's exact words, with a plain-words version and word meanings, plus questions about you, the ten commands from the USCIS exercise, and the Oath of Allegiance. It explains what the questions mean and never how to answer them. Content is in `interview.json`
- The 10 official steps to naturalization in one picture, drawn on the page from `steps.json`. `make_steps_picture.py` draws `naturalization-steps.png` from the same file for saving and sharing
- Works offline after the first visit and can be added to a phone's home screen (`sw.js`, `civics.webmanifest`). While online it always fetches the current page and the current officials
- Progress, ZIP code and state are saved only in the visitor's own browser

## How it stays current

- `update_news.py` pulls the official USCIS Alerts RSS feed into `news.json`. A GitHub Action runs it every day and commits only when something changed.
- `update_officials.py` rebuilds `officials.json` every day from senate.gov, clerk.house.gov, the National Governors Association and the USCIS test updates page. A source that fails or returns an implausible count keeps its previous data and fails the run, so GitHub emails the owner.
- `check_links.py` runs every Monday and fails the workflow (GitHub emails the owner) if any link on either page returns 404 or 410, or points to a website that no longer exists. Links it cannot check (some sites answer 403 to scripts) are listed in the log.
- The scripts are plain Python 3, standard library only. Run any of them by hand, for example `python3 update_news.py`. Only `make_steps_picture.py` needs more: Pillow, and the Arial fonts on a Mac.

## Disclaimer

This is not legal advice. It's an unofficial, community-made checklist and isn't connected to USCIS or any government agency. Rules and fees change, so always check the official links or talk to an immigration attorney. Last reviewed September 2026.
