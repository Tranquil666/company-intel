import httpx
from models.schemas import Review


async def scrape_hackernews(company_name: str, max_results: int = 20) -> list[Review]:
    """
    Algolia HN API — open, no auth, no blocking from cloud IPs.
    Searches for posts discussing the company on Hacker News.
    """
    reviews: list[Review] = []
    seen_ids: set[str] = set()

    queries = [
        f"{company_name} work culture",
        f"{company_name} employee",
        f"{company_name} toxic",
        f"working at {company_name}",
    ]

    async with httpx.AsyncClient(timeout=12) as client:
        for query in queries:
            try:
                resp = await client.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={
                        "query": query,
                        "tags": "story",
                        "hitsPerPage": 8,
                    },
                )
                if resp.status_code != 200:
                    continue

                hits = resp.json().get("hits", [])
                for hit in hits:
                    hit_id = hit.get("objectID", "")
                    if hit_id in seen_ids:
                        continue
                    seen_ids.add(hit_id)

                    title = hit.get("title", "")
                    body = (hit.get("story_text") or "").strip()[:800]
                    author = hit.get("author", "")
                    points = hit.get("points", 0)

                    # Only include posts that mention the company
                    combined = (title + " " + body).lower()
                    if company_name.lower() not in combined:
                        continue

                    if not title:
                        continue

                    reviews.append(Review(
                        source="HackerNews",
                        author=f"@{author}" if author else "Anonymous",
                        rating=None,
                        title=title[:200],
                        pros=None,
                        cons=None,
                        body=body or title,
                        role=f"{points} points",
                        date=hit.get("created_at", "")[:10] or None,
                        sentiment=None,
                    ))

                    if len(reviews) >= max_results:
                        return reviews

            except Exception:
                continue

    return reviews
