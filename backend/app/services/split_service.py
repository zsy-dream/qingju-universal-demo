"""
合租公平分摊计算服务

NOTE: 基于加权面积法——在纯面积基础上叠加独卫、阳台、采光、朝向等权重，
      输出每间房的"等效面积占比"和对应的月租分摊金额。
"""

from __future__ import annotations

import logging
from pydantic import BaseModel, Field

logger = logging.getLogger("app")


class RoomInput(BaseModel):
    """单间房信息"""
    name: str = Field(description="房间名称，如'主卧A'")
    area_sqm: float = Field(ge=1, description="房间面积（㎡）")
    has_private_bathroom: bool = Field(default=False, description="是否有独卫")
    has_balcony: bool = Field(default=False, description="是否有阳台")
    has_good_light: bool = Field(default=True, description="采光是否良好")
    orientation: str = Field(default="", description="朝向")


class SplitRequest(BaseModel):
    """分摊请求"""
    total_rent: float = Field(ge=0, description="总月租金（元）")
    rooms: list[RoomInput] = Field(min_length=2, max_length=8, description="房间列表")


class RoomResult(BaseModel):
    """单间分摊结果"""
    name: str
    area_sqm: float
    weighted_area: float
    weight_ratio: float
    monthly_rent: float
    weight_details: list[dict]


class SplitResponse(BaseModel):
    """分摊结果"""
    total_rent: float
    rooms: list[RoomResult]
    formula_explanation: str


class SplitService:
    """合租分摊计算核心服务"""

    # NOTE: 各权重因子的溢价比例，基于合租经验值设定
    WEIGHT_CONFIG = {
        "private_bathroom": 0.20,  # 独卫加权20%
        "balcony": 0.10,           # 阳台加权10%
        "good_light": 0.05,        # 采光良好加权5%
        "south_facing": 0.08,      # 朝南加权8%
    }

    def calculate_split(self, req: SplitRequest) -> SplitResponse:
        """
        执行合租分摊计算

        算法：weighted_area = area × (1 + Σ权重因子)
        每间月租 = total_rent × (weighted_area / Σall_weighted_area)

        Args:
            req: 包含总租金和各房间信息的请求

        Returns:
            分摊结果，包含每间加权面积、占比和月租
        """
        room_results: list[RoomResult] = []
        total_weighted = 0.0

        for room in req.rooms:
            multiplier = 1.0
            details: list[dict] = []

            if room.has_private_bathroom:
                multiplier += self.WEIGHT_CONFIG["private_bathroom"]
                details.append({"factor": "独卫", "bonus": f"+{int(self.WEIGHT_CONFIG['private_bathroom'] * 100)}%"})

            if room.has_balcony:
                multiplier += self.WEIGHT_CONFIG["balcony"]
                details.append({"factor": "阳台", "bonus": f"+{int(self.WEIGHT_CONFIG['balcony'] * 100)}%"})

            if room.has_good_light:
                multiplier += self.WEIGHT_CONFIG["good_light"]
                details.append({"factor": "采光良好", "bonus": f"+{int(self.WEIGHT_CONFIG['good_light'] * 100)}%"})

            ori = (room.orientation or "").lower()
            if any(k in ori for k in ["南", "south"]):
                multiplier += self.WEIGHT_CONFIG["south_facing"]
                details.append({"factor": "朝南", "bonus": f"+{int(self.WEIGHT_CONFIG['south_facing'] * 100)}%"})

            weighted_area = room.area_sqm * multiplier
            total_weighted += weighted_area

            room_results.append(RoomResult(
                name=room.name,
                area_sqm=room.area_sqm,
                weighted_area=round(weighted_area, 2),
                weight_ratio=0.0,
                monthly_rent=0.0,
                weight_details=details,
            ))

        # 计算占比和月租
        for r in room_results:
            r.weight_ratio = round(r.weighted_area / total_weighted, 4)
            r.monthly_rent = round(req.total_rent * r.weight_ratio, 0)

        formula = (
            "加权面积 = 实际面积 × (1"
            f" + 独卫{int(self.WEIGHT_CONFIG['private_bathroom']*100)}%"
            f" + 阳台{int(self.WEIGHT_CONFIG['balcony']*100)}%"
            f" + 采光{int(self.WEIGHT_CONFIG['good_light']*100)}%"
            f" + 朝南{int(self.WEIGHT_CONFIG['south_facing']*100)}%"
            ")；月租 = 总租 × (加权面积占比)"
        )

        return SplitResponse(
            total_rent=req.total_rent,
            rooms=room_results,
            formula_explanation=formula,
        )
