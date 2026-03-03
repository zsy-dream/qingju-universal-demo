from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    listing_id: int = Field(ge=1)
    title: str = Field(default="")
    
    # Valuation data
    asking_rent: float = Field(gt=0)
    fair_rent_low: float = Field(gt=0)
    fair_rent_high: float = Field(gt=0)
    deviation_pct: float
    factors: list[dict] = Field(default_factory=list)
    
    # Risk data
    risk_score: int = Field(ge=0, le=200)
    risk_level: str = Field(default="可租")
    top_risks: list[dict] = Field(default_factory=list)
    
    # Evidence count
    evidence_count: int = Field(default=0, ge=0)


class ReportSection(BaseModel):
    title: str
    content: str
    highlights: list[str] = Field(default_factory=list)


class ReportResponse(BaseModel):
    report_title: str
    generated_at: str
    executive_summary: str
    sections: list[ReportSection]
    action_items: list[str]
    confidence_score: int  # 0-100
