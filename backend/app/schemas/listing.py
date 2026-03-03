from pydantic import BaseModel, Field


class ListingBase(BaseModel):
    title: str = ""
    city: str = ""
    district: str = ""

    area_sqm: float = Field(default=0, ge=0)
    layout: str = ""
    floor: int = Field(default=0, ge=0)
    total_floors: int = Field(default=0, ge=0)
    orientation: str = ""
    decoration: str = ""
    has_elevator: bool = False

    subway_distance_m: float = Field(default=0, ge=0)
    commute_minutes: float = Field(default=0, ge=0)

    asking_rent: float = Field(default=0, ge=0)


class ListingCreate(ListingBase):
    pass


class ListingOut(ListingBase):
    id: int

    class Config:
        from_attributes = True
