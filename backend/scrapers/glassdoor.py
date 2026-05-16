import re
from bs4 import BeautifulSoup
from models.schemas import Review
from scrapers.proxy import proxied_client


async def scrape_glassdoor(company_name: str, max_reviews: int = 15) -> list[Review]:
    reviews: list[Review] = []
    slug = re.sub(r"[^a-z0-9]+", "-", company_name.lower()).strip("-")

    urls_to_try = [
        f"https://www.glassdoor.com/Reviews/{slug}-reviews-SRCH_KE0,{len(company_name)}.htm",
        f"https://www.glassdoor.com/Search/results.htm?keyword={company_name.replace(' ', '+')}",
    ]

    async with proxied_client(timeout=30) as client:
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
