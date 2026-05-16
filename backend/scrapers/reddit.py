import httpx
import xml.etree.ElementTree as ET
import re
from models.schemas import Review

# Reddit RSS works without proxy — keeping direct headers
HEADERS = {
    "User-Agent": "CompanyIntel:research:1.0 (by /u/companyintel_bot)",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# Reddit JSON via ScraperAPI to bypass 403
from scrapers.proxy import proxied_client

QUERIES = [
    '"{company}" work culture',
    '"{company}" toxic workplace',
    '"{company}" employee experience',
]


async def _rss_posts(company_name: str, max_posts: int) -> list[Review]:
    reviews: list[Review] = []
    seen: set[str] = set()

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=12) as client:
        for q_template in QUERIES[:2]:
            query = q_template.format(company=company_name)
            encoded = query.replace(" ", "+").replace('"', "%22")
            try:
                resp = await client.get(
                    f"https://www.reddit.com/search.rss?q={encoded}&sort=relevance&t=all"
                )
                if resp.status_code != 200:
                    continue

                root = ET.fromstring(resp.text)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                for entry in root.findall("atom:entry", ns):
                    title_el = entry.find("atom:title", ns)
                    content_el = entry.find("atom:content", ns)
                    author_el = entry.find(".//atom:name", ns)

                    title = title_el.text if title_el is not None else ""
                    body = content_el.text if content_el is not None else ""
                    author = author_el.text if author_el is not None else ""

                    if body:
                        body = re.sub(r"<[^>]+>", "", body).strip()[:600]

                    key = title[:60]
                    if key in seen:
                        continue
                    seen.add(key)

                    combined = (title + " " + body).lower()
                    if company_name.lower() not in combined:
                        continue

                    reviews.append(Review(
                        source="Reddit",
                        author=f"u/{author}" if author else "Anonymous",
                        rating=None,
                        title=title[:200] or None,
                        pros=None,
                        cons=None,
                        body=body or title,
                        role=None,
                        date=None,
                        sentiment=None,
                    ))

                    if len(reviews) >= max_posts:
                        return reviews
            except Exception:
                continue

    return reviews


async def _json_posts(company_name: str, max_posts: int) -> list[Review]:
    """Reddit JSON API via ScraperAPI proxy."""
    reviews: list[Review] = []
    seen: set[str] = set()

    subreddits = ["cscareerquestions", "jobs", "antiwork", "ExperiencedDevs", "careerguidance"]

    async with proxied_client(timeout=30) as client:
        for sub in subreddits:
            try:
                url = f"https://www.reddit.com/r/{sub}/search.json?q={company_name}&restrict_sr=on&sort=relevance&limit=5"
                resp = await client.get(url)
                if resp.status_code != 200:
                    continue

                posts = resp.json().get("data", {}).get("children", [])
                for post in posts:
                    p = post.get("data", {})
                    pid = p.get("id", "")
                    if pid in seen:
                        continue
                    seen.add(pid)

                    title = p.get("title", "")
                    body = (p.get("selftext") or "").strip()[:600]
                    author = p.get("author", "")

                    if not title:
                        continue

                    reviews.append(Review(
                        source="Reddit",
                        author=f"u/{author}" if author else "Anonymous",
                        rating=None,
                        title=title[:200],
                        pros=None,
                        cons=None,
                        body=body or title,
                        role=f"r/{sub}",
                        date=None,
                        sentiment=None,
                    ))

                    if len(reviews) >= max_posts:
                        return reviews
            except Exception:
                continue

    return reviews


async def scrape_reddit(company_name: str, max_posts: int = 20) -> list[Review]:
    # Try RSS first (no proxy needed), fall back to proxied JSON
    reviews = await _rss_posts(company_name, max_posts)
    if len(reviews) < 5:
        proxied = await _json_posts(company_name, max_posts - len(reviews))
        seen_titles = {r.title for r in reviews}
        for r in proxied:
            if r.title not in seen_titles:
                reviews.append(r)
    return reviews[:max_posts]
