"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Shield, TrendingUp, Users, Zap, ArrowRight, Sparkles } from "lucide-react";

const FEATURES = [
  { icon: Shield,     label: "Toxicity Score",    desc: "AI-powered culture analysis" },
  { icon: TrendingUp, label: "Culture Breakdown",  desc: "6-dimension workplace rating" },
  { icon: Users,      label: "Multi-Source",       desc: "Reddit, HackerNews, News & more" },
  { icon: Zap,        label: "Red Flags",          desc: "Spot warning signs instantly" },
];

const EXAMPLE_COMPANIES = ["Google", "Amazon", "Goldman Sachs", "Meta", "Tesla", "Uber"];

export default function Home() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSearch = (name: string) => {
    const q = name || query;
    if (!q.trim()) return;
    setLoading(true);
    router.push(`/company/${encodeURIComponent(q.trim())}`);
  };

  return (
    <main className="relative min-h-screen flex flex-col items-center justify-center px-4 py-20 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-grid pointer-events-none" />
      <div className="absolute inset-0 pointer-events-none">
        <div
          className="absolute top-[-10%] left-1/2 -translate-x-1/2 w-[820px] h-[820px] rounded-full animate-pulse-glow"
          style={{ background: "var(--gradient-radial)" }}
        />
        <div className="absolute bottom-0 left-1/4 w-[400px] h-[400px] rounded-full bg-primary/10 blur-[120px]" />
        <div className="absolute top-1/3 right-0 w-[380px] h-[380px] rounded-full opacity-60 blur-[120px]"
          style={{ background: "oklch(0.72 0.22 295 / 0.12)" }} />
      </div>

      <div className="relative z-10 w-full max-w-2xl flex flex-col items-center gap-12 animate-float-up">
        {/* Header */}
        <div className="text-center space-y-5">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary/30 bg-primary/10 backdrop-blur-sm text-primary text-xs font-semibold tracking-wide uppercase">
            <Sparkles className="w-3.5 h-3.5" />
            AI-Powered Workplace Intelligence
          </div>
          <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-[1.05]">
            Know before<br />you <span className="text-gradient">join.</span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-lg mx-auto leading-relaxed">
            Search any company for a real-time culture score, toxicity rating, and
            aggregated employee sentiment from across the web.
          </p>
        </div>

        {/* Search */}
        <div className="w-full">
          <div className="relative group">
            <div
              className="absolute -inset-px rounded-2xl opacity-50 group-focus-within:opacity-100 blur-sm transition-opacity duration-300"
              style={{ background: "var(--gradient-primary)" }}
            />
            <div className="relative flex gap-2 p-2 rounded-2xl bg-card border border-border shadow-elegant">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                <input
                  className="w-full pl-11 pr-4 h-12 bg-transparent border-0 text-base outline-none placeholder:text-muted-foreground"
                  placeholder="Search a company (e.g. Amazon, Google)..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch("")}
                />
              </div>
              <button
                className="h-12 px-6 font-semibold rounded-xl text-white text-sm flex items-center gap-1.5 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none shadow-glow"
                style={{ background: "var(--gradient-primary)" }}
                onClick={() => handleSearch("")}
                disabled={loading || !query.trim()}
              >
                {loading ? "Searching…" : <><span>Analyze</span><ArrowRight className="w-4 h-4" /></>}
              </button>
            </div>
          </div>

          {/* Example pills */}
          <div className="flex flex-wrap gap-2 justify-center mt-5">
            <span className="text-xs text-muted-foreground self-center mr-1">Try:</span>
            {EXAMPLE_COMPANIES.map((c) => (
              <button
                key={c}
                onClick={() => handleSearch(c)}
                className="px-3 py-1.5 text-xs font-medium rounded-full border border-border bg-card/60 backdrop-blur-sm hover:border-primary/50 hover:bg-primary/10 hover:text-primary transition-all hover:-translate-y-0.5"
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full">
          {FEATURES.map((f, i) => {
            const Icon = f.icon;
            return (
              <div
                key={f.label}
                className="group flex flex-col items-center gap-2.5 p-5 rounded-2xl border border-border bg-card/60 backdrop-blur-sm text-center hover:border-primary/40 hover:bg-card transition-all duration-300 hover:-translate-y-1 hover:shadow-glow animate-float-up"
                style={{ animationDelay: `${i * 80}ms` }}
              >
                <span className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary/15 text-primary group-hover:bg-primary/25 transition-colors">
                  <Icon className="w-5 h-5" />
                </span>
                <span className="text-sm font-semibold">{f.label}</span>
                <span className="text-xs text-muted-foreground leading-snug">{f.desc}</span>
              </div>
            );
          })}
        </div>
      </div>
    </main>
  );
}
