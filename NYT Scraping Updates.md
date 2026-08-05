## Current status

| File | Status | What it contains |
|---|---|---|
| `NYT-Scraping-Workflow.md` | **Updated** | The complete metadata-search, basic scraper, and Playwright login workflow |
| `README.md` | **Updated** | A quick reference and link to the complete NYT workflow |
| `code/nytscraper.py` | **Updated** | The basic `requests` and BeautifulSoup scraper, including clearer handling for JavaScript or paywall responses |
| `code/nytscraper_login.py` | **Added** | A Playwright-based scraper that signs in with credentials supplied through environment variables |
| `requirements-nyt-login.txt` | **Added** | Dependencies for the Playwright login workflow |

The file previously called `New York Times Scraping.md` in this change summary corresponds to `NYT-Scraping-Workflow.md` in the repository. The earlier summary also used `Code/`; the actual directory is lowercase `code/`.

---

## What is implemented

### Basic scraper

`code/nytscraper.py` reads article URLs from `nytlinks.csv` and writes results to `articlefulltext.csv`.

Because it uses HTTP requests rather than a browser, it cannot execute JavaScript or authenticate through an NYT account. Pages that appear to require JavaScript or paywall access are marked unavailable instead of being recorded as successful article text.

### Playwright login scraper

`code/nytscraper_login.py` uses Playwright and Chromium to:

1. Read URLs from `nytlinks.csv`.
2. Sign in using `NYT_EMAIL` and `NYT_PASSWORD` from the environment or an optional local `.env` file.
3. Visit article pages in an authenticated browser session.
4. Extract paragraphs from recognized article-body containers.
5. Write the date, URL, and collected text to `articlefulltext.csv`.

Credentials must not be hardcoded or committed to the repository. Authentication may still require a visible browser for 2FA or CAPTCHA, and changes to the NYT website may require selector updates.

The automated tests validate the expected login sequence and extraction logic with mock pages. They do not perform a live login or confirm access to a real subscription; that final check must be completed manually with a valid NYT account.

---

## Current Playwright instructions

From the repository root, install the additional dependencies:

```bash
python3 -m pip install -r requirements-nyt-login.txt
python3 -m playwright install chromium
```

Set your credentials:

```bash
export NYT_EMAIL="you@example.com"
export NYT_PASSWORD="your-password"
```

Create `nytlinks.csv` with one NYT article URL per row, then run:

```bash
python3 code/nytscraper_login.py --input nytlinks.csv --output articlefulltext.csv
```

For a visible browser, including manual authentication steps, run:

```bash
python3 code/nytscraper_login.py --headed --input nytlinks.csv --output articlefulltext.csv
```

See the New York Times section of `README.md` for the maintained quick-start instructions.

---

## Testing status

The scraper and test modules compile successfully. The offline test suite covers:

- URL and CSV parsing
- Date extraction
- Invalid URL handling
- JavaScript and paywall-message detection
- Article-body extraction
- Duplicate and non-article paragraph filtering
- The expected Playwright email and password sequence
- The post-login NYT redirect
- The extended headed-mode timeout for manual authentication

The tests use mock pages and do not contact NYT. A live authenticated run must still be verified manually using a valid NYT account.

---

## Documentation status

`NYT-Scraping-Workflow.md` now contains the complete Playwright setup, credential, headed-browser, output, testing, and troubleshooting instructions. The README links to it as the full NYT workflow guide.