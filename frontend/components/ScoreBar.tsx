"use client";

interface ScoreBarProps {
  label: string;
  value: number; // 1–10
}

function scoreColor(v: number) {
  if (v >= 7.5) return "oklch(0.72 0.18 160)";  // green
  if (v >= 5) return "oklch(0.72 0.18 80)";       // yellow
  return "oklch(0.62 0.22 27)";                   // red
}

export default function ScoreBar({ label, value }: ScoreBarProps) {
  const pct = ((value - 1) / 9) * 100;
  const color = scoreColor(value);

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-semibold tabular-nums" style={{ color }}>
          {value.toFixed(1)}
        </span>
      </div>
      <div className="h-1.5 rounded-full bg-secondary overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
