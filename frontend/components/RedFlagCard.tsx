"use client";

import { AlertTriangle, AlertCircle, Info } from "lucide-react";
import type { RedFlag } from "@/lib/api";

const SEV = {
  high:   { icon: <AlertTriangle className="w-4 h-4" />, border: "border-red-500/30",    bg: "bg-red-500/8",    text: "text-red-400",    badge: "bg-red-500/20 text-red-300",    label: "HIGH" },
  medium: { icon: <AlertCircle   className="w-4 h-4" />, border: "border-amber-500/30",  bg: "bg-amber-500/8",  text: "text-amber-400",  badge: "bg-amber-500/20 text-amber-300",  label: "MEDIUM" },
  low:    { icon: <Info          className="w-4 h-4" />, border: "border-sky-500/30",    bg: "bg-sky-500/8",    text: "text-sky-400",    badge: "bg-sky-500/20 text-sky-300",    label: "LOW" },
};

export default function RedFlagCard({ flag }: { flag: RedFlag }) {
  const s = SEV[flag.severity] ?? SEV.low;
  return (
    <div className={`flex items-start gap-3 rounded-2xl border p-3.5 ${s.border} ${s.bg} ${s.text}`}>
      <span className="mt-0.5 shrink-0">{s.icon}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-semibold">{flag.category}</span>
          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${s.badge}`}>{s.label}</span>
        </div>
        <p className="text-xs opacity-80 leading-relaxed">{flag.description}</p>
      </div>
    </div>
  );
}
