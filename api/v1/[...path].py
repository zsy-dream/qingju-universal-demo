from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Qingju Demo API", version="demo")


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


# -------------------------
# Demo in-memory data store
# -------------------------

LISTINGS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "城西地铁口｜精装一居｜拎包入住",
        "city": "杭州",
        "district": "西湖",
        "layout": "1室1厅",
        "asking_rent": 4200,
        "area_sqm": 32,
        "floor": 8,
        "total_floors": 18,
        "orientation": "南",
        "decoration": "精装",
        "has_elevator": True,
        "subway_distance_m": 350,
        "commute_minutes": 32,
        "created_at": _now_iso(),
        "is_archived": False,
    },
    {
        "id": 2,
        "title": "滨江｜采光好｜朝南次卧（可短租）",
        "city": "杭州",
        "district": "滨江",
        "layout": "合租次卧",
        "asking_rent": 2600,
        "area_sqm": 14,
        "floor": 10,
        "total_floors": 26,
        "orientation": "南",
        "decoration": "简装",
        "has_elevator": True,
        "subway_distance_m": 800,
        "commute_minutes": 28,
        "created_at": _now_iso(),
        "is_archived": False,
    },
    {
        "id": 3,
        "title": "下沙大学城｜通勤40min｜性价比整租一室",
        "city": "杭州",
        "district": "钱塘",
        "layout": "1室0厅",
        "asking_rent": 2300,
        "area_sqm": 28,
        "floor": 6,
        "total_floors": 11,
        "orientation": "东",
        "decoration": "简装",
        "has_elevator": False,
        "subway_distance_m": 1200,
        "commute_minutes": 45,
        "created_at": _now_iso(),
        "is_archived": False,
    },
]

EVIDENCE: List[Dict[str, Any]] = []
ISSUES: List[Dict[str, Any]] = []


# -------------------------
# Schemas (minimal, demo)
# -------------------------


class ListingCreate(BaseModel):
    title: str
    city: str = "杭州"
    district: str = ""
    layout: str = ""
    asking_rent: int
    area_sqm: float
    floor: int = 1
    total_floors: int = 1
    orientation: str = "南"
    decoration: str = "简装"
    has_elevator: bool = False
    subway_distance_m: int = 1000
    commute_minutes: int = 45


class EvidenceCreate(BaseModel):
    listing_id: int
    title: str = "证据"
    source_type: str = "照片"
    tags: List[str] = Field(default_factory=list)
    notes: str = ""
    file_url: Optional[str] = None


class IssueCreate(BaseModel):
    listing_id: int
    title: str
    category: str = "维修"
    severity: str = "一般"
    description: str
    evidence_ids: List[int] = Field(default_factory=list)


class IssueUpdate(BaseModel):
    status: Optional[str] = None
    landlord_response: Optional[str] = None
    resolution: Optional[str] = None


class ComparisonPayload(BaseModel):
    listing_ids: List[int]


class SplitRoom(BaseModel):
    name: str
    area_sqm: float
    has_private_bathroom: bool = False
    has_balcony: bool = False
    has_good_light: bool = True
    orientation: str = ""


class SplitPayload(BaseModel):
    total_rent: float
    rooms: List[SplitRoom]


# -------------------------
# Helpers
# -------------------------


def _find_listing(listing_id: int) -> Dict[str, Any]:
    for l in LISTINGS:
        if l["id"] == listing_id:
            return l
    raise HTTPException(status_code=404, detail="房源不存在")


def _estimate_fair_rent(l: Dict[str, Any]) -> Dict[str, Any]:
    base_per_sqm = 120 if l.get("city") == "杭州" else 100
    deco_bonus = {"毛坯": -8, "简装": 0, "精装": 12}.get(l.get("decoration"), 0)
    elevator_bonus = 5 if l.get("has_elevator") else 0
    subway_penalty = min(max(l.get("subway_distance_m", 1000) - 400, 0) / 200, 6) * 3
    commute_penalty = min(max(l.get("commute_minutes", 45) - 35, 0) / 10, 6) * 4

    per_sqm = base_per_sqm + deco_bonus + elevator_bonus - subway_penalty - commute_penalty
    per_sqm = max(per_sqm, 60)

    fair_mid = per_sqm * float(l.get("area_sqm", 20))
    fair_low = int(round(fair_mid * 0.92))
    fair_high = int(round(fair_mid * 1.08))

    asking = float(l.get("asking_rent", fair_mid))
    deviation_pct = 0.0 if fair_mid == 0 else (asking - fair_mid) / fair_mid * 100

    factors = [
        {"name": "地段基准", "value": int(round(base_per_sqm * float(l.get("area_sqm", 20))))},
        {"name": "装修溢价", "value": int(round(deco_bonus * float(l.get("area_sqm", 20))))},
        {"name": "电梯溢价", "value": int(round(elevator_bonus * float(l.get("area_sqm", 20))))},
        {"name": "地铁距离折价", "value": -int(round(subway_penalty * float(l.get("area_sqm", 20))))},
        {"name": "通勤折价", "value": -int(round(commute_penalty * float(l.get("area_sqm", 20))))},
    ]

    return {
        "fair_rent_low": fair_low,
        "fair_rent_high": fair_high,
        "fair_rent_mid": int(round(fair_mid)),
        "deviation_pct": round(deviation_pct, 1),
        "factors": factors,
    }


