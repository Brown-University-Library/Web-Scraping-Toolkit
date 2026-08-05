import re

from code.nytscraper_login import get_article_text, login


class TextLocator:
    def __init__(self, texts):
        self._texts = texts

    def all_inner_texts(self):
        return self._texts


class TextPage:
    def __init__(self, selectors_to_texts):
        self._selectors_to_texts = selectors_to_texts

    def locator(self, selector):
        return TextLocator(self._selectors_to_texts.get(selector, []))


class LoginLocator:
    def __init__(self, selector, events):
        self.selector = selector
        self.events = events

    @property
    def first(self):
        return self

    def wait_for(self, **kwargs):
        self.events.append(("wait_for", self.selector, kwargs))

    def fill(self, value):
        self.events.append(("fill", self.selector, value))

    def click(self):
        self.events.append(("click", self.selector))


class LoginPage:
    def __init__(self):
        self.events = []

    def goto(self, url, **kwargs):
        self.events.append(("goto", url, kwargs))

    def locator(self, selector):
        return LoginLocator(selector, self.events)

    def wait_for_url(self, pattern, **kwargs):
        assert isinstance(pattern, re.Pattern)
        self.events.append(("wait_for_url", pattern.pattern, kwargs))


def test_get_article_text_prefers_non_trivial_content():
    long_text = "Paragraph " * 100
    page = TextPage({'section[data-testid="article-body"] p': [long_text]})

    result = get_article_text(page)
    assert "Paragraph" in result
    assert len(result) == len(long_text.strip())


def test_get_article_text_returns_placeholder_when_empty():
    page = TextPage({})
    result = get_article_text(page)
    assert result == "[UNAVAILABLE: could not find article body]"


def test_login_fills_email_and_password_and_waits_for_redirect():
    page = LoginPage()
    login(page, "reader@example.com", "secret", completion_timeout=120_000)

    assert ("fill", 'input[name="email"]', "reader@example.com") in page.events
    assert ("fill", 'input[name="password"]', "secret") in page.events
    assert any(event[0] == "click" for event in page.events)
    assert (
        "wait_for_url",
        r"https://(?:www\.)?nytimes\.com(?:/|$)",
        {"timeout": 120_000},
    ) in page.events