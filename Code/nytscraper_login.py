"""
NYT scraper that logs in with your account (e.g. student subscription) so full
article text can be retrieved. Uses Playwright to run a real browser.

Credentials are read from environment variables (never stored in code):
  NYT_EMAIL    – your NYT account email
  NYT_PASSWORD – your NYT account password

Usage:
  1. pip install playwright && playwright install chromium
  2. Set NYT_EMAIL and NYT_PASSWORD in your environment (or .env file).
  3. In the same folder: nytlinks.csv (one URL per line), this script.
  4. Run: python nytscraper_login.py

Output: articlefulltext.csv (Date, Article Url, Article Full Text)
"""

import csv
import os
import re
import sys

# Optional: load .env so you can set NYT_EMAIL and NYT_PASSWORD in a file (add python-dotenv to requirements if you use this)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://myaccount.nytimes.com/auth/enter-email?redirect_uri=https%3A%2F%2Fwww.nytimes.com%2F"
LINKS_FILE = "nytlinks.csv"
OUTPUT_FILE = "articlefulltext.csv"

# Selectors that commonly contain article body text (NYT structure can change)
ARTICLE_BODY_SELECTORS = [
    'section[data-testid="article-body"] p',
    'section[name="articleBody"] p',
    'article section p',
    '.StoryBodyCompanionColumn p',
    '.article-body p',
    'article p',
]


def get_article_text(page):
    """Extract article full text from the current page using a list of fallback selectors."""
    full_text = ""
    for selector in ARTICLE_BODY_SELECTORS:
        try:
            loc = page.locator(selector)
            if loc.count() > 0:
                full_text = "\n".join(loc.all_inner_texts())
                # Prefer a block that looks like article content (several paragraphs, not just one line)
                if full_text and len(full_text.strip()) > 200 and "please enable" not in full_text.lower():
                    return full_text.strip()
        except Exception:
            continue
    return full_text.strip() if full_text else "[UNAVAILABLE: could not find article body]"


def main():
    email = os.environ.get("NYT_EMAIL", "").strip()
    password = os.environ.get("NYT_PASSWORD", "").strip()
    if not email or not password:
        print(
            "Credentials not set. Set NYT_EMAIL and NYT_PASSWORD in your environment (or in a .env file).",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.path.isfile(LINKS_FILE):
        print(f"Links file not found: {LINKS_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(LINKS_FILE, "r", encoding="utf-8", errors="replace") as f:
        articles = [line.rstrip("\n").strip() for line in f if line.strip()]

    if not articles:
        print(f"No URLs found in {LINKS_FILE}.", file=sys.stderr)
        sys.exit(1)

    results = []  # list of (date, url, text)

    with sync_playwright() as p:
        # Launch browser (headless=True runs in background; set to False to watch)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_default_timeout(30000)

        try:
            # Step 1: Go to login and submit email
            page.goto(LOGIN_URL, wait_until="domcontentloaded")
            page.fill('input[name="email"], input[type="email"]', email)
            page.click('button[type="submit"], input[type="submit"], [data-testid="email-continue"]')
            page.wait_for_load_state("networkidle", timeout=15000)

            # Step 2: Enter password (page may have moved to password step)
            page.fill('input[name="password"], input[type="password"]', password)
            page.click('button[type="submit"], input[type="submit"], [data-testid="password-login"]')
            page.wait_for_url(re.compile(r"nytimes\.com"), timeout=15000)

            # Step 3: Visit each article URL and extract text
            for i, url in enumerate(articles):
                if not url.startswith("http"):
                    results.append((url[:10] if len(url) >= 10 else url, url, "[INVALID URL]"))
                    continue
                try:
                    page.goto(url, wait_until="domcontentloaded")
                    page.wait_for_timeout(2000)  # allow JS to render article body
                    text = get_article_text(page)
                except Exception as e:
                    text = f"[ERROR: {e}]"
                # Date from URL (e.g. .../2024/01/15/...)
                date_match = re.search(r"/(\d{4}/\d{2}/\d{2})/", url)
                date = date_match.group(1).replace("/", "-") if date_match else url[24:34] if len(url) >= 34 else ""
                results.append((date, url, text))
                print(f"  [{i+1}/{len(articles)}] {url[:60]}...")

        finally:
            context.close()
            browser.close()

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Article Url", "Article Full Text"])
        for date, url, text in results:
            writer.writerow([date, url, text])

    print("Done Scraping! Output written to", OUTPUT_FILE)


if __name__ == "__main__":
    main()