# -------------------------
# API v1
# -------------------------


@app.get("/api/v1/dashboard/summary")
async def dashboard_summary() -> Dict[str, Any]:
    latest = sorted(LISTINGS, key=lambda x: x.get("id", 0), reverse=True)[:12]
    if not latest:
        return {"listing_count": 0, "avg_deviation_pct": 0, "high_risk_count": 0, "latest_listings": []}

    devs = []
    latest_out = []
    high_risk = 0

    for l in latest:
        est = _estimate_fair_rent(l)
        devs.append(est["deviation_pct"])

        risk_score = 0
        if l.get("commute_minutes", 0) >= 50:
            risk_score += 60
        if l.get("subway_distance_m", 0) >= 1200:
            risk_score += 50
        if not l.get("has_elevator") and l.get("floor", 1) >= 6:
            risk_score += 40
        if risk_score >= 90:
            high_risk += 1

        latest_out.append(
            {
                "id": l["id"],
                "title": l["title"],
                "asking_rent": l["asking_rent"],
                "fair_low": est["fair_rent_low"],
                "fair_high": est["fair_rent_high"],
                "deviation_pct": est["deviation_pct"],
            }
        )

    avg = sum(devs) / max(len(devs), 1)
    return {
        "listing_count": len(LISTINGS),
        "avg_deviation_pct": round(avg, 1),
        "high_risk_count": high_risk,
        "latest_listings": list(reversed(latest_out)),
    }


@app.get("/api/v1/listings/")
async def list_listings(limit: int = 20) -> List[Dict[str, Any]]:
    return sorted(LISTINGS, key=lambda x: x.get("id", 0), reverse=True)[: max(1, min(limit, 200))]


@app.post("/api/v1/listings/")
async def create_listing(payload: ListingCreate) -> Dict[str, Any]:
    new_id = (max([l["id"] for l in LISTINGS]) + 1) if LISTINGS else 1
    l = payload.model_dump()
    l.update({"id": new_id, "created_at": _now_iso(), "is_archived": False})
    LISTINGS.append(l)
    return l


@app.get("/api/v1/listings/{listing_id}")
async def get_listing(listing_id: int) -> Dict[str, Any]:
    return _find_listing(listing_id)


@app.delete("/api/v1/listings/{listing_id}")
async def delete_listing(listing_id: int) -> Dict[str, Any]:
    global LISTINGS
    _find_listing(listing_id)
    LISTINGS = [l for l in LISTINGS if l["id"] != listing_id]
    return {"ok": True}


@app.post("/api/v1/assessments/estimate")
async def assessments_estimate(payload: Dict[str, Any]) -> Dict[str, Any]:
    l = {
        "city": payload.get("city", "杭州"),
        "asking_rent": payload.get("asking_rent", 0),
        "area_sqm": payload.get("area_sqm", 20),
        "floor": payload.get("floor", 1),
        "total_floors": payload.get("total_floors", 1),
        "orientation": payload.get("orientation", "南"),
        "decoration": payload.get("decoration", "简装"),
        "has_elevator": payload.get("has_elevator", False),
        "subway_distance_m": payload.get("subway_distance_m", 1000),
        "commute_minutes": payload.get("commute_minutes", 45),
    }
    est = _estimate_fair_rent(l)
    return {
        "fair_rent_low": est["fair_rent_low"],
        "fair_rent_high": est["fair_rent_high"],
        "fair_rent_mid": est["fair_rent_mid"],
        "deviation_pct": est["deviation_pct"],
        "factors": est["factors"],
        "benchmarks": [
            {"name": "同区同户型A", "rent": int(est["fair_rent_mid"] * 0.95)},
            {"name": "同区同户型B", "rent": int(est["fair_rent_mid"] * 1.02)},
            {"name": "同区同户型C", "rent": int(est["fair_rent_mid"] * 1.08)},
        ],
    }


