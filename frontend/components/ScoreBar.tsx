"use client";

interface ScoreBarProps { label: string; value: number }

function color(v: number) {
  if (v >= 7.5) return "oklch(0.72 0.18 160)";
  if (v >= 5)   return "oklch(0.78 0.18 80)";
  return "oklch(0.62 0.22 27)";
}

export default function ScoreBar({ label, value }: ScoreBarProps) {
  const pct = ((value - 1) / 9) * 100;
  const c = color(value);
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between items-center text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-bold tabular-nums" style={{ color: c }}>{value.toFixed(1)}</span>
      </div>
      <div className="h-1.5 rounded-full bg-secondary overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, backgroundColor: c }}
        />
      </div>
    </div>
  );
}
