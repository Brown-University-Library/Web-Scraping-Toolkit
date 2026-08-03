# This program takes in the result of a json file that is the result of
    # a Guardian API search query. It produces a spreadsheet containing the
    # following columns: the article title, the date, the url, and the full
    # text of the article

import csv
import json

import requests
from bs4 import BeautifulSoup


def scrape_guardian_articles(
    input_path: str = "query_result.json", output_path: str = "guardian_results.csv"
) -> None:
    """
    Read a Guardian API search result JSON file and write title, date, URL,
    and full text for each article to output_path.
    """
    with open(input_path, "r") as query_json:
        parsed_query = json.load(query_json)

    results = parsed_query["response"]["results"]

    with open(output_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["title", "date", "url", "full text"])

        for result in results:
            title = result["webTitle"]
            date = result["webPublicationDate"][:10]
            url = result["webUrl"]

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"
                )
            }
            response = requests.get(url, headers=headers)
            page_soup = BeautifulSoup(response.content, features="lxml")

            full_text = ""
            for x in page_soup.find_all("p"):
                full_text = full_text + x.get_text() + "\n"

            writer.writerow([title, date, url, full_text])


if __name__ == "__main__":
    scrape_guardian_articles()
    print("Done Scraping!")
