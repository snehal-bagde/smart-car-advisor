import type { ReactNode } from "react";

type SliderProps = {
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
  valueLabel: ReactNode;
  minLabel: string;
  maxLabel: string;
};

export function Slider({ value, min, max, step, onChange, valueLabel, minLabel, maxLabel }: SliderProps) {
  const percent = ((value - min) / (max - min)) * 100;

  return (
    <div className="w-full">
      <div className="mb-6 text-center text-4xl font-semibold text-indigo-700">{valueLabel}</div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="w-full h-2 appearance-none rounded-full bg-slate-200 accent-indigo-600 cursor-pointer"
        style={{
          background: `linear-gradient(to right, #4f46e5 ${percent}%, #e2e8f0 ${percent}%)`,
        }}
      />
      <div className="mt-2 flex justify-between text-xs font-medium text-slate-400">
        <span>{minLabel}</span>
        <span>{maxLabel}</span>
      </div>
    </div>
  );
}
