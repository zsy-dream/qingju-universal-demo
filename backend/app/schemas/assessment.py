from pydantic import BaseModel, Field


class EstimateRequest(BaseModel):
    listing_id: int | None = Field(default=None, ge=1)

    # allow ad-hoc estimation without saving listing
    asking_rent: float = Field(default=0, ge=0)
    area_sqm: float = Field(default=0, ge=0)
    floor: int = Field(default=0, ge=0)
    total_floors: int = Field(default=0, ge=0)
    orientation: str = ""
    decoration: str = ""
    has_elevator: bool = False
    subway_distance_m: float = Field(default=0, ge=0)
    commute_minutes: float = Field(default=0, ge=0)


class EstimateResponse(BaseModel):
    fair_rent_low: float
    fair_rent_high: float
    deviation_pct: float
    factors: list[dict]
    comparable_samples: list[dict]


class RiskRequest(BaseModel):
    listing_id: int | None = Field(default=None, ge=1)

    # user-checked risk signals
    noise: int = Field(default=0, ge=0, le=2)  # 0 none, 1 suspect, 2 confirmed
    mold: int = Field(default=0, ge=0, le=2)
    poor_light: int = Field(default=0, ge=0, le=2)
    old_appliances: int = Field(default=0, ge=0, le=2)
    sublease_risk: int = Field(default=0, ge=0, le=2)
    contract_unfair: int = Field(default=0, ge=0, le=2)


class RiskResponse(BaseModel):
    risk_score: int
    risk_level: str
    top_risks: list[dict]
    suggestions: list[str]
    radar_data: list[dict] = []  # 雷达图数据，每项包含 name/value/max_value/weight


class DashboardSummary(BaseModel):
    listing_count: int
    avg_deviation_pct: float
    high_risk_count: int
    latest_listings: list[dict]
