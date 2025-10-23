import asyncio
import argparse
import csv
from pathlib import Path
from typing import List, Dict, Optional
import aiohttp
from aiohttp.client_exceptions import ClientConnectorCertificateError
from bs4 import BeautifulSoup


async def fetch_html(url: str, session: aiohttp.ClientSession, *, timeout: int = 30) -> str:
    async with session.get(url, timeout=timeout) as resp:
        resp.raise_for_status()
        return await resp.text()


def _extract_text(el) -> str:
    return " ".join(el.get_text(" ", strip=True).split()) if el else ""


def _parse_speakers_dc_week(html: str) -> List[Dict[str, str]]:
    """
    Parse Digital Construction Week speakers page.

    The site may change; this parser tries a few reasonable selectors.
    Returns list of dicts with keys: name, title, company.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: List[Dict[str, str]] = []

    # Prefer the current DCW grid structure if present
    grid_items = soup.select('.speaker-grid-item')
    results: List[Dict[str, str]] = []
    if grid_items:
        for card in grid_items:
            # Name: usually in h3 or fallback to image alt
            name = _extract_text(card.select_one('.speaker-grid-details h3') or card.select_one('h3'))
            if not name:
                alt = card.select_one('img')
                name = (alt.get('alt', '').strip() if alt else '')

            job_text = _extract_text(card.select_one('p.speaker-job') or card.select_one('.speaker-job'))

            title_text = job_text
            company_text = ""
            if job_text:
                # Split on the last ' at ' to avoid splitting role names that contain 'at'
                lower = job_text.lower()
                idx = lower.rfind(' at ')
                if idx != -1:
                    title_text = job_text[:idx].strip(' ,')
                    company_text = job_text[idx + 4 :].strip(' ,')

            if name:
                results.append({
                    'name': name,
                    'title': title_text,
                    'company': company_text,
                })

        # Deduplicate by name+company
        uniq = {}
        for r in results:
            uniq[(r['name'], r['company'].lower())] = r
        return list(uniq.values())

    # Common patterns to try (fallbacks included) when grid structure not found
    card_selectors = [
        ".speaker-card",  
        ".presenter-card",
        ".speaker",
        ".presenter",
        "article",  # generic containers
        "li",
        "div[class*='speaker']",
        "div[class*='presenter']",
    ]
    seen = set()
    for sel in card_selectors:
        for card in soup.select(sel):
            # Heuristics for name
            name = _extract_text(
                card.select_one(".speaker-name, .presenter-name, h3, h2, .name, [itemprop='name']")
            )
            # Heuristics for title/company block
            title_text = _extract_text(
                card.select_one(
                    ".speaker-title, .presenter-title, .title, [itemprop='jobTitle']"
                )
            )
            company_text = _extract_text(
                card.select_one(
                    ".speaker-company, .presenter-company, .company, [itemprop='affiliation'], [itemprop='worksFor']"
                )
            )

            # Some sites use a single block like "Title, Company"
            if not company_text and "," in title_text:
                maybe_title, maybe_company = [x.strip() for x in title_text.split(",", 1)]
                if len(maybe_company) >= 2:
                    title_text, company_text = maybe_title, maybe_company

            # Skip incomplete or duplicate entries
            key = (name, title_text, company_text)
            if not name or key in seen:
                continue
            seen.add(key)
            results.append({"name": name, "title": title_text, "company": company_text})

    # Deduplicate by name+company fallback
    if results:
        uniq = {}
        for r in results:
            k = (r["name"], r.get("company", "").lower())
            uniq[k] = r
        results = list(uniq.values())

    return results


async def scrape_speakers(
    url: str,
    session: Optional[aiohttp.ClientSession] = None,
    *,
    insecure: bool = False,
) -> List[Dict[str, str]]:
    """
    Scrape speakers from a DCW-like page. Returns a list of dicts with
    keys: name, title, company.
    """
    owns_session = False
    if session is None:
        connector = aiohttp.TCPConnector(ssl=not insecure) if insecure else None
        session = aiohttp.ClientSession(connector=connector)
        owns_session = True
    try:
        try:
            html = await fetch_html(url, session)
        except ClientConnectorCertificateError:
            # Automatic fallback: if SSL verification fails, retry with ssl disabled
            fallback = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
            try:
                html = await fetch_html(url, fallback)
            finally:
                await fallback.close()
        return _parse_speakers_dc_week(html)
    finally:
        if owns_session:
            await session.close()


async def scrape_dcw_speakers(
    url: str = "https://www.digitalconstructionweek.com/all-speakers/",
    *,
    insecure: bool = False,
) -> List[Dict[str, str]]:
    """
    Scrape the Digital Construction Week speakers page and return a list of
    dicts with the exact keys required for downstream CSV export:

    - "Speaker Name"
    - "Speaker Title"
    - "Speaker Company"

    This function targets a single page and does not paginate.
    """
    base = await scrape_speakers(url, insecure=insecure)
    normalized: List[Dict[str, str]] = []
    for r in base:
        normalized.append(
            {
                "Speaker Name": r.get("name", "").strip(),
                "Speaker Title": r.get("title", "").strip(),
                "Speaker Company": r.get("company", "").strip(),
            }
        )
    return normalized


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_speakers_csv(rows: List[Dict[str, str]], out_path: Path) -> None:
    """Write speaker rows to CSV with required headers."""
    headers = ["Speaker Name", "Speaker Title", "Speaker Company"]
    _ensure_parent(out_path)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "Speaker Name": r.get("Speaker Name", ""),
                "Speaker Title": r.get("Speaker Title", ""),
                "Speaker Company": r.get("Speaker Company", ""),
            })


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape DCW speakers and write an input CSV.")
    parser.add_argument(
        "--url",
        type=str,
        default="https://www.digitalconstructionweek.com/all-speakers/",
        help="Speakers page URL to scrape",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output CSV path (default: <repo>/dd_gtm_ai_eng_exercise/in/speakers.csv)",
    )
    parser.add_argument("--insecure", action="store_true", help="Skip SSL verification for scraping")
    args = parser.parse_args()
    if args.out is None:
        # Default relative to this file's directory to avoid CWD confusion
        args.out = Path(__file__).resolve().parent.parent / "in" / "speakers.csv"
    return args


def main() -> None:
    args = parse_args()
    rows: List[Dict[str, str]] = asyncio.run(scrape_dcw_speakers(args.url, insecure=args.insecure))
    write_speakers_csv(rows, args.out)
    print(f"Wrote {len(rows)} speakers to {args.out}")


if __name__ == "__main__":
    main()
