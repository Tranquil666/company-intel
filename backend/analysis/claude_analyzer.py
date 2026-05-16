import json
import os
from groq import Groq
from models.schemas import Review, CompanyAnalysis, CultureScores, RedFlag

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an expert workplace culture analyst. You analyze employee reviews and public sentiment to produce structured, honest assessments of company work culture, toxicity, and employee experience. Be direct, evidence-based, and fair. Output must be valid JSON only — no markdown, no explanation."""

ANALYSIS_PROMPT = """Analyze the following {review_count} reviews for "{company_name}" and produce a structured JSON report.

REVIEWS:
{reviews_text}

There are exactly {review_count} reviews above (numbered [1] through [{review_count}]).

Respond with ONLY a JSON object:
{{
  "toxicity_score": <float 1-10, where 1=extremely healthy, 10=extremely toxic>,
  "culture_scores": {{
    "work_life_balance": <float 1-10>,
    "management": <float 1-10>,
    "compensation": <float 1-10>,
    "career_growth": <float 1-10>,
    "diversity": <float 1-10>,
    "overall": <float 1-10>
  }},
  "red_flags": [
    {{"category": "<string>", "description": "<string>", "severity": "low|medium|high"}}
  ],
  "ai_summary": "<2-3 paragraph honest summary of what it's like to work there>",
  "strengths": ["<string>"],
  "weaknesses": ["<string>"],
  "verdict": "<one of: Great | Good | Mixed | Toxic | Avoid>",
  "review_sentiments": ["<EXACTLY {review_count} values, one per review, each must be positive|neutral|negative>"]
}}

Rules:
- toxicity_score: based on overwork, poor management, retaliation, discrimination, burnout signals
- culture_scores: 1=terrible, 10=excellent
- red_flags: only include if evidence supports it, max 6
- review_sentiments array MUST have exactly {review_count} entries matching reviews [1]–[{review_count}]
- sentiment is negative if the review criticises the company, positive if it praises, neutral otherwise"""


NEGATIVE_KEYWORDS = {
    "toxic", "terrible", "awful", "horrible", "worst", "bad", "poor", "nightmare",
    "miserable", "hate", "fired", "layoff", "layoffs", "burnout", "overwork",
    "underpaid", "exploited", "discrimination", "harassed", "hostile", "retaliation",
    "micromanage", "no work life balance", "avoid", "quit", "resignation", "abusive",
    "manipulative", "cult", "fear", "stressed", "exhausted", "crunch", "not recommended",
    "do not work", "stay away", "run away",
}

POSITIVE_KEYWORDS = {
    "great", "amazing", "excellent", "love", "best", "wonderful", "fantastic",
    "incredible", "awesome", "recommend", "happy", "positive", "supportive",
    "collaborative", "innovative", "growth", "opportunity", "learning", "flexible",
    "good pay", "good culture", "work life balance", "inclusive", "transparent",
    "good management", "great team", "exciting", "rewarding",
}


def _keyword_sentiment(review: Review) -> str:
    text = " ".join(filter(None, [
        review.title, review.body, review.pros, review.cons
    ])).lower()

    neg_hits = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text)
    pos_hits = sum(1 for kw in POSITIVE_KEYWORDS if kw in text)

    # Cons carry extra negative weight
    if review.cons:
        neg_hits += review.cons.lower().count(" ") // 5  # rough word count boost

    if neg_hits > pos_hits:
        return "negative"
    elif pos_hits > neg_hits:
        return "positive"
    return "neutral"


def _build_review_text(reviews: list[Review]) -> str:
    parts = []
    for i, r in enumerate(reviews, 1):
        parts.append(
            f"[{i}] Source: {r.source} | Rating: {r.rating or 'N/A'} | Role: {r.role or 'Unknown'}\n"
            f"     Title: {r.title or ''}\n"
            f"     Pros: {r.pros or ''}\n"
            f"     Cons: {r.cons or ''}\n"
            f"     Body: {(r.body or '')[:300]}\n"
        )
    return "\n".join(parts)


async def analyze_company(company_name: str, reviews: list[Review]) -> CompanyAnalysis:
    # Cap at 40 for Groq token limits, but keyword-score all reviews first
    capped = reviews[:40]
    review_count = len(capped)

    # Pre-fill every review with keyword sentiment as a guaranteed fallback
    for r in reviews:
        r.sentiment = _keyword_sentiment(r)

    reviews_text = _build_review_text(capped)
    prompt = ANALYSIS_PROMPT.format(
        company_name=company_name,
        reviews_text=reviews_text,
        review_count=review_count,
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=3000,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content.strip()
    data = json.loads(raw)

    # Override keyword sentiment with Groq's richer analysis where available
    groq_sentiments = data.get("review_sentiments", [])
    for i, review in enumerate(capped):
        if i < len(groq_sentiments) and groq_sentiments[i] in ("positive", "neutral", "negative"):
            review.sentiment = groq_sentiments[i]
        # else: already has keyword-based sentiment from above

    return CompanyAnalysis(
        company_name=company_name,
        toxicity_score=data["toxicity_score"],
        culture_scores=CultureScores(**data["culture_scores"]),
        red_flags=[RedFlag(**rf) for rf in data.get("red_flags", [])],
        ai_summary=data["ai_summary"],
        strengths=data.get("strengths", []),
        weaknesses=data.get("weaknesses", []),
        verdict=data["verdict"],
        reviews=reviews,
        total_reviews=len(reviews),
        sources_scraped=list({r.source for r in reviews}),
    )
