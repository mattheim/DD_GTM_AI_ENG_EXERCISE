import asyncio
from pathlib import Path
from typing import List, Dict

from utils.scraper import scrape_dcw_speakers, write_speakers_csv

DEFAULT_URL = "https://www.digitalconstructionweek.com/all-speakers/"
DEFAULT_OUT = Path(__file__).resolve().parent / "in" / "speakers.csv"


def main() -> None:
    rows: List[Dict[str, str]] = asyncio.run(scrape_dcw_speakers(DEFAULT_URL))
    write_speakers_csv(rows, DEFAULT_OUT)
    print(f"Wrote {len(rows)} speakers to {DEFAULT_OUT}")


if __name__ == "__main__":
    main()
