# Code — Scraper Scripts

These Python scripts visit web pages and extract article text. Each one reads an input file of URLs (or JSON) and produces a CSV of results.

## Scripts

| Script | Source | Input | Output | Login? |
|--------|--------|-------|--------|--------|
| `nytscraper.py` | NYT | `nytlinks.csv` | `articlefulltext.csv` | No |
| `nytscraper_login.py` | NYT | `nytlinks.csv` | `articlefulltext.csv` | Yes |
| `guardian_scraping.py` | Guardian | `query_result.json` | `guardian_results.csv` | No |
| `__init__.py` | — | — | — | Package marker for tests |

---

### nytscraper.py

The simple version. Downloads each URL with `requests`, pulls text from `<p>` tags with BeautifulSoup, and writes Date / URL / Full Text to CSV.

Pages that return a JavaScript/paywall error are marked `[UNAVAILABLE]` instead of saving the error message. Most paywalled NYT articles will hit this — use the login scraper below for serious collection.

```bash
python3 nytscraper.py
```

---

### nytscraper_login.py

Logs into your NYT account with a real browser (Playwright + Chromium), then scrapes articles while authenticated. Same output format as the basic scraper.

**Setup (one time):**
```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

**Set credentials** via environment variables or a `.env` file — never hardcode them:
```bash
export NYT_EMAIL="you@example.com"
export NYT_PASSWORD="your-password"
python3 nytscraper_login.py
```

If your account uses 2FA, change `headless=True` to `headless=False` in the script so you can see and complete the login.

---

### guardian_scraping.py

Reads a Guardian API search result (`query_result.json`), visits each article, extracts `<p>` tag text, and writes title / date / URL / full text to CSV.

```bash
python3 guardian_scraping.py
```

---

## Key libraries used

- **requests** — downloads web pages (fast, but can't run JavaScript)
- **BeautifulSoup** — parses HTML so you can extract text from specific tags like `<p>`
- **Playwright** — controls a real browser from Python (handles JavaScript, logins, paywalls)
- **csv** — Python's built-in module for reading/writing spreadsheet-friendly files

## Troubleshooting

- **"No module named …"** → Run `python3 -m pip install -r requirements.txt` from the project root
- **Most NYT articles say `[UNAVAILABLE]`** → Expected with the basic scraper; switch to `nytscraper_login.py`
- **Login scraper fails at password step** → Run with `headless=False` to see what the browser shows
- **"Links file not found"** → Make sure you're running the script from the folder containing the input file