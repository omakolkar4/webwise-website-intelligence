
import requests
from bs4 import BeautifulSoup


def load_website(url):
    """Extract readable text from a website."""

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WebsiteQABot/1.0)"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unnecessary elements
        for element in soup([
            "script", "style", "nav", "footer",
            "header", "noscript", "svg"
        ]):
            element.decompose()

        title = (
            soup.title.get_text(strip=True)
            if soup.title else url
        )

        text = soup.get_text(separator=" ", strip=True)

        if len(text) < 100:
            raise ValueError("Not enough readable website content.")

        return {
            "url": url,
            "title": title,
            "text": text
        }

    except requests.RequestException as error:
        raise Exception(f"Website loading failed: {error}")
