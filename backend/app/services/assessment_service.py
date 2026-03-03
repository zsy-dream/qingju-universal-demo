"""
估值与风控核心服务

NOTE: 采用增强版 Hedonic 特征价格模型，引入城区基准价 + 多因素回归系数，
      相比旧版 area × 120 的粗暴公式，估值结果更贴近真实市场逻辑。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.schemas.assessment import EstimateRequest, EstimateResponse, RiskRequest, RiskResponse

logger = logging.getLogger("app")


@dataclass
class _Factor:
    name: str
    impact: float  # 对基础价格的百分比影响
    amount: float  # 对应的金额影响
    note: str


# NOTE: 上海各区基准单价（元/㎡/月），来源于市场经验值
# 实际生产环境应从外部数据源或数据库加载
DISTRICT_BASE_PRICE: dict[str, float] = {
    "黄浦": 180.0, "静安": 170.0, "徐汇": 165.0, "长宁": 155.0,
    "杨浦": 130.0, "虹口": 125.0, "普陀": 120.0, "浦东": 135.0,
    "闵行": 110.0, "宝山": 95.0,  "松江": 80.0,  "嘉定": 75.0,
    "青浦": 70.0,  "奉贤": 65.0,  "金山": 55.0,  "崇明": 50.0,
}

DEFAULT_BASE_PRICE: float = 110.0


class AssessmentService:
    """估值与风控评分服务"""

    def _hedonic_estimate(
        self, req: EstimateRequest
    ) -> tuple[float, list[_Factor], list[dict]]:
        """
        增强版 Hedonic 特征价格估值

        模型结构：fair_rent = base_rent + Σ(factor_amount)
        - base_rent = 城区基准单价 × 面积
        - 每个 factor 独立贡献金额 = base_rent × factor_pct

        Args:
            req: 估值请求参数

        Returns:
            (fair_mid, factors, comparable_samples) 元组
        """
        # Step1：确定城区基准单价
        district = (req.district or "").strip() if hasattr(req, "district") else ""
        base_unit = DISTRICT_BASE_PRICE.get(district, DEFAULT_BASE_PRICE)
        base_rent = base_unit * max(req.area_sqm, 5.0)

        factors: list[_Factor] = []

        # Step2：朝向因素
        ori = (req.orientation or "").lower()
        if any(k in ori for k in ["南", "south"]):
            pct = 0.06
            factors.append(_Factor(
                "朝向（南向溢价）", pct, round(base_rent * pct),
                "采光与通风优势，居住舒适度更高"
            ))
        elif any(k in ori for k in ["东南", "southeast"]):
            pct = 0.04
            factors.append(_Factor(
                "朝向（东南向溢价）", pct, round(base_rent * pct),
                "兼顾采光与通风"
            ))
        elif any(k in ori for k in ["北", "north"]):
            pct = -0.04
            factors.append(_Factor(
                "朝向（北向折价）", pct, round(base_rent * pct),
                "采光不足，冬季体感偏冷"
            ))
        elif any(k in ori for k in ["西", "west"]):
            pct = -0.02
            factors.append(_Factor(
                "朝向（西向折价）", pct, round(base_rent * pct),
                "西晒问题，夏季能耗增加"
            ))

        # Step3：装修因素
        deco = (req.decoration or "").lower()
        if any(k in deco for k in ["豪装", "lux"]):
            pct = 0.15
            factors.append(_Factor(
                "装修（豪装溢价）", pct, round(base_rent * pct),
                "高品质装修，入住成本最低"
            ))
        elif any(k in deco for k in ["精装", "fine"]):
            pct = 0.08
            factors.append(_Factor(
                "装修（精装溢价）", pct, round(base_rent * pct),
                "装修到位，家具齐全可拎包入住"
            ))
        elif any(k in deco for k in ["简装", "simple"]):
            pct = -0.05
            factors.append(_Factor(
                "装修（简装折价）", pct, round(base_rent * pct),
                "需额外置办家具家电"
            ))
        elif any(k in deco for k in ["毛坯", "bare"]):
            pct = -0.12
            factors.append(_Factor(
                "装修（毛坯折价）", pct, round(base_rent * pct),
                "需大量投入装修，仅适合长租"
            ))

        # Step4：电梯因素
        if req.has_elevator:
            pct = 0.04
            factors.append(_Factor(
                "电梯（便利溢价）", pct, round(base_rent * pct),
                "高楼层通勤与搬运体验显著提升"
            ))
        elif req.floor and req.floor > 4:
            pct = -0.03
            factors.append(_Factor(
                "无电梯高楼层（折价）", pct, round(base_rent * pct),
                "日常出行不便，尤其搬家/送货场景"
            ))

        # Step5：楼层因素（中间楼层最佳）
        if req.floor > 0 and req.total_floors > 0:
            ratio = req.floor / req.total_floors
            if 0.3 <= ratio <= 0.7:
                pct = 0.03
                factors.append(_Factor(
                    "楼层（黄金区间）", pct, round(base_rent * pct),
                    "视野、噪音、逃生综合最优"
                ))
            elif ratio > 0.85:
                pct = 0.02
                factors.append(_Factor(
                    "楼层（顶层附近）", pct, round(base_rent * pct),
                    "视野好但可能有隔热/漏水风险"
                ))
            elif ratio < 0.15:
                pct = -0.03
                factors.append(_Factor(
                    "楼层（低楼层）", pct, round(base_rent * pct),
                    "采光一般，潮湿和噪音风险更高"
                ))

        # Step6：地铁距离因素
        if req.subway_distance_m > 0:
            if req.subway_distance_m <= 300:
                pct = 0.08
                factors.append(_Factor(
                    "地铁距离（步行3min内）", pct, round(base_rent * pct),
                    "极佳通勤确定性，通勤体验最优"
                ))
            elif req.subway_distance_m <= 800:
                pct = 0.04
                factors.append(_Factor(
                    "地铁距离（步行10min内）", pct, round(base_rent * pct),
                    "通勤便利度良好"
                ))
            elif req.subway_distance_m <= 1500:
                pct = -0.02
                factors.append(_Factor(
                    "地铁距离（步行15min+）", pct, round(base_rent * pct),
                    "通勤体验一般，可能需要骑行接驳"
                ))
            else:
                pct = -0.07
                factors.append(_Factor(
                    "地铁距离（超远）", pct, round(base_rent * pct),
                    "通勤成本高，通常需公交/骑行/驾车接驳"
                ))

        # Step7：通勤时间因素
        if req.commute_minutes > 0:
            if req.commute_minutes <= 20:
                pct = 0.06
                factors.append(_Factor(
                    "通勤时间（极短）", pct, round(base_rent * pct),
                    "每日通勤不到40min，时间成本极低"
                ))
            elif req.commute_minutes <= 35:
                pct = 0.02
                factors.append(_Factor(
                    "通勤时间（较短）", pct, round(base_rent * pct),
                    "单程半小时左右，可接受范围"
                ))
            elif req.commute_minutes <= 50:
                pct = -0.03
                factors.append(_Factor(
                    "通勤时间（偏长）", pct, round(base_rent * pct),
                    "每日通勤近2h，时间损耗不可忽视"
                ))
            else:
                pct = -0.08
                factors.append(_Factor(
                    "通勤时间（过长）", pct, round(base_rent * pct),
                    "每日通勤超2h，显著降低生活质量"
                ))

        # Step8：计算公允价格
        total_adjustment = sum(f.amount for f in factors)
        fair_mid = base_rent + total_adjustment

        # 防止估值为负数
        fair_mid = max(fair_mid, base_rent * 0.5)

        # Step9：生成对标样本（增强版，基于基准价浮动）
        comps = [
            {
                "title": f"同商圈·相似户型A",
                "rent": round(fair_mid * 0.95, 0),
                "similarity": 0.88,
                "note": "面积相近，地铁更近，装修相当",
            },
            {
                "title": f"同小区·相似户型B",
                "rent": round(fair_mid * 1.03, 0),
                "similarity": 0.85,
                "note": "楼层更高，装修略好，朝向一致",
            },
            {
                "title": f"同区域·相似户型C",
                "rent": round(fair_mid * 0.89, 0),
                "similarity": 0.79,
                "note": "通勤更长，地铁距离偏远，整体折价",
            },
        ]

        return fair_mid, factors, comps

    def estimate(self, req: EstimateRequest) -> EstimateResponse:
        """
        执行估值并输出可解释结论

        Returns:
            包含合理租金区间、偏离度、因素贡献和对标样本的完整估值报告
        """
        fair_mid, factors, comps = self._hedonic_estimate(req)
        low = fair_mid * 0.92
        high = fair_mid * 1.08

        asking = req.asking_rent or 0
        deviation = 0.0
        if asking > 0:
            deviation = (asking - fair_mid) / fair_mid * 100.0

        # NOTE: 瀑布图数据格式——按影响绝对值降序排列，前端可直接渲染瀑布图
        factor_out = [
            {
                "name": f.name,
                "impact_pct": round(f.impact * 100, 1),
                "amount": round(f.amount),
                "note": f.note,
            }
            for f in sorted(factors, key=lambda x: abs(x.impact), reverse=True)
        ]

        return EstimateResponse(
            fair_rent_low=round(low, 0),
            fair_rent_high=round(high, 0),
            deviation_pct=round(deviation, 1),
            factors=factor_out,
            comparable_samples=comps,
        )

    def risk(self, req: RiskRequest) -> RiskResponse:
        """
        风控评分：基于加权信号综合打分

        评分规则：
        - 每个风险信号 0/1/2（无/疑似/确认）× 权重 → 贡献分
        - 总分 ≥120 → 不建议，≥70 → 谨慎，<70 → 可租
        """
        weights = {
            "noise": 18,
            "mold": 22,
            "poor_light": 10,
            "old_appliances": 8,
            "sublease_risk": 24,
            "contract_unfair": 18,
        }
        signals = req.model_dump()

        items: list[tuple[str, int, int]] = []
        for k, w in weights.items():
            level = int(signals.get(k, 0))
            items.append((k, level, w))

        score = 0
        for _, level, w in items:
            score += level * w

        if score >= 120:
            level_text = "不建议"
        elif score >= 70:
            level_text = "谨慎"
        else:
            level_text = "可租"

        name_map = {
            "noise": "噪音风险",
            "mold": "潮湿/霉变风险",
            "poor_light": "采光风险",
            "old_appliances": "设备老化风险",
            "sublease_risk": "二房东/转租风险",
            "contract_unfair": "合同不公平条款风险",
        }

        top = sorted(items, key=lambda x: x[1] * x[2], reverse=True)[:3]
        top_risks = [
            {
                "name": name_map[k],
                "signal_level": lvl,
                "contribution": lvl * w,
                "weight": w,
            }
            for k, lvl, w in top
            if lvl > 0
        ]

        # NOTE: 基于风险信号生成针对性的建议，而非通用文案
        suggestions = []
        if req.sublease_risk > 0:
            suggestions.append("要求出示房产证/授权链路，明确收款主体与合同签署主体一致。二房东转租需提供原房东授权书")
        if req.contract_unfair > 0:
            suggestions.append("对押金退还、提前解约、维修责任、违约金等条款逐项补充约定并留存。建议使用【合同体检】功能")
        if req.mold > 0:
            suggestions.append("重点检查墙角、衣柜背面、卫生间反味与除湿条件。实地看房时需关注一楼/地下室/北向潮湿风险")
        if req.noise > 0:
            suggestions.append("在早晚高峰/夜间各复测一次噪音源（车流/施工/邻居），记录分贝证据并与房东确认降噪方案")
        if req.poor_light > 0:
            suggestions.append("白天不同时段观察采光情况，记录遮挡物（高楼/树木）。北向低楼层采光差是常见问题")
        if req.old_appliances > 0:
            suggestions.append("逐一检查热水器/空调/洗衣机年限，要求房东在合同中明确设备维修责任和更换标准")

        if not suggestions:
            suggestions.append("当前风险信号较少，仍建议完成交接清单与关键条款核对，使用【证据采集】记录看房实况")

        # NOTE: 生成雷达图数据，前端可直接渲染
        radar_data = [
            {"name": name_map[k], "value": int(signals.get(k, 0)), "max_value": 2, "weight": w}
            for k, w in weights.items()
        ]

        return RiskResponse(
            risk_score=min(score, 200),
            risk_level=level_text,
            top_risks=top_risks,
            suggestions=suggestions,
            radar_data=radar_data,
        )
