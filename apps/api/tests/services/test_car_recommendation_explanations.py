from app.models.review import Review
from app.repositories.car_recommendation_repository import ReviewAggregate
from app.services.car_recommendation_explanations import (
    generate_key_feature_highlights,
    generate_match_reasons,
    generate_trade_offs,
    select_representative_reviews,
)
from app.services.car_recommendation_scoring import score_candidates
from tests.services.factories import build_criteria, build_variant


def _review(id: int, rating: int, comment: str = "fine") -> Review:
    return Review(id=id, model_id=1, reviewer_name="Test User", rating=rating, comment=comment)


class TestGenerateMatchReasons:
    def test_explicit_fuel_preference_match_is_always_mentioned(self):
        from app.models.car_variant import FuelType

        variant = build_variant(id=1, price=500_000, fuel_type=FuelType.ELECTRIC)
        criteria = build_criteria(budget=1_000_000, fuel_preference="electric")
        scored = score_candidates([variant], {}, criteria)

        reasons = generate_match_reasons(scored[0], scored, criteria)

        assert any("electric fuel preference" in reason for reason in reasons)

    def test_top_tier_dimension_produces_a_specific_reason(self):
        strong = build_variant(id=1, price=400_000, mileage_kmpl=28)
        weak = build_variant(id=2, price=900_000, mileage_kmpl=12)
        criteria = build_criteria(budget=1_000_000, priorities=["fuel_economy"])
        scored = score_candidates([strong, weak], {}, criteria)

        top = next(c for c in scored if c.variant.id == 1)
        reasons = generate_match_reasons(top, scored, criteria)

        assert any("kmpl" in reason for reason in reasons)

    def test_never_returns_more_than_the_cap(self):
        variant = build_variant(
            id=1,
            price=100_000,
            mileage_kmpl=30,
            power_bhp=200,
            feature_names=["ABS with EBD", "Sunroof"],
        )
        criteria = build_criteria(budget=1_000_000)
        scored = score_candidates([variant], {1: ReviewAggregate(4.8, 20)}, criteria)

        reasons = generate_match_reasons(scored[0], scored, criteria)

        assert len(reasons) <= 4


class TestGenerateTradeOffs:
    def test_over_budget_variant_gets_an_explicit_price_trade_off(self):
        over_budget = build_variant(id=1, price=1_050_000)
        criteria = build_criteria(budget=1_000_000)
        scored = score_candidates([over_budget], {}, criteria)

        trade_offs = generate_trade_offs(scored[0], scored, criteria)

        assert any("over your stated budget" in trade_off for trade_off in trade_offs)

    def test_seating_shortfall_is_always_disclosed_even_if_dimension_scores_well(self):
        # A car can still score well overall despite a seating shortfall (it's a soft
        # signal, not a hard filter) -- but the shortfall must always be disclosed
        # honestly, not silently absorbed into a blended comfort score.
        too_small = build_variant(
            id=1,
            price=500_000,
            seating_capacity=5,
            mileage_kmpl=30,
            power_bhp=200,
            feature_names=["ABS with EBD", "Dual Front Airbags", "Sunroof"],
        )
        criteria = build_criteria(budget=1_000_000, family_size=7)
        scored = score_candidates([too_small], {}, criteria)

        trade_offs = generate_trade_offs(scored[0], scored, criteria)

        assert any(
            "Seats 5" in trade_off and "family size of 7" in trade_off for trade_off in trade_offs
        )

    def test_dominant_candidate_gets_honest_no_compromise_fallback(self):
        dominant = build_variant(
            id=1,
            price=400_000,
            mileage_kmpl=30,
            power_bhp=200,
            torque_nm=300,
            feature_names=["ABS with EBD", "Dual Front Airbags", "Sunroof"],
        )
        weak = build_variant(id=2, price=900_000, mileage_kmpl=10, power_bhp=40)
        criteria = build_criteria(budget=1_000_000)
        scored = score_candidates(
            [dominant, weak], {1: ReviewAggregate(4.8, 10), 2: ReviewAggregate(3.0, 10)}, criteria
        )

        top = next(c for c in scored if c.variant.id == 1)
        trade_offs = generate_trade_offs(top, scored, criteria)

        assert trade_offs == [
            "No significant compromises among your shortlisted priorities -- "
            "a strong all-round match."
        ]

    def test_electric_variant_never_gets_fuel_efficiency_trade_off(self):
        from app.models.car_variant import FuelType

        ev = build_variant(id=1, price=900_000, fuel_type=FuelType.ELECTRIC, mileage_kmpl=None)
        ice = build_variant(id=2, price=500_000, mileage_kmpl=25)
        criteria = build_criteria(budget=1_000_000)
        scored = score_candidates([ev, ice], {}, criteria)

        ev_scored = next(c for c in scored if c.variant.id == 1)
        trade_offs = generate_trade_offs(ev_scored, scored, criteria)

        assert not any("kmpl" in trade_off for trade_off in trade_offs)


class TestGenerateKeyFeatureHighlights:
    def test_prefers_advanced_features_over_basic(self):
        variant = build_variant(
            id=1,
            price=500_000,
            feature_names=["Manual Air Conditioning", "ADAS (Level 2)", "Sunroof"],
        )
        criteria = build_criteria(budget=1_000_000)
        scored = score_candidates([variant], {}, criteria)

        highlights = generate_key_feature_highlights(scored[0])

        assert "ADAS (Level 2)" in highlights
        assert "Sunroof" in highlights

    def test_backfills_with_basic_features_when_fewer_than_limit(self):
        variant = build_variant(
            id=1, price=500_000, feature_names=["Manual Air Conditioning", "Power Windows"]
        )
        criteria = build_criteria(budget=1_000_000)
        scored = score_candidates([variant], {}, criteria)

        highlights = generate_key_feature_highlights(scored[0])

        assert set(highlights) == {"Manual Air Conditioning", "Power Windows"}


class TestSelectRepresentativeReviews:
    def test_empty_reviews_returns_empty_list(self):
        assert select_representative_reviews([]) == []

    def test_spans_highest_lowest_and_closest_to_average(self):
        reviews = [_review(1, 5), _review(2, 3), _review(3, 1)]

        picks = select_representative_reviews(reviews)

        ratings = {review.rating for review in picks}
        assert ratings == {5, 3, 1}

    def test_deduplicates_when_same_review_fills_multiple_roles(self):
        reviews = [_review(1, 5), _review(2, 5)]

        picks = select_representative_reviews(reviews)

        assert len(picks) == len({review.id for review in picks})
