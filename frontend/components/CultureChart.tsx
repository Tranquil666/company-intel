"use client";

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { CultureScores } from "@/lib/api";

interface CultureChartProps {
  scores: CultureScores;
}

export default function CultureChart({ scores }: CultureChartProps) {
  const data = [
    { subject: "Work-Life Balance", value: scores.work_life_balance },
    { subject: "Management", value: scores.management },
    { subject: "Compensation", value: scores.compensation },
    { subject: "Career Growth", value: scores.career_growth },
    { subject: "Diversity", value: scores.diversity },
  ];

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
        <PolarGrid stroke="rgba(255,255,255,0.08)" />
        <PolarAngleAxis
          dataKey="subject"
          tick={{ fill: "oklch(0.58 0.02 264)", fontSize: 11 }}
        />
        <Radar
          name="Score"
          dataKey="value"
          stroke="oklch(0.62 0.22 270)"
          fill="oklch(0.62 0.22 270)"
          fillOpacity={0.2}
          strokeWidth={2}
        />
        <Tooltip
          contentStyle={{
            background: "oklch(0.13 0.02 264)",
            border: "1px solid oklch(1 0 0 / 10%)",
            borderRadius: "8px",
            color: "oklch(0.93 0.01 264)",
            fontSize: "13px",
          }}
          formatter={(value) => [typeof value === "number" ? `${value.toFixed(1)}/10` : value, "Score"]}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
