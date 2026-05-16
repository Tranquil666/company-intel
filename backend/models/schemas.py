from pydantic import BaseModel
from typing import Optional


class Review(BaseModel):
    source: str
    author: str
    rating: Optional[float]
    title: Optional[str]
    pros: Optional[str]
    cons: Optional[str]
    body: Optional[str]
    role: Optional[str]
    date: Optional[str]
    sentiment: Optional[str]  # positive | neutral | negative


class CultureScores(BaseModel):
    work_life_balance: float
    management: float
    compensation: float
    career_growth: float
    diversity: float
    overall: float


class RedFlag(BaseModel):
    category: str
    description: str
    severity: str  # low | medium | high


class CompanyAnalysis(BaseModel):
    company_name: str
    toxicity_score: float          # 1-10 (10 = most toxic)
    culture_scores: CultureScores
    red_flags: list[RedFlag]
    ai_summary: str
    strengths: list[str]
    weaknesses: list[str]
    verdict: str                   # Great | Good | Mixed | Toxic | Avoid
    reviews: list[Review]
    total_reviews: int
    sources_scraped: list[str]
