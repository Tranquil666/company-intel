"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Shield, TrendingUp, Users, Zap } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const FEATURES = [
  { icon: <Shield className="w-5 h-5" />, label: "Toxicity Score", desc: "AI-powered culture analysis" },
  { icon: <TrendingUp className="w-5 h-5" />, label: "Culture Breakdown", desc: "6-dimension workplace rating" },
  { icon: <Users className="w-5 h-5" />, label: "Multi-Source", desc: "Glassdoor, Indeed, Reddit & more" },
  { icon: <Zap className="w-5 h-5" />, label: "Red Flags", desc: "Spot warning signs instantly" },
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
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-16 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-primary/5 blur-3xl" />
      </div>

      <div className="relative z-10 w-full max-w-2xl flex flex-col items-center gap-10">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-primary/30 bg-primary/10 text-primary text-xs font-semibold mb-2">
            <Zap className="w-3 h-3" />
            AI-Powered Workplace Intelligence
          </div>
          <h1 className="text-5xl font-bold tracking-tight">
            Know before you{" "}
            <span className="text-primary">join.</span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-lg mx-auto">
            Search any company to get a real-time culture score, toxicity rating,
            and aggregated employee reviews from across the web.
          </p>
        </div>

        {/* Search */}
        <div className="w-full flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
            <Input
              className="pl-10 h-12 bg-card border-border text-base focus-visible:ring-primary/50"
              placeholder="Search a company (e.g. Amazon, Google)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch("")}
            />
          </div>
          <Button
            className="h-12 px-6 font-semibold"
            onClick={() => handleSearch("")}
            disabled={loading || !query.trim()}
          >
            {loading ? "Searching..." : "Analyze"}
          </Button>
        </div>

        {/* Example companies */}
        <div className="flex flex-wrap gap-2 justify-center">
          <span className="text-xs text-muted-foreground self-center">Try:</span>
          {EXAMPLE_COMPANIES.map((c) => (
            <button
              key={c}
              onClick={() => handleSearch(c)}
              className="px-3 py-1 text-xs rounded-full border border-border bg-card hover:border-primary/40 hover:bg-primary/10 hover:text-primary transition-colors"
            >
              {c}
            </button>
          ))}
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full mt-4">
          {FEATURES.map((f) => (
            <div
              key={f.label}
              className="flex flex-col items-center gap-2 p-4 rounded-xl border border-border bg-card text-center"
            >
              <span className="text-primary">{f.icon}</span>
              <span className="text-sm font-semibold">{f.label}</span>
              <span className="text-xs text-muted-foreground">{f.desc}</span>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
