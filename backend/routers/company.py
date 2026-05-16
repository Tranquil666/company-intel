import asyncio
from fastapi import APIRouter, HTTPException, Query
from models.schemas import CompanyAnalysis
from scrapers.glassdoor import scrape_glassdoor
from scrapers.indeed import scrape_indeed
from scrapers.reddit import scrape_reddit
from scrapers.wikipedia import scrape_wikipedia
from scrapers.hackernews import scrape_hackernews
from scrapers.googlenews import scrape_google_news
from scrapers.comparably import scrape_comparably
from analysis.claude_analyzer import analyze_company

router = APIRouter(prefix="/api/company", tags=["company"])


@router.get("/debug")
async def debug(name: str = Query(..., min_length=2)):
    import traceback
    out = {}
    for label, coro in [
        ("wikipedia",   scrape_wikipedia(name)),
        ("hackernews",  scrape_hackernews(name, max_results=5)),
        ("googlenews",  scrape_google_news(name, max_results=5)),
        ("comparably",  scrape_comparably(name, max_reviews=5)),
        ("reddit",      scrape_reddit(name, max_posts=5)),
        ("glassdoor",   scrape_glassdoor(name, max_reviews=3)),
        ("indeed",      scrape_indeed(name, max_reviews=3)),
    ]:
        try:
            r = await coro
            out[label] = {"count": len(r), "sample": r[0].body[:80] if r else None}
        except Exception:
            out[label] = {"error": traceback.format_exc()[-200:]}
    return out


@router.get("/analyze", response_model=CompanyAnalysis)
async def analyze(
    name: str = Query(..., min_length=2),
):
    results = await asyncio.gather(
        scrape_hackernews(name, max_results=20),
        scrape_wikipedia(name),
        scrape_google_news(name, max_results=15),
        scrape_comparably(name, max_reviews=15),
        scrape_glassdoor(name, max_reviews=15),
        scrape_indeed(name, max_reviews=15),
        scrape_reddit(name, max_posts=20),
        return_exceptions=True,
    )

    all_reviews = []
    for result in results:
        if isinstance(result, list):
            all_reviews.extend(result)

    if not all_reviews:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for '{name}'. Try a more common spelling of the company name.",
        )

    try:
        analysis = await analyze_company(name, all_reviews)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    return analysis
