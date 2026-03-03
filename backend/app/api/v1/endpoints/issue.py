from fastapi import APIRouter, HTTPException, Query

from app.schemas.issue import IssueCreate, IssueUpdate, IssueOut
from app.services.issue_service import IssueService

router = APIRouter()
service = IssueService()


@router.post("/", response_model=IssueOut)
async def create_issue(payload: IssueCreate):
    try:
        return await service.create(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[IssueOut])
async def list_issues(listing_id: int | None = Query(None)):
    try:
        if listing_id:
            return await service.list_by_listing(listing_id)
        return await service.list_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{issue_id}", response_model=IssueOut)
async def update_issue(issue_id: int, payload: IssueUpdate):
    try:
        result = await service.update(issue_id, payload)
        if not result:
            raise HTTPException(status_code=404, detail="Issue not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{issue_id}")
async def delete_issue(issue_id: int):
    try:
        success = await service.delete(issue_id)
        if not success:
            raise HTTPException(status_code=404, detail="Issue not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