@app.post("/api/v1/assessments/risk")
async def assessments_risk(payload: Dict[str, Any]) -> Dict[str, Any]:
    weights = {
        "noise": 25,
        "mold": 35,
        "poor_light": 25,
        "old_appliances": 20,
        "sublease_risk": 45,
        "contract_unfair": 50,
    }

    score = 0
    items = []
    for k, w in weights.items():
        lvl = int(payload.get(k, 0) or 0)
        score += lvl * w
        items.append({"key": k, "level": lvl, "weight": w})

    if score >= 120:
        level = "慎租"
        advice = ["建议要求补充证据/整改后再决定", "对合同条款逐条修改并留痕", "必要时考虑备选房源"]
    elif score >= 70:
        level = "可租但需注意"
        advice = ["看房时重点复核高权重风险项", "拍照录像留证", "约定维修与押金退还时限"]
    else:
        level = "可租"
        advice = ["整体风险可控，仍建议保留证据链", "签约前做合同体检"]

    top = sorted(items, key=lambda x: x["level"] * x["weight"], reverse=True)[:3]
    name_map = {
        "noise": "噪音",
        "mold": "潮湿/霉变",
        "poor_light": "采光",
        "old_appliances": "设备老化",
        "sublease_risk": "二房东/转租",
        "contract_unfair": "合同不公平",
    }

    return {
        "risk_score": score,
        "risk_level": level,
        "suggestions": advice,
        "top_risks": [
            {
                "name": name_map.get(x["key"], x["key"]),
                "signal_level": x["level"],
                "weight": x["weight"],
                "contribution": x["level"] * x["weight"],
            }
            for x in top
            if x["level"] > 0
        ],
    }


@app.post("/api/v1/negotiation/script")
async def negotiation_script(payload: Dict[str, Any]) -> Dict[str, Any]:
    asking = float(payload.get("asking_rent", 0) or 0)
    fair = float(payload.get("fair_rent_mid", asking) or asking)
    dev = 0 if fair == 0 else (asking - fair) / fair * 100
    target = int(round(min(asking, fair * 0.98)))

    script = {
        "opening": "您好，我对这套房子很感兴趣，想基于客观信息再确认一下价格空间。",
        "evidence": [
            f"我们做了同片区对标，合理区间大致在 {int(fair*0.92)}~{int(fair*1.08)} 元/月。",
            f"当前报价偏离约 {round(dev,1)}%，希望能有更合理的成交价。",
        ],
        "proposal": f"如果可以的话，我希望按 {target} 元/月尽快定下来，今天就能走流程。",
        "fallback": "如果价格不方便调整，也可以考虑免中介费/减免押金/赠送保洁等方式补偿。",
        "closing": "感谢理解，我们也希望长期稳定居住，减少双方成本。",
    }

    return {"script": script, "target_rent": target, "deviation_pct": round(dev, 1)}


@app.post("/api/v1/report/generate")
async def report_generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    listing_id = payload.get("listing_id")
    l = _find_listing(int(listing_id)) if listing_id else None

    title = f"房源综合评估报告（演示版）#{l['id']}" if l else "房源综合评估报告（演示版）"
    summary = "本报告为演示模式生成，包含估值偏离、风险信号、对比建议与议价话术等模块，适用于路演展示。"

    return {
        "title": title,
        "generated_at": _now_iso(),
        "executive_summary": summary,
        "sections": [
            {"title": "估值结论", "content": "给出合理租金区间与偏离率，并解释主要特征贡献。"},
            {"title": "风险结论", "content": "基于噪音/潮湿/采光/合同等信号给出可解释的风险等级与行动建议。"},
            {"title": "对比与建议", "content": "对候选房源进行多维对比，输出首选/备选/排除建议。"},
            {"title": "议价要点", "content": "提供可直接复制给房东/中介的议价脚本与备选策略。"},
        ],
        "action_items": [
            "看房全程拍照录像，补齐证据链",
            "合同条款逐条确认并要求书面补充",
            "若偏离过高，优先谈价或选择备选房源",
        ],
    }


