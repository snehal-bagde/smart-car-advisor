import type { CarRecommendationRequest, DraftAnswers } from "@/lib/types";

export function draftToRequest(answers: DraftAnswers): CarRecommendationRequest {
  return {
    budget: answers.budget,
    daily_driving_distance_km: answers.daily_driving_distance_km,
    primary_usage: answers.primary_usage ?? "mixed",
    family_size: answers.family_size,
    fuel_preference: answers.fuel_preference,
    transmission_preference: answers.transmission_preference,
    body_type_preference: answers.body_type_preference.length ? answers.body_type_preference : null,
    priorities: answers.priorities,
  };
}

export function requestToDraft(request: CarRecommendationRequest): DraftAnswers {
  return {
    budget: request.budget,
    daily_driving_distance_km: request.daily_driving_distance_km,
    primary_usage: request.primary_usage,
    family_size: request.family_size,
    fuel_preference: request.fuel_preference ?? null,
    transmission_preference: request.transmission_preference ?? null,
    body_type_preference: request.body_type_preference ?? [],
    priorities: request.priorities,
  };
}
