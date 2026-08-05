import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from code import nytscraper, nytscraper_login


class SharedHelpersTests(unittest.TestCase):
    def test_read_urls_accepts_header_and_utf8_bom(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "links.csv"
            path.write_text("\ufeffArticle Url\nhttps://www.nytimes.com/2024/01/15/a.html\n\n")
            self.assertEqual(
                nytscraper.read_urls(path),
                ["https://www.nytimes.com/2024/01/15/a.html"],
            )
            self.assertEqual(nytscraper_login.read_urls(path), nytscraper.read_urls(path))

    def test_date_extraction_does_not_depend_on_string_position(self):
        url = "https://www.nytimes.com/2024/01/15/world/example.html?x=1"
        self.assertEqual(nytscraper.extract_date(url), "2024-01-15")
        self.assertEqual(nytscraper_login.extract_date(url), "2024-01-15")
        self.assertEqual(nytscraper.extract_date("https://nyti.ms/example"), "")

    def test_url_validation(self):
        self.assertTrue(nytscraper.is_http_url("https://www.nytimes.com/a"))
        self.assertFalse(nytscraper.is_http_url("Article Url"))
        self.assertFalse(nytscraper.is_http_url("javascript:alert(1)"))


class BasicScraperTests(unittest.TestCase):
    def test_extracts_paragraphs(self):
        html = "<html><p>First paragraph.</p><p>Second <b>paragraph</b>.</p></html>"
        self.assertEqual(
            nytscraper.extract_article_text(html),
            "First paragraph.\nSecond paragraph .",
        )

    def test_detects_js_block_page(self):
        html = "<p>Please enable JS and disable any ad blocker.</p>"
        self.assertEqual(nytscraper.extract_article_text(html), nytscraper.UNAVAILABLE)


class FakeLocator:
    def __init__(self, texts):
        self._texts = texts

    def all_inner_texts(self):
        return self._texts


class LoginScraperTests(unittest.TestCase):
    def test_article_extraction_deduplicates_paragraphs(self):
        paragraph = "A sufficiently detailed article paragraph " * 4
        page = Mock()
        page.locator.return_value = FakeLocator([paragraph, paragraph, paragraph + "ending"])
        text = nytscraper_login.get_article_text(page)
        self.assertEqual(text.count(paragraph.strip()), 2)

    def test_short_non_article_text_is_unavailable(self):
        page = Mock()
        page.locator.return_value = FakeLocator(["Sign up for our newsletter"])
        self.assertEqual(nytscraper_login.get_article_text(page), nytscraper_login.UNAVAILABLE)

    def test_invalid_url_is_written_without_navigation(self):
        page = Mock()
        rows = []

        class Writer:
            def writerow(self, row):
                rows.append(row)

        nytscraper_login.scrape_articles(page, ["not-a-url"], Writer())
        page.goto.assert_not_called()
        self.assertEqual(rows[0][2], "[INVALID URL]")


if __name__ == "__main__":
    unittest.main()