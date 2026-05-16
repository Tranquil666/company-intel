import httpx
from bs4 import BeautifulSoup
from models.schemas import Review


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


async def scrape_linkedin(company_name: str, max_results: int = 10) -> list[Review]:
    """
    Scrapes basic public LinkedIn company page info.
    LinkedIn heavily guards reviews — this retrieves what's publicly visible.
    """
    reviews: list[Review] = []
    slug = company_name.lower().replace(" ", "-").replace(",", "").replace(".", "").replace("&", "and")

    url = f"https://www.linkedin.com/company/{slug}/about/"

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=20) as client:
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return reviews

            soup = BeautifulSoup(resp.text, "lxml")

            about_sections = soup.select("p, [class*='about'], [class*='description']")
            for section in about_sections[:5]:
                text = section.get_text(strip=True)
                if len(text) > 80:
                    reviews.append(Review(
                        source="LinkedIn",
                        author="Company Page",
                        rating=None,
                        title="Company Overview",
                        pros=None,
                        cons=None,
                        body=text[:1000],
                        role=None,
                        date=None,
                        sentiment=None,
                    ))
                    break

        except Exception:
            pass

    return reviews
