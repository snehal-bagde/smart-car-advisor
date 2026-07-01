from app.models.car_model import BodyType
from app.models.car_variant import FuelType
from app.repositories.car_recommendation_repository import ReviewAggregate
from app.services.car_recommendation_scoring import (
    comfort_raw,
    compute_weights,
    fuel_efficiency_raw,
    normalize_dimension,
    performance_raw,
    price_value_raw,
    reliability_raw,
    safety_raw,
    score_candidates,
)
from tests.services.factories import build_criteria, build_variant


class TestNormalizeDimension:
    def test_normalize_dimension_min_max_range_maps_to_0_100(self):
        result = normalize_dimension({1: 10.0, 2: 20.0, 3: 30.0})
        assert result == {1: 0.0, 2: 50.0, 3: 100.0}

    def test_normalize_dimension_all_none_returns_neutral_50_for_everyone(self):
        result = normalize_dimension({1: None, 2: None})
        assert result == {1: 50.0, 2: 50.0}

    def test_normalize_dimension_single_none_gets_neutral_50_without_skewing_others(self):
        result = normalize_dimension({1: 10.0, 2: None, 3: 30.0})
        assert result[2] == 50.0
        assert result[1] == 0.0
        assert result[3] == 100.0

    def test_normalize_dimension_identical_values_returns_100_for_everyone(self):
        result = normalize_dimension({1: 5.0, 2: 5.0})
        assert result == {1: 100.0, 2: 100.0}


class TestRawValueFunctions:
    def test_price_value_raw_at_exact_budget_has_no_penalty(self):
        variant = build_variant(id=1, price=500_000)
        assert price_value_raw(variant, budget=500_000) == 100.0

    def test_price_value_raw_over_budget_is_penalized_below_in_budget(self):
        in_budget = price_value_raw(build_variant(id=1, price=500_000), budget=500_000)
        over_budget = price_value_raw(build_variant(id=2, price=540_000), budget=500_000)
        assert over_budget < in_budget

    def test_fuel_efficiency_raw_electric_uses_fixed_substitute(self):
        variant = build_variant(id=1, fuel_type=FuelType.ELECTRIC, mileage_kmpl=None)
        assert fuel_efficiency_raw(variant) == 95.0

    def test_fuel_efficiency_raw_ice_uses_actual_mileage(self):
        variant = build_variant(id=1, mileage_kmpl=22.5)
        assert fuel_efficiency_raw(variant) == 22.5

    def test_fuel_efficiency_raw_missing_mileage_returns_none(self):
        variant = build_variant(id=1, mileage_kmpl=None)
        assert fuel_efficiency_raw(variant) is None

    def test_performance_raw_missing_power_returns_none(self):
        variant = build_variant(id=1, power_bhp=None)
        assert performance_raw(variant) is None

    def test_performance_raw_higher_power_scores_higher(self):
        weak = build_variant(id=1, power_bhp=60, torque_nm=90)
        strong = build_variant(id=2, power_bhp=150, torque_nm=250)
        assert performance_raw(strong) > performance_raw(weak)

    def test_safety_raw_counts_only_curated_safety_features(self):
        variant = build_variant(
            id=1, feature_names=["ABS with EBD", "Sunroof", "Dual Front Airbags"]
        )
        assert safety_raw(variant) == 2.0

    def test_comfort_raw_rewards_seating_margin_for_large_family(self):
        tight = build_variant(id=1, seating_capacity=5)
        spacious = build_variant(id=2, seating_capacity=8)
        assert comfort_raw(spacious, family_size=6) > comfort_raw(tight, family_size=6)

    def test_comfort_raw_uses_actual_seating_not_a_body_type_stereotype(self):
        # An SUV that seats 5 is just as poor a fit for a family of 7 as a hatchback
        # that seats 5 -- body type must never override the real seating_capacity.
        suv = build_variant(id=1, body_type=BodyType.SUV, seating_capacity=5)
        hatchback = build_variant(id=2, body_type=BodyType.HATCHBACK, seating_capacity=5)
        assert comfort_raw(suv, family_size=7) == comfort_raw(hatchback, family_size=7)

    def test_comfort_raw_seating_shortfall_penalty_dominates_feature_count(self):
        # A short-on-seats car with many features should still lose to an
        # adequately-seated car with fewer features once family_size isn't met.
        feature_rich_but_too_small = build_variant(
            id=1,
            seating_capacity=5,
            feature_names=[
                "Automatic Climate Control",
                "Rear AC Vents",
                "Ventilated Front Seats",
                "Wireless Android Auto & Apple CarPlay",
            ],
        )
        adequately_seated = build_variant(id=2, seating_capacity=7, feature_names=[])
        assert comfort_raw(adequately_seated, family_size=7) > comfort_raw(
            feature_rich_but_too_small, family_size=7
        )

    def test_reliability_raw_missing_reviews_returns_none(self):
        assert reliability_raw(1, {}) is None

    def test_reliability_raw_uses_aggregate_average(self):
        aggregates = {1: ReviewAggregate(average_rating=4.2, review_count=10)}
        assert reliability_raw(1, aggregates) == 4.2


