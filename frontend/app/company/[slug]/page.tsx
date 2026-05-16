"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { analyzeCompany, type CompanyAnalysis } from "@/lib/api";
import CultureChart from "@/components/CultureChart";
import ScoreBar from "@/components/ScoreBar";
import ReviewCard from "@/components/ReviewCard";
import RedFlagCard from "@/components/RedFlagCard";
import ToxicityMeter from "@/components/ToxicityMeter";
import {
  ArrowLeft, CheckCircle2, XCircle, AlertTriangle,
  Building2, Loader2, RefreshCw, Sparkles,
} from "lucide-react";

const VERDICT_CONFIG: Record<string, { emoji: string; gradient: string; border: string; text: string }> = {
  Great:  { emoji: "🌟", gradient: "from-emerald-500/20 to-green-500/10",   border: "border-emerald-500/30", text: "text-emerald-300" },
  Good:   { emoji: "✅", gradient: "from-green-500/20 to-teal-500/10",      border: "border-green-500/30",   text: "text-green-300" },
  Mixed:  { emoji: "⚠️", gradient: "from-amber-500/20 to-yellow-500/10",   border: "border-amber-500/30",   text: "text-amber-300" },
  Toxic:  { emoji: "☣️", gradient: "from-orange-500/20 to-red-500/10",     border: "border-orange-500/30",  text: "text-orange-300" },
  Avoid:  { emoji: "🚫", gradient: "from-red-500/20 to-rose-500/10",       border: "border-red-500/30",     text: "text-red-300" },
};

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`rounded-2xl bg-secondary/60 animate-pulse ${className}`} />;
}

