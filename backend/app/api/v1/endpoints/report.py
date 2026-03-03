from fastapi import APIRouter, HTTPException

from app.schemas.report import ReportRequest, ReportResponse
from app.services.report_service import ReportService

router = APIRouter()
service = ReportService()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(payload: ReportRequest):
    try:
        return service.generate_report(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
