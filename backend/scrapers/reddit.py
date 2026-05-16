import httpx
from models.schemas import Review

HEADERS = {
    "User-Agent": "CompanyIntel:research:1.0 (by /u/companyintel_bot)",
    "Accept": "application/json",
}

SUBREDDITS = [
    "cscareerquestions", "jobs", "antiwork",
    "ExperiencedDevs", "careerguidance", "AskHR", "WorkReform",
]


async def _search_reddit(client: httpx.AsyncClient, query: str, subreddit: str | None, limit: int) -> list[dict]:
    if subreddit:
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
    else:
        url = "https://www.reddit.com/search.json"

    params = {"q": query, "sort": "relevance", "limit": limit, "type": "link", "t": "all"}
    try:
        resp = await client.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", {}).get("children", [])
    except Exception:
        pass
    return []


async def scrape_reddit(company_name: str, max_posts: int = 20) -> list[Review]:
    reviews: list[Review] = []
    seen_ids: set[str] = set()

    queries = [
        f'"{company_name}" work culture',
        f'"{company_name}" toxic workplace',
        f'"{company_name}" employee review',
        f'"{company_name}" interview experience',
    ]

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        # Global search across all of Reddit
        for query in queries:
            posts = await _search_reddit(client, query, None, 10)
            for post in posts:
                p = post.get("data", {})
                post_id = p.get("id", "")
                if post_id in seen_ids:
                    continue
                seen_ids.add(post_id)

                title = p.get("title", "")
                body = p.get("selftext", "").strip()[:800]
                subreddit = p.get("subreddit", "")
                author = p.get("author", "")

                # Only include posts that actually mention the company
                combined = (title + " " + body).lower()
                if company_name.lower() not in combined:
                    continue

                if not title and not body:
                    continue

                reviews.append(Review(
                    source="Reddit",
                    author=f"u/{author}" if author and author != "[deleted]" else "Anonymous",
                    rating=None,
                    title=title[:200] if title else None,
                    pros=None,
                    cons=None,
                    body=body or title,
                    role=f"r/{subreddit}" if subreddit else None,
                    date=None,
                    sentiment=None,
                ))

                if len(reviews) >= max_posts:
                    return reviews

        # Also search key subreddits directly
        if len(reviews) < 5:
            for sub in SUBREDDITS[:3]:
                posts = await _search_reddit(client, company_name, sub, 5)
                for post in posts:
                    p = post.get("data", {})
                    post_id = p.get("id", "")
                    if post_id in seen_ids:
                        continue
                    seen_ids.add(post_id)

                    title = p.get("title", "")
                    body = p.get("selftext", "").strip()[:800]
                    author = p.get("author", "")

                    if not title and not body:
                        continue

                    reviews.append(Review(
                        source="Reddit",
                        author=f"u/{author}" if author and author != "[deleted]" else "Anonymous",
                        rating=None,
                        title=title[:200] if title else None,
                        pros=None,
                        cons=None,
                        body=body or title,
                        role=f"r/{sub}",
                        date=None,
                        sentiment=None,
                    ))

                    if len(reviews) >= max_posts:
                        return reviews

    return reviews
