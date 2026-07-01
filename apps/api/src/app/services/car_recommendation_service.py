from dataclasses import dataclass

from fastapi import Depends

from app.core.exceptions import NoMatchingCarsError
from app.models.car_variant import CarVariant
from app.models.review import Review
from app.repositories.car_recommendation_repository import (
    CarRecommendationRepository,
    ReviewAggregate,
    get_car_recommendation_repository,
)
from app.services.car_recommendation_explanations import (
    generate_key_feature_highlights,
    generate_match_reasons,
    generate_trade_offs,
    select_representative_reviews,
)
from app.services.car_recommendation_scoring import score_candidates

TOP_N_RESULTS = 5
BUDGET_OVER_TOLERANCE_FRACTION = 0.08
RELAXED_BUDGET_TOLERANCE_FRACTION = 0.20


@dataclass(frozen=True)
class RecommendationCriteria:
    budget: float
    daily_driving_distance_km: float
    primary_usage: str
    family_size: int
    fuel_preference: str | None
    transmission_preference: str | None
    body_type_preference: list[str] | None
    priorities: list[str]


@dataclass(frozen=True)
class RankedRecommendation:
    variant: CarVariant
    review_aggregate: ReviewAggregate
    overall_score: float
    score_confidence: float
    match_reasons: list[str]
    trade_offs: list[str]
    key_feature_highlights: list[str]
    representative_reviews: list[Review]


@dataclass(frozen=True)
class RecommendationResult:
    items: list[RankedRecommendation]
    total_candidates_matched: int


class CarRecommendationService:
    def __init__(self, repository: CarRecommendationRepository):
        self.repository = repository

    def recommend(self, criteria: RecommendationCriteria) -> RecommendationResult:
        candidates = self._fetch_candidates(criteria)
        if not candidates:
            candidates = self._fetch_candidates_with_relaxation(criteria)
        if not candidates:
            raise NoMatchingCarsError(budget=criteria.budget, family_size=criteria.family_size)

        model_ids = list({variant.model_id for variant in candidates})
        review_aggregates = self.repository.get_review_aggregates(model_ids)

        scored = score_candidates(candidates, review_aggregates, criteria)
        top_scored = scored[:TOP_N_RESULTS]

        top_model_ids = [candidate.variant.model_id for candidate in top_scored]
        reviews_by_model = self.repository.get_reviews_for_models(top_model_ids)

        items = [
            RankedRecommendation(
                variant=candidate.variant,
                review_aggregate=candidate.review_aggregate,
                overall_score=candidate.overall_score,
                score_confidence=candidate.score_confidence,
                match_reasons=generate_match_reasons(candidate, scored, criteria),
                trade_offs=generate_trade_offs(candidate, scored, criteria),
                key_feature_highlights=generate_key_feature_highlights(candidate),
                representative_reviews=select_representative_reviews(
                    reviews_by_model.get(candidate.variant.model_id, [])
                ),
            )
            for candidate in top_scored
        ]

        return RecommendationResult(items=items, total_candidates_matched=len(candidates))

    def _fetch_candidates(self, criteria: RecommendationCriteria) -> list[CarVariant]:
        return self.repository.get_candidate_variants(
            max_price=criteria.budget * (1 + BUDGET_OVER_TOLERANCE_FRACTION),
            fuel_type=criteria.fuel_preference,
            transmission_type=criteria.transmission_preference,
            body_types=criteria.body_type_preference or None,
        )

    def _fetch_candidates_with_relaxation(
        self, criteria: RecommendationCriteria
    ) -> list[CarVariant]:
        """Progressive relaxation ladder: drop constraints one at a time (least
        user-intent-violating first), accumulating relaxations, until >=TOP_N_RESULTS
        candidates are found or every step has been tried. Returns whatever the last
        step yields -- possibly still empty."""
        relaxation_steps = [
            {"body_types": None},
            {"max_price": criteria.budget * (1 + RELAXED_BUDGET_TOLERANCE_FRACTION)},
            {"transmission_type": None},
            {"fuel_type": None},
        ]
        params = {
            "max_price": criteria.budget * (1 + BUDGET_OVER_TOLERANCE_FRACTION),
            "fuel_type": criteria.fuel_preference,
            "transmission_type": criteria.transmission_preference,
            "body_types": criteria.body_type_preference or None,
        }

        candidates: list[CarVariant] = []
        for step in relaxation_steps:
            params.update(step)
            candidates = self.repository.get_candidate_variants(**params)
            if len(candidates) >= TOP_N_RESULTS:
                break
        return candidates


def get_car_recommendation_service(
    repository: CarRecommendationRepository = Depends(get_car_recommendation_repository),
) -> CarRecommendationService:
    return CarRecommendationService(repository)
