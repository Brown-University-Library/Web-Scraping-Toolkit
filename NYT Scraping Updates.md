# New York Times Workflow: Summary of All Changes

This document describes every change made to the NYT scraping workflow, scripts, and documentation. It is intended as a single reference for what was updated, why, and how to use the new or modified pieces.

---

## 1. Overview of What Changed

| Item | Type | Summary |
|------|------|--------|
| **New York Times Scraping.md** | Updated | Install steps, Frank’s script link, output CSV name, connection to scraper, JS/paywall note, new section 6a for login scraper. |
| **Code/nytscraper.py** | Updated | Detects “Please enable JS / ad blocker” and writes a clear placeholder; CSV opened with `newline=''`; minor formatting. |
| **Code/nytscraper_login.py** | **New** | Playwright-based scraper that logs in with your NYT account and scrapes full article text. |
| **requirements-nyt-login.txt** | **New** | Lists `playwright` (and optional `python-dotenv`) for the login scraper. |

---

## 2. Changes to the Workflow Document (`New York Times Scraping.md`)

### 2.1 Installations (Step 2 – Python packages)

- **Before:** One long paragraph describing `python3 -m pip install requests`, `bs4`, and `lxml` in prose.
- **After:**
  - The three install commands are shown in a single code block so they can be copied and run one after the other.
  - Added a note that on some systems `pip install ...` may work instead of `python3 -m pip install ...`.
  - Kept the existing explanatory text but tightened it.

**Reason:** Makes it clear exactly what to type and avoids missing a package.

---

### 2.2 Link to Frank’s script and how to get it (Section 4)

- **Before:** Link pointed to the **folder** (`tree/main/nytimes`). Instructions said to download the **entire repository** as a ZIP.
- **After:**
  - Link now points **directly to the script file**:  
    `https://github.com/Brown-University-Library/geodata_api_tutorials/blob/main/nytimes/nyt_archives_api.py`
  - Instructions say you can either:
    - Download the full repo as a ZIP and extract it, **or**
    - Open that file on GitHub and save only `nyt_archives_api.py` into your working folder.

**Reason:** Aligns with your note that the full repo isn’t strictly required and makes the exact file obvious.

---

### 2.3 Customizing search (Section 4 – new content)

- **Before:** No guidance on how to change search terms or date range.
- **After:** Added step 3 under Instructions:
  - Open `nyt_archives_api.py` in a text editor.
  - Find the variables for **year**, **month**, and any **search terms** (e.g. used to filter abstracts/lead paragraphs).
  - Edit those values for your topic and time period, then save.

**Reason:** Answers “How to actually search your terms by adapting Frank’s script?”

---

### 2.4 Output file name and where to get URLs (Section 4)

- **Before:** Did not name the output file or say where to get URLs for scraping.
- **After:**
  - After the “Run the Python script” step, added: when the script finishes, it writes a CSV in the **same directory** named like **`nyt_extracts_1.csv`** (the number may vary). That file contains metadata and **URLs** for the articles that matched your search.
  - Added: “You will use the URL column from this `nyt_extracts_[number].csv` file in the next section when setting up the scraper.”

**Reason:** Matches your note that results go to `nyt_extracts_[number].csv` and that this is where you grab URLs.

---

### 2.5 Setting up for scraping (Section 5)

- **Before:** Said “after you have created a spreadsheet with the results of your NYT search” and “select the column that contains the article urls” without naming the file.
- **After:**
  - Explicitly says to open **`nyt_extracts_[number].csv`** and select the **column that contains the article URLs**, then copy that column into a new spreadsheet and save as **`nytlinks.csv`**.
  - Added: “If you have an NYT subscription (e.g. student account) and want to scrape full text by logging in, use `nytscraper_login.py` instead and follow **section 6a** below.”

**Reason:** Connects Frank’s output file to the scraper input and points to the login option.

---

### 2.6 Scraping command and output (Section 6)

- **Before:** Run command was in prose; output file name was not in code formatting.
- **After:**
  - Run command is in a code block: `python3 nytscraper.py`.
  - References to `articlefulltext.csv` use backticks.
  - Added a **bold note** about NYT and JavaScript/paywalls:
    - Many NYT pages rely on JavaScript and paywalls.
    - The simple `requests` + `BeautifulSoup` scraper does **not** run JavaScript.
    - Some rows may contain “Please enable JS and disable any ad blocker” or similar instead of article text.
    - Treat the basic scraper as a learning tool; for serious use, consider official NYT APIs and their terms of service.

**Reason:** Sets expectations and explains why some rows are not full article text.

---

### 2.7 New section 6a: Scraping with your NYT account (login)

- **New section** after the main scraping instructions:
  - **Title:** “Alternative: Scraping with your NYT account (login).”
  - **Purpose:** For users with access (e.g. student subscription) who want to log in and get full article text.
  - **Contents:**
    1. Install Playwright: `python3 -m pip install playwright` then `python3 -m playwright install chromium`.
    2. Set credentials via **environment variables** (`NYT_EMAIL`, `NYT_PASSWORD`) or via a **`.env`** file (with optional `python-dotenv`). Explicit warning not to commit credentials.
    3. Run `python3 nytscraper_login.py` in the folder that contains `nytlinks.csv` (and the script). Output is again `articlefulltext.csv`.
  - Note about **two-factor authentication (2FA):** If the account uses 2FA, user may need to run with the browser visible (e.g. set `headless=False` in the script) to complete login.

