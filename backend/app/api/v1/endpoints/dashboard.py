from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.assessment import DashboardSummary, EstimateRequest, RiskRequest
from app.services.assessment_service import AssessmentService
from app.services.listing_service import ListingService

router = APIRouter()
listing_service = ListingService()
assess_service = AssessmentService()


@router.get("/summary", response_model=DashboardSummary)
async def summary(db: AsyncSession = Depends(get_db)):
    try:
        listings = await listing_service.list_listings(db, limit=12)
        if not listings:
            return DashboardSummary(listing_count=0, avg_deviation_pct=0, high_risk_count=0, latest_listings=[])

        deviations = []
        high_risk = 0
        latest = []
        for l in listings:
            est = assess_service.estimate(
                EstimateRequest(
                    asking_rent=l.asking_rent,
                    area_sqm=l.area_sqm,
                    floor=l.floor,
                    total_floors=l.total_floors,
                    orientation=l.orientation,
                    decoration=l.decoration,
                    has_elevator=bool(l.has_elevator),
                    subway_distance_m=l.subway_distance_m,
                    commute_minutes=l.commute_minutes,
                )
            )
            deviations.append(est.deviation_pct)
            # quick mock risk signal
            risk = assess_service.risk(RiskRequest(noise=0, mold=0, poor_light=0, old_appliances=0, sublease_risk=0, contract_unfair=0))
            if risk.risk_level != "可租":
                high_risk += 1

            latest.append(
                {
                    "id": l.id,
                    "title": l.title,
                    "asking_rent": l.asking_rent,
                    "fair_low": est.fair_rent_low,
                    "fair_high": est.fair_rent_high,
                    "deviation_pct": est.deviation_pct,
                }
            )

        avg = sum(deviations) / max(len(deviations), 1)

        return DashboardSummary(
            listing_count=len(listings),
            avg_deviation_pct=round(avg, 1),
            high_risk_count=high_risk,
            latest_listings=latest,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
