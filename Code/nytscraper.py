import csv
import requests
from bs4 import BeautifulSoup


def scrape_nyt_articles(input_path: str = "nytlinks.csv", output_path: str = "articlefulltext.csv") -> None:
    """
    Read NYT article URLs from input_path and write date, URL, and full text to output_path.
    """
    with open(input_path, "r") as fil1:
        articles = [line.rstrip("\n") for line in fil1 if line.strip()]

    articles_text = []

    for article in articles:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"
            )
        }
        response = requests.get(article, headers=headers)
        page_soup = BeautifulSoup(response.content, features="lxml")

        full_text = ""
        for x in page_soup.find_all("p"):
            full_text = full_text + x.get_text() + "\n"

        lowered = full_text.lower()
        if "please enable js" in lowered or "disable any ad blocker" in lowered:
            full_text = "[UNAVAILABLE: page requires JavaScript / paywall; full text not scraped]"

        articles_text.append(full_text)

    with open(output_path, "w", newline="") as fil2:
        writer = csv.writer(fil2)
        writer.writerow(["Date", "Article Url", "Article Full Text"])

        for i, article in enumerate(articles):
            date = article[24:34]
            writer.writerow([date, article, articles_text[i]])


if __name__ == "__main__":
    scrape_nyt_articles()
    print("Done Scraping!")
