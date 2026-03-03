from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    listing_ids: list[int] = Field(min_length=2, max_length=6)


class ComparisonFactor(BaseModel):
    name: str
    values: list[dict]  # [{"listing_id": 1, "value": "...", "score": 8}, ...]
    winner_id: int | None = None


class ComparisonRecommendation(BaseModel):
    best_choice_id: int
    best_choice_reason: str
    second_choice_id: int | None = None
    avoid_ids: list[int] = Field(default_factory=list)


class ComparisonResponse(BaseModel):
    listings: list[dict]
    factors: list[ComparisonFactor]
    scores: list[dict]  # [{"listing_id": 1, "total_score": 85, "breakdown": {...}}, ...]
    recommendation: ComparisonRecommendation
    summary: str
