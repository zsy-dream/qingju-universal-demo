from datetime import datetime
from sqlalchemy import select, desc
from app.models.issue import Issue
from app.schemas.issue import IssueCreate, IssueUpdate, IssueOut
from app.core.db import AsyncSessionLocal


class IssueService:
    async def create(self, data: IssueCreate) -> IssueOut:
        async with AsyncSessionLocal() as session:
            issue = Issue(
                listing_id=data.listing_id,
                title=data.title,
                category=data.category,
                severity=data.severity,
                description=data.description,
                evidence_ids=",".join(map(str, data.evidence_ids)) if data.evidence_ids else ""
            )
            session.add(issue)
            await session.commit()
            await session.refresh(issue)
            return self._to_out(issue)

    async def list_by_listing(self, listing_id: int) -> list[IssueOut]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Issue).where(Issue.listing_id == listing_id).order_by(desc(Issue.reported_at))
            )
            issues = result.scalars().all()
            return [self._to_out(i) for i in issues]

    async def list_all(self, limit: int = 100) -> list[IssueOut]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Issue).order_by(desc(Issue.reported_at)).limit(limit)
            )
            issues = result.scalars().all()
            return [self._to_out(i) for i in issues]

    async def update(self, issue_id: int, data: IssueUpdate) -> IssueOut | None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Issue).where(Issue.id == issue_id))
            issue = result.scalar_one_or_none()
            if not issue:
                return None
            
            issue.status = data.status
            issue.landlord_response = data.landlord_response
            issue.resolution = data.resolution
            if data.status == "已解决" and not issue.resolved_at:
                issue.resolved_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(issue)
            return self._to_out(issue)

    async def delete(self, issue_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Issue).where(Issue.id == issue_id))
            issue = result.scalar_one_or_none()
            if not issue:
                return False
            await session.delete(issue)
            await session.commit()
            return True

    def _to_out(self, issue: Issue) -> IssueOut:
        return IssueOut(
            id=issue.id,
            listing_id=issue.listing_id,
            title=issue.title,
            category=issue.category,
            severity=issue.severity,
            status=issue.status,
            description=issue.description,
            landlord_response=issue.landlord_response,
            resolution=issue.resolution,
            reported_at=issue.reported_at,
            resolved_at=issue.resolved_at,
            evidence_ids=[int(x) for x in issue.evidence_ids.split(",") if x]
        )
