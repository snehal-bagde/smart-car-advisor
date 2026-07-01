"""Idempotent seed entrypoint. Populates makers, models, variants, specs, features, and
reviews from the curated data in `app.seed_data`.

Safe to re-run at any time: every entity is looked up by its natural key before insert
(see `upsert_utils.get_or_create`), so reruns never duplicate existing rows and will
restore any rows that were deleted by mistake.

Usage: uv run python -m app.seed.run_seed
"""

import logging

from app.core.database import SessionLocal
from app.models.car_model import CarModel
from app.models.car_variant import CarVariant
from app.models.feature import Feature
from app.models.maker import Maker
from app.models.review import Review
from app.models.variant_feature import VariantFeature
from app.models.variant_specification import VariantSpecification
from app.seed.generators import (
    generate_reviews,
    generate_spec,
    generate_variant_plan,
    pick_features_for,
)
from app.seed.upsert_utils import get_or_create
from app.seed_data.features import FEATURE_POOL
from app.seed_data.makers_and_models import MAKERS_AND_MODELS

logger = logging.getLogger(__name__)


def seed_features(db) -> dict[str, int]:
    feature_ids = {}
    for name, _category, _tier in FEATURE_POOL:
        feature, _created = get_or_create(db, Feature, {"name": name})
        feature_ids[name] = feature.id
    db.commit()
    return feature_ids


def seed_maker_subtree(
    db, maker_name: str, country: str, model_rows: list[dict], feature_ids: dict[str, int]
) -> None:
    maker, _ = get_or_create(db, Maker, {"name": maker_name}, {"country_of_origin": country})

    for row in model_rows:
        model_name, body_type, segment = row["model"], row["body_type"], row["segment"]

        car_model, _ = get_or_create(
            db, CarModel, {"maker_id": maker.id, "name": model_name}, {"body_type": body_type}
        )

        for plan in generate_variant_plan(maker_name, model_name, segment, body_type):
            variant, _ = get_or_create(
                db,
                CarVariant,
                {"model_id": car_model.id, "name": plan["name"]},
                {
                    "fuel_type": plan["fuel_type"],
                    "transmission_type": plan["transmission_type"],
                    "price": plan["price"],
                },
            )

            get_or_create(
                db,
                VariantSpecification,
                {"variant_id": variant.id},
                generate_spec(maker_name, model_name, plan["name"], segment, body_type),
            )

            for feature_name in pick_features_for(maker_name, model_name, plan["name"], segment):
                get_or_create(
                    db,
                    VariantFeature,
                    {"variant_id": variant.id, "feature_id": feature_ids[feature_name]},
                )

        if db.query(Review).filter_by(model_id=car_model.id).count() == 0:
            for review in generate_reviews(maker_name, model_name):
                db.add(Review(model_id=car_model.id, **review))

    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        feature_ids = seed_features(db)
        logger.info("Seeded %d features", len(feature_ids))

        by_maker: dict[tuple[str, str], list[dict]] = {}
        for row in MAKERS_AND_MODELS:
            by_maker.setdefault((row["maker"], row["country"]), []).append(row)

        for (maker_name, country), model_rows in by_maker.items():
            try:
                seed_maker_subtree(db, maker_name, country, model_rows, feature_ids)
                logger.info("Seeded maker: %s (%d models)", maker_name, len(model_rows))
            except Exception:
                db.rollback()
                logger.exception("Failed seeding maker %s, continuing with the rest", maker_name)
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()
