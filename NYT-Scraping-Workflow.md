# New York Times Collection and Scraping Workflow

## Overview

This workflow explains how to:

1. Retrieve New York Times article metadata with the NYT Archive API.
2. Filter the results for a topic and save the matching article URLs.
3. Attempt to collect article text with either the basic scraper or the Playwright login scraper.

The Archive API returns article metadata rather than full article text. The scraping stage visits the returned URLs separately. Access to article text depends on the page, your subscription, NYT's terms and technical controls, and the current website structure. **Please note that as of the last update to this toolkit in August 2026, NYT bot detection is very robust and blocks most attempts to scrape with automated methods, meaning that you can retrieve article metadata but likely not full text.**

---

## 1. Requirements

You will need:

- Python 3.10 or newer
- An NYT developer account and API key for the metadata-search stage
- A valid NYT subscription if you use the authenticated Playwright scraper
- A text editor and Terminal on macOS/Linux or Command Prompt/PowerShell on Windows

Clone or download this toolkit, open a terminal in its root directory, and install the basic dependencies:

```bash
python3 -m pip install -r requirements.txt
```

If that command does not work on your system, try:

```bash
pip install -r requirements.txt
```

If you receive a permission error, create and activate a Python virtual environment before installing the dependencies.

### Additional Playwright dependencies

If you plan to use the NYT login scraper, also run:

```bash
python3 -m pip install -r requirements-nyt-login.txt
python3 -m playwright install chromium
```

Playwright controls a real Chromium browser, allowing JavaScript to run and an authenticated NYT session to be used.

---

## 2. Get an NYT API key

