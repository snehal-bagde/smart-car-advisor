import enum

from pydantic import BaseModel, Field, field_validator


class FuelPreference(enum.StrEnum):
    PETROL = "petrol"
    DIESEL = "diesel"
    CNG = "cng"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


class TransmissionPreference(enum.StrEnum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    AMT = "amt"
    CVT = "cvt"
    DCT = "dct"


class BodyTypePreference(enum.StrEnum):
    HATCHBACK = "hatchback"
    SEDAN = "sedan"
    SUV = "suv"
    MUV = "muv"
    COUPE = "coupe"
    CONVERTIBLE = "convertible"
    PICKUP = "pickup"


class PrimaryUsage(enum.StrEnum):
    CITY = "city"
    HIGHWAY = "highway"
    MIXED = "mixed"


class Priority(enum.StrEnum):
    FUEL_ECONOMY = "fuel_economy"
    SAFETY = "safety"
    COMFORT_FEATURES = "comfort_features"
    PERFORMANCE = "performance"
    LOW_PRICE = "low_price"
    RELIABILITY_BRAND_TRUST = "reliability_brand_trust"


class CarRecommendationRequest(BaseModel):
    budget: float = Field(gt=0, description="Maximum budget in INR")
    daily_driving_distance_km: float = Field(ge=0)
    primary_usage: PrimaryUsage
    family_size: int = Field(ge=1, le=9)
    fuel_preference: FuelPreference | None = None
    transmission_preference: TransmissionPreference | None = None
    body_type_preference: list[BodyTypePreference] | None = None
    priorities: list[Priority] = Field(default_factory=list, max_length=6)

    @field_validator("priorities")
    @classmethod
    def priorities_must_be_unique(cls, v: list[Priority]) -> list[Priority]:
        if len(v) != len(set(v)):
            raise ValueError("priorities must not contain duplicates")
        return v

    @field_validator("body_type_preference")
    @classmethod
    def body_type_preference_must_be_unique(
        cls, v: list[BodyTypePreference] | None
    ) -> list[BodyTypePreference] | None:
        if v is not None and len(v) != len(set(v)):
            raise ValueError("body_type_preference must not contain duplicates")
        return v


class ReviewSnippet(BaseModel):
    reviewer_name: str
    rating: int
    comment: str | None


class ReviewSummary(BaseModel):
    average_rating: float | None
    review_count: int
    snippets: list[ReviewSnippet]


class CarRecommendationResult(BaseModel):
    variant_id: int
    maker_name: str
    model_name: str
    variant_name: str
    price: float
    fuel_type: FuelPreference
    transmission_type: TransmissionPreference
    body_type: BodyTypePreference
    seating_capacity: int | None
    mileage_kmpl: float | None
    power_bhp: float | None
    boot_space_litres: int | None
    overall_score: float
    score_confidence: float
    match_reasons: list[str]
    trade_offs: list[str]
    key_feature_highlights: list[str]
    reviews: ReviewSummary


class CarRecommendationResponse(BaseModel):
    results: list[CarRecommendationResult]
    total_candidates_matched: int
