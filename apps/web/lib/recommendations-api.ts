import { apiFetch } from "@/lib/api-client";
import type { CarRecommendationRequest, CarRecommendationResponse } from "@/lib/types";

export function getCarRecommendations(
  payload: CarRecommendationRequest,
): Promise<CarRecommendationResponse> {
  return apiFetch<CarRecommendationResponse>("/car-recommendations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
