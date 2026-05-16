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
