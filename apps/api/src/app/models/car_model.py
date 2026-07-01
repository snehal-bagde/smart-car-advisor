import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.car_variant import CarVariant
    from app.models.maker import Maker
    from app.models.review import Review


class BodyType(enum.StrEnum):
    HATCHBACK = "hatchback"
    SEDAN = "sedan"
    SUV = "suv"
    MUV = "muv"
    COUPE = "coupe"
    CONVERTIBLE = "convertible"
    PICKUP = "pickup"


class CarModel(Base):
    __tablename__ = "car_models"
    __table_args__ = (UniqueConstraint("maker_id", "name", name="uq_car_models_maker_id_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    maker_id: Mapped[int] = mapped_column(
        ForeignKey("makers.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    body_type: Mapped[BodyType] = mapped_column(
        Enum(BodyType, name="body_type_enum"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    maker: Mapped["Maker"] = relationship(back_populates="car_models")
    variants: Mapped[list["CarVariant"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )
