#!/usr/bin/env python3
"""
job_scraper.py — Daily automated job discovery pipeline.

Scrapes LinkedIn + Indeed via JobSpy, scores every new posting against
the CV keyword banks, keeps the top 10 (status: 'queued') and logs the
rest (status: 'skipped') — all written directly to Tracker.xlsx.
A prep folder with the raw JD and match details is created for every
queued job, ready for the full Claude CLAUDE.md workflow.

Usage:
    python3 job_scraper.py          # run once
    (scheduled daily at 20:00 via Claude scheduler)
"""

import sys
import os
import time
import random
from pathlib import Path
from datetime import date, datetime
import re

import pandas as pd
import openpyxl

# ── Paths ──────────────────────────────────────────────────────────────────────
_HERE       = Path(__file__).parent
CV_DIR      = _HERE.parent                              # C:\Users\Admin\Documents\CV
TRACKER     = CV_DIR / 'Tracker.xlsx'

# ── Search configuration ───────────────────────────────────────────────────────
SEARCHES: list[dict] = [
    # Ottawa — Software
    dict(term='junior software developer',          location='Ottawa, ON',   sites=['linkedin', 'indeed']),
    dict(term='junior software engineer',           location='Ottawa, ON',   sites=['linkedin', 'indeed']),
    dict(term='junior embedded software developer', location='Ottawa, ON',   sites=['linkedin', 'indeed']),

    # Ottawa — AI / Data
    dict(term='junior data analyst',  location='Ottawa, ON',   sites=['linkedin', 'indeed']),
    dict(term='junior data scientist', location='Ottawa, ON',   sites=['linkedin', 'indeed']),
    dict(term='junior machine learning', location='Ottawa, ON',   sites=['linkedin', 'indeed']),

    # Ottawa — Hardware
    dict(term='junior hardware engineer',           location='Ottawa, ON',   sites=['linkedin', 'indeed']),
    dict(term='junior FPGA developer',              location='Ottawa, ON',   sites=['linkedin', 'indeed']),
    # Ottawa — IT
    dict(term='systems administrator',       location='Ottawa, ON',   sites=['linkedin', 'indeed']),
    # Montreal — Software (FR/EN)
    dict(term='junior développeur logiciel',        location='Montreal, QC', sites=['linkedin', 'indeed']),
    dict(term='junior génie logiciel',          location='Montreal, QC', sites=['linkedin', 'indeed']),
    dict(term='junior développeur circuit intégré',          location='Montreal, QC', sites=['linkedin', 'indeed']),

    # Montreal — AI / Data
    dict(term='junior data analyste',                location='Montreal, QC', sites=['linkedin', 'indeed']),
    dict(term='junior data scientiste',              location='Montreal, QC', sites=['linkedin', 'indeed']),
    dict(term='junior machine learning',            location='Montreal, QC', sites=['linkedin', 'indeed']),

    # Montreal — Hardware
    dict(term='junior génie électrique',           location='Montreal, QC', sites=['linkedin', 'indeed']),
    dict(term='junior FPGA développeur',              location='Montreal, QC', sites=['linkedin', 'indeed']), 

    # Montreal — IT
    dict(term='administrateur système',       location='Montreal, QC',   sites=['linkedin', 'indeed']),   
]

RESULTS_PER_SEARCH = 8   # JobSpy cap per call; tune to stay under rate limits
HOURS_OLD          = 26   # catch jobs posted in the last ~24 h (with buffer)


# ══════════════════════════════════════════════════════════════════════════════
#  Scoring
# ══════════════════════════════════════════════════════════════════════════════

sys.path.insert(0, str(_HERE))
from keywords import suggest_base   # noqa: E402

#scoring is done in keywords.py, this file just calls the function and uses the score to sort the jobs into queued and skipped.

# ══════════════════════════════════════════════════════════════════════════════
#  Tracker integration
# ══════════════════════════════════════════════════════════════════════════════

