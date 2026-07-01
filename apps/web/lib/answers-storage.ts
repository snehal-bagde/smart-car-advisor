import type { CarRecommendationRequest } from "@/lib/types";

const STORAGE_KEY = "smart-car-advisor:questionnaire-answers";

export function saveAnswers(answers: CarRecommendationRequest): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(answers));
}

export function loadAnswers(): CarRecommendationRequest | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as CarRecommendationRequest;
  } catch {
    return null;
  }
}
