const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Review {
  source: string;
  author: string;
  rating: number | null;
  title: string | null;
  pros: string | null;
  cons: string | null;
  body: string | null;
  role: string | null;
  date: string | null;
  sentiment: "positive" | "neutral" | "negative" | null;
}

export interface CultureScores {
  work_life_balance: number;
  management: number;
  compensation: number;
  career_growth: number;
  diversity: number;
  overall: number;
}

export interface RedFlag {
  category: string;
  description: string;
  severity: "low" | "medium" | "high";
}

export interface CompanyAnalysis {
  company_name: string;
  toxicity_score: number;
  culture_scores: CultureScores;
  red_flags: RedFlag[];
  ai_summary: string;
  strengths: string[];
  weaknesses: string[];
  verdict: "Great" | "Good" | "Mixed" | "Toxic" | "Avoid";
  reviews: Review[];
  total_reviews: number;
  sources_scraped: string[];
}

export async function analyzeCompany(name: string): Promise<CompanyAnalysis> {
  const res = await fetch(
    `${API_BASE}/api/company/analyze?name=${encodeURIComponent(name)}`
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || "Failed to analyze company");
  }
  return res.json();
}
