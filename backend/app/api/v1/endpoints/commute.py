from fastapi import APIRouter, HTTPException

from app.services.commute_service import CommuteService, CommuteAnalysisRequest, CommuteAnalysisResponse

router = APIRouter()
service = CommuteService()


@router.post("/analyze", response_model=CommuteAnalysisResponse)
async def analyze_commute(payload: CommuteAnalysisRequest):
    """通勤-租金边际替代分析"""
    try:
        return service.analyze(payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
