from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing
from app.schemas.listing import ListingCreate


class ListingService:
    async def create_listing(self, db: AsyncSession, data: ListingCreate) -> Listing:
        obj = Listing(
            title=data.title,
            city=data.city,
            district=data.district,
            area_sqm=data.area_sqm,
            layout=data.layout,
            floor=data.floor,
            total_floors=data.total_floors,
            orientation=data.orientation,
            decoration=data.decoration,
            has_elevator=1 if data.has_elevator else 0,
            subway_distance_m=data.subway_distance_m,
            commute_minutes=data.commute_minutes,
            asking_rent=data.asking_rent,
        )
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def list_listings(self, db: AsyncSession, limit: int = 20) -> list[Listing]:
        stmt = select(Listing).order_by(Listing.id.desc()).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_listing(self, db: AsyncSession, listing_id: int) -> Listing | None:
        stmt = select(Listing).where(Listing.id == listing_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def delete_listing(self, db: AsyncSession, listing_id: int) -> bool:
        stmt = select(Listing).where(Listing.id == listing_id)
        res = await db.execute(stmt)
        obj = res.scalar_one_or_none()
        if not obj:
            return False
        await db.delete(obj)
        await db.commit()
        return True

    async def find_comparable(
        self, db: AsyncSession, area_sqm: float, district: str = "",
        orientation: str = "", exclude_id: int | None = None, limit: int = 3
    ) -> list[dict]:
        """
        从数据库中检索与目标房源相似的对标样本

        相似度算法：基于面积差、区域匹配和朝向匹配的加权得分

        Args:
            area_sqm: 目标房源面积
            district: 目标房源所在区域
            orientation: 目标房源朝向
            exclude_id: 需要排除的房源ID
            limit: 返回数量上限

        Returns:
            相似房源列表（含相似度得分）
        """
        stmt = select(Listing)
        if exclude_id:
            stmt = stmt.where(Listing.id != exclude_id)
        stmt = stmt.limit(50)
        res = await db.execute(stmt)
        all_listings = list(res.scalars().all())

        if not all_listings:
            return []

        scored: list[tuple[Listing, float]] = []
        for l in all_listings:
            sim = 0.0
            # 面积相似度（最高0.4）：差距越小越相似
            area_diff = abs(l.area_sqm - area_sqm)
            sim += max(0, 0.4 - area_diff * 0.01)

            # 区域匹配（最高0.35）
            if district and l.district == district:
                sim += 0.35
            elif district and l.city and district != l.district:
                sim += 0.10

            # 朝向匹配（最高0.25）
            if orientation and l.orientation:
                if orientation in l.orientation or l.orientation in orientation:
                    sim += 0.25
                elif "南" in orientation and "南" in l.orientation:
                    sim += 0.20

            scored.append((l, round(sim, 2)))

        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:limit]

        return [
            {
                "title": f"{l.district or l.city}·{l.layout or '相似户型'}",
                "rent": round(l.asking_rent, 0),
                "similarity": s,
                "note": f"面积{l.area_sqm}㎡·{l.orientation or ''}·{l.decoration or ''}",
            }
            for l, s in top
            if s > 0.05
        ]