@app.post("/api/v1/contract/inspect")
async def contract_inspect(payload: Dict[str, Any]) -> Dict[str, Any]:
    quick = bool(payload.get("quick_mode", True))
    if not quick and not payload.get("user_clauses"):
        raise HTTPException(status_code=400, detail="user_clauses 不能为空")

    checked = [
        {
            "clause_name": "押金退还",
            "severity": "critical",
            "description": "押金退还条件与时限",
            "current_text": "退房时无息退还，如有损坏从押金中扣除",
            "suggested_alternative": "费用结清后7个工作日内退还；扣除需清单与双方签字。",
            "why_it_matters": "押金纠纷高发，需要明确边界与时限。",
        },
        {
            "clause_name": "提前解约",
            "severity": "warning",
            "description": "提前退租违约金",
            "current_text": "提前解约需支付2个月租金",
            "suggested_alternative": "提前30日通知，违约金不超过1个月。",
            "why_it_matters": "过高违约金可能显失公平。",
        },
    ]

    return {
        "overall_risk": "medium",
        "critical_count": 1,
        "warning_count": 1,
        "checked_clauses": checked,
        "red_flags": ["【押金退还】存在高风险条款，必须修改"],
        "general_advice": ["签约前逐条核对合同与口头承诺是否一致", "水电气表读数、家具清单拍照签字"],
    }


@app.post("/api/v1/evidence/")
async def create_evidence(payload: EvidenceCreate) -> Dict[str, Any]:
    new_id = (max([e["id"] for e in EVIDENCE]) + 1) if EVIDENCE else 1
    e = payload.model_dump()
    e.update({"id": new_id, "created_at": _now_iso()})
    EVIDENCE.append(e)
    return e


@app.get("/api/v1/evidence/")
async def list_evidence(listing_id: Optional[int] = None) -> List[Dict[str, Any]]:
    if listing_id is None:
        return list(reversed(EVIDENCE))
    return [e for e in reversed(EVIDENCE) if int(e.get("listing_id", 0)) == int(listing_id)]


@app.delete("/api/v1/evidence/{evidence_id}")
async def delete_evidence(evidence_id: int) -> Dict[str, Any]:
    global EVIDENCE
    EVIDENCE = [e for e in EVIDENCE if e.get("id") != evidence_id]
    return {"ok": True}


@app.post("/api/v1/issues/")
async def create_issue(payload: IssueCreate) -> Dict[str, Any]:
    new_id = (max([i["id"] for i in ISSUES]) + 1) if ISSUES else 1
    issue = payload.model_dump()
    issue.update(
        {
            "id": new_id,
            "status": "处理中",
            "reported_at": _now_iso(),
            "landlord_response": "",
            "resolution": "",
        }
    )
    ISSUES.append(issue)
    return issue


@app.get("/api/v1/issues/")
async def list_issues(listing_id: Optional[int] = None) -> List[Dict[str, Any]]:
    items = list(reversed(ISSUES))
    if listing_id is None:
        return items
    return [i for i in items if int(i.get("listing_id", 0)) == int(listing_id)]


@app.put("/api/v1/issues/{issue_id}")
async def update_issue(issue_id: int, payload: IssueUpdate) -> Dict[str, Any]:
    for i in ISSUES:
        if i.get("id") == issue_id:
            data = payload.model_dump(exclude_unset=True)
            i.update({k: v for k, v in data.items() if v is not None})
            return i
    raise HTTPException(status_code=404, detail="记录不存在")


@app.delete("/api/v1/issues/{issue_id}")
async def delete_issue(issue_id: int) -> Dict[str, Any]:
    global ISSUES
    ISSUES = [i for i in ISSUES if i.get("id") != issue_id]
    return {"ok": True}


