import httpx
import xml.etree.ElementTree as ET
from models.schemas import Review

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


async def scrape_google_news(company_name: str, max_results: int = 15) -> list[Review]:
    reviews: list[Review] = []

    queries = [
        f'"{company_name}" work culture employees',
        f'"{company_name}" toxic workplace layoffs',
        f'"{company_name}" employee review',
    ]

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=12) as client:
        for query in queries:
            try:
                url = "https://news.google.com/rss/search"
                resp = await client.get(url, params={"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"})
                if resp.status_code != 200:
                    continue

                root = ET.fromstring(resp.text)
                items = root.findall(".//item")

                for item in items[:6]:
                    title_el = item.find("title")
                    desc_el = item.find("description")
                    pub_el = item.find("pubDate")
                    source_el = item.find("source")

                    title = title_el.text if title_el is not None else None
                    desc = desc_el.text if desc_el is not None else None
                    date = pub_el.text[:16] if pub_el is not None else None
                    source = source_el.text if source_el is not None else "News"

                    if not title:
                        continue

                    # Strip HTML tags from description
                    if desc:
                        import re
                        desc = re.sub(r"<[^>]+>", "", desc).strip()[:500]

                    reviews.append(Review(
                        source="Google News",
                        author=source,
                        rating=None,
                        title=title[:200],
                        pros=None,
                        cons=None,
                        body=desc or title,
                        role="News Article",
                        date=date,
                        sentiment=None,
                    ))

                    if len(reviews) >= max_results:
                        return reviews

            except Exception:
                continue

    return reviews
