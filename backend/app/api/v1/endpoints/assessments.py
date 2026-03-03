from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.assessment import EstimateRequest, EstimateResponse, RiskRequest, RiskResponse
from app.schemas.listing import ListingOut
from app.services.assessment_service import AssessmentService
from app.services.listing_service import ListingService

router = APIRouter()
assess_service = AssessmentService()
listing_service = ListingService()


@router.post("/estimate", response_model=EstimateResponse)
async def estimate(payload: EstimateRequest, db: AsyncSession = Depends(get_db)):
    """
    执行 Hedonic 估值

    NOTE: 当数据库中存在足够房源时，使用真实对标样本替代 Mock 数据
    """
    try:
        if payload.listing_id:
            obj = await listing_service.get_listing(db, payload.listing_id)
            if not obj:
                raise HTTPException(status_code=404, detail="listing not found")
            payload = EstimateRequest(
                listing_id=obj.id,
                asking_rent=obj.asking_rent,
                area_sqm=obj.area_sqm,
                floor=obj.floor,
                total_floors=obj.total_floors,
                orientation=obj.orientation,
                decoration=obj.decoration,
                has_elevator=bool(obj.has_elevator),
                subway_distance_m=obj.subway_distance_m,
                commute_minutes=obj.commute_minutes,
            )

        result = assess_service.estimate(payload)

        # NOTE: 尝试从数据库检索真实对标样本，替代默认的 Mock 数据
        real_comps = await listing_service.find_comparable(
            db,
            area_sqm=payload.area_sqm,
            district="",  # 前端暂不传 district，后续可按需扩展
            orientation=payload.orientation,
            exclude_id=payload.listing_id,
            limit=3,
        )
        if real_comps:
            result.comparable_samples = real_comps

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk", response_model=RiskResponse)
async def risk(payload: RiskRequest):
    try:
        return assess_service.risk(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
