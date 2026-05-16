import httpx
import re
from bs4 import BeautifulSoup
from models.schemas import Review

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


async def scrape_comparably(company_name: str, max_reviews: int = 15) -> list[Review]:
    reviews: list[Review] = []

    slug = re.sub(r"[^a-z0-9]+", "-", company_name.lower()).strip("-")
    urls = [
        f"https://www.comparably.com/companies/{slug}/reviews",
        f"https://www.comparably.com/companies/{slug}",
    ]

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=15) as client:
        for url in urls:
            try:
                resp = await client.get(url)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")

                # Extract overall ratings if available
                rating_el = soup.select_one("[class*='overallGrade'], [class*='score'], .grade")
                overall_rating = None
                if rating_el:
                    nums = re.findall(r"\d+\.?\d*", rating_el.get_text())
                    if nums:
                        overall_rating = float(nums[0])
                        if overall_rating > 10:
                            overall_rating = overall_rating / 10

                # Extract review cards
                cards = soup.select("[class*='reviewCard'], [class*='review-item'], .cmt-body, [class*='ReviewCard']")

                for card in cards[:max_reviews]:
                    title_el = card.select_one("h3, h4, [class*='title']")
                    body_el = card.select_one("p, [class*='body'], [class*='text']")
                    role_el = card.select_one("[class*='role'], [class*='job'], [class*='position']")
                    date_el = card.select_one("time, [class*='date']")

                    title = title_el.get_text(strip=True) if title_el else None
                    body = body_el.get_text(strip=True) if body_el else None
                    role = role_el.get_text(strip=True) if role_el else None
                    date = date_el.get_text(strip=True) if date_el else None

                    if not body and not title:
                        continue

                    reviews.append(Review(
                        source="Comparably",
                        author="Anonymous",
                        rating=overall_rating,
                        title=title,
                        pros=None,
                        cons=None,
                        body=body or title,
                        role=role,
                        date=date,
                        sentiment=None,
                    ))

                if reviews:
                    break

            except Exception:
                continue

    return reviews
