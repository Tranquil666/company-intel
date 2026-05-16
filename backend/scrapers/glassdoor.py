import asyncio
import random
from typing import Optional
from playwright.async_api import async_playwright, Page
from models.schemas import Review


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


async def _scroll_and_wait(page: Page):
    await page.evaluate("window.scrollBy(0, 600)")
    await asyncio.sleep(random.uniform(0.8, 1.5))


async def scrape_glassdoor(company_name: str, max_reviews: int = 15) -> list[Review]:
    reviews: list[Review] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=HEADERS["User-Agent"],
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = await context.new_page()

        try:
            search_url = (
                f"https://www.glassdoor.com/Search/results.htm"
                f"?keyword={company_name.replace(' ', '+')}"
            )
            await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)

            company_link = await page.query_selector("a[data-test='employer-short-name']")
            if not company_link:
                company_link = await page.query_selector(".EmployerSearchResult a")
            if not company_link:
                return reviews

            reviews_url = await company_link.get_attribute("href")
            if reviews_url and not reviews_url.startswith("http"):
                reviews_url = "https://www.glassdoor.com" + reviews_url
            reviews_url = reviews_url.replace("/Overview/", "/Reviews/")

            await page.goto(reviews_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
            await _scroll_and_wait(page)

            review_cards = await page.query_selector_all("[id^='empReview']")

            for card in review_cards[:max_reviews]:
                try:
                    rating_el = await card.query_selector(".ratingNumber, .rating-headline-average")
                    rating = None
                    if rating_el:
                        raw = await rating_el.inner_text()
                        rating = float(raw.strip()) if raw.strip() else None

                    title_el = await card.query_selector(".reviewLink, .summary")
                    title = await title_el.inner_text() if title_el else None

                    pros_el = await card.query_selector("[data-test='pros']")
                    pros = await pros_el.inner_text() if pros_el else None

                    cons_el = await card.query_selector("[data-test='cons']")
                    cons = await cons_el.inner_text() if cons_el else None

                    role_el = await card.query_selector(".reviewer, .job-title")
                    role = await role_el.inner_text() if role_el else None

                    date_el = await card.query_selector(".date, .review-date")
                    date = await date_el.inner_text() if date_el else None

                    reviews.append(Review(
                        source="Glassdoor",
                        author="Anonymous",
                        rating=rating,
                        title=title.strip() if title else None,
                        pros=pros.strip() if pros else None,
                        cons=cons.strip() if cons else None,
                        body=f"{pros or ''} {cons or ''}".strip() or None,
                        role=role.strip() if role else None,
                        date=date.strip() if date else None,
                        sentiment=None,
                    ))
                except Exception:
                    continue

        except Exception:
            pass
        finally:
            await browser.close()

    return reviews