export default function CompanyPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);
  const companyName = decodeURIComponent(slug);

  const [data, setData]         = useState<CompanyAnalysis | null>(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState<string | null>(null);
  const [activeSource, setActiveSource] = useState("All");
  const [activeTab, setActiveTab]       = useState<"all" | "negative" | "positive">("all");

  const fetchData = async () => {
    setLoading(true); setError(null);
    try { setData(await analyzeCompany(companyName)); }
    catch (e: unknown) { setError(e instanceof Error ? e.message : "Something went wrong"); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, [companyName]);

  const sources        = data ? ["All", ...data.sources_scraped] : [];
  const sourceFiltered = data
    ? activeSource === "All" ? data.reviews : data.reviews.filter(r => r.source === activeSource)
    : [];
  const tabReviews     =
    activeTab === "negative" ? sourceFiltered.filter(r => r.sentiment === "negative") :
    activeTab === "positive" ? sourceFiltered.filter(r => r.sentiment === "positive") :
    sourceFiltered;

  const verdict = data ? VERDICT_CONFIG[data.verdict] ?? VERDICT_CONFIG.Mixed : null;

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-grid pointer-events-none opacity-50" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] rounded-full pointer-events-none"
        style={{ background: "var(--gradient-radial)", opacity: 0.6 }} />

      <main className="relative z-10 max-w-6xl mx-auto px-4 py-8">
        {/* Nav */}
        <Link href="/" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-8 transition-colors group">
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
          Back to search
        </Link>

        {/* ── Loading ── */}
        {loading && (
          <div className="space-y-6 animate-float-up">
            <div className="flex items-center justify-center gap-3 py-16 text-muted-foreground">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
              <span>Scraping Reddit, HackerNews, Google News…</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Skeleton className="h-48" /><Skeleton className="h-48" /><Skeleton className="h-48" />
            </div>
            <Skeleton className="h-64" />
          </div>
        )}

        {/* ── Error ── */}
        {error && !loading && (
          <div className="flex flex-col items-center gap-5 py-24 text-center animate-float-up">
            <div className="w-16 h-16 rounded-2xl bg-destructive/10 border border-destructive/30 flex items-center justify-center">
              <AlertTriangle className="w-7 h-7 text-destructive" />
            </div>
            <div>
              <p className="text-lg font-semibold mb-1">Could not analyze this company</p>
              <p className="text-muted-foreground text-sm max-w-md">{error}</p>
            </div>
            <button onClick={fetchData}
              className="px-5 py-2.5 rounded-xl text-white text-sm font-semibold shadow-glow transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{ background: "var(--gradient-primary)" }}>
              Try again
            </button>
          </div>
        )}

        {/* ── Results ── */}
        {data && !loading && (
          <div className="space-y-5 animate-float-up">

            {/* Hero header */}
            <div className={`relative overflow-hidden rounded-3xl border bg-gradient-to-br p-6 ${verdict?.gradient} ${verdict?.border}`}>
              <div className="flex items-center justify-between gap-4 flex-wrap">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-primary/20 border border-primary/30 flex items-center justify-center shadow-glow">
                    <Building2 className="w-7 h-7 text-primary" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold">{companyName}</h1>
                    <p className="text-sm text-muted-foreground">
                      {data.total_reviews} reviews · {data.sources_scraped.join(", ")}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className={`flex items-center gap-2 px-4 py-2 rounded-full border ${verdict?.border} bg-black/20 backdrop-blur-sm`}>
                    <span className="text-lg">{verdict?.emoji}</span>
                    <span className={`font-bold text-sm ${verdict?.text}`}>{data.verdict}</span>
                  </div>
                  <button onClick={fetchData}
                    className="p-2 rounded-xl hover:bg-white/10 transition-colors text-muted-foreground hover:text-foreground">
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Metrics row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Toxicity */}
              <div className="p-6 rounded-3xl border border-border bg-card/60 backdrop-blur-sm shadow-elegant">
                <ToxicityMeter score={data.toxicity_score} />
              </div>

              {/* Score bars */}
              <div className="p-6 rounded-3xl border border-border bg-card/60 backdrop-blur-sm shadow-elegant">
                <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-5">Culture Scores</p>
                <div className="space-y-3.5">
                  <ScoreBar label="Work-Life Balance" value={data.culture_scores.work_life_balance} />
                  <ScoreBar label="Management"        value={data.culture_scores.management} />
                  <ScoreBar label="Compensation"      value={data.culture_scores.compensation} />
                  <ScoreBar label="Career Growth"     value={data.culture_scores.career_growth} />
                  <ScoreBar label="Diversity"         value={data.culture_scores.diversity} />
                </div>
              </div>

              {/* Radar */}
              <div className="p-6 rounded-3xl border border-border bg-card/60 backdrop-blur-sm shadow-elegant flex flex-col">
                <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">Culture Radar</p>
                <CultureChart scores={data.culture_scores} />
              </div>
            </div>

            {/* Red flags */}
            {data.red_flags.length > 0 && (
              <div className="p-6 rounded-3xl border border-border bg-card/60 backdrop-blur-sm shadow-elegant">
                <h2 className="font-semibold mb-4 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  Red Flags
                  <span className="px-2 py-0.5 text-xs rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/20 font-bold">
                    {data.red_flags.length}
                  </span>
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {data.red_flags.map((flag, i) => <RedFlagCard key={i} flag={flag} />)}
                </div>
              </div>
            )}

            {/* AI Summary + Strengths / Weaknesses */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2 p-6 rounded-3xl border border-border bg-card/60 backdrop-blur-sm shadow-elegant">
                <h2 className="font-semibold mb-4 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-primary" />
                  AI Analysis
                </h2>
                <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
                  {data.ai_summary}
                </p>
              </div>

              <div className="space-y-4">
                <div className="p-5 rounded-3xl border border-emerald-500/20 bg-emerald-500/5 backdrop-blur-sm">
                  <h3 className="text-sm font-semibold text-emerald-400 flex items-center gap-1.5 mb-3">
                    <CheckCircle2 className="w-4 h-4" />Strengths
                  </h3>
                  <ul className="space-y-2">
                    {data.strengths.map((s, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-emerald-500 mt-0.5 shrink-0">•</span>{s}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="p-5 rounded-3xl border border-red-500/20 bg-red-500/5 backdrop-blur-sm">
                  <h3 className="text-sm font-semibold text-red-400 flex items-center gap-1.5 mb-3">
                    <XCircle className="w-4 h-4" />Weaknesses
                  </h3>
                  <ul className="space-y-2">
                    {data.weaknesses.map((w, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-red-500 mt-0.5 shrink-0">•</span>{w}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Reviews */}
            <div className="p-6 rounded-3xl border border-border bg-card/60 backdrop-blur-sm shadow-elegant">
              {/* Header + source filter */}
              <div className="flex items-center justify-between gap-3 flex-wrap mb-5">
                <h2 className="font-semibold">
                  Reviews
                  <span className="ml-2 text-muted-foreground font-normal text-sm">({sourceFiltered.length})</span>
                </h2>
                <div className="flex gap-1.5 flex-wrap">
                  {sources.map(s => (
                    <button key={s} onClick={() => setActiveSource(s)}
                      className={`px-3 py-1 text-xs font-medium rounded-full border transition-all ${
                        activeSource === s
                          ? "text-white border-primary shadow-glow"
                          : "border-border text-muted-foreground hover:border-primary/40 hover:text-foreground"
                      }`}
                      style={activeSource === s ? { background: "var(--gradient-primary)" } : {}}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              {/* Sentiment tabs */}
              {(() => {
                const negN = sourceFiltered.filter(r => r.sentiment === "negative").length;
                const posN = sourceFiltered.filter(r => r.sentiment === "positive").length;
                const tabs = [
                  { id: "all"      as const, label: `All (${sourceFiltered.length})` },
                  { id: "negative" as const, label: `Negative (${negN})` },
                  { id: "positive" as const, label: `Positive (${posN})` },
                ];
                return (
                  <>
                    <div className="flex gap-1 mb-5 p-1 rounded-xl bg-secondary/50 w-fit">
                      {tabs.map(t => (
                        <button key={t.id} onClick={() => setActiveTab(t.id)}
                          className={`px-3.5 py-1.5 text-sm rounded-lg font-medium transition-all ${
                            activeTab === t.id
                              ? "bg-card text-foreground shadow-sm"
                              : "text-muted-foreground hover:text-foreground"
                          }`}>
                          {t.label}
                        </button>
                      ))}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {tabReviews.map((r, i) => <ReviewCard key={i} review={r} />)}
                      {tabReviews.length === 0 && (
                        <p className="text-muted-foreground text-sm col-span-2 text-center py-10">
                          No {activeTab !== "all" ? activeTab : ""} reviews found.
                        </p>
                      )}
                    </div>
                  </>
                );
              })()}
            </div>

          </div>
        )}
      </main>
    </div>
  );
}
