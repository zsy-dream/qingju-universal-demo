from app.schemas.comparison import CompareRequest, ComparisonResponse, ComparisonFactor, ComparisonRecommendation
from app.services.listing_service import ListingService
from app.services.assessment_service import AssessmentService

listing_service = ListingService()
assessment_service = AssessmentService()


class ComparisonService:
    async def compare(self, req: CompareRequest, db) -> ComparisonResponse:
        # Fetch all listings
        listings = []
        for lid in req.listing_ids:
            listing = await listing_service.get_listing(db, lid)
            if listing:
                listings.append({
                    "id": listing.id,
                    "title": listing.title,
                    "city": listing.city,
                    "district": listing.district,
                    "asking_rent": listing.asking_rent,
                    "area_sqm": listing.area_sqm,
                    "commute_minutes": listing.commute_minutes,
                    "subway_distance_m": listing.subway_distance_m,
                    "orientation": listing.orientation,
                    "decoration": listing.decoration,
                    "has_elevator": listing.has_elevator,
                    "floor": listing.floor,
                    "total_floors": listing.total_floors
                })

        if len(listings) < 2:
            raise ValueError("需要至少2个有效房源进行对比")

        # Calculate metrics for each listing
        listing_metrics = []
        for lst in listings:
            # Calculate value score (lower price per sqm is better)
            price_per_sqm = lst["asking_rent"] / lst["area_sqm"] if lst["area_sqm"] > 0 else 9999
            
            # Calculate commute score (shorter is better)
            commute_score = max(0, 100 - lst["commute_minutes"] * 2)
            
            # Calculate location score (closer to subway is better)
            location_score = max(0, 100 - lst["subway_distance_m"] / 50)
            
            # Calculate facility score
            facility_score = 60
            if lst["has_elevator"]:
                facility_score += 10
            if lst["decoration"] in ["精装", "豪装"]:
                facility_score += 15
            elif lst["decoration"] in ["简装"]:
                facility_score += 5
            if lst["orientation"] in ["南", "东南", "西南"]:
                facility_score += 15
            
            # Floor score (middle floors better)
            floor_ratio = lst["floor"] / lst["total_floors"] if lst["total_floors"] > 0 else 0.5
            floor_score = 100 - abs(floor_ratio - 0.5) * 100
            
            # Total weighted score
            total_score = (
                price_per_sqm * 0.3 +  # lower is better (we'll invert later)
                commute_score * 0.25 +
                location_score * 0.2 +
                facility_score * 0.15 +
                floor_score * 0.1
            )
            
            listing_metrics.append({
                "listing_id": lst["id"],
                "listing": lst,
                "price_per_sqm": price_per_sqm,
                "commute_score": commute_score,
                "location_score": location_score,
                "facility_score": facility_score,
                "floor_score": floor_score,
                "total_score": total_score
            })

        # Normalize price score (invert so lower price = higher score)
        max_price = max(m["price_per_sqm"] for m in listing_metrics)
        min_price = min(m["price_per_sqm"] for m in listing_metrics)
        price_range = max_price - min_price if max_price > min_price else 1
        
        for m in listing_metrics:
            # Invert price score: (max - current) / range * 100
            price_score = (max_price - m["price_per_sqm"]) / price_range * 100 if price_range > 0 else 50
            # Recalculate total with proper price weighting
            m["total_score"] = (
                price_score * 0.3 +
                m["commute_score"] * 0.25 +
                m["location_score"] * 0.2 +
                m["facility_score"] * 0.15 +
                m["floor_score"] * 0.1
            )
            m["price_score"] = price_score

        # Sort by total score
        listing_metrics.sort(key=lambda x: x["total_score"], reverse=True)

        # Build factors comparison
        factors = [
            ComparisonFactor(
                name="性价比（每平米价格）",
                values=[{
                    "listing_id": m["listing_id"],
                    "value": f"{m['price_per_sqm']:.0f}元/㎡",
                    "score": round(m["price_score"], 0)
                } for m in listing_metrics],
                winner_id=listing_metrics[0]["listing_id"] if listing_metrics else None
            ),
            ComparisonFactor(
                name="通勤便利度",
                values=[{
                    "listing_id": m["listing_id"],
                    "value": f"{m['listing']['commute_minutes']}分钟",
                    "score": m["commute_score"]
                } for m in listing_metrics],
                winner_id=min(listing_metrics, key=lambda x: x["listing"]["commute_minutes"])["listing_id"] if listing_metrics else None
            ),
            ComparisonFactor(
                name="地铁距离",
                values=[{
                    "listing_id": m["listing_id"],
                    "value": f"{m['listing']['subway_distance_m']}米",
                    "score": m["location_score"]
                } for m in listing_metrics],
                winner_id=min(listing_metrics, key=lambda x: x["listing"]["subway_distance_m"])["listing_id"] if listing_metrics else None
            ),
            ComparisonFactor(
                name="房屋配置",
                values=[{
                    "listing_id": m["listing_id"],
                    "value": f"{m['listing']['decoration']}/{m['listing']['orientation']}/{'有电梯' if m['listing']['has_elevator'] else '无电梯'}",
                    "score": m["facility_score"]
                } for m in listing_metrics],
                winner_id=max(listing_metrics, key=lambda x: x["facility_score"])["listing_id"] if listing_metrics else None
            ),
            ComparisonFactor(
                name="楼层位置",
                values=[{
                    "listing_id": m["listing_id"],
                    "value": f"{m['listing']['floor']}/{m['listing']['total_floors']}层",
                    "score": round(m["floor_score"], 0)
                } for m in listing_metrics],
                winner_id=max(listing_metrics, key=lambda x: x["floor_score"])["listing_id"] if listing_metrics else None
            )
        ]

        # Build scores
        scores = []
        for m in listing_metrics:
            scores.append({
                "listing_id": m["listing_id"],
                "title": m["listing"]["title"],
                "asking_rent": m["listing"]["asking_rent"],
                "total_score": round(m["total_score"], 1),
                "breakdown": {
                    "价格得分": round(m["price_score"], 0),
                    "通勤得分": m["commute_score"],
                    "位置得分": m["location_score"],
                    "配置得分": m["facility_score"],
                    "楼层得分": round(m["floor_score"], 0)
                }
            })

        # Generate recommendation
        best = listing_metrics[0] if listing_metrics else None
        second = listing_metrics[1] if len(listing_metrics) > 1 else None
        
        # Find listings to avoid (bottom 2 or scores below 50)
        avoid_ids = []
        for m in listing_metrics[-2:]:
            if m["total_score"] < 50:
                avoid_ids.append(m["listing_id"])

        reason_parts = []
        if best:
            if best["price_score"] >= 80:
                reason_parts.append("价格优势明显")
            if best["commute_score"] >= 80:
                reason_parts.append("通勤便利")
            if best["facility_score"] >= 80:
                reason_parts.append("房屋配置较好")
            if not reason_parts:
                reason_parts.append("综合性价比最优")
        
        recommendation = ComparisonRecommendation(
            best_choice_id=best["listing_id"] if best else None,
            best_choice_reason="、".join(reason_parts) if reason_parts else "综合评分最高",
            second_choice_id=second["listing_id"] if second else None,
            avoid_ids=avoid_ids
        )

        # Generate summary
        summary_parts = [f"共对比{len(listings)}套房源。"]
        if best:
            summary_parts.append(f"推荐首选：【{best['listing']['title'][:20]}...】（综合得分{best['total_score']:.1f}分）。")
        if second:
            summary_parts.append(f"备选：【{second['listing']['title'][:20]}...】。")
        if avoid_ids:
            summary_parts.append(f"建议排除{len(avoid_ids)}套评分较低的房源。")
        summary_parts.append("请结合实地看房证据和风险评估结果做最终决策。")

        return ComparisonResponse(
            listings=[m["listing"] for m in listing_metrics],
            factors=factors,
            scores=scores,
            recommendation=recommendation,
            summary="".join(summary_parts)
        )
