"""Plain in-memory ORM object builders for unit-testing scoring/explanation logic
without a database -- SQLAlchemy model instances work fine as plain Python objects as
long as no lazy-loaded attribute is touched."""

from decimal import Decimal

from app.models.car_model import BodyType, CarModel
from app.models.car_variant import CarVariant, FuelType, TransmissionType
from app.models.feature import Feature
from app.models.maker import Maker
from app.models.variant_specification import VariantSpecification


def build_variant(
    *,
    id: int,
    price: float = 500_000.0,
    fuel_type: FuelType = FuelType.PETROL,
    transmission_type: TransmissionType = TransmissionType.MANUAL,
    body_type: BodyType = BodyType.HATCHBACK,
    model_id: int = 1,
    maker_name: str = "TestMaker",
    model_name: str = "TestModel",
    variant_name: str = "TestVariant",
    seating_capacity: int | None = 5,
    mileage_kmpl: float | None = 18.0,
    power_bhp: float | None = 80.0,
    torque_nm: float | None = 110.0,
    boot_space_litres: int | None = 300,
    feature_names: list[str] | None = None,
) -> CarVariant:
    maker = Maker(id=model_id, name=maker_name, country_of_origin="India")
    model = CarModel(id=model_id, maker_id=maker.id, name=model_name, body_type=body_type)
    model.maker = maker

    spec = VariantSpecification(
        id=id,
        variant_id=id,
        seating_capacity=seating_capacity,
        mileage_kmpl=Decimal(str(mileage_kmpl)) if mileage_kmpl is not None else None,
        power_bhp=Decimal(str(power_bhp)) if power_bhp is not None else None,
        torque_nm=Decimal(str(torque_nm)) if torque_nm is not None else None,
        boot_space_litres=boot_space_litres,
    )

    variant = CarVariant(
        id=id,
        model_id=model.id,
        name=variant_name,
        fuel_type=fuel_type,
        transmission_type=transmission_type,
        price=Decimal(str(price)),
    )
    variant.model = model
    variant.specification = spec
    variant.features = [
        Feature(id=1000 + index, name=name) for index, name in enumerate(feature_names or [])
    ]
    return variant


def build_criteria(**overrides):
    from app.services.car_recommendation_service import RecommendationCriteria

    defaults = {
        "budget": 1_000_000.0,
        "daily_driving_distance_km": 20.0,
        "primary_usage": "mixed",
        "family_size": 3,
        "fuel_preference": None,
        "transmission_preference": None,
        "body_type_preference": None,
        "priorities": [],
    }
    defaults.update(overrides)
    return RecommendationCriteria(**defaults)
