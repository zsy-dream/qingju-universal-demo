from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceCreate


class EvidenceService:
    async def create_evidence(self, db: AsyncSession, data: EvidenceCreate) -> Evidence:
        obj = Evidence(
            listing_id=data.listing_id,
            risk_tag=data.risk_tag,
            source_type=data.source_type,
            note=data.note,
            content=data.content,
        )
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def list_by_listing(self, db: AsyncSession, listing_id: int) -> list[Evidence]:
        stmt = select(Evidence).where(Evidence.listing_id == listing_id).order_by(Evidence.id.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def delete_evidence(self, db: AsyncSession, evidence_id: int) -> bool:
        stmt = select(Evidence).where(Evidence.id == evidence_id)
        res = await db.execute(stmt)
        obj = res.scalar_one_or_none()
        if not obj:
            return False
        await db.delete(obj)
        await db.commit()
        return True
