type ProgressBarProps = {
  current: number;
  total: number;
};

export function ProgressBar({ current, total }: ProgressBarProps) {
  const percent = Math.min(100, Math.round((current / total) * 100));

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2 text-xs font-medium text-slate-500">
        <span>
          Question {current} of {total}
        </span>
        <span>{percent}%</span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-slate-200 overflow-hidden">
        <div
          className="h-full rounded-full bg-indigo-600 transition-all duration-300 ease-out"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
