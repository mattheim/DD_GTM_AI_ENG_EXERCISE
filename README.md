# dd_gtm_ai_eng_exercise

AI workflow: scrape speakers → classify companies → generate outreach emails → export.

**Project Structure**

- `main.py` — Runs the pipeline over `in/speakers.csv`: classifies the company, checks exclusion (skip partners/competitors), and generates emails into `out/email_output.csv`.
- `seed.py` — Minimal seeding script that scrapes the default speakers page and writes `in/speakers.csv`.
- `utils/` — Helper modules used by the pipeline.
  - `utils/scraper.py` — Scrape and CSV writing utilities.
  - `utils/safeparse.py` — Defensive JSON parsing for LLM output.
  - `utils/exclusions.py` — Outreach exclusion (skip competitor/partner).
  - `utils/csv_write.py` — Append rows to `out/email_output.csv`.
- `in/` — Input files (seed writes `in/speakers.csv`).
- `out/` — Output files (pipeline appends to `out/email_output.csv`).
- `.env_sample` — Copy to `.env` and fill in required values.
- `Makefile` — Beginner‑friendly tasks (`setup`, `seed`, `run`).

**Setup**

~these steps get you running:

1) Install Python 3.10+.
- macOS (Homebrew): `brew install python@3.12`

2) Create and activate a virtual environment from the repo folder:
- `python3 -m venv .venv`
- `source .venv/bin/activate`  (Windows: `.\.venv\Scripts\activate`)

3) Install dependencies and seed input data (one command):
- `make setup`
- This creates the venv, installs requirements, and writes `in/speakers.csv`.

4) Configure environment variables:
- Copy `.env_sample` to `.env`.
- Set `OPENAI_API_KEY` and `MODEL_NAME` (for example: `gpt-4o-mini`).

If you prefer manual setup instead of Make:
- `python3 -m venv .venv && source .venv/bin/activate`
- `pip install -r requirements.txt`
- `python3 seed.py`

**Run The Project**

- With Makefile: `make run`
- Or directly: `.venv/bin/python main.py` (Windows: `.\.venv\Scripts\python.exe main.py`)

What happens: 
the program reads `in/speakers.csv`, classifies each company, skips outreach for competitors/partners, and writes emails to `out/email_output.csv`. 
Depending on the size of the input and API latency, this can take a few minutes. 
Basic console logging is included so you can follow progress.
