"use client";

import { AlertCircle, ArrowLeft, RefreshCw, SearchX } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { RecommendationCard } from "@/components/recommendations/RecommendationCard";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { ApiError } from "@/lib/api-client";
import { loadAnswers } from "@/lib/answers-storage";
import { getCarRecommendations } from "@/lib/recommendations-api";
import type { CarRecommendationResponse } from "@/lib/types";

type ViewState =
  | { status: "no-answers" }
  | { status: "loading" }
  | { status: "error"; error: ApiError }
  | { status: "success"; data: CarRecommendationResponse };

const LOADING_MESSAGES = [
  "Comparing prices, specs, and reviews...",
  "Weighing what matters most to you...",
  "Almost there...",
];

export default function RecommendationsPage() {
  const [view, setView] = useState<ViewState>({ status: "loading" });
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);

  const fetchRecommendations = useCallback(async () => {
    const answers = loadAnswers();
    if (!answers) {
      setView({ status: "no-answers" });
      return;
    }
    setView({ status: "loading" });
    try {
      const data = await getCarRecommendations(answers);
      setView({ status: "success", data });
    } catch (error) {
      setView({
        status: "error",
        error: error instanceof ApiError ? error : new ApiError("Something went wrong.", "unknown_error", {}),
      });
    }
  }, []);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  useEffect(() => {
    if (view.status !== "loading") return;
    const interval = setInterval(() => {
      setLoadingMessageIndex((index) => (index + 1) % LOADING_MESSAGES.length);
    }, 1800);
    return () => clearInterval(interval);
  }, [view.status]);

  if (view.status === "no-answers") {
    return (
      <EmptyState
        icon={SearchX}
        title="Let's start with a few questions"
        description="We don't have your preferences yet — answer a few quick questions and we'll find cars that fit."
        action={
          <Link href="/questionnaire">
            <Button>Start the questionnaire</Button>
          </Link>
        }
      />
    );
  }

  if (view.status === "loading") {
    return (
      <main className="flex flex-1 flex-col items-center justify-center gap-4 px-6 py-24 text-center">
        <Spinner className="h-8 w-8" />
        <p className="text-slate-600">{LOADING_MESSAGES[loadingMessageIndex]}</p>
      </main>
    );
  }

  if (view.status === "error") {
    const isNoMatch = view.error.code === "no_matching_cars";
    return (
      <EmptyState
        icon={isNoMatch ? SearchX : AlertCircle}
        title={isNoMatch ? "No cars match all your preferences" : "We hit a snag"}
        description={
          isNoMatch
            ? "Try widening your budget or relaxing a preference, and we'll look again."
            : view.error.message
        }
        action={
          <div className="flex flex-wrap items-center justify-center gap-3">
            {isNoMatch ? (
              <Link href="/questionnaire">
                <Button>
                  <ArrowLeft className="h-4 w-4" />
                  Adjust my answers
                </Button>
              </Link>
            ) : (
              <Button onClick={fetchRecommendations}>
                <RefreshCw className="h-4 w-4" />
                Try again
              </Button>
            )}
          </div>
        }
      />
    );
  }

  const { results, total_candidates_matched } = view.data;

  return (
    <main className="flex-1 px-6 py-12">
      <div className="mx-auto max-w-2xl">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-slate-900 sm:text-3xl">
            Your top {results.length} {results.length === 1 ? "match" : "matches"}
          </h1>
          <p className="mt-2 text-slate-500">
            Compared against {total_candidates_matched} car{total_candidates_matched === 1 ? "" : "s"}{" "}
            that fit your budget and preferences.
          </p>
        </div>

        <div className="mt-10 flex flex-col gap-6">
          {results.map((result, index) => (
            <RecommendationCard key={result.variant_id} result={result} rank={index + 1} />
          ))}
        </div>

        <div className="mt-10 text-center">
          <Link href="/questionnaire" className="text-sm font-medium text-indigo-600 hover:text-indigo-700">
            Start over with different preferences
          </Link>
        </div>
      </div>
    </main>
  );
}

function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon: typeof SearchX;
  title: string;
  description: string;
  action: React.ReactNode;
}) {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-4 px-6 py-24 text-center">
      <span className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100">
        <Icon className="h-7 w-7 text-slate-400" />
      </span>
      <h1 className="text-xl font-semibold text-slate-900">{title}</h1>
      <p className="max-w-sm text-slate-500">{description}</p>
      <div className="mt-2">{action}</div>
    </main>
  );
}
