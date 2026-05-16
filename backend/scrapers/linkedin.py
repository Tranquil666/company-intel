from bs4 import BeautifulSoup
from models.schemas import Review
from scrapers.proxy import proxied_client


async def scrape_linkedin(company_name: str, max_results: int = 5) -> list[Review]:
    reviews: list[Review] = []
    slug = (
        company_name.lower()
        .replace(" ", "-").replace(",", "")
        .replace(".", "").replace("&", "and")
    )
    url = f"https://www.linkedin.com/company/{slug}/about/"

    async with proxied_client(timeout=30) as client:
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return reviews

            soup = BeautifulSoup(resp.text, "lxml")
            for section in soup.select("p, [class*='about'], [class*='description']")[:5]:
                text = section.get_text(strip=True)
                if len(text) > 80 and "linkedin" not in text.lower():
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
