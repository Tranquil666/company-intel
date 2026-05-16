import httpx
import xml.etree.ElementTree as ET
import re
from models.schemas import Review

HEADERS = {
    "User-Agent": "CompanyIntel:research:1.0 (by /u/companyintel_bot)",
    "Accept": "application/rss+xml, application/xml, text/xml, application/json, */*",
}

QUERIES = [
    '"{company}" work culture',
    '"{company}" toxic workplace',
    '"{company}" employee experience',
    '"{company}" interview',
]


async def _try_rss(client: httpx.AsyncClient, url: str) -> list[dict]:
    """Try Reddit RSS endpoint."""
    posts = []
    try:
        resp = await client.get(url, timeout=12)
        if resp.status_code != 200:
            return posts
        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns)[:8]:
            title_el = entry.find("atom:title", ns)
            content_el = entry.find("atom:content", ns)
            author_el = entry.find(".//atom:name", ns)
            title = title_el.text if title_el is not None else ""
            content = content_el.text if content_el is not None else ""
            author = author_el.text if author_el is not None else ""
            if content:
                content = re.sub(r"<[^>]+>", "", content).strip()[:600]
            posts.append({"title": title, "body": content, "author": author})
    except Exception:
        pass
    return posts


async def scrape_reddit(company_name: str, max_posts: int = 20) -> list[Review]:
    reviews: list[Review] = []
    seen: set[str] = set()

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        for q_template in QUERIES:
            query = q_template.format(company=company_name)
            encoded = query.replace(" ", "+").replace('"', "%22")

            # Try RSS (different route than JSON API)
            rss_url = f"https://www.reddit.com/search.rss?q={encoded}&sort=relevance&t=all"
            posts = await _try_rss(client, rss_url)

            for post in posts:
                key = post["title"][:60]
                if key in seen:
                    continue
                seen.add(key)

                combined = (post["title"] + " " + post["body"]).lower()
                if company_name.lower() not in combined:
                    continue

                reviews.append(Review(
                    source="Reddit",
                    author=f"u/{post['author']}" if post["author"] else "Anonymous",
                    rating=None,
                    title=post["title"][:200] or None,
                    pros=None,
                    cons=None,
                    body=post["body"] or post["title"],
                    role=None,
                    date=None,
                    sentiment=None,
                ))

                if len(reviews) >= max_posts:
                    return reviews

    return reviews