**Reason:** Documents the new login-based scraper and keeps credentials out of the repo.

---

## 3. Changes to the Basic Scraper (`Code/nytscraper.py`)

### 3.1 Detecting “Please enable JS / ad blocker” and replacing with a placeholder

- **Before:** Whatever text was in the `<p>` tags was written to the CSV. When NYT returned the “Please enable JS and disable any ad blocker” page, that text was saved as if it were the article.
- **After:**
  - After building `full_text` from all `<p>` tags, the script lowercases it and checks for:
    - `"please enable js"`
    - `"disable any ad blocker"`
  - If either phrase is present, it **replaces** the scraped text with:  
    **`[UNAVAILABLE: page requires JavaScript / paywall; full text not scraped]`**
  - That string is written to the “Article Full Text” column instead of the raw message.

**Reason:** So the CSV clearly shows which URLs could not be scraped with the simple method, instead of looking like successful full text.

### 3.2 CSV writing and formatting

- **Before:** `open('articlefulltext.csv', 'w')` without `newline=''`.
- **After:** `open('articlefulltext.csv', 'w', newline='')` when creating the CSV writer.

**Reason:** Avoids extra blank lines in the CSV on some platforms (e.g. Windows).

### 3.3 Code style

- **Before:** Long `User-Agent` string on one line.
- **After:** `headers` dict is split across lines for readability. Behavior is unchanged.

---

## 4. New Login-Based Scraper (`Code/nytscraper_login.py`)

### 4.1 Purpose

- Uses a **real browser** (Playwright + Chromium) to:
  - Log in to the New York Times with **your** account (e.g. student subscription).
  - Visit each URL from `nytlinks.csv` **while logged in**.
  - Extract the **article body text** from the rendered page (after JavaScript runs).
- Writes the same kind of output as the basic scraper: **Date**, **Article Url**, **Article Full Text** in **`articlefulltext.csv`**.

### 4.2 Credentials (no secrets in code)

- **Required environment variables:**
  - **`NYT_EMAIL`** – Your NYT account email.
  - **`NYT_PASSWORD`** – Your NYT account password.
- If **`python-dotenv`** is installed, the script also loads a **`.env`** file from the current directory (so you can put `NYT_EMAIL=...` and `NYT_PASSWORD=...` there and **not** commit that file).
- The script **exits with a clear error** if either variable is missing or empty.

### 4.3 How it works (high level)

1. Reads URLs from **`nytlinks.csv`** (same as the basic scraper).
2. Launches Chromium (headless by default).
3. Goes to the NYT login flow (`myaccount.nytimes.com/auth/enter-email` with redirect to nytimes.com).
4. Fills email and submits; then fills password and submits; waits until the URL is on `nytimes.com`.
5. For each article URL:
   - Navigates to the URL.
   - Waits a short time for content to render.
   - Tries several **article-body selectors** (e.g. `section[data-testid="article-body"] p`, `article section p`, etc.) and concatenates paragraph text.
   - If no suitable content is found, writes `[UNAVAILABLE: could not find article body]`.
6. Extracts **date** from the URL when possible (e.g. `YYYY/MM/DD` pattern).
7. Writes all rows to **`articlefulltext.csv`** with columns: **Date**, **Article Url**, **Article Full Text**.

### 4.4 Optional: visible browser and 2FA

- By default the browser runs **headless** (no window). To see the browser (e.g. to complete 2FA or captcha), change in the script:
  - `browser = p.chromium.launch(headless=True)`  
  to  
  - `browser = p.chromium.launch(headless=False)`.

### 4.5 Dependencies

- **Playwright** and a browser (Chromium). Install with:
  - `python3 -m pip install playwright`
  - `python3 -m playwright install chromium`
- Optional: **python-dotenv** if you want to use a `.env` file for credentials.

---

## 5. New File: `requirements-nyt-login.txt`

- **Purpose:** Lists dependencies **only for the login-based scraper**.
- **Contents:**
  - `playwright>=1.40.0`
  - Comment that the basic workflow uses `requests`, `bs4`, `lxml` (as in the main doc).
  - Optional: `python-dotenv>=1.0.0` for `.env` support.

**Reason:** So anyone using `nytscraper_login.py` knows what to install without digging through the workflow doc.

---

## 6. Quick Reference: Which Script When

| Situation | Script | Output |
|-----------|--------|--------|
| No NYT account; learning the pipeline; okay with many “UNAVAILABLE” or paywall text | **`nytscraper.py`** | `articlefulltext.csv` |
| You have NYT access (e.g. student account) and want full article text | **`nytscraper_login.py`** (after setting `NYT_EMAIL` and `NYT_PASSWORD`) | `articlefulltext.csv` |

Both scripts read **`nytlinks.csv`** (one URL per line) from the current directory and write **`articlefulltext.csv`** there.

---

## 7. Files Touched – Summary

- **Modified:** `New York Times Scraping.md`, `Code/nytscraper.py`
- **Created:** `Code/nytscraper_login.py`, `requirements-nyt-login.txt`, **`NYT-Workflow-Changes.md`** (this document)

No other files were changed. The Guardian workflow and other parts of the toolkit were left as-is.
