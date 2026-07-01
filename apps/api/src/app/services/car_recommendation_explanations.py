"""Rule-based, deterministic explanation generation for car recommendations.

Every string here is built from template + real computed numbers -- never an LLM call.
Pure functions: ScoredCandidate + the full candidate set + criteria in, plain strings
(or Review rows) out.
"""

from typing import TYPE_CHECKING

from app.models.car_variant import FuelType
from app.models.review import Review
from app.services.car_recommendation_scoring import (
    ADVANCED_FEATURES,
    COMFORT_FEATURES,
    DIMENSIONS,
    FEATURE_CATEGORY,
    INFOTAINMENT_FEATURES,
    ScoredCandidate,
)

if TYPE_CHECKING:
    from app.services.car_recommendation_service import RecommendationCriteria

TOP_TIER_THRESHOLD = 100 * (2 / 3)
TRADE_OFF_WEIGHT_THRESHOLD = 0.10
MAX_MATCH_REASONS = 4
MAX_TRADE_OFFS = 3
MAX_KEY_FEATURE_HIGHLIGHTS = 5

HIGHLIGHT_CATEGORY_ORDER = ["safety", "infotainment", "comfort", "exterior"]


def _average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 0:
        return (ordered[mid - 1] + ordered[mid]) / 2
    return ordered[mid]


def _comparison_phrase(value: float, average: float) -> str:
    if average <= 0:
        return "in line with"
    ratio = value / average
    if ratio >= 1.15:
        return "well above"
    if ratio >= 1.0:
        return "above"
    return "below"


def _non_ev_mileage_average(all_scored: list[ScoredCandidate]) -> float:
    values = [
        c.raw_values["fuel_efficiency"]
        for c in all_scored
        if c.variant.fuel_type != FuelType.ELECTRIC and c.raw_values["fuel_efficiency"] is not None
    ]
    return _average(values)


def _reliability_average(all_scored: list[ScoredCandidate]) -> float:
    values = [
        c.review_aggregate.average_rating
        for c in all_scored
        if c.review_aggregate.average_rating is not None
    ]
    return _average(values)


# Match reasons -------------------------------------------------------------------


def _fuel_efficiency_reason(candidate: ScoredCandidate, all_scored, criteria) -> str:
    variant = candidate.variant
    if variant.fuel_type == FuelType.ELECTRIC:
        return (
            "As an EV, running costs are a fraction of petrol/diesel alternatives -- "
            f"well suited to your {criteria.daily_driving_distance_km:.0f} km/day driving."
        )
    mileage = candidate.raw_values["fuel_efficiency"] or 0.0
    average = _non_ev_mileage_average(all_scored)
    return (
        f"Delivers {mileage:.1f} kmpl, {_comparison_phrase(mileage, average)} the "
        f"candidate average of {average:.1f} kmpl -- well suited to your "
        f"{criteria.daily_driving_distance_km:.0f} km/day driving."
    )


def _safety_reason(candidate: ScoredCandidate, all_scored, criteria) -> str:
    count = int(candidate.raw_values["safety"] or 0)
    average = _average([c.raw_values["safety"] or 0.0 for c in all_scored])
    return (
        f"Comes with {count} of the safety features we track, "
        f"{_comparison_phrase(count, average)} the {average:.1f}-feature average "
        "among your shortlisted matches."
    )


def _performance_reason(candidate: ScoredCandidate, all_scored, criteria) -> str:
    spec = candidate.variant.specification
    power = float(spec.power_bhp) if spec and spec.power_bhp is not None else 0.0
    torque = float(spec.torque_nm) if spec and spec.torque_nm is not None else 0.0
    return (
        f"Puts out {power:.0f} bhp / {torque:.0f} Nm -- one of the stronger "
        "performers in your shortlist."
    )


def _price_value_reason(candidate: ScoredCandidate, all_scored, criteria) -> str:
    price_lakh = float(candidate.variant.price) / 100_000
    budget_lakh = criteria.budget / 100_000
    return (
        f"Priced at ₹{price_lakh:.1f}L against your ₹{budget_lakh:.1f}L budget -- "
        "strong value among your shortlisted matches."
    )