1. Create or sign in to an account at the [NYT Developer Portal](https://developer.nytimes.com/).
2. Open **My Apps** and create a new app.
3. Enable the API product used by the archive script, normally the **Archive API**.
4. Save the app and copy its API key.
5. Review the portal's current rate limits before running a large query.

![NYT developer site](Images/NYT/nytsite.png)

The developer API key is only used to retrieve metadata. It does not provide subscription access to paywalled article text.

---

## 3. Save the API key

Frank Donnelly's archive script reads the API key from a plain-text file named `nyt_key.txt`.

Create `nyt_key.txt` in the same directory as `nyt_archives_api.py`, paste only the API key into it, and save the file.

> **Security:** Do not commit `nyt_key.txt`, `.env`, passwords, or other credentials to Git. Confirm that credential files are covered by `.gitignore` before committing.

---

## 4. Search the NYT Archive API and collect article metadata

The metadata-search stage uses Frank Donnelly's [`nyt_archives_api.py`](https://github.com/Brown-University-Library/geodata_api_tutorials/blob/main/nytimes/nyt_archives_api.py) script.

You can either:

- Download the complete `geodata_api_tutorials` repository as a ZIP file and extract it, or
- Open the linked script on GitHub and save only `nyt_archives_api.py` into your working directory.

Keep `nyt_key.txt` in the same directory as the script.

### Customize the search

Before running the script, open `nyt_archives_api.py` in a text editor and locate the variables that control:

- Year
- Month
- Search terms used to filter article abstracts or lead paragraphs

Change those values for your research topic and time period, then save the script.

### Run the search

In Terminal or Command Prompt, navigate to the directory containing `nyt_archives_api.py` and `nyt_key.txt`, then run:

```bash
python3 nyt_archives_api.py
```

On systems where the Python command is `python`, use:

```bash
python nyt_archives_api.py
```

The script writes a CSV file in the same directory with a name such as `nyt_extracts_1.csv`; the number may vary. This file will contain the matching article metadata collected using the Archive API, with columns for headline,	byline,	pub_date,	abstract,	lead_paragraph, word_count,	uri, and	web_url. See the [Archive API documentation](https://developer.nytimes.com/docs/archive-product/1/overview) (Overview > Resource Types) for more information on these fields.  

There are many interesting research questions you can investigate with this data. If you wish to attempt to collect article full-text, proceed to step #5, but depending on the current NYT Terms of Use, this may not be possible.
---

## 5. Prepare `nytlinks.csv`

1. Open the generated `nyt_extracts_[number].csv` file.
2. Find the column containing the article URLs.
3. Copy that column into a new spreadsheet containing one URL per row.
4. An optional first-row header may be named `Article Url`.
5. Export or save the new file as `nytlinks.csv`.
6. Put `nytlinks.csv` in the root directory of this toolkit.

You do not need to create `articlefulltext.csv` yourself. The selected scraper creates or replaces it when the program runs.

---

## 6. Choose a scraper

| Scraper | Recommended use | Important limitation |
|---|---|---|
| `code/nytscraper.py` | Learning the basic requests/BeautifulSoup workflow | Does not run JavaScript or log in; many NYT pages will be unavailable |
| `code/nytscraper_login.py` | Attempting collection through a valid NYT subscription | Requires Playwright and credentials; live login and page structure can change |

Both scripts read `nytlinks.csv` and write these columns to `articlefulltext.csv`:

- `Date`
- `Article Url`
- `Article Full Text`

### 6a. Basic scraper without login

From the toolkit's root directory, run:

```bash
python3 code/nytscraper.py
```

The basic scraper downloads the HTML with `requests` and extracts text from paragraph elements with BeautifulSoup. It cannot execute JavaScript or access subscription content through an authenticated account.

When a page appears to require JavaScript, login, or paywall access, the result is marked with an `[UNAVAILABLE: ...]` placeholder instead of being recorded as successful article text.

### 6b. Playwright scraper with NYT login

The login scraper launches Chromium, signs in with credentials supplied through the environment, and visits each article in the authenticated browser session.

#### Set credentials on macOS or Linux

```bash
export NYT_EMAIL="you@example.com"
export NYT_PASSWORD="your-password"
```

#### Set credentials in Windows PowerShell

```powershell
$env:NYT_EMAIL="you@example.com"
$env:NYT_PASSWORD="your-password"
```

#### Optional `.env` file

If `python-dotenv` is installed, you may instead create a local `.env` file in the toolkit's root directory:

```text
NYT_EMAIL=you@example.com
NYT_PASSWORD=your-password
```

Do not commit this file.

#### Run the login scraper

From the toolkit's root directory, run:

```bash
python3 code/nytscraper_login.py --input nytlinks.csv --output articlefulltext.csv
```

The browser runs in the background by default.

If login requires 2FA, CAPTCHA, institutional authentication, or another manual step, display the browser with `--headed`:

```bash
python3 code/nytscraper_login.py --headed --input nytlinks.csv --output articlefulltext.csv
```

Headed mode allows additional time to complete a manual authentication step. If the login flow or page selectors have changed, the script may still need to be updated.

---

## 7. Review the output

When the scraper finishes, open `articlefulltext.csv` in a spreadsheet application.

Review the `Article Full Text` column for status values such as:

- `[UNAVAILABLE: ...]` — the scraper could not locate accessible article text
- `[INVALID URL]` — the input row was not a valid HTTP or HTTPS URL
- `[ERROR: ...]` — the page or request could not be completed

Do not assume that every non-empty row contains complete article text. Inspect a sample of the output against the corresponding pages before beginning analysis.

---

## 8. Run the offline tests

From the toolkit's root directory, run:

```bash
pytest
```

The tests cover URL parsing, date extraction, error handling, article-body extraction, and the expected Playwright email/password sequence using mock pages.

Passing tests confirms the offline code paths. The tests do not contact NYT or verify a real subscription. A live authenticated run must still be tested manually with a valid account.

---

## 9. Responsible use and troubleshooting

- Review the NYT's current terms of service and `robots.txt` before collecting pages.
- Use official APIs when they provide the data you need.
- Add appropriate delays and retry limits for larger collections.
- Do not redistribute copyrighted article text without confirming that you have permission.
- If the password field, login button, or article body cannot be found, rerun with `--headed` to inspect the live page.
- If Playwright is missing, reinstall the login requirements and Chromium using the commands in section 1.
- If the basic scraper returns many unavailable rows, use the login scraper only when your account and the site's terms permit it.

---

## Next steps

To explore possible uses of the collected article data, see the Brown University Library's [resources on text mining](https://library.brown.edu/).

## Special credits

The Archive API search stage is based on work by Frank Donnelly, GIS and Data Librarian at Brown University Library. The scraping examples in this toolkit demonstrate separate approaches for unauthenticated HTML requests and authenticated browser automation.
