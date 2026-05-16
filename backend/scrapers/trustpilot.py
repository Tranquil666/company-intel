import httpx
import re
from bs4 import BeautifulSoup
from models.schemas import Review

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}


async def scrape_trustpilot(company_name: str, max_reviews: int = 10) -> list[Review]:
    reviews: list[Review] = []
    slug = re.sub(r"[^a-z0-9]+", "-", company_name.lower()).strip("-")

    # Try common domain patterns
    domains_to_try = [f"{slug}.com", slug, f"{slug}.io", f"{slug}.co"]

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=15) as client:
        # First search Trustpilot for the company
        try:
            search_resp = await client.get(
                "https://www.trustpilot.com/search",
                params={"query": company_name},
            )
            if search_resp.status_code == 200:
                soup = BeautifulSoup(search_resp.text, "lxml")
                first_result = soup.select_one("a[href*='/review/']")
                if first_result:
                    href = first_result.get("href", "")
                    match = re.search(r"/review/([^/?]+)", href)
                    if match:
                        domains_to_try = [match.group(1)] + domains_to_try
        except Exception:
            pass

        for domain in domains_to_try[:3]:
            try:
                resp = await client.get(f"https://www.trustpilot.com/review/{domain}")
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")

                # Overall rating
                rating_el = soup.select_one("[data-rating-typography], [class*='rating_rating']")
                overall = None
                if rating_el:
                    nums = re.findall(r"\d+\.?\d*", rating_el.get_text())
                    if nums:
                        overall = float(nums[0])

                for card in soup.select("[class*='reviewCard'], article[class*='paper']")[:max_reviews]:
                    title_el = card.select_one("h2, [class*='title']")
                    body_el = card.select_one("p, [class*='body'], [class*='text']")
                    date_el = card.select_one("time")
                    star_el = card.select_one("[class*='star'], [data-service-review-rating]")

                    title = title_el.get_text(strip=True) if title_el else None
                    body = body_el.get_text(strip=True)[:600] if body_el else None
                    date = date_el.get("datetime", "")[:10] if date_el else None

                    rating = None
                    if star_el:
                        nums = re.findall(r"\d+", star_el.get("data-service-review-rating", "") or star_el.get_text())
                        if nums:
                            rating = float(nums[0])

                    if not body and not title:
                        continue

                    reviews.append(Review(
                        source="Trustpilot",
                        author="Anonymous",
                        rating=rating or overall,
                        title=title,
                        pros=None,
                        cons=None,
                        body=body or title,
                        role=None,
                        date=date,
                        sentiment=None,
                    ))

                if reviews:
                    return reviews

            except Exception:
                continue

    return reviews
