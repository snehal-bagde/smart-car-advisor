from unittest.mock import MagicMock

import pytest

from app.core.exceptions import NoMatchingCarsError
from app.repositories.car_recommendation_repository import ReviewAggregate
from app.services.car_recommendation_service import CarRecommendationService
from tests.services.factories import build_criteria, build_variant


def _repository_with(candidate_responses: list[list], review_aggregates=None, reviews=None):
    repository = MagicMock()
    repository.get_candidate_variants.side_effect = candidate_responses
    repository.get_review_aggregates.return_value = review_aggregates or {}
    repository.get_reviews_for_models.return_value = reviews or {}
    return repository


class TestCarRecommendationServiceHappyPath:
    def test_recommend_returns_top_5_sorted_and_total_candidates_matched(self):
        candidates = [build_variant(id=i, price=500_000 + i * 10_000) for i in range(1, 8)]
        repository = _repository_with([candidates])
        service = CarRecommendationService(repository)

        result = service.recommend(build_criteria(budget=1_000_000))

        assert len(result.items) == 5
        assert result.total_candidates_matched == 7
        scores = [item.overall_score for item in result.items]
        assert scores == sorted(scores, reverse=True)

    def test_recommend_returns_fewer_than_5_without_padding(self):
        candidates = [build_variant(id=1, price=500_000), build_variant(id=2, price=600_000)]
        repository = _repository_with([candidates])
        service = CarRecommendationService(repository)

        result = service.recommend(build_criteria(budget=1_000_000))

        assert len(result.items) == 2
        assert result.total_candidates_matched == 2


class TestCarRecommendationServiceRelaxation:
    def test_recommend_falls_back_to_relaxation_when_strict_filter_is_empty(self):
        relaxed_candidates = [build_variant(id=i, price=500_000) for i in range(1, 6)]
        repository = _repository_with(
            [
                [],  # strict filter: nothing
                relaxed_candidates,  # first relaxation step: enough candidates
            ]
        )
        service = CarRecommendationService(repository)

        result = service.recommend(build_criteria(budget=1_000_000, body_type_preference=["suv"]))

        assert result.total_candidates_matched == 5
        repository.get_candidate_variants.assert_called()

    def test_recommend_raises_no_matching_cars_when_fully_relaxed_and_still_empty(self):
        repository = _repository_with([[], [], [], [], []])
        service = CarRecommendationService(repository)

        with pytest.raises(NoMatchingCarsError):
            service.recommend(build_criteria(budget=1_000_000))


class TestCarRecommendationServiceReviews:
    def test_recommend_attaches_review_aggregates_and_snippets(self):
        variant = build_variant(id=1, price=500_000)
        repository = _repository_with(
            [[variant]],
            review_aggregates={1: ReviewAggregate(average_rating=4.5, review_count=10)},
        )
        service = CarRecommendationService(repository)

        result = service.recommend(build_criteria(budget=1_000_000))

        assert result.items[0].review_aggregate.average_rating == 4.5
        assert result.items[0].review_aggregate.review_count == 10
