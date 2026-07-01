import { Car, MessageCircleQuestion, ShieldCheck, Sparkles } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/Button";

const FEATURES = [
  {
    icon: MessageCircleQuestion,
    title: "A few quick questions",
    description:
      "No long forms. We ask about your budget, driving habits, and priorities — one question at a time.",
  },
  {
    icon: Sparkles,
    title: "Matched to you",
    description:
      "Every recommendation is scored against your answers, not a generic “top 10 cars” list.",
  },
  {
    icon: ShieldCheck,
    title: "Honest trade-offs",
    description:
      "We show you why a car fits and where it falls short — real reviews included.",
  },
];

export default function LandingPage() {
  return (
    <main className="flex-1">
      <section className="relative overflow-hidden">
        <div
          className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,theme(colors.indigo.100),transparent_60%)]"
          aria-hidden="true"
        />
        <div className="mx-auto flex max-w-3xl flex-col items-center px-6 pt-24 pb-20 text-center sm:pt-32">
          <span className="inline-flex items-center gap-2 rounded-full bg-indigo-100 px-4 py-1.5 text-sm font-medium text-indigo-700">
            <Car className="h-4 w-4" />
            Smart Car Advisor
          </span>
          <h1 className="mt-6 text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
            Find the right car through a conversation, not a search bar.
          </h1>
          <p className="mt-5 max-w-xl text-lg text-slate-600">
            Tell us how you drive and what matters to you. We&apos;ll walk you through a
            few simple questions and match you with cars that actually fit your life.
          </p>
          <div className="mt-10">
            <Link href="/questionnaire">
              <Button size="lg">Find my car</Button>
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-6 pb-24">
        <div className="grid gap-6 sm:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-600 text-white">
                <Icon className="h-5 w-5" />
              </span>
              <h2 className="mt-4 font-semibold text-slate-900">{title}</h2>
              <p className="mt-1.5 text-sm text-slate-600">{description}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
