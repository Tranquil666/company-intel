"use client";

import type { Review } from "@/lib/api";
import { Star, ThumbsUp, ThumbsDown, MessageSquare } from "lucide-react";

const SOURCE_STYLES: Record<string, string> = {
  Glassdoor:   "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  Indeed:      "bg-blue-500/10 text-blue-400 border-blue-500/20",
  Reddit:      "bg-orange-500/10 text-orange-400 border-orange-500/20",
  LinkedIn:    "bg-sky-500/10 text-sky-400 border-sky-500/20",
  HackerNews:  "bg-amber-500/10 text-amber-400 border-amber-500/20",
  "Google News": "bg-red-500/10 text-red-400 border-red-500/20",
  Wikipedia:   "bg-slate-500/10 text-slate-400 border-slate-500/20",
  Trustpilot:  "bg-green-500/10 text-green-400 border-green-500/20",
  Comparably:  "bg-purple-500/10 text-purple-400 border-purple-500/20",
};

const SENTIMENT: Record<string, { icon: React.ReactNode; cls: string }> = {
  positive: { icon: <ThumbsUp className="w-3 h-3" />,    cls: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
  neutral:  { icon: <MessageSquare className="w-3 h-3" />, cls: "bg-slate-500/10 text-slate-400 border-slate-500/20" },
  negative: { icon: <ThumbsDown className="w-3 h-3" />,   cls: "bg-red-500/10 text-red-400 border-red-500/20" },
};

export default function ReviewCard({ review }: { review: Review }) {
  const src = SOURCE_STYLES[review.source] ?? "bg-muted text-muted-foreground border-border";
  const snt = review.sentiment ? SENTIMENT[review.sentiment] : null;

  return (
    <div className="group flex flex-col gap-3 p-4 rounded-2xl border border-border bg-card/60 backdrop-blur-sm hover:border-primary/30 hover:bg-card hover:shadow-elegant transition-all duration-300">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border ${src}`}>
            {review.source}
          </span>
          {snt && (
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${snt.cls}`}>
              {snt.icon}{review.sentiment}
            </span>
          )}
          {review.role && (
            <span className="text-xs text-muted-foreground">{review.role}</span>
          )}
        </div>
        {review.rating !== null && (
          <div className="flex items-center gap-1 shrink-0">
            <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
            <span className="text-sm font-bold tabular-nums">{review.rating.toFixed(1)}</span>
          </div>
        )}
      </div>

      {/* Content */}
      {review.title && <p className="font-semibold text-sm line-clamp-2 leading-snug">{review.title}</p>}
      {review.pros && (
        <p className="text-sm text-muted-foreground">
          <span className="text-emerald-400 font-semibold text-xs uppercase tracking-wide">Pros: </span>
          {review.pros}
        </p>
      )}
      {review.cons && (
        <p className="text-sm text-muted-foreground">
          <span className="text-red-400 font-semibold text-xs uppercase tracking-wide">Cons: </span>
          {review.cons}
        </p>
      )}
      {!review.pros && !review.cons && review.body && (
        <p className="text-sm text-muted-foreground line-clamp-4 leading-relaxed">{review.body}</p>
      )}
      {review.date && <p className="text-xs text-muted-foreground/50 mt-auto">{review.date}</p>}
    </div>
  );
}
