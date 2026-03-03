from pydantic import BaseModel, Field


class EvidenceCreate(BaseModel):
    listing_id: int = Field(ge=1)
    risk_tag: str = Field(default="", max_length=50)
    source_type: str = Field(default="user", max_length=30)
    note: str = Field(default="", max_length=200)
    content: str = Field(default="")  # URL or base64 data


class EvidenceOut(EvidenceCreate):
    id: int

    class Config:
        from_attributes = True
