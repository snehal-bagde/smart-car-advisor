from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, SmallInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.car_variant import CarVariant


class VariantSpecification(Base):
    __tablename__ = "variant_specifications"
    __table_args__ = (
        CheckConstraint(
            "engine_displacement_cc > 0", name="ck_variant_specs_displacement_positive"
        ),
        CheckConstraint("power_bhp > 0", name="ck_variant_specs_power_positive"),
        CheckConstraint("torque_nm > 0", name="ck_variant_specs_torque_positive"),
        CheckConstraint("mileage_kmpl > 0", name="ck_variant_specs_mileage_positive"),
        CheckConstraint("seating_capacity > 0", name="ck_variant_specs_seating_positive"),
        CheckConstraint("length_mm > 0", name="ck_variant_specs_length_positive"),
        CheckConstraint("width_mm > 0", name="ck_variant_specs_width_positive"),
        CheckConstraint("height_mm > 0", name="ck_variant_specs_height_positive"),
        CheckConstraint("wheelbase_mm > 0", name="ck_variant_specs_wheelbase_positive"),
        CheckConstraint("boot_space_litres > 0", name="ck_variant_specs_boot_space_positive"),
        CheckConstraint(
            "fuel_tank_capacity_litres > 0", name="ck_variant_specs_fuel_tank_positive"
        ),
        CheckConstraint(
            "ground_clearance_mm > 0", name="ck_variant_specs_ground_clearance_positive"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("car_variants.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    engine_displacement_cc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    power_bhp: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    torque_nm: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    mileage_kmpl: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    seating_capacity: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    length_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    width_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wheelbase_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    boot_space_litres: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fuel_tank_capacity_litres: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    ground_clearance_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    variant: Mapped["CarVariant"] = relationship(back_populates="specification")
