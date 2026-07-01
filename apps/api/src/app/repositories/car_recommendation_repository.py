from dataclasses import dataclass

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, contains_eager, selectinload

from app.core.database import get_db
from app.models.car_model import CarModel
from app.models.car_variant import CarVariant
from app.models.review import Review


@dataclass(frozen=True)
class ReviewAggregate:
    average_rating: float | None
    review_count: int


class CarRecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_candidate_variants(
        self,
        *,
        max_price: float,
        fuel_type: str | None = None,
        transmission_type: str | None = None,
        body_types: list[str] | None = None,
    ) -> list[CarVariant]:
        """Hard-filtered candidate variants, fully eager-loaded: variant.specification,
        variant.features, variant.model, and variant.model.maker are all safe to access
        with zero additional queries."""
        stmt = (
            select(CarVariant)
            .join(CarVariant.model)
            .join(CarModel.maker)
            .options(
                contains_eager(CarVariant.model).contains_eager(CarModel.maker),
                selectinload(CarVariant.specification),
                selectinload(CarVariant.features),
            )
            .where(CarVariant.price <= max_price)
        )
        if fuel_type is not None:
            stmt = stmt.where(CarVariant.fuel_type == fuel_type)
        if transmission_type is not None:
            stmt = stmt.where(CarVariant.transmission_type == transmission_type)
        if body_types:
            stmt = stmt.where(CarModel.body_type.in_(body_types))

        return list(self.db.scalars(stmt).unique())

    def get_review_aggregates(self, model_ids: list[int]) -> dict[int, ReviewAggregate]:
        """Avg rating + count per CarModel.id, computed live (never stored)."""
        if not model_ids:
            return {}

        stmt = (
            select(
                Review.model_id,
                func.avg(Review.rating).label("average_rating"),
                func.count(Review.id).label("review_count"),
            )
            .where(Review.model_id.in_(model_ids))
            .group_by(Review.model_id)
        )
        return {
            row.model_id: ReviewAggregate(
                average_rating=float(row.average_rating) if row.average_rating else None,
                review_count=row.review_count,
            )
            for row in self.db.execute(stmt)
        }

    def get_reviews_for_models(self, model_ids: list[int]) -> dict[int, list[Review]]:
        """ALL reviews for the given models (no per-model limit) -- representative-snippet
        selection needs the full set to correctly pick highest/lowest/closest-to-average,
        not a pre-truncated slice. Only ever called for the final top-5 result models, so
        the volume stays small (<=8 reviews/model in seed data)."""
        if not model_ids:
            return {}

        stmt = select(Review).where(Review.model_id.in_(model_ids))
        reviews_by_model: dict[int, list[Review]] = {model_id: [] for model_id in model_ids}
        for review in self.db.scalars(stmt):
            reviews_by_model[review.model_id].append(review)
        return reviews_by_model


def get_car_recommendation_repository(
    db: Session = Depends(get_db),
) -> CarRecommendationRepository:
    return CarRecommendationRepository(db)
