from fastapi import APIRouter, HTTPException

from app.schemas.negotiation import NegotiationRequest, NegotiationResponse
from app.services.negotiation_service import NegotiationService

router = APIRouter()
service = NegotiationService()


@router.post("/script", response_model=NegotiationResponse)
async def generate_script(payload: NegotiationRequest):
    try:
        return service.generate_script(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
