"""Dimension scoring, weight combination, and confidence for car recommendations.

Pure functions operating on plain data (ORM objects + a criteria dataclass) in, plain
`ScoredCandidate` objects out -- no DB session, no Pydantic. This is what keeps the
algorithm unit-testable without a database.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.models.car_variant import CarVariant, FuelType
from app.repositories.car_recommendation_repository import ReviewAggregate

if TYPE_CHECKING:
    from app.services.car_recommendation_service import RecommendationCriteria

DIMENSIONS = [
    "price_value",
    "fuel_efficiency",
    "performance",
    "safety",
    "comfort_features",
    "reliability",
]

# Curated feature-name sets, mirrored by name against seed_data/features.py's
# FEATURE_POOL (category/tier there are seed-time-only, not DB columns, so scoring
# re-derives membership by exact name match rather than importing seed data at runtime).
SAFETY_FEATURES = {
    "ABS with EBD",
    "Dual Front Airbags",
    "Rear Parking Sensors",
    "Rear View Camera",
    "Hill Hold Assist",
    "ISOFIX Child Seat Mounts",
    "Electronic Stability Control",
    "Hill Descent Control",
    "TPMS (Tyre Pressure Monitoring)",
    "360-Degree Camera",
    "ADAS (Level 2)",
    "Automatic Emergency Braking",
    "Lane Keep Assist",
    "Blind Spot Monitor",
}

COMFORT_FEATURES = {
    "Manual Air Conditioning",
    "Power Windows",
    "Keyless Entry with Push Button Start",
    "Automatic Climate Control",
    "Rear AC Vents",
    "Ventilated Front Seats",
    "Heated Front Seats",
    "Power Adjustable Driver Seat",
    "Cruise Control",
    "Adaptive Cruise Control",
    "Rain-Sensing Wipers",
    "Wireless Phone Charger",
}

INFOTAINMENT_FEATURES = {
    "Basic Audio System with USB/Bluetooth",
    "Touchscreen Infotainment System",
    "Wireless Android Auto & Apple CarPlay",
    "Connected Car Tech (App-Based)",
    "Premium Sound System (Harman/Bose/JBL)",
    "Digital Instrument Cluster",
    "Head-Up Display",
    "Ambient Interior Lighting",
}

EXTERIOR_FEATURES = {
    "Halogen Headlamps",
    "Body-Colored ORVMs with Turn Indicators",
    "LED Projector Headlamps",
    "LED DRLs",
    "Alloy Wheels",
    "Sunroof",
    "Panoramic Sunroof",
    "Roof Rails",
}

FEATURE_CATEGORY = (
    {name: "safety" for name in SAFETY_FEATURES}
    | {name: "comfort" for name in COMFORT_FEATURES}
    | {name: "infotainment" for name in INFOTAINMENT_FEATURES}
    | {name: "exterior" for name in EXTERIOR_FEATURES}
)

ADVANCED_FEATURES = {
    "Electronic Stability Control",
    "Hill Descent Control",
    "TPMS (Tyre Pressure Monitoring)",
    "360-Degree Camera",
    "ADAS (Level 2)",
    "Automatic Emergency Braking",
    "Lane Keep Assist",
    "Blind Spot Monitor",
    "Automatic Climate Control",
    "Rear AC Vents",
    "Ventilated Front Seats",
    "Heated Front Seats",
    "Power Adjustable Driver Seat",
    "Cruise Control",
    "Adaptive Cruise Control",
    "Rain-Sensing Wipers",
    "Wireless Phone Charger",
    "Wireless Android Auto & Apple CarPlay",
    "Connected Car Tech (App-Based)",
    "Premium Sound System (Harman/Bose/JBL)",
    "Digital Instrument Cluster",
    "Head-Up Display",
    "Ambient Interior Lighting",
    "LED Projector Headlamps",
    "LED DRLs",
    "Alloy Wheels",
    "Sunroof",
    "Panoramic Sunroof",
    "Roof Rails",
}

# Weight combination -----------------------------------------------------------------

BASE_WEIGHTS = {
    "price_value": 0.20,
    "fuel_efficiency": 0.15,
    "performance": 0.15,
    "safety": 0.20,
    "comfort_features": 0.15,
    "reliability": 0.15,
}

PRIORITY_TO_DIMENSION = {
    "fuel_economy": "fuel_efficiency",
    "safety": "safety",
    "comfort_features": "comfort_features",
    "performance": "performance",
    "low_price": "price_value",
    "reliability_brand_trust": "reliability",
}

PRIORITY_BOOST = 0.15
MIN_WEIGHT = 0.02

USAGE_ADJUSTMENTS = {
    "city": {
        "fuel_efficiency": 0.05,
        "comfort_features": 0.05,
        "performance": -0.05,
        "safety": -0.05,
    },
    "highway": {
        "performance": 0.08,
        "safety": 0.07,
        "fuel_efficiency": -0.05,
        "comfort_features": -0.05,
        "reliability": -0.05,
    },
    "mixed": {},
}


def distance_adjustment(daily_driving_distance_km: float) -> dict[str, float]:
    if daily_driving_distance_km >= 60:
        return {
            "fuel_efficiency": 0.10,
            "reliability": 0.05,
            "performance": -0.05,
            "comfort_features": -0.05,
            "price_value": -0.05,
        }
    if daily_driving_distance_km >= 30:
        return {"fuel_efficiency": 0.05}
    return {}


def family_size_adjustment(family_size: int) -> dict[str, float]:
    if family_size >= 7:
        return {"comfort_features": 0.10}
    if family_size >= 5:
        return {"comfort_features": 0.05}
    return {}


def compute_weights(criteria: "RecommendationCriteria") -> dict[str, float]:
    weights = dict(BASE_WEIGHTS)

    for priority in criteria.priorities:
        dimension = PRIORITY_TO_DIMENSION.get(priority)
        if dimension:
            weights[dimension] += PRIORITY_BOOST

    for dimension, delta in USAGE_ADJUSTMENTS.get(criteria.primary_usage, {}).items():
        weights[dimension] += delta

    for dimension, delta in distance_adjustment(criteria.daily_driving_distance_km).items():
        weights[dimension] += delta

    for dimension, delta in family_size_adjustment(criteria.family_size).items():
        weights[dimension] += delta

    weights = {dimension: max(value, MIN_WEIGHT) for dimension, value in weights.items()}
    total = sum(weights.values())
    return {dimension: value / total for dimension, value in weights.items()}


# Per-dimension raw values -------------------------------------------------------------

OVER_BUDGET_PENALTY_FACTOR = 200.0
EV_FUEL_EFFICIENCY_SCORE = 95.0
FAMILY_SEATING_SHORTFALL_PENALTY = 60.0
FAMILY_SEATING_SURPLUS_BONUS = 2.0


def price_value_raw(variant: CarVariant, budget: float) -> float:
    price_ratio = float(variant.price) / budget
    over_budget_penalty = max(0.0, price_ratio - 1.0) * OVER_BUDGET_PENALTY_FACTOR
    return (1.0 / price_ratio) * 100.0 - over_budget_penalty


def fuel_efficiency_raw(variant: CarVariant) -> float | None:
    if variant.fuel_type == FuelType.ELECTRIC:
        return EV_FUEL_EFFICIENCY_SCORE
    spec = variant.specification
    if spec is None or spec.mileage_kmpl is None:
        return None
    return float(spec.mileage_kmpl)


def performance_raw(variant: CarVariant) -> float | None:
    spec = variant.specification
    if spec is None or spec.power_bhp is None:
        return None
    power = float(spec.power_bhp)
    torque = float(spec.torque_nm) if spec.torque_nm is not None else power * 1.3
    seats = spec.seating_capacity or 5
    return power * 0.7 + (torque / seats) * 0.3


def safety_raw(variant: CarVariant) -> float:
    names = {feature.name for feature in variant.features}
    return float(len(names & SAFETY_FEATURES))


def comfort_raw(variant: CarVariant, family_size: int) -> float:
    names = {feature.name for feature in variant.features}
    feature_count = len(names & (COMFORT_FEATURES | INFOTAINMENT_FEATURES))
    spec = variant.specification

    boot = spec.boot_space_litres if spec else None
    boot_component = float(boot) / 10.0 if boot is not None else 0.0

    # Seating fit uses the real seating_capacity directly rather than a body-type
    # stereotype (an SUV that only seats 5 is just as poor a fit for a family of 7 as a
    # hatchback that seats 5). feature_count*5 alone can swing ~20-110 across segments
    # (RICHNESS_TIER_COUNTS spans 4-22 features), so the shortfall penalty must be large
    # enough that even one missing seat reliably outweighs a premium car's extra feature
    # count -- "can this car actually fit my family" matters far more than an extra USB
    # port. A surplus gets a modest, secondary bonus instead.
    seats = spec.seating_capacity if spec else None
    if seats is None:
        space_component = 0.0
    else:
        margin = seats - family_size
        space_component = (
            margin * FAMILY_SEATING_SURPLUS_BONUS
            if margin >= 0
            else margin * FAMILY_SEATING_SHORTFALL_PENALTY
        )

    return feature_count * 5.0 + boot_component + space_component


def reliability_raw(model_id: int, review_aggregates: dict[int, ReviewAggregate]) -> float | None:
    aggregate = review_aggregates.get(model_id)
    if aggregate is None or aggregate.average_rating is None:
        return None
    return aggregate.average_rating


# Normalization --------------------------------------------------------------------

NEUTRAL_SCORE = 50.0


def normalize_dimension(raw_values: dict[int, float | None]) -> dict[int, float]:
    """Min-max normalize within the candidate set. A variant missing this raw value
    gets a neutral 50 (never 0, never 100) and is excluded from the min/max computation
    so it doesn't skew everyone else's normalized range."""
    present = {key: value for key, value in raw_values.items() if value is not None}
    if not present:
        return dict.fromkeys(raw_values, NEUTRAL_SCORE)

    lo, hi = min(present.values()), max(present.values())
    result = {}
    for key, value in raw_values.items():
        if value is None:
            result[key] = NEUTRAL_SCORE
        elif hi == lo:
            result[key] = 100.0
        else:
            result[key] = (value - lo) / (hi - lo) * 100.0
    return result


# Confidence -------------------------------------------------------------------------

GAP_CONFIDENCE_SCALE = 10.0
COMPLETENESS_REVIEW_TARGET = 8.0


def gap_confidence(gap: float | None) -> float:
    if gap is None:
        return 50.0
    return min(gap * GAP_CONFIDENCE_SCALE, 100.0)


def pool_confidence(candidate_count: int) -> float:
    if candidate_count >= 15:
        return 100.0
    if candidate_count <= 1:
        return 20.0
    return 20.0 + (candidate_count - 1) * (80.0 / 14.0)


def completeness_confidence(variant: CarVariant, review_count: int) -> float:
    spec = variant.specification
    present = 0
    total = 5
    if variant.fuel_type == FuelType.ELECTRIC or (spec and spec.mileage_kmpl is not None):
        present += 1
    if spec and spec.power_bhp is not None:
        present += 1
    if spec and spec.torque_nm is not None:
        present += 1
    if spec and spec.seating_capacity is not None:
        present += 1
    if spec and spec.boot_space_litres is not None:
        present += 1
    spec_completeness = (present / total) * 100.0

    review_component = min(review_count / COMPLETENESS_REVIEW_TARGET, 1.0) * 100.0
    return spec_completeness * 0.6 + review_component * 0.4


# Orchestration ------------------------------------------------------------------------


@dataclass(frozen=True)
class ScoredCandidate:
    variant: CarVariant
    review_aggregate: ReviewAggregate
    raw_values: dict[str, float | None]
    dimension_scores: dict[str, float]
    weights: dict[str, float]
    overall_score: float
    score_confidence: float


def score_candidates(
    candidates: list[CarVariant],
    review_aggregates: dict[int, ReviewAggregate],
    criteria: "RecommendationCriteria",
) -> list[ScoredCandidate]:
    """Pure function: scores, ranks, and computes confidence for every candidate.
    Returns a list sorted descending by overall_score (confidence depends on knowing
    each candidate's neighbors post-sort, so sorting happens here, not in the caller).
    Does NOT populate match_reasons/trade_offs/key_feature_highlights -- see
    car_recommendation_explanations.py for that."""
    if not candidates:
        return []

    weights = compute_weights(criteria)

    raw_by_dimension: dict[str, dict[int, float | None]] = {
        dimension: {} for dimension in DIMENSIONS
    }
    for variant in candidates:
        raw_by_dimension["price_value"][variant.id] = price_value_raw(variant, criteria.budget)
        raw_by_dimension["fuel_efficiency"][variant.id] = fuel_efficiency_raw(variant)
        raw_by_dimension["performance"][variant.id] = performance_raw(variant)
        raw_by_dimension["safety"][variant.id] = safety_raw(variant)
        raw_by_dimension["comfort_features"][variant.id] = comfort_raw(
            variant, criteria.family_size
        )
        raw_by_dimension["reliability"][variant.id] = reliability_raw(
            variant.model_id, review_aggregates
        )

    normalized_by_dimension = {
        dimension: normalize_dimension(values) for dimension, values in raw_by_dimension.items()
    }

    overall_scores: dict[int, float] = {}
    dimension_scores_by_id: dict[int, dict[str, float]] = {}
    raw_values_by_id: dict[int, dict[str, float | None]] = {}
    for variant in candidates:
        dimension_scores = {
            dimension: normalized_by_dimension[dimension][variant.id] for dimension in DIMENSIONS
        }
        dimension_scores_by_id[variant.id] = dimension_scores
        raw_values_by_id[variant.id] = {
            dimension: raw_by_dimension[dimension][variant.id] for dimension in DIMENSIONS
        }
        overall_scores[variant.id] = round(
            sum(dimension_scores[dimension] * weights[dimension] for dimension in DIMENSIONS), 1
        )

    ordered = sorted(candidates, key=lambda variant: (-overall_scores[variant.id], variant.id))
    scores_in_order = [overall_scores[variant.id] for variant in ordered]
    pool_size = len(ordered)

    scored: list[ScoredCandidate] = []
    for index, variant in enumerate(ordered):
        gaps = []
        if index > 0:
            gaps.append(abs(scores_in_order[index] - scores_in_order[index - 1]))
        if index < pool_size - 1:
            gaps.append(abs(scores_in_order[index] - scores_in_order[index + 1]))
        tightest_gap = min(gaps) if gaps else None

        review_aggregate = review_aggregates.get(variant.model_id, ReviewAggregate(None, 0))
        confidence = round(
            gap_confidence(tightest_gap) * 0.4
            + pool_confidence(pool_size) * 0.3
            + completeness_confidence(variant, review_aggregate.review_count) * 0.3,
            1,
        )

        scored.append(
            ScoredCandidate(
                variant=variant,
                review_aggregate=review_aggregate,
                raw_values=raw_values_by_id[variant.id],
                dimension_scores=dimension_scores_by_id[variant.id],
                weights=weights,
                overall_score=overall_scores[variant.id],
                score_confidence=confidence,
            )
        )

    # Deterministic tie-break: higher confidence, then lower price, then lower id.
    scored.sort(
        key=lambda candidate: (
            -candidate.overall_score,
            -candidate.score_confidence,
            float(candidate.variant.price),
            candidate.variant.id,
        )
    )
    return scored