def _safe_str(v) -> str:
    return '' if v is None or (isinstance(v, float) and v != v) else str(v).strip()


def get_tracked_urls() -> set[str]:
    """
    Return all URLs already logged in Tracker.xlsx — both Sheet1 (queued/created)
    and Sheet2 (skipped) — so neither sheet ever gets duplicate entries.
    """
    wb = openpyxl.load_workbook(TRACKER)
    urls: set[str] = set()
    for sheet in wb.worksheets:
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row and row[4]:
                urls.add(_safe_str(row[4]))
    wb.close()
    return urls


def _ensure_sheet2(wb: openpyxl.Workbook) -> openpyxl.worksheet.worksheet.Worksheet:
    """Return Sheet2, creating it with a header row if it doesn't exist yet."""
    if 'Sheet2' not in wb.sheetnames:
        ws2 = wb.create_sheet('Sheet2')
        ws2.append(['Job Title', 'Company', 'Score', 'Status', 'URL', 'Description', 'Date Found'])
    return wb['Sheet2']


def append_jobs_to_tracker(queued: list[dict], skipped: list[dict]) -> None:
    """
    Queued jobs  → Sheet1 (main tracker), columns A-E, status='queued'.
    Skipped jobs → Sheet2,               columns A-G, status='skipped' + date.

    Existing Sheet1 rows and their column D values are NEVER touched.
    """
    wb = openpyxl.load_workbook(TRACKER)

    # ── Sheet1: queued jobs only ───────────────────────────────────────────
    ws1 = wb.active
    next_row = ws1.max_row + 1
    for job in queued:
        ws1.cell(next_row, 1).value = job['title']
        ws1.cell(next_row, 2).value = job['company']
        ws1.cell(next_row, 3).value = job['score']
        ws1.cell(next_row, 4).value = 'queued'
        ws1.cell(next_row, 5).value = job['url']
        ws1.cell(next_row, 6).value = job['description']
        next_row += 1

    # ── Sheet2: skipped jobs ───────────────────────────────────────────────
    ws2 = _ensure_sheet2(wb)
    today = str(date.today())
    for job in skipped:
        ws2.append([
            job['title'],
            job['company'],
            job['score'],
            'skipped',
            job['url'],
            job['description'],
            today,
        ])

    wb.save(TRACKER)
    wb.close()


# ══════════════════════════════════════════════════════════════════════════════
#  Scraping
# ══════════════════════════════════════════════════════════════════════════════

def scrape_all() -> pd.DataFrame:
    """Run all configured searches and return a deduplicated DataFrame."""
    from jobspy import scrape_jobs   # imported here so the module is optional at import time

    frames: list[pd.DataFrame] = []
    for i, s in enumerate(SEARCHES):
        try:
            df = scrape_jobs(
                site_name        = s['sites'],
                search_term      = s['term'],
                location         = s['location'],
                results_wanted   = RESULTS_PER_SEARCH,
                hours_old        = HOURS_OLD,
                country_indeed   = 'Canada',
                linkedin_fetch_description = True,
            )
            print(f"  {s['term'][:35]:<35} @ {s['location']}: {len(df)} jobs")
            frames.append(df)
        except Exception as exc:
            print(f"  WARN [{s['term']} @ {s['location']}]: {exc}")

        # Polite pause between requests to avoid rate-limiting
        if i < len(SEARCHES) - 1:
            delay = random.uniform(2, 5)
            print(f"  (waiting {delay:.1f}s…)")
            time.sleep(delay)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(subset=['job_url'])
    return combined


# ══════════════════════════════════════════════════════════════════════════════
#  Digest
# ══════════════════════════════════════════════════════════════════════════════

