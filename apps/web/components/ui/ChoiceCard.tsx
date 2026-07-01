import { Check } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type ChoiceCardProps = {
  label: string;
  description?: string;
  icon?: ReactNode;
  selected: boolean;
  onClick: () => void;
};

export function ChoiceCard({ label, description, icon, selected, onClick }: ChoiceCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={selected}
      className={cn(
        "group flex w-full items-center gap-3 rounded-2xl border-2 px-4 py-3.5 text-left transition-all",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2",
        selected
          ? "border-indigo-600 bg-indigo-50"
          : "border-slate-200 bg-white hover:border-indigo-300 hover:bg-indigo-50/40",
      )}
    >
      {icon && (
        <span
          className={cn(
            "flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-lg",
            selected ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-500",
          )}
        >
          {icon}
        </span>
      )}
      <span className="flex-1 min-w-0">
        <span
          className={cn(
            "block font-medium",
            selected ? "text-indigo-900" : "text-slate-800",
          )}
        >
          {label}
        </span>
        {description && (
          <span className="block text-sm text-slate-500 mt-0.5">{description}</span>
        )}
      </span>
      <span
        className={cn(
          "flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 transition-colors",
          selected ? "border-indigo-600 bg-indigo-600" : "border-slate-300 bg-white",
        )}
      >
        {selected && <Check className="h-3.5 w-3.5 text-white" strokeWidth={3} />}
      </span>
    </button>
  );
}
