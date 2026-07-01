"""Deterministic, pure data generators for seeding variants/specs/features/reviews.

Every function derives its randomness from `random.Random(natural_key)` rather than the
global RNG, so re-running the seed script produces identical generated values for
existing rows regardless of run order -- this is what keeps the seed idempotent.
"""

import random
from decimal import ROUND_HALF_UP, Decimal

from app.seed_data.features import FEATURE_POOL, RICHNESS_TIER_COUNTS
from app.seed_data.review_templates import (
    RATING_DISTRIBUTION,
    REVIEW_TEMPLATES,
    REVIEWER_FIRST_NAMES,
)

FUEL_LABELS = {"petrol": "Petrol", "diesel": "Diesel", "cng": "CNG", "electric": "Electric", "hybrid": "Hybrid"}
TRANSMISSION_LABELS = {"manual": "MT", "automatic": "AT", "amt": "AMT", "cvt": "CVT", "dct": "DCT"}

SEGMENT_PRICE_BANDS_LAKH = {
    "entry": (4.0, 7.0),
    "economy": (6.0, 12.0),
    "mid": (9.0, 20.0),
    "premium": (18.0, 35.0),
    "luxury": (35.0, 120.0),
    "ev": (12.0, 70.0),
}

# (trim, fuel_type, transmission_type, price_factor relative to the model's base price)
SEGMENT_VARIANT_TEMPLATES = {
    "entry": [("LXI", "petrol", "manual", 1.0), ("VXI", "petrol", "manual", 1.12)],
    "economy": [
        ("LXI", "petrol", "manual", 1.0),
        ("VXI", "petrol", "manual", 1.15),
        ("ZXI", "petrol", "automatic", 1.32),
    ],
    "mid": [
        ("Base", "petrol", "manual", 1.0),
        ("Mid", "petrol", "automatic", 1.18),
        ("Top", "diesel", "automatic", 1.32),
    ],
    "premium": [("Standard", "petrol", "automatic", 1.0), ("Top", "diesel", "automatic", 1.14)],
    "luxury": [("Standard", "petrol", "automatic", 1.0), ("Top", "diesel", "automatic", 1.12)],
    "ev": [
        ("Standard Range", "electric", "automatic", 1.0),
        ("Long Range", "electric", "automatic", 1.28),
    ],
}

SEGMENT_SPEC_BANDS = {
    "entry": {"engine_cc": (796, 1197), "power_bhp": (40, 70), "torque_nm": (60, 95), "mileage_kmpl": (19.0, 25.0)},
    "economy": {"engine_cc": (999, 1497), "power_bhp": (65, 100), "torque_nm": (85, 135), "mileage_kmpl": (17.0, 22.0)},
    "mid": {"engine_cc": (1197, 1997), "power_bhp": (90, 170), "torque_nm": (110, 250), "mileage_kmpl": (13.0, 19.0)},
    "premium": {"engine_cc": (1498, 2494), "power_bhp": (140, 250), "torque_nm": (200, 400), "mileage_kmpl": (10.0, 16.0)},
    "luxury": {"engine_cc": (1998, 2998), "power_bhp": (190, 400), "torque_nm": (300, 600), "mileage_kmpl": (7.0, 13.0)},
    "ev": {"engine_cc": None, "power_bhp": (95, 320), "torque_nm": (140, 500), "mileage_kmpl": None},
}

# Seating is driven by body type, not segment -- a compact EV crossover shouldn't
# roll a 7-seat result just because EVs skew toward the upper segment bands.
BODY_SEAT_RANGE = {
    "hatchback": (4, 5),
    "sedan": (5, 5),
    "suv": (5, 7),
    "muv": (6, 8),
    "pickup": (2, 5),
    "coupe": (2, 4),
    "convertible": (2, 4),
}

BODY_DIMENSIONS_MM = {
    "hatchback": {"length": (3600, 4000), "width": (1600, 1750), "height": (1500, 1600), "wheelbase": (2350, 2500)},
    "sedan": {"length": (4300, 4900), "width": (1700, 1850), "height": (1450, 1500), "wheelbase": (2550, 2900)},
    "suv": {"length": (3800, 5100), "width": (1750, 1950), "height": (1650, 1850), "wheelbase": (2450, 2950)},
    "muv": {"length": (4200, 5100), "width": (1700, 1850), "height": (1700, 1850), "wheelbase": (2650, 3000)},
    "pickup": {"length": (5200, 5400), "width": (1800, 1900), "height": (1800, 1850), "wheelbase": (3000, 3100)},
    "coupe": {"length": (4300, 4700), "width": (1800, 1900), "height": (1350, 1420), "wheelbase": (2600, 2800)},
    "convertible": {"length": (4200, 4600), "width": (1800, 1900), "height": (1350, 1420), "wheelbase": (2500, 2700)},
}

BODY_GROUND_CLEARANCE_MM = {
    "hatchback": (155, 175),
    "sedan": (155, 175),
    "suv": (180, 220),
    "muv": (170, 200),
    "pickup": (200, 230),
    "coupe": (130, 150),
    "convertible": (130, 150),
}

BODY_BOOT_SPACE_LITRES = {
    "hatchback": (250, 350),
    "sedan": (400, 520),
    "suv": (350, 600),
    "muv": (200, 450),
    "coupe": (200, 350),
    "convertible": (200, 320),
    # pickup: no conventional boot -- left out on purpose, handled as None below.
}

BODY_FUEL_TANK_LITRES = {
    "hatchback": (28.0, 40.0),
    "sedan": (35.0, 50.0),
    "suv": (40.0, 60.0),
    "muv": (45.0, 65.0),
    "pickup": (65.0, 80.0),
    "coupe": (45.0, 60.0),
    "convertible": (45.0, 60.0),
}


def _round_price(price_lakh: float) -> Decimal:
    rupees = round(price_lakh * 100_000 / 5000) * 5000
    return Decimal(rupees).quantize(Decimal("0.01"))


def _build_variant_name(trim: str, fuel_type: str, transmission_type: str) -> str:
    fuel_label = FUEL_LABELS[fuel_type]
    transmission_label = TRANSMISSION_LABELS[transmission_type]
    if trim.upper() == fuel_label.upper():
        return f"{trim} {transmission_label}"
    return f"{trim} {fuel_label} {transmission_label}"


def generate_variant_plan(maker: str, model: str, segment: str, body_type: str) -> list[dict]:
    rng = random.Random(f"{maker}:{model}:variants")
    price_lo, price_hi = SEGMENT_PRICE_BANDS_LAKH[segment]
    base_price_lakh = rng.uniform(price_lo, price_hi)

    templates = list(SEGMENT_VARIANT_TEMPLATES[segment])
    allows_cng = segment in ("entry", "economy") and body_type in ("hatchback", "sedan")
    if allows_cng and rng.random() < 0.5:
        last_factor = templates[-1][3]
        templates.append(("CNG", "cng", "manual", round(last_factor * 1.05, 3)))

    variants = []
    for trim, fuel_type, transmission_type, price_factor in templates:
        variants.append(
            {
                "name": _build_variant_name(trim, fuel_type, transmission_type),
                "fuel_type": fuel_type,
                "transmission_type": transmission_type,
                "price": _round_price(base_price_lakh * price_factor),
            }
        )
    return variants


def _round_decimal(value: float, places: str = "0.1") -> Decimal:
    return Decimal(str(value)).quantize(Decimal(places), rounding=ROUND_HALF_UP)


def generate_spec(maker: str, model: str, variant_name: str, segment: str, body_type: str) -> dict:
    rng = random.Random(f"{maker}:{model}:{variant_name}:spec")
    bands = SEGMENT_SPEC_BANDS[segment]
    is_ev = segment == "ev"

    dims = BODY_DIMENSIONS_MM[body_type]
    boot_range = BODY_BOOT_SPACE_LITRES.get(body_type)

    return {
        "engine_displacement_cc": None if is_ev else rng.randint(*bands["engine_cc"]),
        "power_bhp": _round_decimal(rng.uniform(*bands["power_bhp"])),
        "torque_nm": _round_decimal(rng.uniform(*bands["torque_nm"])),
        "mileage_kmpl": None if is_ev else _round_decimal(rng.uniform(*bands["mileage_kmpl"])),
        "seating_capacity": rng.randint(*BODY_SEAT_RANGE[body_type]),
        "length_mm": rng.randint(*dims["length"]),
        "width_mm": rng.randint(*dims["width"]),
        "height_mm": rng.randint(*dims["height"]),
        "wheelbase_mm": rng.randint(*dims["wheelbase"]),
        "boot_space_litres": rng.randint(*boot_range) if boot_range else None,
        "fuel_tank_capacity_litres": (
            None if is_ev else _round_decimal(rng.uniform(*BODY_FUEL_TANK_LITRES[body_type]))
        ),
        "ground_clearance_mm": rng.randint(*BODY_GROUND_CLEARANCE_MM[body_type]),
    }


def pick_features_for(maker: str, model: str, variant_name: str, segment: str) -> list[str]:
    rng = random.Random(f"{maker}:{model}:{variant_name}:features")
    lo, hi = RICHNESS_TIER_COUNTS[segment]

    basic = [name for name, _category, tier in FEATURE_POOL if tier == "basic"]
    advanced = [name for name, _category, tier in FEATURE_POOL if tier == "advanced"]
    pool = basic if segment in ("entry", "economy") else basic + advanced

    count = min(rng.randint(lo, hi), len(pool))
    return rng.sample(pool, count)


def generate_reviews(maker: str, model: str) -> list[dict]:
    rng = random.Random(f"{maker}:{model}:reviews")
    ratings = list(RATING_DISTRIBUTION.keys())
    weights = list(RATING_DISTRIBUTION.values())

    reviews = []
    for _ in range(rng.randint(4, 8)):
        rating = rng.choices(ratings, weights=weights, k=1)[0]
        reviews.append(
            {
                "reviewer_name": rng.choice(REVIEWER_FIRST_NAMES),
                "rating": rating,
                "comment": rng.choice(REVIEW_TEMPLATES[rating]).format(model=model),
            }
        )
    return reviews
