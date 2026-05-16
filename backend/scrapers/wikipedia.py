import httpx
from models.schemas import Review

# Wikipedia API requires a meaningful User-Agent identifying the app
HEADERS = {
    "User-Agent": "CompanyIntel/1.0 (https://github.com/Tranquil666/company-intel; research tool)",
    "Accept": "application/json",
}


async def scrape_wikipedia(company_name: str) -> list[Review]:
    reviews: list[Review] = []

    async with httpx.AsyncClient(headers=HEADERS, timeout=12) as client:
        try:
            search_resp = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": f"{company_name} company",
                    "format": "json",
                    "srlimit": 1,
                    "formatversion": "2",
                },
            )
            if search_resp.status_code != 200:
                return reviews

            results = search_resp.json().get("query", {}).get("search", [])
            if not results:
                return reviews

            title = results[0]["title"]

            extract_resp = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "titles": title,
                    "prop": "extracts",
                    "exintro": True,
                    "explaintext": True,
                    "format": "json",
                    "formatversion": "2",
                },
            )
            if extract_resp.status_code != 200:
                return reviews

            pages = extract_resp.json().get("query", {}).get("pages", [])
            for page in pages:
                extract = page.get("extract", "").strip()
                if len(extract) > 100:
                    reviews.append(Review(
                        source="Wikipedia",
                        author="Wikipedia",
                        rating=None,
                        title=f"{title} — Overview",
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
