from bs4 import BeautifulSoup
from models.schemas import Review
from scrapers.proxy import scraperapi_url
import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


async def scrape_indeed(company_name: str, max_reviews: int = 15) -> list[Review]:
    reviews: list[Review] = []
    slug = company_name.lower().replace(" ", "-").replace(",", "").replace(".", "")
    target = f"https://www.indeed.com/cmp/{slug}/reviews"
    api_url = scraperapi_url(target, render_js=True)

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=40) as client:
        try:
            resp = await client.get(api_url)
            if resp.status_code != 200 or len(resp.text) < 5000:
                return reviews

            soup = BeautifulSoup(resp.text, "lxml")

            for card in soup.select("[data-tn-component='review'], .cmp-Review, [class*='Review']")[:max_reviews]:
                try:
                    import re
                    rating_el = card.select_one("[class*='ratingNumber'], [class*='rating']")
                    rating = None
                    if rating_el:
                        try:
                            rating = float(rating_el.get_text(strip=True).split()[0])
                        except (ValueError, IndexError):
                            pass

                    title_el = card.select_one("[class*='title'], h2, h3")
                    title = title_el.get_text(strip=True) if title_el else None

                    pros_el = card.select_one("[class*='pro'], [data-tn-element='pros']")
                    pros = pros_el.get_text(strip=True) if pros_el else None

                    cons_el = card.select_one("[class*='con'], [data-tn-element='cons']")
                    cons = cons_el.get_text(strip=True) if cons_el else None

                    body_el = card.select_one("[class*='body'], [class*='text'], p")
                    body = body_el.get_text(strip=True) if body_el else None

                    role_el = card.select_one("[class*='job'], [class*='role']")
                    role = role_el.get_text(strip=True) if role_el else None

                    date_el = card.select_one("[class*='date'], time")
                    date = date_el.get_text(strip=True) if date_el else None

                    if not any([title, body, pros, cons]):
                        continue

                    reviews.append(Review(
                        source="Indeed",
                        author="Anonymous",
                        rating=rating,
                        title=title,
                        pros=pros,
                        cons=cons,
                        body=body,
                        role=role,
                        date=date,
                        sentiment=None,
                    ))
                except Exception:
                    continue
        except Exception:
            pass

    return reviews
