"""Scrape publicly available text from New York Times article URLs.

This lightweight version uses requests and does not log in or execute
JavaScript. Use nytscraper_login.py for an authenticated browser workflow.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_INPUT = "nytlinks.csv"
DEFAULT_OUTPUT = "articlefulltext.csv"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
UNAVAILABLE = "[UNAVAILABLE: page requires JavaScript, login, or paywall access]"
BLOCKED_PHRASES = (
    "please enable js",
    "please enable javascript",
    "disable any ad blocker",
    "subscribe to continue reading",
)


def read_urls(path: str | Path) -> list[str]:
    """Read the first non-empty CSV field on each row, skipping a header."""
    urls: list[str] = []
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as source:
        for row in csv.reader(source):
            if not row:
                continue
            value = row[0].strip()
            if not value or value.lower() in {"url", "article url", "article_url"}:
                continue
            urls.append(value)
    return urls


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def extract_date(url: str) -> str:
    """Return an ISO date from a dated NYT URL, or an empty string."""
    match = re.search(r"/(\d{4})/(\d{2})/(\d{2})(?:/|$)", url)
    return "-".join(match.groups()) if match else ""


def extract_article_text(html: bytes | str) -> str:
    """Extract paragraph text and identify common block/paywall responses."""
    soup = BeautifulSoup(html, "lxml")
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = "\n".join(paragraph for paragraph in paragraphs if paragraph).strip()
    lowered = text.lower()
    if not text or any(phrase in lowered for phrase in BLOCKED_PHRASES):
        return UNAVAILABLE
    return text


def scrape_nyt_articles(
    input_path: str | Path = DEFAULT_INPUT,
    output_path: str | Path = DEFAULT_OUTPUT,
    *,
    timeout: float = 30,
) -> None:
    """Scrape each input URL and write Date, URL, and text to a CSV file."""
    articles = read_urls(input_path)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    with open(output_path, "w", newline="", encoding="utf-8") as destination:
        writer = csv.writer(destination)
        writer.writerow(["Date", "Article Url", "Article Full Text"])

        for index, url in enumerate(articles, start=1):
            if not is_http_url(url):
                text = "[INVALID URL]"
            else:
                try:
                    response = session.get(url, timeout=timeout)
                    response.raise_for_status()
                    text = extract_article_text(response.content)
                except requests.RequestException as exc:
                    status = getattr(getattr(exc, "response", None), "status_code", None)
                    suffix = f" HTTP {status}" if status else ""
                    text = f"[ERROR: request failed{suffix}]"

            writer.writerow([extract_date(url), url, text])
            print(f"[{index}/{len(articles)}] {url}")


if __name__ == "__main__":
    scrape_nyt_articles()
    print(f"Done scraping. Output written to {DEFAULT_OUTPUT}")