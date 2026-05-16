import re
from bs4 import BeautifulSoup
from models.schemas import Review
from scrapers.proxy import proxied_client, scraperapi_url
import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


async def scrape_glassdoor(company_name: str, max_reviews: int = 15) -> list[Review]:
    reviews: list[Review] = []
    slug = re.sub(r"[^a-z0-9]+", "-", company_name.lower()).strip("-")

    target = f"https://www.glassdoor.com/Reviews/{slug}-reviews-SRCH_KE0,{len(company_name)}.htm"
    # Use JS rendering since Glassdoor renders reviews via React
    api_url = scraperapi_url(target, render_js=True)

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=40) as client:
        try:
            resp = await client.get(api_url)
            if resp.status_code != 200 or len(resp.text) < 5000:
                return reviews

            soup = BeautifulSoup(resp.text, "lxml")

            for card in soup.select("[id^='empReview'], [class*='ReviewCard'], [class*='review']")[:max_reviews]:
                try:
                    rating_el = card.select_one("[class*='ratingNumber'], [class*='StarRating'], .rating")
                    rating = None
                    if rating_el:
                        nums = re.findall(r"\d+\.?\d*", rating_el.get_text())
                        if nums:
                            rating = float(nums[0])
                            if rating > 10:
                                rating = None

                    title_el = card.select_one("[class*='reviewLink'], [class*='summary'], h2, h3")
                    title = title_el.get_text(strip=True) if title_el else None

                    pros_el = card.select_one("[data-test='pros'], [class*='pros'], [class*='Pros']")
                    pros = pros_el.get_text(strip=True) if pros_el else None

                    cons_el = card.select_one("[data-test='cons'], [class*='cons'], [class*='Cons']")
                    cons = cons_el.get_text(strip=True) if cons_el else None

                    role_el = card.select_one("[class*='reviewer'], [class*='jobTitle'], [class*='role']")
                    role = role_el.get_text(strip=True) if role_el else None

                    date_el = card.select_one("time, [class*='date']")
                    date = date_el.get_text(strip=True) if date_el else None

                    if not any([title, pros, cons]):
                        continue

                    reviews.append(Review(
                        source="Glassdoor",
                        author="Anonymous",
                        rating=rating,
                        title=title,
                        pros=pros,
                        cons=cons,
                        body=f"{pros or ''} {cons or ''}".strip() or None,
                        role=role,
                        date=date,
                        sentiment=None,
                    ))
                except Exception:
                    continue
        except Exception:
            pass

    return reviews
