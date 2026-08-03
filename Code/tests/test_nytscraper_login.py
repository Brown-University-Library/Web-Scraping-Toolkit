from types import SimpleNamespace

from Code.nytscraper_login import get_article_text


class FakeLocator:
    def __init__(self, texts):
        self._texts = texts

    def count(self):
        return len(self._texts)

    def all_inner_texts(self):
        return self._texts


class FakePage:
    def __init__(self, selectors_to_texts):
        self._selectors_to_texts = selectors_to_texts

    def locator(self, selector):
        texts = self._selectors_to_texts.get(selector, [])
        return FakeLocator(texts)


def test_get_article_text_prefers_non_trivial_content():
    """
    get_article_text should return a substantial body of text when available.
    """
    long_text = "Paragraph " * 100
    page = FakePage({"section[data-testid=\"article-body\"] p": [long_text]})

    result = get_article_text(page)
    assert "Paragraph" in result
    assert len(result) == len(long_text.strip())


def test_get_article_text_returns_placeholder_when_empty():
    """
    If no selectors match, get_article_text should return the UNAVAILABLE placeholder.
    """
    page = FakePage({})
    result = get_article_text(page)
    assert result == "[UNAVAILABLE: could not find article body]"

