import type { ReactNode } from "react";

type QuestionShellProps = {
  title: string;
  subtitle?: string;
  children: ReactNode;
};

export function QuestionShell({ title, subtitle, children }: QuestionShellProps) {
  return (
    <div className="w-full">
      <h1 className="text-2xl font-semibold text-slate-900 sm:text-3xl">{title}</h1>
      {subtitle && <p className="mt-2 text-slate-500">{subtitle}</p>}
      <div className="mt-8">{children}</div>
    </div>
  );
}
