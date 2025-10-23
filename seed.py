import asyncio
import argparse
from pathlib import Path
from typing import List, Dict

from utils.scraper import scrape_dcw_speakers, write_speakers_csv

DEFAULT_URL = "https://www.digitalconstructionweek.com/all-speakers/"
DEFAULT_OUT = Path(__file__).resolve().parent / "in" / "speakers.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed speakers.csv by scraping DCW")
    parser.add_argument("--url", type=str, default=DEFAULT_URL, help="Speakers page URL")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output CSV path")
    parser.add_argument("--insecure", action="store_true", help="Skip SSL verification while scraping")
    args = parser.parse_args()

    rows: List[Dict[str, str]] = asyncio.run(
        scrape_dcw_speakers(args.url, insecure=args.insecure)
    )
    write_speakers_csv(rows, args.out)
    print(f"Wrote {len(rows)} speakers to {args.out}")


if __name__ == "__main__":
    main()