def _comfort_features_reason(candidate: ScoredCandidate, all_scored, criteria) -> str:
    names = {feature.name for feature in candidate.variant.features}
    count = len(names & (COMFORT_FEATURES | INFOTAINMENT_FEATURES))
    average = _average(
        [
            len({f.name for f in c.variant.features} & (COMFORT_FEATURES | INFOTAINMENT_FEATURES))
            for c in all_scored
        ]
    )

    seating_note = ""
    spec = candidate.variant.specification
    if spec and spec.seating_capacity is not None and spec.seating_capacity >= criteria.family_size:
        seating_note = (
            f"Seats {spec.seating_capacity}, comfortably covering your "
            f"family of {criteria.family_size}."
        )

    feature_note = ""
    if count >= average:
        feature_note = (
            f"Loaded with {count} comfort & infotainment features, "
            f"{_comparison_phrase(count, average)} the {average:.1f}-feature average."
        )

    # This dimension can score well from seating/space fit alone (see comfort_raw), so
    # only mention feature count when it's actually a strength -- otherwise the seating
    # fit is the honest reason this scored well, not a contradictory "below average" claim.
    parts = [part for part in (seating_note, feature_note) if part]
    if not parts:
        parts = [
            f"Comes with {count} comfort & infotainment features, "
            "a reasonable fit for this budget."
        ]
    return " ".join(parts)


def _reliability_reason(candidate: ScoredCandidate, all_scored, criteria) -> str:
    rating = candidate.review_aggregate.average_rating or 0.0
    count = candidate.review_aggregate.review_count
    average = _reliability_average(all_scored)
    return (
        f"Owners rate the {candidate.variant.model.name} {rating:.1f}/5 across "
        f"{count} reviews, {_comparison_phrase(rating, average)} the "
        f"{average:.1f}/5 average among your matches."
    )


_REASON_BUILDERS = {
    "fuel_efficiency": _fuel_efficiency_reason,
    "safety": _safety_reason,
    "performance": _performance_reason,
    "price_value": _price_value_reason,
    "comfort_features": _comfort_features_reason,
    "reliability": _reliability_reason,
}


def generate_match_reasons(
    candidate: ScoredCandidate,
    all_scored: list[ScoredCandidate],
    criteria: "RecommendationCriteria",
) -> list[str]:
    variant = candidate.variant
    reasons: list[str] = []

    if criteria.fuel_preference and variant.fuel_type.value == criteria.fuel_preference:
        reasons.append(f"Matches your {criteria.fuel_preference} fuel preference exactly.")
    if (
        criteria.transmission_preference
        and variant.transmission_type.value == criteria.transmission_preference
    ):
        reasons.append(
            f"Matches your {criteria.transmission_preference} transmission preference exactly."
        )
    if (
        criteria.body_type_preference
        and variant.model.body_type.value in criteria.body_type_preference
    ):
        reasons.append(f"Matches your preferred body type ({variant.model.body_type.value}).")

    ranked_dimensions = sorted(DIMENSIONS, key=lambda dim: candidate.weights[dim], reverse=True)
    for dimension in ranked_dimensions:
        if len(reasons) >= MAX_MATCH_REASONS:
            break
        if candidate.dimension_scores[dimension] < TOP_TIER_THRESHOLD:
            continue
        reasons.append(_REASON_BUILDERS[dimension](candidate, all_scored, criteria))

    if not reasons:
        reasons.append("A solid, well-rounded option among your shortlisted matches.")
    return reasons[:MAX_MATCH_REASONS]


# Trade-offs ------------------------------------------------------------------------

_TRADE_OFF_TEMPLATES = {
    "fuel_efficiency": lambda c, avg: (
        f"Mileage of {c.raw_values['fuel_efficiency']:.1f} kmpl trails the candidate "
        f"average of {avg:.1f} kmpl -- expect higher running costs."
    ),
    "safety": lambda c, avg: (
        f"Fewer safety features ({int(c.raw_values['safety'])}) than the "
        f"{avg:.1f}-feature average among your shortlisted matches."
    ),
    "performance": lambda c, avg: (
        "Less power on tap than most other shortlisted options -- may feel stretched "
        "for highway overtaking."
    ),
    "comfort_features": lambda c, avg: (
        "Comes with fewer comfort/infotainment features than other shortlisted options."
    ),
    "reliability": lambda c, avg: (
        f"Based on only {c.review_aggregate.review_count} reviews averaging "
        f"{(c.review_aggregate.average_rating or 0):.1f}/5 -- less review history than "
        "some other shortlisted options, so this rating carries more uncertainty."
    ),
}


