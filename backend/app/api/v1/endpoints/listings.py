from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.listing import ListingCreate, ListingOut
from app.services.listing_service import ListingService

router = APIRouter()
service = ListingService()


@router.post("/", response_model=ListingOut)
async def create_listing(payload: ListingCreate, db: AsyncSession = Depends(get_db)):
    try:
        obj = await service.create_listing(db, payload)
        return obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[ListingOut])
async def list_listings(limit: int = 20, db: AsyncSession = Depends(get_db)):
    try:
        return await service.list_listings(db, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{listing_id}", response_model=ListingOut)
async def get_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    try:
        listing = await service.get_listing(db, listing_id)
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        return listing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{listing_id}")
async def delete_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    try:
        success = await service.delete_listing(db, listing_id)
        if not success:
            raise HTTPException(status_code=404, detail="Listing not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
