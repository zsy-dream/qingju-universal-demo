from pydantic import BaseModel, Field


class NegotiationRequest(BaseModel):
    asking_rent: float = Field(gt=0)
    fair_rent_low: float = Field(gt=0)
    fair_rent_high: float = Field(gt=0)
    deviation_pct: float
    factors: list[dict] = Field(default_factory=list)
    risk_level: str = Field(default="可租")


class NegotiationResponse(BaseModel):
    target_price_low: float
    target_price_high: float
    recommended_offer: float
    script_sections: list[dict]
    fallback_tactics: list[str]