def generate_trade_offs(
    candidate: ScoredCandidate,
    all_scored: list[ScoredCandidate],
    criteria: "RecommendationCriteria",
) -> list[str]:
    trade_offs: list[str] = []

    if float(candidate.variant.price) > criteria.budget:
        over_by = float(candidate.variant.price) - criteria.budget
        trade_offs.append(
            f"Priced ₹{over_by / 100_000:.1f}L over your stated budget of "
            f"₹{criteria.budget / 100_000:.1f}L."
        )

    spec = candidate.variant.specification
    seats = spec.seating_capacity if spec else None
    seating_shortfall = seats is not None and seats < criteria.family_size
    if seating_shortfall:
        trade_offs.append(
            f"Seats {seats}, short of your stated family size of {criteria.family_size} -- "
            "you may need to split up for longer trips."
        )

    medians = {
        dimension: _median([c.dimension_scores[dimension] for c in all_scored])
        for dimension in DIMENSIONS
    }
    candidates_for_dimension = [
        dimension
        for dimension in DIMENSIONS
        if dimension != "price_value"
        and not (dimension == "comfort_features" and seating_shortfall)
        and candidate.weights[dimension] >= TRADE_OFF_WEIGHT_THRESHOLD
        and candidate.dimension_scores[dimension] < medians[dimension]
    ]
    candidates_for_dimension.sort(
        key=lambda dimension: (
            -candidate.weights[dimension],
            candidate.dimension_scores[dimension] - medians[dimension],
        )
    )

    for dimension in candidates_for_dimension:
        if len(trade_offs) >= MAX_TRADE_OFFS:
            break
        if dimension == "fuel_efficiency" and candidate.variant.fuel_type == FuelType.ELECTRIC:
            continue  # EVs never get a fuel-efficiency trade-off
        average = _average([c.raw_values[dimension] or 0.0 for c in all_scored])
        trade_offs.append(_TRADE_OFF_TEMPLATES[dimension](candidate, average))

    if not trade_offs:
        trade_offs.append(
            "No significant compromises among your shortlisted priorities -- "
            "a strong all-round match."
        )
    return trade_offs[:MAX_TRADE_OFFS]


# Key feature highlights --------------------------------------------------------------


def generate_key_feature_highlights(
    candidate: ScoredCandidate, limit: int = MAX_KEY_FEATURE_HIGHLIGHTS
) -> list[str]:
    names = [feature.name for feature in candidate.variant.features]
    advanced = [name for name in names if name in ADVANCED_FEATURES]
    advanced_sorted = sorted(
        advanced,
        key=lambda name: HIGHLIGHT_CATEGORY_ORDER.index(FEATURE_CATEGORY.get(name, "exterior")),
    )
    if len(advanced_sorted) >= limit:
        return advanced_sorted[:limit]

    remaining_basic = [name for name in names if name not in ADVANCED_FEATURES]
    return advanced_sorted + remaining_basic[: limit - len(advanced_sorted)]


# Representative reviews --------------------------------------------------------------


def select_representative_reviews(reviews: list[Review], limit: int = 3) -> list[Review]:
    """Highest, lowest, and closest-to-average rated reviews -- never falsely all-positive."""
    if not reviews:
        return []

    average = sum(review.rating for review in reviews) / len(reviews)
    highest = max(reviews, key=lambda review: review.rating)
    lowest = min(reviews, key=lambda review: review.rating)
    closest_to_average = min(reviews, key=lambda review: abs(review.rating - average))

    picks: list[Review] = []
    seen_ids: set[int] = set()
    for review in (highest, closest_to_average, lowest):
        if review.id not in seen_ids:
            picks.append(review)
            seen_ids.add(review.id)
    return picks[:limit]
