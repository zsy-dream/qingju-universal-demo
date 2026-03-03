from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(Integer, ForeignKey("listings.id", ondelete="CASCADE"))

    risk_tag: Mapped[str] = mapped_column(String(50), default="")  # e.g. noise/mold/contract
    source_type: Mapped[str] = mapped_column(String(30), default="user")  # user/landlord/other
    note: Mapped[str] = mapped_column(String(200), default="")

    # Store as text URL or base64 (for demo we keep URL/text)
    content: Mapped[str] = mapped_column(Text, default="")
