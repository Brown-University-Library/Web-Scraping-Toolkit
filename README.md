# Web Scraping Toolkit

## What can I do with this toolkit?

This toolkit helps you go from **a research question** to **a usable text dataset**. Here are the main things you can do:

| I want to…                                      | Start here                                                        |
|--------------------------------------------------|-------------------------------------------------------------------|
| Collect articles from **The New York Times**     | [NYT Workflow →](New%20York%20Times%20Scraping.md)                |
| Collect articles from **The Guardian**           | [Guardian Workflow →](Guardian%20Collection%20Workflow.md)         |
| Download full-text items from **Archive.org**    | [Internet Archive Workflow →](Internet-Archive-API-Workflow.md)   |
| Learn **web scraping from scratch** with Python  | [Beautiful Soup Tutorial →](V2-Getting%20Started%20with%20Beautiful%20Soup.md) |
| Split a spreadsheet into **individual text files** for analysis | [Spreadsheet Splitting →](Spreadsheet-Splitting-Workflow.md) |

> **New to all of this?** Start with the [Beautiful Soup Tutorial](V2-Getting%20Started%20with%20Beautiful%20Soup.md). It introduces the core concepts of web scraping through hands-on examples, and the skills you learn there will help you understand every other workflow in this toolkit.

---

## How the workflows fit together

Most workflows in this toolkit follow the same general pattern:

```
1. SEARCH        →  2. COLLECT URLs  →  3. SCRAPE full text  →  4. ANALYZE
   (use an API        (save results       (visit each URL,        (text mining,
   to find articles)   as a CSV file)      extract the text)       topic modeling, etc.)
```

For example, the NYT workflow uses the NYT Archive API to search for articles (step 1), saves the matching URLs into a CSV (step 2), then runs a Python scraper to visit each URL and download the full article text (step 3). You then take the resulting dataset into whatever analysis tool you prefer (step 4).

The toolkit covers steps 1–3. For step 4, check out the library's [resources on text mining](https://library.brown.edu/).

---

## Prerequisites

### Python
You'll need **Python 3.8 or newer**. If you don't have it installed, download it from [python.org](https://www.python.org/downloads/).

### Install dependencies

Open **Terminal** (Mac/Linux) or **Command Prompt** (Windows), navigate to the folder where you cloned or downloaded this toolkit, and run:

```bash
python3 -m pip install -r requirements.txt
```

> **Tip:** On some systems, `pip install -r requirements.txt` works instead. If you get a "permission denied" error, try adding `sudo` before the command (Mac/Linux) or running your terminal as Administrator (Windows).

This installs everything you need for all the workflows:

- `requests` — lets Python download web pages
- `beautifulsoup4` — parses HTML so you can extract text and links
- `lxml` — a fast HTML parser that works with BeautifulSoup
- `playwright` — drives a real browser (only needed for the NYT login scraper)
- `python-dotenv` — loads credentials from a file (only needed for the NYT login scraper)
- `pytest` — runs the automated tests

If you plan to use the **NYT login-based scraper**, you'll also need to install a browser for Playwright:

```bash
python3 -m playwright install chromium
```

---

## Workflow guides

### New York Times

The NYT workflow has two phases: **searching** for articles using the NYT Archive API, and **scraping** the full text of those articles.

**Searching:** You'll use [Frank Donnelly's script](https://github.com/Brown-University-Library/geodata_api_tutorials/blob/main/nytimes/nyt_archives_api.py) from the Brown University Library, which queries the NYT Archive API and saves matching article metadata (including URLs) to a CSV file.

**Scraping:** You then feed those URLs into one of two scrapers:

| Scraper                  | When to use it                                                    | How it works                      |
|--------------------------|-------------------------------------------------------------------|-----------------------------------|
| `Code/nytscraper.py`     | Learning the pipeline; OK with some pages being unavailable       | Simple HTTP requests (no login)   |
| `Code/nytscraper_login.py` | You have an NYT subscription and want full article text         | Logs in with a real browser       |

Both scrapers read URLs from `nytlinks.csv` and write results to `articlefulltext.csv`.

> **Note:** Many NYT pages require JavaScript and sit behind a paywall. The basic scraper will mark these as `[UNAVAILABLE]` rather than silently saving error text. For best results, use the login scraper with a valid NYT account.

📖 **[Full NYT workflow guide →](New%20York%20Times%20Scraping.md)**

### The Guardian

The Guardian workflow uses the Guardian's open API to search for articles, then scrapes the full text from each result.

1. Search the [Guardian API Explorer](http://open-platform.theguardian.com/explore/) and copy the JSON results
2. Save the JSON as `query_result.json`
3. Run `Code/guardian_scraping.py` to scrape full text into `guardian_results.csv`

📖 **[Full Guardian workflow guide →](Guardian%20Collection%20Workflow.md)**

### Internet Archive

If your source material lives on Archive.org, this workflow shows you how to use `wget` to bulk-download items by identifier.

📖 **[Full Internet Archive workflow guide →](Internet-Archive-API-Workflow.md)**

### Beautiful Soup tutorial

A hands-on introduction to web scraping with Python. You'll learn to extract links, filter results, scrape text, and save structured data to CSV — all using a practice website designed for learning.

📖 **[Start the tutorial →](V2-Getting%20Started%20with%20Beautiful%20Soup.md)**

### Spreadsheet splitting

Once you have your data in a spreadsheet, you may want to split it into individual text files (one per row) for text analysis tools. This workflow shows you how using the command line.

📖 **[Spreadsheet splitting guide →](Spreadsheet-Splitting-Workflow.md)**

---

## Running the tests

The toolkit includes automated tests to verify that the scrapers work correctly. The tests don't hit any real websites — they use mock data so you can run them offline.

```bash
pytest
```

If all tests pass, your environment is set up correctly.

---

## Considerations

Web scraping is a powerful tool, but it comes with responsibilities:

- **Respect terms of service.** Always review a site's ToS before scraping. The NYT, Guardian, and most major publications have terms governing automated access.
- **Check `robots.txt`.** Most websites publish a `robots.txt` file (e.g., `https://www.nytimes.com/robots.txt`) that specifies which pages can be accessed by automated tools.
- **Be gentle with servers.** Include delays between requests (the scrapers in this toolkit do this). Hammering a server with rapid requests can disrupt service for everyone.
- **Use APIs when available.** APIs are the *intended* way to access data programmatically. Scraping HTML should be a fallback, not a first choice.
- **Respect copyright.** Collecting text for research is often covered by fair use, but redistribution may not be. Consult your institution's policies.