class TestComputeWeights:
    def test_base_weights_sum_to_one(self):
        weights = compute_weights(build_criteria())
        assert abs(sum(weights.values()) - 1.0) < 1e-9

    def test_selected_priority_increases_its_dimension_share(self):
        baseline = compute_weights(build_criteria(priorities=[]))
        boosted = compute_weights(build_criteria(priorities=["safety"]))
        assert boosted["safety"] > baseline["safety"]

    def test_high_daily_distance_boosts_fuel_efficiency_weight(self):
        low_distance = compute_weights(build_criteria(daily_driving_distance_km=10))
        high_distance = compute_weights(build_criteria(daily_driving_distance_km=70))
        assert high_distance["fuel_efficiency"] > low_distance["fuel_efficiency"]

    def test_large_family_boosts_comfort_features_weight(self):
        small_family = compute_weights(build_criteria(family_size=2))
        large_family = compute_weights(build_criteria(family_size=7))
        assert large_family["comfort_features"] > small_family["comfort_features"]

    def test_no_weight_is_ever_zero_or_negative(self):
        weights = compute_weights(
            build_criteria(priorities=["fuel_economy"], daily_driving_distance_km=70)
        )
        assert all(value > 0 for value in weights.values())


class TestScoreCandidates:
    def test_score_candidates_empty_input_returns_empty_list(self):
        assert score_candidates([], {}, build_criteria()) == []

    def test_score_candidates_sorts_descending_by_overall_score(self):
        cheap_and_efficient = build_variant(id=1, price=400_000, mileage_kmpl=24)
        expensive_and_thirsty = build_variant(id=2, price=1_200_000, mileage_kmpl=10)
        criteria = build_criteria(budget=1_000_000, priorities=["low_price", "fuel_economy"])

        scored = score_candidates(
            [expensive_and_thirsty, cheap_and_efficient], {}, criteria
        )

        assert [c.variant.id for c in scored] == [1, 2]
        assert scored[0].overall_score >= scored[1].overall_score

    def test_score_candidates_deterministic_tie_break_prefers_lower_price(self):
        variant_a = build_variant(id=1, price=500_000)
        variant_b = build_variant(id=2, price=500_000)
        criteria = build_criteria(budget=1_000_000)

        scored = score_candidates([variant_a, variant_b], {}, criteria)

        # Identical inputs -> identical scores and confidence; price then id break the tie.
        assert scored[0].overall_score == scored[1].overall_score
        assert scored[0].variant.id == 1

    def test_score_candidates_confidence_is_bounded_0_to_100(self):
        variants = [build_variant(id=i, price=400_000 + i * 50_000) for i in range(1, 4)]
        scored = score_candidates(variants, {}, build_criteria(budget=1_000_000))
        assert all(0.0 <= c.score_confidence <= 100.0 for c in scored)
