from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.evidence import EvidenceCreate, EvidenceOut
from app.services.evidence_service import EvidenceService

router = APIRouter()
service = EvidenceService()


@router.post("/", response_model=EvidenceOut)
async def create_evidence(payload: EvidenceCreate, db: AsyncSession = Depends(get_db)):
    try:
        obj = await service.create_evidence(db, payload)
        return obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[EvidenceOut])
async def list_evidence(listing_id: int = Query(..., ge=1), db: AsyncSession = Depends(get_db)):
    try:
        return await service.list_by_listing(db, listing_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{evidence_id}")
async def delete_evidence(evidence_id: int, db: AsyncSession = Depends(get_db)):
    try:
        ok = await service.delete_evidence(db, evidence_id)
        if not ok:
            raise HTTPException(status_code=404, detail="evidence not found")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
