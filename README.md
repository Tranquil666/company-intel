# CompanyIntel — Workplace Culture Intelligence

> Know before you join. AI-powered company culture analysis aggregated from Reddit, HackerNews, Google News, Wikipedia, Glassdoor, and more.

**Live demo → [frontend-tranquil666s-projects.vercel.app](https://frontend-tranquil666s-projects.vercel.app)**

---

## What it does

Search any company and get an instant, AI-generated intelligence report:

- **Toxicity Score** (1–10) — how healthy or toxic the work culture is
- **Culture Breakdown** — work-life balance, management, compensation, career growth, diversity
- **Red Flags** — specific warnings with severity levels (high / medium / low)
- **AI Summary** — honest 2–3 paragraph analysis powered by Groq (Llama 3.3 70B)
- **Strengths & Weaknesses** — bullet-point highlights
- **Verdict** — Great / Good / Mixed / Toxic / Avoid
- **Reviews** — raw data from each source, filterable by source and sentiment (positive / negative / neutral)

![CompanyIntel Screenshot](https://github.com/Tranquil666/company-intel/raw/main/docs/screenshot.png)

---

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 16, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| Backend | FastAPI (Python 3.12), httpx, BeautifulSoup |
| AI Analysis | Groq API — `llama-3.3-70b-versatile` |
| Scraping Proxy | ScraperAPI (bypasses bot protection for Glassdoor/Indeed) |
| Deployment | Vercel (both frontend + backend serverless) |

---

## Data Sources

| Source | What it provides | Method |
|---|---|---|
| **HackerNews** | Tech community discussions on company culture | Algolia API (open) |
| **Reddit** | Employee experiences, subreddit discussions | RSS feed + JSON API via ScraperAPI |
| **Google News** | Recent news articles about company culture & employees | RSS feed (open) |
| **Wikipedia** | Company background and public record | Wikipedia API (open) |
| **Glassdoor** | Employee ratings and reviews | ScraperAPI + JS rendering |
| **Indeed** | Employee reviews | ScraperAPI + JS rendering |

---

## Project Structure

```
company-intel/
├── backend/                    # FastAPI Python backend
│   ├── main.py                 # App entry point + CORS
│   ├── api/
│   │   └── index.py            # Vercel serverless entry point
│   ├── routers/
│   │   └── company.py          # /api/company/analyze endpoint
│   ├── scrapers/
│   │   ├── proxy.py            # ScraperAPI proxy helper
│   │   ├── glassdoor.py        # Glassdoor scraper (JS rendered)
│   │   ├── indeed.py           # Indeed scraper (JS rendered)
│   │   ├── reddit.py           # Reddit RSS + JSON scraper
│   │   ├── hackernews.py       # HackerNews Algolia API
│   │   ├── googlenews.py       # Google News RSS
│   │   ├── wikipedia.py        # Wikipedia API
│   │   ├── linkedin.py         # LinkedIn (via ScraperAPI)
│   │   ├── trustpilot.py       # Trustpilot scraper
│   │   └── comparably.py       # Comparably scraper
│   ├── analysis/
│   │   └── claude_analyzer.py  # Groq LLM analysis + sentiment
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   ├── requirements.txt
│   ├── Dockerfile              # For Railway/self-hosted deployment
│   └── vercel.json             # Vercel serverless config
│
├── frontend/                   # Next.js frontend
│   ├── app/
│   │   ├── page.tsx            # Search home page
│   │   └── company/[slug]/
│   │       └── page.tsx        # Company results page
│   ├── components/
│   │   ├── ToxicityMeter.tsx   # Animated 1–10 toxicity gauge
│   │   ├── CultureChart.tsx    # Radar chart (Recharts)
│   │   ├── ScoreBar.tsx        # Colored score bar
│   │   ├── ReviewCard.tsx      # Individual review card
│   │   └── RedFlagCard.tsx     # Red flag warning card
│   └── lib/
│       └── api.ts              # Backend API client + TypeScript types
│
└── start.sh                    # Local development startup script
```

---

## Getting Started (Local)

### Prerequisites

- Node.js 18+
- Python 3.12+
- A [Groq API key](https://console.groq.com) (free)
- A [ScraperAPI key](https://scraperapi.com) (free — 5,000 req/month)
- Optional: [Reddit API credentials](https://www.reddit.com/prefs/apps)

### 1. Clone

```bash
git clone https://github.com/Tranquil666/company-intel.git
cd company-intel
```

### 2. Configure environment

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
GROQ_API_KEY=gsk_...
SCRAPER_API_KEY=your_scraperapi_key

# Optional — for Reddit JSON API (RSS works without these)
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
```

### 3. Start everything

```bash
chmod +x start.sh
./start.sh
```

This will:
- Create a Python virtualenv and install dependencies
- Install Playwright's Chromium browser
- Start the FastAPI backend on **http://localhost:8000**
- Start the Next.js frontend on **http://localhost:3001**

---

## Deploying Your Own Instance

### Frontend → Vercel

```bash
cd frontend
npx vercel --prod
# Set NEXT_PUBLIC_API_URL to your backend URL
```

### Backend → Vercel (Serverless)

```bash
cd backend
npx vercel --prod
# Add environment variables in the Vercel dashboard:
# GROQ_API_KEY, SCRAPER_API_KEY
```

> **Note:** Vercel's serverless functions have a 60-second max execution time. All scrapers run concurrently so this is typically fine.

### Backend → Railway (Recommended for Glassdoor/Indeed)

Railway supports Docker and has different IP ranges than AWS, which means Glassdoor/Indeed scraping works without ScraperAPI:

1. Go to [railway.app](https://railway.app/new) → Deploy from GitHub
2. Select `Tranquil666/company-intel` → Root directory: `backend`
3. Railway auto-detects the Dockerfile
4. Add environment variables: `GROQ_API_KEY`, optionally `SCRAPER_API_KEY`

---

## API Reference

### `GET /api/company/analyze`

Analyze a company by name.

**Query params:**

| Param | Type | Description |
|---|---|---|
| `name` | string | Company name (e.g. `Amazon`, `Google`) |

**Response:**

```json
{
  "company_name": "Amazon",
  "toxicity_score": 8.2,
  "culture_scores": {
    "work_life_balance": 3.5,
    "management": 4.0,
    "compensation": 7.0,
    "career_growth": 6.5,
    "diversity": 5.5,
    "overall": 5.1
  },
  "red_flags": [
    {
      "category": "Overwork",
      "description": "Multiple reports of 60+ hour weeks and burnout",
      "severity": "high"
    }
  ],
  "ai_summary": "...",
  "strengths": ["Competitive compensation", "Career acceleration"],
  "weaknesses": ["Work-life balance", "Management inconsistency"],
  "verdict": "Mixed",
  "reviews": [...],
  "total_reviews": 51,
  "sources_scraped": ["HackerNews", "Reddit", "Google News", "Wikipedia"]
}
```

### `GET /health`

Returns `{"status": "ok"}`.

---

## How Sentiment Analysis Works

Every review gets a sentiment label via a two-layer approach:

1. **Keyword matching (instant fallback)** — runs on every review using a curated list of positive/negative workplace keywords. Guarantees no review is ever left unlabeled.

2. **Groq LLM (rich analysis)** — Llama 3.3 70B analyses up to 40 reviews at once and returns a per-review sentiment array. This overrides the keyword fallback where available.

The LLM is also responsible for the toxicity score, culture scores, red flags, summary, and verdict.

---

## Environment Variables

### Backend

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ | Groq API key for LLM analysis |
| `SCRAPER_API_KEY` | Recommended | ScraperAPI key for Glassdoor/Indeed/Reddit |
| `REDDIT_CLIENT_ID` | Optional | Reddit OAuth for JSON API |
| `REDDIT_CLIENT_SECRET` | Optional | Reddit OAuth secret |

### Frontend

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | ✅ | Backend base URL (e.g. `https://your-backend.vercel.app`) |

---

## License

MIT
