import csv
from pathlib import Path
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup

DEFAULT_URL = "https://news.ycombinator.com/"
OUTPUT_FILE = Path("scraped_data.csv")


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.text


def extract_headlines(html: str) -> List[Tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    results: List[Tuple[str, str]] = []

    selectors = [".titleline > a", "h2 a", "h3 a", "a.storylink"]
    seen = set()

    for selector in selectors:
        for element in soup.select(selector):
            title = element.get_text(strip=True)
            link = element.get("href", "")
            key = (title, link)
            if title and key not in seen:
                seen.add(key)
                results.append(key)

        if results:
            break

    return results


def save_to_csv(rows: List[Tuple[str, str]], output_file: Path) -> None:
    with output_file.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["title", "link"])
        writer.writerows(rows)


def main() -> None:
    print("Web Scraping with BeautifulSoup")
    print("Leave blank to use default URL (Hacker News).\n")

    raw_url = input("Enter webpage URL: ").strip()
    url = raw_url or DEFAULT_URL

    try:
        html = fetch_html(url)
        data = extract_headlines(html)

        if not data:
            print("No matching headline/link elements found on this page.")
            return

        save_to_csv(data, OUTPUT_FILE)
        print(f"Successfully extracted {len(data)} rows.")
        print(f"Saved to: {OUTPUT_FILE.resolve()}")
    except requests.exceptions.MissingSchema:
        print("Invalid URL format. Include http:// or https://")
    except requests.exceptions.ConnectionError:
        print("Network error. Please check your internet connection.")
    except requests.exceptions.Timeout:
        print("Request timed out. Please try again.")
    except requests.exceptions.HTTPError as exc:
        code = exc.response.status_code if exc.response is not None else "Unknown"
        print(f"HTTP error while fetching page: {code}")
    except requests.exceptions.RequestException as exc:
        print(f"Request failed: {exc}")
    except OSError as exc:
        print(f"Failed to write CSV file: {exc}")


if __name__ == "__main__":
    main()
