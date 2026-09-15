# Job Search

Automated job-application pipeline: a daily scraper finds and scores new postings, and Claude Code (via `CLAUDE.md`) turns each queued posting into a tailored resume, cover letter, and interview prep doc — all tracked in a single spreadsheet.

## How it fits together

1. **`job_scraper/job_scraper.py`** scrapes LinkedIn and Indeed (via JobSpy) across a configured list of search terms/locations, scores each new posting against the keyword banks in `job_scraper/keywords.py`, and writes results to `Tracker.xlsx`:
   - Top 50% of new postings → `Sheet1`, status `queued`, with a suggested base CV (software/hardware/IT, EN/FR).
   - Bottom 50% → `Sheet2`, status `skipped`.
   - Already-tracked URLs (either sheet) are never re-added.
2. **`CLAUDE.md`** defines the workflow Claude Code follows for each queued job: pull the matching reference resume from Overleaf, score it against the job description, produce a tailored one-page resume (LaTeX + PDF), mock interview questions, a cover letter (French if the job is in Quebec), and mark the tracker row `created`.
3. **`Overleaf-mcp/`** is the MCP server/connector Claude Code uses to read and edit the reference resumes stored in Overleaf.
4. **`Watch-TexFiles.ps1`** / **`Install-TexWatcher.ps1`** watch the CV output folder and auto-compile any `.tex` file to PDF with `pdflatex` as soon as it's written or changed; `Install-TexWatcher.ps1` registers the watcher as a Windows Scheduled Task so it starts automatically at login.
5. **`Tracker.xlsx`** / **`Tracker_Backup.xlsx`** is the single source of truth for application status. `Tracker_Backup.xlsx` is used as a fallback copy if the tracker can't be written directly (see Tracker Rules in `CLAUDE.md`).

## Layout

```
Job_Search/
├── CLAUDE.md                Workflow instructions for Claude Code
├── Tracker.xlsx             Job tracker (Sheet1 = queued/created, Sheet2 = skipped)
├── Tracker_Backup.xlsx      Fallback copy of the tracker
├── job_scraper/
│   ├── job_scraper.py       Daily scrape + score + tracker update
│   └── keywords.py          Keyword banks per CV type, used for scoring
├── Overleaf-mcp/            MCP server for reading/editing resumes in Overleaf
├── Watch-TexFiles.ps1       Auto-compiles .tex → .pdf on save
└── Install-TexWatcher.ps1   Registers the watcher as a scheduled task
```

## Setup

- **Scraper**: requires Python 3 with `pandas`, `openpyxl`, and `jobspy` installed. Run manually with:
  ```bash
  python3 job_scraper/job_scraper.py
  ```
  or schedule it to run daily (the docstring assumes a 20:00 run via the Claude scheduler).
- **TeX watcher**: requires a MiKTeX installation with `pdflatex` on `PATH`. Update the `INSERT PATH` placeholders in `Watch-TexFiles.ps1` and `Install-TexWatcher.ps1` to your CV folder, then run `Install-TexWatcher.ps1` as Administrator once.
- **Overleaf connector**: see [`Overleaf-mcp/README.md`](Overleaf-mcp/README.md) for setup; update the `INSERT PATH` placeholder in `CLAUDE.md` to point at it.

## License

MIT — see [`LICENSE`](LICENSE).
