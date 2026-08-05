"""Authenticated New York Times article scraper using Playwright.

Credentials must be supplied through NYT_EMAIL and NYT_PASSWORD. They are
never written to disk by this script. Run with --headed when login requires
2FA, CAPTCHA, or other manual confirmation.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


LOGIN_URL = (
    "https://myaccount.nytimes.com/auth/enter-email"
    "?redirect_uri=https%3A%2F%2Fwww.nytimes.com%2F"
)
DEFAULT_INPUT = "nytlinks.csv"
DEFAULT_OUTPUT = "articlefulltext.csv"
UNAVAILABLE = "[UNAVAILABLE: could not find article body]"
BLOCKED_PHRASES = (
    "please enable js",
    "please enable javascript",
    "disable any ad blocker",
    "subscribe to continue reading",
)
ARTICLE_BODY_SELECTORS = (
    'section[data-testid="article-body"] p',
    'section[name="articleBody"] p',
    'article section p',
    '.StoryBodyCompanionColumn p',
    '.article-body p',
)
EMAIL_SELECTORS = ('input[name="email"]', 'input[type="email"]')
PASSWORD_SELECTORS = ('input[name="password"]', 'input[type="password"]')
EMAIL_SUBMIT_SELECTORS = (
    '[data-testid="email-continue"]',
    'button[type="submit"]',
    'input[type="submit"]',
)
PASSWORD_SUBMIT_SELECTORS = (
    '[data-testid="password-login"]',
    'button[type="submit"]',
    'input[type="submit"]',
)


def read_urls(path: str | Path) -> list[str]:
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
    match = re.search(r"/(\d{4})/(\d{2})/(\d{2})(?:/|$)", url)
    return "-".join(match.groups()) if match else ""


def _first_visible(page, selectors: tuple[str, ...], timeout: int = 15_000):
    """Return the first selector that becomes visible, without strict-mode ambiguity."""
    last_error = None
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return locator
        except Exception as exc:  # Playwright raises several timeout/error subclasses
            last_error = exc
    raise RuntimeError(f"None of the expected controls appeared: {selectors}") from last_error


def login(
    page,
    email: str,
    password: str,
    *,
    completion_timeout: int = 30_000,
) -> None:
    page.goto(LOGIN_URL, wait_until="domcontentloaded")
    _first_visible(page, EMAIL_SELECTORS).fill(email)
    _first_visible(page, EMAIL_SUBMIT_SELECTORS).click()
    _first_visible(page, PASSWORD_SELECTORS, timeout=30_000).fill(password)
    _first_visible(page, PASSWORD_SUBMIT_SELECTORS).click()

    try:
        page.wait_for_url(
            re.compile(r"https://(?:www\.)?nytimes\.com(?:/|$)"),
            timeout=completion_timeout,
        )
    except Exception as exc:
        raise RuntimeError(
            "NYT login did not complete. Re-run with --headed to handle 2FA or CAPTCHA."
        ) from exc


def get_article_text(page) -> str:
    """Extract de-duplicated paragraphs from a recognized article-body container."""
    for selector in ARTICLE_BODY_SELECTORS:
        try:
            texts = page.locator(selector).all_inner_texts()
        except Exception:
            continue

        paragraphs: list[str] = []
        seen: set[str] = set()
        for value in texts:
            clean = " ".join(value.split())
            if clean and clean not in seen:
                seen.add(clean)
                paragraphs.append(clean)

        article = "\n".join(paragraphs).strip()
        lowered = article.lower()
        if len(article) >= 200 and not any(phrase in lowered for phrase in BLOCKED_PHRASES):
            return article
    return UNAVAILABLE


def scrape_articles(page, urls: list[str], writer: csv.writer) -> None:
    for index, url in enumerate(urls, start=1):
        if not is_http_url(url):
            text = "[INVALID URL]"
        else:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45_000)
                try:
                    page.locator(ARTICLE_BODY_SELECTORS[0]).first.wait_for(
                        state="attached", timeout=8_000
                    )
                except Exception:
                    pass
                text = get_article_text(page)
            except Exception:
                text = "[ERROR: page could not be loaded]"

        writer.writerow([extract_date(url), url, text])
        print(f"[{index}/{len(urls)}] {url}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=DEFAULT_INPUT, help="CSV containing one URL per row")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="destination CSV")
    parser.add_argument("--headed", action="store_true", help="show the browser for 2FA/CAPTCHA")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    email = os.environ.get("NYT_EMAIL", "").strip()
    password = os.environ.get("NYT_PASSWORD", "").strip()
    if not email or not password:
        print("Set NYT_EMAIL and NYT_PASSWORD in your environment or .env file.", file=sys.stderr)
        return 1
    if not Path(args.input).is_file():
        print(f"Links file not found: {args.input}", file=sys.stderr)
        return 1

    urls = read_urls(args.input)
    if not urls:
        print(f"No URLs found in {args.input}.", file=sys.stderr)
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Playwright is not installed. Run: python3 -m pip install playwright && "
            "python3 -m playwright install chromium",
            file=sys.stderr,
        )
        return 1

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(15_000)
        try:
            login(
                page,
                email,
                password,
                completion_timeout=120_000 if args.headed else 30_000,
            )
            with open(args.output, "w", newline="", encoding="utf-8") as destination:
                writer = csv.writer(destination)
                writer.writerow(["Date", "Article Url", "Article Full Text"])
                scrape_articles(page, urls, writer)
        finally:
            context.close()
            browser.close()

    print(f"Done scraping. Output written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())