from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.comparison import CompareRequest, ComparisonResponse
from app.services.comparison_service import ComparisonService
from app.db.session import get_db

router = APIRouter()
service = ComparisonService()


@router.post("/compare", response_model=ComparisonResponse)
async def compare_listings(payload: CompareRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await service.compare(payload, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
