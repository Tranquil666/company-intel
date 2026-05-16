"use client";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { Review } from "@/lib/api";
import { Star, ThumbsUp, ThumbsDown, MessageSquare } from "lucide-react";

const SOURCE_COLORS: Record<string, string> = {
  Glassdoor: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  Indeed: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  Reddit: "bg-orange-500/15 text-orange-400 border-orange-500/20",
  LinkedIn: "bg-sky-500/15 text-sky-400 border-sky-500/20",
};

const SENTIMENT_STYLES: Record<string, { icon: React.ReactNode; cls: string }> = {
  positive: {
    icon: <ThumbsUp className="w-3 h-3" />,
    cls: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  },
  neutral: {
    icon: <MessageSquare className="w-3 h-3" />,
    cls: "bg-slate-500/10 text-slate-400 border-slate-500/20",
  },
  negative: {
    icon: <ThumbsDown className="w-3 h-3" />,
    cls: "bg-red-500/10 text-red-400 border-red-500/20",
  },
};

interface ReviewCardProps {
  review: Review;
}

export default function ReviewCard({ review }: ReviewCardProps) {
  const sentimentStyle = review.sentiment ? SENTIMENT_STYLES[review.sentiment] : null;
  const sourceStyle = SOURCE_COLORS[review.source] || "bg-muted text-muted-foreground border-border";

  return (
    <Card className="p-4 bg-card border-border hover:border-primary/20 transition-colors">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline" className={`text-xs ${sourceStyle}`}>
            {review.source}
          </Badge>
          {sentimentStyle && (
            <Badge variant="outline" className={`text-xs flex items-center gap-1 ${sentimentStyle.cls}`}>
              {sentimentStyle.icon}
              {review.sentiment}
            </Badge>
          )}
          {review.role && (
            <span className="text-xs text-muted-foreground">{review.role}</span>
          )}
        </div>
        {review.rating !== null && (
          <div className="flex items-center gap-1 shrink-0">
            <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
            <span className="text-sm font-semibold tabular-nums">{review.rating.toFixed(1)}</span>
          </div>
        )}
      </div>

      {review.title && (
        <p className="font-semibold text-sm mb-2 line-clamp-2">{review.title}</p>
      )}

      {review.pros && (
        <div className="mb-2">
          <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wide">Pros: </span>
          <span className="text-sm text-muted-foreground">{review.pros}</span>
        </div>
      )}

      {review.cons && (
        <div className="mb-2">
          <span className="text-xs font-semibold text-red-400 uppercase tracking-wide">Cons: </span>
          <span className="text-sm text-muted-foreground">{review.cons}</span>
        </div>
      )}

      {!review.pros && !review.cons && review.body && (
        <p className="text-sm text-muted-foreground line-clamp-4">{review.body}</p>
      )}

      {review.date && (
        <p className="text-xs text-muted-foreground/60 mt-2">{review.date}</p>
      )}
    </Card>
  );
}
