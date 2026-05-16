import json
import os
from groq import Groq
from models.schemas import Review, CompanyAnalysis, CultureScores, RedFlag

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an expert workplace culture analyst. You analyze employee reviews and public sentiment to produce structured, honest assessments of company work culture, toxicity, and employee experience. Be direct, evidence-based, and fair. Output must be valid JSON only — no markdown, no explanation."""

ANALYSIS_PROMPT = """Analyze the following employee and public reviews for "{company_name}" and produce a structured JSON report.

REVIEWS:
{reviews_text}

Respond with ONLY a JSON object with EXACTLY these fields:
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
  "review_sentiments": ["<positive|neutral|negative for each review in order>"]
}}

Rules:
- toxicity_score based on management behavior, overwork, poor communication, retaliation, discrimination
- culture_scores: 1=terrible, 10=excellent
- red_flags: only include if evidence supports it, max 6
- review_sentiments: must have exactly the same count as reviews provided
- Be specific and cite patterns from the reviews"""


def _build_review_text(reviews: list[Review]) -> str:
    parts = []
    for i, r in enumerate(reviews[:40], 1):
        parts.append(
            f"[{i}] Source: {r.source} | Rating: {r.rating or 'N/A'} | Role: {r.role or 'Unknown'}\n"
            f"     Title: {r.title or ''}\n"
            f"     Pros: {r.pros or ''}\n"
            f"     Cons: {r.cons or ''}\n"
            f"     Body: {r.body or ''}\n"
        )
    return "\n".join(parts)


async def analyze_company(company_name: str, reviews: list[Review]) -> CompanyAnalysis:
    reviews_text = _build_review_text(reviews)
    prompt = ANALYSIS_PROMPT.format(company_name=company_name, reviews_text=reviews_text)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=2000,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content.strip()
    data = json.loads(raw)

    sentiments = data.get("review_sentiments", [])
    for i, review in enumerate(reviews):
        if i < len(sentiments):
            review.sentiment = sentiments[i]

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
