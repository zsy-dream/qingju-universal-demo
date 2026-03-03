from fastapi import APIRouter

from app.api.v1.endpoints import listings, assessments, dashboard, evidence, negotiation, report, contract, issue, comparison, split, commute

api_router = APIRouter()

api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
api_router.include_router(negotiation.router, prefix="/negotiation", tags=["negotiation"])
api_router.include_router(report.router, prefix="/report", tags=["report"])
api_router.include_router(contract.router, prefix="/contract", tags=["contract"])
api_router.include_router(issue.router, prefix="/issues", tags=["issues"])
api_router.include_router(comparison.router, prefix="/comparison", tags=["comparison"])
api_router.include_router(split.router, prefix="/split", tags=["split"])
api_router.include_router(commute.router, prefix="/commute", tags=["commute"])

