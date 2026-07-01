import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type BadgeTone = "indigo" | "emerald" | "amber" | "slate";

const TONE_CLASSES: Record<BadgeTone, string> = {
  indigo: "bg-indigo-100 text-indigo-700",
  emerald: "bg-emerald-100 text-emerald-700",
  amber: "bg-amber-100 text-amber-800",
  slate: "bg-slate-100 text-slate-600",
};

export function Badge({ tone = "slate", children }: { tone?: BadgeTone; children: ReactNode }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium",
        TONE_CLASSES[tone],
      )}
    >
      {children}
    </span>
  );
}
