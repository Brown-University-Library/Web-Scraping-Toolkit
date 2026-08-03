import csv
from pathlib import Path
from typing import List

import pytest

from Code.nytscraper import scrape_nyt_articles


class DummyResponse:
    def __init__(self, html: str):
        self.content = html.encode("utf-8")


def _write_links_file(path: Path, urls: List[str]) -> None:
    path.write_text("\n".join(urls) + "\n", encoding="utf-8")


def _read_csv_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return list(reader)


def test_scrape_nyt_articles_basic(monkeypatch, tmp_path):
    """
    Scraper should write one row per URL with full text from <p> tags.
    """

    def fake_get(url, headers=None):
        return DummyResponse("<html><body><p>Paragraph one.</p><p>Paragraph two.</p></body></html>")

    monkeypatch.setattr("Code.nytscraper.requests.get", fake_get)

    links_file = tmp_path / "nytlinks.csv"
    output_file = tmp_path / "articlefulltext.csv"
    urls = ["https://www.nytimes.com/2024/01/15/example-article.html"]
    _write_links_file(links_file, urls)

    scrape_nyt_articles(str(links_file), str(output_file))

    rows = _read_csv_rows(output_file)
    # header + one data row
    assert rows[0] == ["Date", "Article Url", "Article Full Text"]
    assert rows[1][1] == urls[0]
    assert "Paragraph one." in rows[1][2]
    assert "Paragraph two." in rows[1][2]


def test_scrape_nyt_articles_js_placeholder(monkeypatch, tmp_path):
    """
    When the page only contains the JS/paywall message, write the UNAVAILABLE placeholder.
    """

    def fake_get(url, headers=None):
        html = "<html><body><p>Please enable JS and disable any ad blocker</p></body></html>"
        return DummyResponse(html)

    monkeypatch.setattr("Code.nytscraper.requests.get", fake_get)

    links_file = tmp_path / "nytlinks.csv"
    output_file = tmp_path / "articlefulltext.csv"
    urls = ["https://www.nytimes.com/2024/01/15/example-article.html"]
    _write_links_file(links_file, urls)

    scrape_nyt_articles(str(links_file), str(output_file))

    rows = _read_csv_rows(output_file)
    assert rows[1][2] == "[UNAVAILABLE: page requires JavaScript / paywall; full text not scraped]"

