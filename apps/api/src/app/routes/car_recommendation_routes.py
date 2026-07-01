from fastapi import APIRouter, Depends

from app.controllers.car_recommendation_controller import (
    CarRecommendationController,
    get_car_recommendation_controller,
)
from app.core.response import APIResponse
from app.schemas.car_recommendation_schemas import (
    CarRecommendationRequest,
    CarRecommendationResponse,
)

router = APIRouter(prefix="/car-recommendations", tags=["car-recommendations"])


@router.post("", response_model=APIResponse[CarRecommendationResponse])
def recommend_cars(
    request: CarRecommendationRequest,
    controller: CarRecommendationController = Depends(get_car_recommendation_controller),
) -> APIResponse[CarRecommendationResponse]:
    return controller.recommend(request)
