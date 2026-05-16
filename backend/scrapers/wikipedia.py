import httpx
from models.schemas import Review


async def scrape_wikipedia(company_name: str) -> list[Review]:
    """Fetch company summary from Wikipedia's public API — always works from cloud IPs."""
    reviews: list[Review] = []

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            # Search for the company article
            search_resp = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": f"{company_name} company",
                    "format": "json",
                    "srlimit": 1,
                },
            )
            if search_resp.status_code != 200:
                return reviews

            results = search_resp.json().get("query", {}).get("search", [])
            if not results:
                return reviews

            title = results[0]["title"]

            # Fetch the article extract
            extract_resp = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "titles": title,
                    "prop": "extracts",
                    "exintro": True,
                    "explaintext": True,
                    "format": "json",
                },
            )
            if extract_resp.status_code != 200:
                return reviews

            pages = extract_resp.json().get("query", {}).get("pages", {})
            for page in pages.values():
                extract = page.get("extract", "").strip()
                if len(extract) > 100:
                    reviews.append(Review(
                        source="Wikipedia",
                        author="Wikipedia",
                        rating=None,
                        title=f"{title} — Company Overview",
                        pros=None,
                        cons=None,
                        body=extract[:1500],
                        role="Public Record",
                        date=None,
                        sentiment=None,
                    ))
                    break

        except Exception:
            pass

    return reviews
