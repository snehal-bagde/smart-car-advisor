export type FuelPreference = "petrol" | "diesel" | "cng" | "electric" | "hybrid";

export type TransmissionPreference = "manual" | "automatic" | "amt" | "cvt" | "dct";

export type BodyTypePreference =
  | "hatchback"
  | "sedan"
  | "suv"
  | "muv"
  | "coupe"
  | "convertible"
  | "pickup";

export type PrimaryUsage = "city" | "highway" | "mixed";

export type Priority =
  | "fuel_economy"
  | "safety"
  | "comfort_features"
  | "performance"
  | "low_price"
  | "reliability_brand_trust";

/** Questionnaire working state — always fully populated (no `?`), so every step has a
 * concrete value to render. Converted to `CarRecommendationRequest` on submit. */
export type DraftAnswers = {
  budget: number;
  daily_driving_distance_km: number;
  primary_usage: PrimaryUsage | null;
  family_size: number;
  fuel_preference: FuelPreference | null;
  transmission_preference: TransmissionPreference | null;
  body_type_preference: BodyTypePreference[];
  priorities: Priority[];
};

export type CarRecommendationRequest = {
  budget: number;
  daily_driving_distance_km: number;
  primary_usage: PrimaryUsage;
  family_size: number;
  fuel_preference?: FuelPreference | null;
  transmission_preference?: TransmissionPreference | null;
  body_type_preference?: BodyTypePreference[] | null;
  priorities: Priority[];
};

export type ReviewSnippet = {
  reviewer_name: string;
  rating: number;
  comment: string | null;
};

export type ReviewSummary = {
  average_rating: number | null;
  review_count: number;
  snippets: ReviewSnippet[];
};

export type CarRecommendationResult = {
  variant_id: number;
  maker_name: string;
  model_name: string;
  variant_name: string;
  price: number;
  fuel_type: FuelPreference;
  transmission_type: TransmissionPreference;
  body_type: BodyTypePreference;
  seating_capacity: number | null;
  mileage_kmpl: number | null;
  power_bhp: number | null;
  boot_space_litres: number | null;
  overall_score: number;
  score_confidence: number;
  match_reasons: string[];
  trade_offs: string[];
  key_feature_highlights: string[];
  reviews: ReviewSummary;
};

export type CarRecommendationResponse = {
  results: CarRecommendationResult[];
  total_candidates_matched: number;
};
