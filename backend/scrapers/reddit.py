import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import praw
from models.schemas import Review


def _fetch_reddit_sync(company_name: str, max_posts: int) -> list[Review]:
    client_id = os.getenv("REDDIT_CLIENT_ID", "")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
    user_agent = os.getenv("REDDIT_USER_AGENT", "CompanyIntel/1.0")

    reviews: list[Review] = []

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

        subreddits = ["cscareerquestions", "jobs", "antiwork", "ExperiencedDevs", "careerguidance"]
        query = f'"{company_name}" work culture OR review OR toxic OR management OR interview'

        seen_ids = set()
        for sub in subreddits:
            try:
                subreddit = reddit.subreddit(sub)
                for post in subreddit.search(query, sort="relevance", limit=max_posts // len(subreddits) + 2):
                    if post.id in seen_ids:
                        continue
                    seen_ids.add(post.id)

                    body = post.selftext.strip()[:1000] if post.selftext else None
                    if not body and len(post.title) < 20:
                        continue

                    reviews.append(Review(
                        source="Reddit",
                        author=f"u/{post.author.name}" if post.author else "Anonymous",
                        rating=None,
                        title=post.title[:200],
                        pros=None,
                        cons=None,
                        body=body or post.title,
                        role=None,
                        date=None,
                        sentiment=None,
                    ))
                    if len(reviews) >= max_posts:
                        break
            except Exception:
                continue

    except Exception:
        pass

    return reviews


async def scrape_reddit(company_name: str, max_posts: int = 20) -> list[Review]:
    # PRAW is synchronous — run in a thread pool
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        reviews = await loop.run_in_executor(pool, _fetch_reddit_sync, company_name, max_posts)
    return reviews
