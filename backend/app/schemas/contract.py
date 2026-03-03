from pydantic import BaseModel, Field


class ClauseCheckItem(BaseModel):
    clause_name: str = Field(max_length=50)
    severity: str = Field(default="normal")  # normal / warning / critical
    description: str = Field(default="")
    current_text: str = Field(default="")
    suggested_alternative: str = Field(default="")
    why_it_matters: str = Field(default="")


class ContractInspectionRequest(BaseModel):
    user_clauses: list[ClauseCheckItem] = Field(default_factory=list)
    quick_mode: bool = Field(default=True)  # if True, use built-in template


class ContractInspectionResponse(BaseModel):
    overall_risk: str  # low / medium / high
    critical_count: int
    warning_count: int
    checked_clauses: list[dict]
    red_flags: list[str]
    general_advice: list[str]
