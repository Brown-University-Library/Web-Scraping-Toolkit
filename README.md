# Web Scraping Toolkit
*Last updated September 2026*

## What can I do with this toolkit?

This toolkit helps you go from **a research question** to **a usable text dataset**. Here are the main things you can do:

| I want to… | Start here |
|---|---|
| Collect article metadata from **The New York Times** | [NYT Workflow →](NYT-Scraping-Workflow.md) |
| Collect articles from **The Guardian** | [Guardian Workflow →](Guardian-Collection-Workflow.md.md) |
| Download full-text items from **Archive.org** | [Internet Archive Workflow →](Internet-Archive-API-Workflow.md) |
| Learn **web scraping from scratch** with Python | [Beautiful Soup Tutorial →](Beautiful-Soup-Tutorial.md.md) |
| Split a spreadsheet into **individual text files** for analysis | [Spreadsheet Splitting →](Spreadsheet-Splitting-Workflow.md) |

> **New to all of this?** Start with the [Beautiful Soup Tutorial](Beautiful-Soup-Tutorial.md.md). It introduces the core concepts of web scraping through hands-on examples, and the skills you learn there will help you understand every other workflow in this toolkit.

---

## How the workflows fit together

Most workflows in this toolkit follow the same general pattern:

```text
1. SEARCH        →  2. COLLECT URLs  →  3. SCRAPE full text  →  4. ANALYZE
   (use an API        (save results       (visit each URL,        (text mining,
   to find articles)   as a CSV file)      extract the text)       topic modeling, etc.)
```

For example, the NYT workflow uses the NYT Archive API to search for articles and metadata (step 1), saves the matching URLs into a CSV (step 2), then runs a Python scraper to visit each URL and attempt to collect the article text (step 3). You then take the resulting dataset into whatever analysis tool you prefer (step 4).

The toolkit covers steps 1–3. For step 4, check out the library's [resources on text mining](https://library.brown.edu/).

---

## Prerequisites

### Python

You'll need **Python 3.10 or newer**. If you don't have it installed, download it from [python.org](https://www.python.org/downloads/).

### Install dependencies

Open **Terminal** on macOS/Linux or **Command Prompt** on Windows, navigate to the folder where you cloned or downloaded this toolkit, and run:

```bash
python3 -m pip install -r requirements.txt
```

> **Tip:** On some systems, `pip install -r requirements.txt` works instead. If you get a permission error, create and activate a Python virtual environment before installing the dependencies.

This installs the dependencies used by the basic scraping workflows:

- `requests` — lets Python download web pages
- `beautifulsoup4` — parses HTML so you can extract text and links
- `lxml` — a fast HTML parser that works with BeautifulSoup

The NYT login-based scraper has additional dependencies. Install them separately with:

```bash
python3 -m pip install -r requirements-nyt-login.txt
python3 -m playwright install chromium
```

The optional `python-dotenv` package lets the login scraper load credentials from a local `.env` file.

---

## Workflow guides

### New York Times

The NYT workflow has two phases: **searching** for articles and gathering article metadata using the NYT Archive API and **scraping** the article text. In this workflow, you can work from the command line or a Python environment.

**Searching:** You'll use [Frank Donnelly's script](https://github.com/Brown-University-Library/geodata_api_tutorials/blob/main/nytimes/nyt_archives_api.py) from the Brown University Library. It queries the NYT Archive API and saves matching article metadata, including URLs, headline, byline, date, abstract, and lead paragraph to a CSV file.

**Scraping:** You then feed those URLs into one of two scrapers:

| Scraper | When to use it | How it works |
|---|---|---|
| `code/nytscraper.py` | Learning the pipeline; okay with some pages being unavailable | Simple HTTP requests without login |
| `code/nytscraper_login.py` | You have an NYT subscription and want to attempt authenticated collection | Logs in with a Playwright-controlled browser |

Both scrapers read URLs from `nytlinks.csv` and write results to `articlefulltext.csv`.

> **Note:** Many NYT pages require JavaScript and sit behind a paywall. The basic scraper will mark these as `[UNAVAILABLE]` rather than silently saving error text. A valid subscription may improve access, but the login scraper is not guaranteed to retrieve every page. NYT login screens, page selectors, CAPTCHA requirements, and terms of access can change.

📖 **[Full NYT workflow guide →](NYT-Scraping-Workflow.md)**

### The Guardian

The Guardian workflow uses the Guardian's open API to search for articles, then uses Gemini in Google Colab to generate a script that scrapes the full text from each result. For this workflow, you do not need to work from a Python coding environment or the command line, just Colab, a cloud-based tool for writing and running code. 

1. Search the [Guardian API Explorer](http://open-platform.theguardian.com/explore/) and copy the JSON results.
2. Paste JSON into a spreadsheet and use find and replace to clean it up to just a list of URLS
3. Upload the URLs to a Colab notebook and prompt Gemini to create a scraping script for full text

📖 **[Full Guardian workflow guide →](Guardian-Collection-Workflow.md.md)**

### Internet Archive

If your source material lives on Archive.org, this workflow shows you how to use `wget` to bulk-download items by identifier.

📖 **[Full Internet Archive workflow guide →](Internet-Archive-API-Workflow.md)**

### Beautiful Soup tutorial

A hands-on introduction to web scraping with Python. You'll learn to extract links, filter results, scrape text, and save structured data to CSV using a practice website designed for learning.

📖 **[Start the tutorial →](Beautiful-Soup-Tutorial.md.md)**

### Spreadsheet splitting

Once you have your data in a spreadsheet, you may want to split it into individual text files, with one file per row, for use in text-analysis tools.

📖 **[Spreadsheet splitting guide →](Spreadsheet-Splitting-Workflow.md)**

---

## Running the tests

The toolkit includes automated tests for URL parsing, article-text extraction, error handling, and the expected Playwright login sequence. The tests don't contact real websites or authenticate with a real NYT account; they use mock data so you can run them offline.

```bash
pytest
```

Passing tests confirms the offline code paths. A real authenticated collection should still be tested manually with a valid NYT account because the live login flow, 2FA/CAPTCHA requirements, and page structure can change.

---

## Considerations

Web scraping is a powerful tool, but it comes with responsibilities:

- **Respect terms of service.** Always review a site's terms before scraping. The NYT, Guardian, and most major publications have terms governing automated access.
- **Check `robots.txt`.** Most websites publish a `robots.txt` file, such as `https://www.nytimes.com/robots.txt`, that specifies which pages may be accessed by automated tools.
- **Be gentle with servers.** For larger collections, add appropriate delays and retry limits instead of sending rapid requests.
- **Use APIs when available.** APIs are the intended way to access data programmatically. Scraping HTML should generally be a fallback.
- **Respect copyright.** Collecting text for research may be covered by fair use, but redistribution may not be. Consult your institution's policies.
