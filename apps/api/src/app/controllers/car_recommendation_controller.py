from fastapi import Depends

from app.core.response import APIResponse, success_response
from app.schemas.car_recommendation_schemas import (
    CarRecommendationRequest,
    CarRecommendationResponse,
    CarRecommendationResult,
    ReviewSnippet,
    ReviewSummary,
)
from app.services.car_recommendation_service import (
    CarRecommendationService,
    RankedRecommendation,
    RecommendationCriteria,
    get_car_recommendation_service,
)


class CarRecommendationController:
    def __init__(self, service: CarRecommendationService):
        self.service = service

    def recommend(
        self, request: CarRecommendationRequest
    ) -> APIResponse[CarRecommendationResponse]:
        criteria = RecommendationCriteria(
            budget=request.budget,
            daily_driving_distance_km=request.daily_driving_distance_km,
            primary_usage=request.primary_usage.value,
            family_size=request.family_size,
            fuel_preference=request.fuel_preference.value if request.fuel_preference else None,
            transmission_preference=(
                request.transmission_preference.value if request.transmission_preference else None
            ),
            body_type_preference=(
                [body_type.value for body_type in request.body_type_preference]
                if request.body_type_preference
                else None
            ),
            priorities=[priority.value for priority in request.priorities],
        )

        result = self.service.recommend(criteria)

        response = CarRecommendationResponse(
            results=[self._to_result_schema(item) for item in result.items],
            total_candidates_matched=result.total_candidates_matched,
        )
        return success_response(response, message="Car recommendations generated successfully")

    @staticmethod
    def _to_result_schema(item: RankedRecommendation) -> CarRecommendationResult:
        variant = item.variant
        spec = variant.specification
        return CarRecommendationResult(
            variant_id=variant.id,
            maker_name=variant.model.maker.name,
            model_name=variant.model.name,
            variant_name=variant.name,
            price=float(variant.price),
            fuel_type=variant.fuel_type.value,
            transmission_type=variant.transmission_type.value,
            body_type=variant.model.body_type.value,
            seating_capacity=spec.seating_capacity if spec else None,
            mileage_kmpl=(
                float(spec.mileage_kmpl) if spec and spec.mileage_kmpl is not None else None
            ),
            power_bhp=float(spec.power_bhp) if spec and spec.power_bhp is not None else None,
            boot_space_litres=spec.boot_space_litres if spec else None,
            overall_score=item.overall_score,
            score_confidence=item.score_confidence,
            match_reasons=item.match_reasons,
            trade_offs=item.trade_offs,
            key_feature_highlights=item.key_feature_highlights,
            reviews=ReviewSummary(
                average_rating=item.review_aggregate.average_rating,
                review_count=item.review_aggregate.review_count,
                snippets=[
                    ReviewSnippet(
                        reviewer_name=review.reviewer_name,
                        rating=review.rating,
                        comment=review.comment,
                    )
                    for review in item.representative_reviews
                ],
            ),
        )


def get_car_recommendation_controller(
    service: CarRecommendationService = Depends(get_car_recommendation_service),
) -> CarRecommendationController:
    return CarRecommendationController(service)
