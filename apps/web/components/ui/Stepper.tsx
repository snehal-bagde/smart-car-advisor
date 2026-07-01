import { Minus, Plus } from "lucide-react";

import { Button } from "@/components/ui/Button";

type StepperProps = {
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
  unitLabel: (value: number) => string;
};

export function Stepper({ value, min, max, onChange, unitLabel }: StepperProps) {
  return (
    <div className="flex items-center justify-center gap-6">
      <Button
        type="button"
        variant="secondary"
        size="icon"
        className="h-14 w-14"
        onClick={() => onChange(Math.max(min, value - 1))}
        disabled={value <= min}
        aria-label="Decrease"
      >
        <Minus className="h-5 w-5" />
      </Button>
      <div className="w-32 text-center">
        <div className="text-4xl font-semibold text-indigo-700">{value}</div>
        <div className="text-sm text-slate-500">{unitLabel(value)}</div>
      </div>
      <Button
        type="button"
        variant="secondary"
        size="icon"
        className="h-14 w-14"
        onClick={() => onChange(Math.min(max, value + 1))}
        disabled={value >= max}
        aria-label="Increase"
      >
        <Plus className="h-5 w-5" />
      </Button>
    </div>
  );
}
