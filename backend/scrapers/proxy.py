import os
import httpx

SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY", "")


def scraperapi_url(target_url: str, render_js: bool = False) -> str:
    """Wrap any URL with ScraperAPI to bypass bot detection."""
    base = "https://api.scraperapi.com"
    params = f"api_key={SCRAPER_API_KEY}&url={target_url}"
    if render_js:
        params += "&render=true"
    return f"{base}?{params}"


def proxied_client(timeout: int = 25) -> httpx.AsyncClient:
    """httpx client that routes through ScraperAPI proxy."""
    proxy = f"http://scraperapi:{SCRAPER_API_KEY}@proxy-server.scraperapi.com:8001"
    return httpx.AsyncClient(
        proxy=proxy,
        verify=False,
        timeout=timeout,
        follow_redirects=True,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        },
    )
