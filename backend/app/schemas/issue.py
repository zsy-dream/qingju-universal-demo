from datetime import datetime
from pydantic import BaseModel, Field


class IssueCreate(BaseModel):
    listing_id: int = Field(ge=1)
    title: str = Field(max_length=100)
    category: str = Field(default="其他")
    severity: str = Field(default="一般")
    description: str = Field(default="")
    evidence_ids: list[int] = Field(default_factory=list)


class IssueUpdate(BaseModel):
    status: str = Field(default="处理中")
    landlord_response: str = Field(default="")
    resolution: str = Field(default="")


class IssueOut(BaseModel):
    id: int
    listing_id: int
    title: str
    category: str
    severity: str
    status: str
    description: str
    landlord_response: str
    resolution: str
    reported_at: datetime
    resolved_at: datetime | None
    evidence_ids: list[int]
    
    model_config = {"from_attributes": True}
