import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.car_model import CarModel
    from app.models.feature import Feature
    from app.models.variant_specification import VariantSpecification


class FuelType(enum.StrEnum):
    PETROL = "petrol"
    DIESEL = "diesel"
    CNG = "cng"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


class TransmissionType(enum.StrEnum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    AMT = "amt"
    CVT = "cvt"
    DCT = "dct"


class CarVariant(Base):
    __tablename__ = "car_variants"
    __table_args__ = (
        UniqueConstraint("model_id", "name", name="uq_car_variants_model_id_name"),
        CheckConstraint("price > 0", name="ck_car_variants_price_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(
        ForeignKey("car_models.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    fuel_type: Mapped[FuelType] = mapped_column(
        Enum(FuelType, name="fuel_type_enum"), nullable=False, index=True
    )
    transmission_type: Mapped[TransmissionType] = mapped_column(
        Enum(TransmissionType, name="transmission_type_enum"), nullable=False, index=True
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    model: Mapped["CarModel"] = relationship(back_populates="variants")
    specification: Mapped["VariantSpecification"] = relationship(
        back_populates="variant", cascade="all, delete-orphan", uselist=False
    )
    features: Mapped[list["Feature"]] = relationship(
        secondary="variant_features", back_populates="variants"
    )
