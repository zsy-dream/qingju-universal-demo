from fastapi import APIRouter, HTTPException

from app.services.split_service import SplitService, SplitRequest, SplitResponse

router = APIRouter()
service = SplitService()


@router.post("/calculate", response_model=SplitResponse)
async def calculate_split(payload: SplitRequest):
    """计算合租公平分摊"""
    try:
        return service.calculate_split(payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