@app.post("/api/v1/comparison/compare")
async def comparison_compare(payload: ComparisonPayload) -> Dict[str, Any]:
    ids = payload.listing_ids
    if len(ids) < 2:
        raise HTTPException(status_code=400, detail="至少选择2套房源")

    listings = [_find_listing(int(i)) for i in ids]

    scores = []
    for l in listings:
        est = _estimate_fair_rent(l)
        price_score = max(0, 100 - max(0, est["deviation_pct"]) * 1.2)
        commute_score = max(0, 100 - max(0, l.get("commute_minutes", 45) - 25) * 2)
        subway_score = max(0, 100 - max(0, l.get("subway_distance_m", 800) - 300) / 10)
        config_score = 70 + (10 if l.get("has_elevator") else 0) + (10 if l.get("decoration") == "精装" else 0)
        config_score = min(config_score, 100)

        breakdown = {
            "价格": int(round(price_score)),
            "通勤": int(round(commute_score)),
            "地铁": int(round(subway_score)),
            "配置": int(round(config_score)),
        }
        total = sum(breakdown.values()) / len(breakdown)
        scores.append(
            {
                "listing_id": l["id"],
                "title": l["title"],
                "asking_rent": l["asking_rent"],
                "total_score": float(round(total, 1)),
                "breakdown": breakdown,
            }
        )

    scores_sorted = sorted(scores, key=lambda x: x["total_score"], reverse=True)
    best = scores_sorted[0]["listing_id"]
    second = scores_sorted[1]["listing_id"] if len(scores_sorted) > 1 else None
    avoid = [s["listing_id"] for s in scores_sorted[-1:]]

    factors = []
    for name in ["价格", "通勤", "地铁", "配置"]:
        values = []
        winner = None
        best_score = -1
        for s in scores:
            v = s["breakdown"][name]
            values.append({"listing_id": s["listing_id"], "value": f"{v}", "score": v})
            if v > best_score:
                best_score = v
                winner = s["listing_id"]
        factors.append({"name": name, "winner_id": winner, "values": values})

    return {
        "scores": scores,
        "factors": factors,
        "recommendation": {
            "best_choice_id": best,
            "second_choice_id": second,
            "avoid_ids": avoid,
            "best_choice_reason": "综合得分最高，价格偏离较小且通勤/地铁条件更均衡。",
        },
    }


@app.post("/api/v1/split/calculate")
async def split_calculate(payload: SplitPayload) -> Dict[str, Any]:
    total = float(payload.total_rent)
    if total <= 0:
        raise HTTPException(status_code=400, detail="total_rent 必须大于0")

    weighted = []
    for r in payload.rooms:
        w = float(r.area_sqm)
        details = []
        if r.has_private_bathroom:
            details.append({"factor": "独卫", "bonus": "+20%"})
            w *= 1.2
        if r.has_balcony:
            details.append({"factor": "阳台", "bonus": "+10%"})
            w *= 1.1
        if r.has_good_light:
            details.append({"factor": "采光", "bonus": "+5%"})
            w *= 1.05

        weighted.append({"name": r.name, "area_sqm": r.area_sqm, "weighted_area": w, "weight_details": details})

    sum_w = sum(x["weighted_area"] for x in weighted) or 1.0
    rooms_out = []
    for x in weighted:
        ratio = x["weighted_area"] / sum_w
        rent = int(round(total * ratio))
        rooms_out.append(
            {
                "name": x["name"],
                "area_sqm": x["area_sqm"],
                "weighted_area": round(x["weighted_area"], 2),
                "weight_ratio": ratio,
                "monthly_rent": rent,
                "weight_details": x["weight_details"],
            }
        )

    return {
        "formula_explanation": "演示版：加权面积法 = 面积 × (独卫1.2) × (阳台1.1) × (采光1.05)，按加权占比分摊总租金。",
        "rooms": rooms_out,
    }


@app.post("/api/v1/commute/analyze")
async def commute_analyze(payload: Dict[str, Any]) -> Dict[str, Any]:
    salary = float(payload.get("monthly_salary", 12000) or 12000)
    budget = float(payload.get("monthly_rent_budget", 3500) or 3500)
    base_commute = float(payload.get("current_commute_minutes", 35) or 35)

    hourly = salary / 21.75 / 8
    time_value_per_min = hourly / 60

    rings = []
    for minutes in [20, 30, 40, 50, 60]:
        extra = max(0.0, minutes - base_commute)
        extra_cost = extra * 2 * 22 * time_value_per_min
        rent_saving = max(0.0, (minutes - 20) * 60)
        net = rent_saving - extra_cost
        rings.append(
            {
                "commute_minutes": minutes,
                "rent_saving": int(round(rent_saving)),
                "time_cost": int(round(extra_cost)),
                "net_benefit": int(round(net)),
                "suggestion": "推荐" if net > 0 else "不推荐",
            }
        )

    return {
        "hourly_wage": round(hourly, 1),
        "budget": int(round(budget)),
        "rings": rings,
        "summary": "演示版：将通勤时间折现为机会成本，比较不同通勤圈的租金节省与时间成本。",
    }
