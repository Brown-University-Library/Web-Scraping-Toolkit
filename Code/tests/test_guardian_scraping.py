import csv
import json
from pathlib import Path

import pytest

from Code.guardian_scraping import scrape_guardian_articles


class DummyResponse:
    def __init__(self, html: str):
        self.content = html.encode("utf-8")


def _read_csv_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return list(reader)


def test_scrape_guardian_articles_basic(monkeypatch, tmp_path):
    """
    Scraper should read Guardian API JSON and write one row per result with full text from <p> tags.
    """

    def fake_get(url, headers=None):
        html = "<html><body><p>Guardian paragraph.</p></body></html>"
        return DummyResponse(html)

    monkeypatch.setattr("Code.guardian_scraping.requests.get", fake_get)

    query_file = tmp_path / "query_result.json"
    output_file = tmp_path / "guardian_results.csv"

    sample = {
        "response": {
            "results": [
                {
                    "webTitle": "Sample Guardian Article",
                    "webPublicationDate": "2024-02-01T12:00:00Z",
                    "webUrl": "https://www.theguardian.com/example-article",
                }
            ]
        }
    }
    query_file.write_text(json.dumps(sample), encoding="utf-8")

    scrape_guardian_articles(str(query_file), str(output_file))

    rows = _read_csv_rows(output_file)
    assert rows[0] == ["title", "date", "url", "full text"]
    assert rows[1][0] == "Sample Guardian Article"
    assert rows[1][1] == "2024-02-01"
    assert "Guardian paragraph." in rows[1][3]

