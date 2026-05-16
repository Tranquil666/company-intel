import httpx
import re
from bs4 import BeautifulSoup
from models.schemas import Review

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
}


async def scrape_glassdoor(company_name: str, max_reviews: int = 15) -> list[Review]:
    reviews: list[Review] = []

    slug = re.sub(r"[^a-z0-9]+", "-", company_name.lower()).strip("-")
    urls_to_try = [
        f"https://www.glassdoor.com/Reviews/{slug}-reviews-SRCH_KE0,{len(company_name)}.htm",
        f"https://www.glassdoor.com/Search/results.htm?keyword={company_name.replace(' ', '+')}",
    ]

    async with httpx.AsyncClient(
        headers=HEADERS, follow_redirects=True, timeout=20
    ) as client:
        html = None
        for url in urls_to_try:
            try:
                resp = await client.get(url)
                if resp.status_code == 200 and len(resp.text) > 5000:
                    html = resp.text
                    break
            except Exception:
                continue

        if not html:
            return reviews

        soup = BeautifulSoup(html, "lxml")

        for card in soup.select("[id^='empReview'], .review, [class*='ReviewCard']")[:max_reviews]:
            try:
                rating_el = card.select_one("[class*='ratingNumber'], .rating, [class*='StarRating']")
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

                date_el = card.select_one("time, [class*='date'], [class*='Date']")
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

    return reviews
