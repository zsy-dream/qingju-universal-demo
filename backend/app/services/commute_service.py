"""
通勤-租金边际替代测算服务

NOTE: 基于经济学中的"边际替代率"概念，计算不同通勤圈对应的租金区间，
      并将通勤时间转化为经济成本，帮助用户做"该省钱还是省时间"的决策。
"""

from __future__ import annotations

import logging
from pydantic import BaseModel, Field

logger = logging.getLogger("app")


class CommuteAnalysisRequest(BaseModel):
    """通勤分析请求"""
    monthly_salary: float = Field(ge=0, description="月薪（元）")
    budget_max: float = Field(ge=0, description="最高月租预算（元）")
    work_days_per_month: int = Field(default=22, ge=1, le=31)


class CommuteZone(BaseModel):
    """通勤圈数据"""
    zone_name: str
    commute_min: int
    commute_max: int
    rent_median: float
    rent_range: str
    daily_commute_cost: float  # 通勤时间折现为日工资
    monthly_commute_cost: float
    net_monthly_cost: float  # 租金 + 通勤时间成本
    verdict: str


class CommuteAnalysisResponse(BaseModel):
    """通勤分析响应"""
    hourly_wage: float
    zones: list[CommuteZone]
    best_zone: str
    summary: str


# NOTE: 通勤圈划分标准，每个圈层对应的典型租金降幅系数
COMMUTE_ZONES = [
    {"name": "核心圈（≤20min）", "min": 0, "max": 20, "discount": 0.0},
    {"name": "近郊圈（20-35min）", "min": 20, "max": 35, "discount": 0.12},
    {"name": "中郊圈（35-50min）", "min": 35, "max": 50, "discount": 0.25},
    {"name": "远郊圈（50-70min）", "min": 50, "max": 70, "discount": 0.38},
    {"name": "极远圈（70min+）", "min": 70, "max": 90, "discount": 0.50},
]


class CommuteService:
    """通勤-租金替代测算核心服务"""

    def analyze(self, req: CommuteAnalysisRequest) -> CommuteAnalysisResponse:
        """
        计算不同通勤圈的租金-时间替代关系

        核心逻辑：
        1. 月薪 → 时薪
        2. 每个通勤圈的"时间通勤成本" = 单程平均时间 × 2 × 时薪 / 60 × 工作日数
        3. "净月度成本" = 租金中位数 + 通勤时间成本
        4. 净成本最低的圈层即为最优推荐
        """
        hourly_wage = req.monthly_salary / (req.work_days_per_month * 8)

        # 基准租金（核心圈中位数即预算上限的90%）
        base_rent = req.budget_max * 0.9

        zones: list[CommuteZone] = []

        for z in COMMUTE_ZONES:
            rent_median = round(base_rent * (1 - z["discount"]))
            rent_low = round(rent_median * 0.85)
            rent_high = round(rent_median * 1.15)

            avg_commute = (z["min"] + z["max"]) / 2
            # 每日通勤时间成本 = 单程分钟 × 2（往返） × 时薪 / 60
            daily_cost = round(avg_commute * 2 * hourly_wage / 60, 1)
            monthly_cost = round(daily_cost * req.work_days_per_month, 0)

            net = rent_median + monthly_cost

            # 判断性价比
            if net <= req.budget_max * 0.85:
                verdict = "高性价比"
            elif net <= req.budget_max * 1.05:
                verdict = "平衡区间"
            elif net <= req.budget_max * 1.3:
                verdict = "偏高"
            else:
                verdict = "不经济"

            zones.append(CommuteZone(
                zone_name=z["name"],
                commute_min=z["min"],
                commute_max=z["max"],
                rent_median=rent_median,
                rent_range=f"{rent_low}-{rent_high}",
                daily_commute_cost=daily_cost,
                monthly_commute_cost=monthly_cost,
                net_monthly_cost=net,
                verdict=verdict,
            ))

        # 找出净成本最低的圈层
        best = min(zones, key=lambda z: z.net_monthly_cost)

        summary = (
            f"基于月薪{int(req.monthly_salary)}元（时薪{hourly_wage:.1f}元），"
            f"推荐【{best.zone_name}】，"
            f"租金约{int(best.rent_median)}元 + 通勤时间成本约{int(best.monthly_commute_cost)}元/月，"
            f"总月度支出约{int(best.net_monthly_cost)}元，在预算{int(req.budget_max)}元内达到最佳平衡。"
        )

        return CommuteAnalysisResponse(
            hourly_wage=round(hourly_wage, 1),
            zones=zones,
            best_zone=best.zone_name,
            summary=summary,
        )
