from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(200), default="")
    city: Mapped[str] = mapped_column(String(50), default="")
    district: Mapped[str] = mapped_column(String(80), default="")

    area_sqm: Mapped[float] = mapped_column(Float, default=0.0)
    layout: Mapped[str] = mapped_column(String(30), default="")
    floor: Mapped[int] = mapped_column(Integer, default=0)
    total_floors: Mapped[int] = mapped_column(Integer, default=0)
    orientation: Mapped[str] = mapped_column(String(20), default="")
    decoration: Mapped[str] = mapped_column(String(30), default="")
    has_elevator: Mapped[int] = mapped_column(Integer, default=0)  # 0/1

    subway_distance_m: Mapped[float] = mapped_column(Float, default=0.0)
    commute_minutes: Mapped[float] = mapped_column(Float, default=0.0)

    asking_rent: Mapped[float] = mapped_column(Float, default=0.0)
