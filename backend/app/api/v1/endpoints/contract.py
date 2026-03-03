from fastapi import APIRouter, HTTPException

from app.schemas.contract import ContractInspectionRequest, ContractInspectionResponse
from app.services.contract_service import ContractService

router = APIRouter()
service = ContractService()


@router.post("/inspect", response_model=ContractInspectionResponse)
async def inspect_contract(payload: ContractInspectionRequest):
    try:
        return service.inspect(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