def print_digest(queued: list[dict], skipped: list[dict]) -> None:
    sep = '─' * 90
    print(f"\n{sep}")
    print(f"  DAILY JOB DIGEST — {datetime.now():%Y-%m-%d %H:%M}")
    print(sep)

    print(f"\n  QUEUED FOR PREP ({len(queued)} jobs):\n")
    print(f"  {'Score':>5}  {'Company':<28}  {'Title':<38}  {'Base CV'}")
    print(f"  {'─'*5}  {'─'*28}  {'─'*38}  {'─'*7}")
    for j in queued:
        print(f"  {j['score']:>5}  {j['company'][:28]:<28}  {j['title'][:38]:<38}  {j['base_cv']}")

    if skipped:
        print(f"\n  SKIPPED ({len(skipped)} jobs below top-50% threshold):\n")
        print(f"  {'Score':>5}  {'Company':<28}  {'Title'}")
        print(f"  {'─'*5}  {'─'*28}  {'─'*38}")
        for j in skipped:
            print(f"  {j['score']:>5}  {j['company'][:28]:<28}  {j['title'][:38]}")

    print(f"\n{sep}\n")


# ══════════════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    print(f"\n[{ts}] Job scraper starting…\n")

    # ── 1. Scrape ──────────────────────────────────────────────────────────
    raw = scrape_all()
    if raw.empty:
        print("No jobs returned by any search. Exiting.")
        return
    print(f"\nTotal unique raw jobs: {len(raw)}")

    # ── 2. Deduplicate and filter already-tracked URLs ────────────────────
    #    Dedup runs BEFORE scoring so we never waste time scoring a job
    #    we've already seen, and the top-50% split is over truly new jobs only.
    tracked_urls = get_tracked_urls()

    # Within-batch dedup: same URL from multiple searches
    raw = raw.drop_duplicates(subset=['job_url'])
    # Within-batch dedup: same (title, company) even if URL differs slightly
    raw = raw.drop_duplicates(subset=['title', 'company'])

    # Cross-session dedup: remove anything already in Tracker (Sheet1 or Sheet2)
    new_mask    = ~raw['job_url'].isin(tracked_urls)
    new_jobs_df = raw[new_mask].copy()
    print(f"After dedup — new jobs not in Tracker: {len(new_jobs_df)}")

    if new_jobs_df.empty:
        print("Nothing new today.")
        return

    # ── 3. Score every new job ─────────────────────────────────────────────
    scored: list[dict] = []
    for _, row in new_jobs_df.iterrows():
        title    = _safe_str(row.get('title'))
        company  = _safe_str(row.get('company')) or 'Unknown'
        location = _safe_str(row.get('location'))
        url      = _safe_str(row.get('job_url'))
        desc     = _safe_str(row.get('description'))

        # scoring see keywords.py
        score_suggest=suggest_base(title+' '+desc, location)

        seperator = score_suggest.find('_')
        score = int(score_suggest[:seperator])
        suggested_base = score_suggest[seperator+1:]

        scored.append({
            'title':       title,
            'company':     company,
            'location':    location,
            'description':  desc,
            'url':         url,
            'score':       score,
            'description': desc,
            'base_cv':     suggested_base,
        })

    scored.sort(key=lambda j: j['score'], reverse=True)

    # ── 4. Top 10 split ──────────────────────────────────────────────────
    cutoff  = min(len(scored), 10)   # ceiling of 10 jobs, or fewer if <10 new jobs
    queued  = scored[:cutoff]
    skipped = scored[cutoff:]

    for j in queued:
        j['status'] = 'queued'
    for j in skipped:
        j['status'] = 'skipped'

    print(f"Top 10 → queued: {len(queued)}   Rest → skipped: {len(skipped)}\n")

    # ── 6. Write to Tracker.xlsx ──────────────────────────────────────────
    #    Queued → Sheet1 (main tracker)   Skipped → Sheet2
    append_jobs_to_tracker(queued, skipped)
    print(f"\nTracker updated: {len(queued)} queued (Sheet1) · {len(skipped)} skipped (Sheet2).")

    # ── 7. Digest ─────────────────────────────────────────────────────────
    print_digest(queued, skipped)


if __name__ == '__main__':
    main()
