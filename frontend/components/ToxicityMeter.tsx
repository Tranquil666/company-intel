"use client";

interface ToxicityMeterProps {
  score: number; // 1–10
}

const LABELS = ["", "Excellent", "Great", "Good", "Good", "Mixed", "Mixed", "Concerning", "Toxic", "Very Toxic", "Avoid"];
const COLORS = [
  "", "#22c55e", "#4ade80", "#86efac", "#a3e635",
  "#facc15", "#fb923c", "#f97316", "#ef4444", "#dc2626", "#991b1b"
];

export default function ToxicityMeter({ score }: ToxicityMeterProps) {
  const clampedScore = Math.max(1, Math.min(10, Math.round(score)));
  const percentage = ((score - 1) / 9) * 100;
  const color = COLORS[clampedScore];
  const label = LABELS[clampedScore];

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-end justify-between">
        <span className="text-sm text-muted-foreground">Toxicity Level</span>
        <div className="flex items-baseline gap-2">
          <span className="text-5xl font-bold tabular-nums" style={{ color }}>
            {score.toFixed(1)}
          </span>
          <span className="text-muted-foreground text-sm">/10</span>
        </div>
      </div>

      {/* Gradient bar */}
      <div className="relative h-3 rounded-full overflow-hidden bg-secondary">
        <div
          className="absolute inset-y-0 left-0 rounded-full transition-all duration-1000"
          style={{
            width: `${percentage}%`,
            background: `linear-gradient(to right, #22c55e, #facc15, #ef4444)`,
          }}
        />
        <div
          className="absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full border-2 border-background shadow-lg transition-all duration-1000"
          style={{ left: `calc(${percentage}% - 8px)`, backgroundColor: color }}
        />
      </div>

      <div className="flex justify-between text-xs text-muted-foreground">
        <span>Healthy</span>
        <span className="font-semibold" style={{ color }}>{label}</span>
        <span>Toxic</span>
      </div>
    </div>
  );
}
