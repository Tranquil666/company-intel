"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { analyzeCompany, type CompanyAnalysis } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import ToxicityMeter from "@/components/ToxicityMeter";
import CultureChart from "@/components/CultureChart";
import ScoreBar from "@/components/ScoreBar";
import ReviewCard from "@/components/ReviewCard";
import RedFlagCard from "@/components/RedFlagCard";
import {
  ArrowLeft, CheckCircle2, XCircle, AlertTriangle,
  Building2, Loader2, RefreshCw
} from "lucide-react";

const VERDICT_STYLES: Record<string, { cls: string; emoji: string }> = {
  Great:      { cls: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30", emoji: "🌟" },
  Good:       { cls: "bg-green-500/20 text-green-300 border-green-500/30",       emoji: "✅" },
  Mixed:      { cls: "bg-amber-500/20 text-amber-300 border-amber-500/30",       emoji: "⚠️" },
  Toxic:      { cls: "bg-orange-500/20 text-orange-300 border-orange-500/30",    emoji: "☣️" },
  Avoid:      { cls: "bg-red-500/20 text-red-300 border-red-500/30",             emoji: "🚫" },
};

function SkeletonBlock({ className = "" }: { className?: string }) {
  return (
    <div className={`rounded-lg bg-secondary animate-pulse ${className}`} />
  );
}

export default function CompanyPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const companyName = decodeURIComponent(slug);

  const [data, setData] = useState<CompanyAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSource, setActiveSource] = useState<string>("All");

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeCompany(companyName);
      setData(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [companyName]);

  const sources = data ? ["All", ...data.sources_scraped] : [];
  const filteredReviews = data
    ? activeSource === "All"
      ? data.reviews
      : data.reviews.filter((r) => r.source === activeSource)
    : [];

  const verdictStyle = data ? VERDICT_STYLES[data.verdict] || VERDICT_STYLES.Mixed : null;

  return (
    <main className="min-h-screen px-4 py-8 max-w-6xl mx-auto">
      {/* Back nav */}
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-8 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to search
      </Link>

      {/* Company header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="w-12 h-12 rounded-xl bg-primary/15 border border-primary/20 flex items-center justify-center">
          <Building2 className="w-6 h-6 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">{companyName}</h1>
          {data && (
            <p className="text-sm text-muted-foreground">
              {data.total_reviews} reviews · {data.sources_scraped.join(", ")}
            </p>
          )}
        </div>
        {data && verdictStyle && (
          <Badge variant="outline" className={`ml-auto text-sm px-3 py-1 ${verdictStyle.cls}`}>
            {verdictStyle.emoji} {data.verdict}
          </Badge>
        )}
        {data && (
          <button
            onClick={fetchData}
            className="p-2 rounded-lg hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="space-y-6">
          <div className="flex items-center justify-center gap-3 py-16 text-muted-foreground">
            <Loader2 className="w-5 h-5 animate-spin text-primary" />
            <span>Scraping reviews from Glassdoor, Indeed, Reddit…</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <SkeletonBlock className="h-44" />
            <SkeletonBlock className="h-44" />
            <SkeletonBlock className="h-44" />
          </div>
          <SkeletonBlock className="h-72" />
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div className="flex flex-col items-center gap-4 py-20 text-center">
          <AlertTriangle className="w-12 h-12 text-amber-400" />
          <div>
            <p className="text-lg font-semibold mb-1">Could not analyze this company</p>
            <p className="text-muted-foreground text-sm max-w-md">{error}</p>
          </div>
          <button
            onClick={fetchData}
            className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-colors"
          >
            Try again
          </button>
        </div>
      )}

      {/* Results */}
      {data && !loading && (
        <div className="space-y-6">
          {/* Top metrics row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Toxicity */}
            <Card className="p-6 bg-card border-border col-span-1">
              <ToxicityMeter score={data.toxicity_score} />
            </Card>

            {/* Overall score */}
            <Card className="p-6 bg-card border-border">
              <p className="text-sm text-muted-foreground mb-4">Culture Scores</p>
              <div className="space-y-3">
                <ScoreBar label="Work-Life Balance" value={data.culture_scores.work_life_balance} />
                <ScoreBar label="Management" value={data.culture_scores.management} />
                <ScoreBar label="Compensation" value={data.culture_scores.compensation} />
                <ScoreBar label="Career Growth" value={data.culture_scores.career_growth} />
                <ScoreBar label="Diversity" value={data.culture_scores.diversity} />
              </div>
            </Card>

            {/* Radar chart */}
            <Card className="p-6 bg-card border-border flex flex-col">
              <p className="text-sm text-muted-foreground mb-2">Culture Radar</p>
              <CultureChart scores={data.culture_scores} />
            </Card>
          </div>

          {/* Red flags */}
          {data.red_flags.length > 0 && (
            <Card className="p-6 bg-card border-border">
              <h2 className="font-semibold mb-4 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Red Flags ({data.red_flags.length})
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {data.red_flags.map((flag, i) => (
                  <RedFlagCard key={i} flag={flag} />
                ))}
              </div>
            </Card>
          )}

          {/* AI Summary + Strengths/Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="p-6 bg-card border-border md:col-span-2">
              <h2 className="font-semibold mb-3">AI Analysis</h2>
              <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
                {data.ai_summary}
              </p>
            </Card>

            <div className="space-y-4">
              <Card className="p-5 bg-card border-border">
                <h3 className="text-sm font-semibold text-emerald-400 flex items-center gap-1.5 mb-3">
                  <CheckCircle2 className="w-4 h-4" />
                  Strengths
                </h3>
                <ul className="space-y-2">
                  {data.strengths.map((s, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-emerald-500 mt-0.5">•</span>
                      {s}
                    </li>
                  ))}
                </ul>
              </Card>

              <Card className="p-5 bg-card border-border">
                <h3 className="text-sm font-semibold text-red-400 flex items-center gap-1.5 mb-3">
                  <XCircle className="w-4 h-4" />
                  Weaknesses
                </h3>
                <ul className="space-y-2">
                  {data.weaknesses.map((w, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-red-500 mt-0.5">•</span>
                      {w}
                    </li>
                  ))}
                </ul>
              </Card>
            </div>
          </div>

          <Separator className="opacity-30" />

          {/* Reviews section */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold">
                Reviews{" "}
                <span className="text-muted-foreground font-normal text-sm">
                  ({filteredReviews.length})
                </span>
              </h2>
              {/* Source filter */}
              <div className="flex gap-1.5 flex-wrap">
                {sources.map((s) => (
                  <button
                    key={s}
                    onClick={() => setActiveSource(s)}
                    className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                      activeSource === s
                        ? "bg-primary text-primary-foreground border-primary"
                        : "border-border bg-card hover:border-primary/40 text-muted-foreground"
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <Tabs defaultValue="all">
              <TabsList className="mb-4 bg-card">
                <TabsTrigger value="all">All</TabsTrigger>
                <TabsTrigger value="negative">Negative</TabsTrigger>
                <TabsTrigger value="positive">Positive</TabsTrigger>
              </TabsList>

              <TabsContent value="all">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {filteredReviews.map((r, i) => (
                    <ReviewCard key={i} review={r} />
                  ))}
                  {filteredReviews.length === 0 && (
                    <p className="text-muted-foreground text-sm col-span-2 text-center py-8">
                      No reviews from this source.
                    </p>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="negative">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {filteredReviews
                    .filter((r) => r.sentiment === "negative")
                    .map((r, i) => (
                      <ReviewCard key={i} review={r} />
                    ))}
                </div>
              </TabsContent>

              <TabsContent value="positive">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {filteredReviews
                    .filter((r) => r.sentiment === "positive")
                    .map((r, i) => (
                      <ReviewCard key={i} review={r} />
                    ))}
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      )}
    </main>
  );
}
