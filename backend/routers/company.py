import asyncio
from fastapi import APIRouter, HTTPException, Query
from models.schemas import CompanyAnalysis
from scrapers.glassdoor import scrape_glassdoor
from scrapers.indeed import scrape_indeed
from scrapers.reddit import scrape_reddit
from scrapers.linkedin import scrape_linkedin
from scrapers.wikipedia import scrape_wikipedia
from analysis.claude_analyzer import analyze_company

router = APIRouter(prefix="/api/company", tags=["company"])


@router.get("/debug")
async def debug(name: str = Query(..., min_length=2)):
    """Step-by-step tracer for Wikipedia + Reddit scrapers."""
    import httpx, traceback
    out = {}

    # --- Wikipedia step-by-step ---
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params={"action": "query", "list": "search",
                        "srsearch": f"{name} company", "format": "json", "srlimit": 1},
            )
            out["wiki_status"] = r.status_code
            data = r.json()
            hits = data.get("query", {}).get("search", [])
            out["wiki_hits"] = len(hits)
            out["wiki_title"] = hits[0]["title"] if hits else None
    except Exception:
        out["wiki_error"] = traceback.format_exc()[-300:]

    # --- Reddit step-by-step ---
    try:
        async with httpx.AsyncClient(
            headers={"User-Agent": "CompanyIntel:research:1.0 (by /u/companyintel_bot)",
                     "Accept": "application/json"},
            timeout=12
        ) as client:
            r = await client.get(
                "https://www.reddit.com/search.json",
                params={"q": f'"{name}" work culture', "sort": "relevance", "limit": 5},
            )
            out["reddit_status"] = r.status_code
            data = r.json()
            posts = data.get("data", {}).get("children", [])
            out["reddit_posts"] = len(posts)
            out["reddit_sample"] = posts[0]["data"]["title"][:80] if posts else None
    except Exception:
        out["reddit_error"] = traceback.format_exc()[-300:]

    return out


@router.get("/analyze", response_model=CompanyAnalysis)
async def analyze(
    name: str = Query(..., min_length=2, description="Company name to analyze"),
):
    if not name.strip():
        raise HTTPException(status_code=400, detail="Company name is required")

    results = await asyncio.gather(
        scrape_glassdoor(name, max_reviews=15),
        scrape_indeed(name, max_reviews=15),
        scrape_reddit(name, max_posts=25),
        scrape_linkedin(name, max_results=5),
        scrape_wikipedia(name),
        return_exceptions=True,
    )

    all_reviews = []
    for result in results:
        if isinstance(result, list):
            all_reviews.extend(result)

    if not all_reviews:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No data found for '{name}'. "
                "Try a shorter or more commonly known version of the company name."
            ),
        )

    try:
        analysis = await analyze_company(name, all_reviews)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    return analysis


@router.get("/nettest")
async def nettest():
    """Test if outbound HTTP works from this serverless function."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://httpbin.org/get")
            return {"status": r.status_code, "ok": r.status_code == 200}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
