from sqlalchemy.ext.asyncio import AsyncEngine

from app.models.base import Base

# Import models so they are registered on Base.metadata before create_all
# Import all models to ensure they are registered with Base.metadata
from app.models.listing import Listing
from app.models.evidence import Evidence
from app.models.issue import Issue


async def init_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
