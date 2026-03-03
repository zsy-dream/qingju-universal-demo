from datetime import datetime

from app.schemas.report import ReportRequest, ReportResponse, ReportSection


class ReportService:
    def generate_report(self, req: ReportRequest) -> ReportResponse:
        # Generate a comprehensive LLM-style report based on valuation and risk data
        # In a real implementation, this would call an LLM API
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Calculate confidence based on data completeness
        confidence = 70
        if req.evidence_count > 0:
            confidence += 10
        if len(req.factors) >= 3:
            confidence += 10
        if req.risk_score < 50:
            confidence += 5
        confidence = min(confidence, 95)
        
        # Build executive summary
        deviation_abs = abs(req.deviation_pct)
        price_assessment = ""
        if req.deviation_pct > 15:
            price_assessment = f"当前报价显著高于合理区间约{int(deviation_abs)}%，存在较大议价空间。"
        elif req.deviation_pct > 5:
            price_assessment = f"当前报价略高于合理区间约{int(deviation_abs)}%，存在一定议价空间。"
        elif req.deviation_pct < -10:
            price_assessment = f"当前报价低于合理区间约{int(deviation_abs)}%，性价比较高但需警惕潜在风险。"
        else:
            price_assessment = "当前报价处于合理区间内，价格相对公允。"
        
        risk_assessment = ""
        if req.risk_level == "不建议":
            risk_assessment = "⚠️ 综合风险评估为「不建议」，存在多项显著风险信号，建议谨慎决策。"
        elif req.risk_level == "谨慎":
            risk_assessment = "⚡ 综合风险评估为「谨慎」，存在部分风险信号，需在签约前完成核实与谈判。"
        else:
            risk_assessment = "✓ 综合风险评估为「可租」，风险信号较少，但仍建议完成标准核验流程。"
        
        executive_summary = f"""基于Hedonic估值模型与风险评分系统的综合分析：

{price_assessment}
合理租金区间：{int(req.fair_rent_low)}-{int(req.fair_rent_high)}元/月
当前报价：{int(req.asking_rent)}元/月

{risk_assessment}
风险评分：{req.risk_score}/200

建议行动：{"优先议价后再签约" if req.deviation_pct > 10 else "可正常推进，注意核查"}。{"需补充证据降低不确定性" if req.evidence_count < 3 else "证据充分，决策依据充足"}。"""

        # Build sections
        sections = []
        
        # Section 1: Valuation Analysis
        factor_analysis = ""
        if req.factors:
            positive = [f for f in req.factors if f.get("impact_pct", 0) > 0]
            negative = [f for f in req.factors if f.get("impact_pct", 0) < 0]
            
            if positive:
                factor_analysis += f"**溢价因素**：{'、'.join([f['name'] for f in positive[:3]])}。"
            if negative:
                factor_analysis += f"\n**折价因素**：{'、'.join([f['name'] for f in negative[:3]])}。"
        
        sections.append(ReportSection(
            title="一、估值分析",
            content=f"""基于房源特征与市场对标样本的估值分析：

{factor_analysis if factor_analysis else '该房源无明显溢价或折价因素，价格主要由基础面积与区位决定。'}

**核心结论**：
- 合理租金区间：{int(req.fair_rent_low)}-{int(req.fair_rent_high)}元/月（置信度{confidence}%）
- 当前报价偏离：{req.deviation_pct}%
- 每平米单价合理性：{"需关注" if abs(req.deviation_pct) > 20 else "基本合理"}""",
            highlights=["基于Hedonic特征分解", f"对标{len(req.factors)}个影响因素"]
        ))
        
        # Section 2: Risk Analysis
        risk_content = f"""综合风险评估结果：

**风险等级**：{req.risk_level}（评分：{req.risk_score}/200）

"""
        if req.top_risks:
            risk_content += "**主要风险贡献**：\n"
            for risk in req.top_risks[:3]:
                risk_content += f"- {risk.get('name', '未知风险')}：贡献{risk.get('contribution', 0)}分\n"
        else:
            risk_content += "**风险信号**：未检测到显著风险信号，保持常规警惕即可。\n"
        
        sections.append(ReportSection(
            title="二、风险分析",
            content=risk_content,
            highlights=[f"Top {len(req.top_risks)} 风险项", "量化风险评分"]
        ))
        
        # Section 3: Evidence Assessment
        evidence_status = f"已采集 **{req.evidence_count}** 项证据"
        if req.evidence_count == 0:
            evidence_status = "⚠️ 尚未采集任何证据，建议在签约前完成证据采集"
        elif req.evidence_count < 3:
            evidence_status += "，建议补充更多关键证据以降低决策不确定性"
        else:
            evidence_status += "，证据链较为完整"
        
        sections.append(ReportSection(
            title="三、证据评估",
            content=f"""{evidence_status}

证据化决策是降低信息不对称的核心手段。建议采集的关键证据包括：
- 房屋实景照片（噪音源、采光、设施状况）
- 合同条款截图（押金、维修、解约条款）
- 产权/授权证明（房东身份证、房产证或转租授权）
- 水电气表读数与缴费记录""",
            highlights=["可验证证据", "风险-证据绑定"]
        ))
        
        # Section 4: Negotiation Strategy
        negotiation_content = ""
        if req.deviation_pct > 10:
            target = int((req.fair_rent_low + req.fair_rent_high) / 2)
            negotiation_content = f"""**议价空间分析**：

当前报价显著高于合理区间，建议采取以下议价策略：

1. **锚定效应**：以{req.fair_rent_low}元为谈判起点，逐步让步至{target}元左右
2. **数据支撑**：展示Hedonic估值区间与对标样本，增强说服力
3. **风险对冲**：如价格无法降低，要求房东书面承诺维修责任与提前解约条款
4. **替代方案**：提出免物业费、降低押金比例等替代让步方案"""
        elif req.deviation_pct < -10:
            negotiation_content = """**议价空间分析**：

当前报价低于市场合理区间，建议：

1. 快速锁定房源，避免被他人抢先
2. 在签约前完成充分的风险核查（低价可能伴随隐藏问题）
3. 可适度提出小幅议价（2-3%）测试房东反应
4. 重点关注合同条款的公平性"""
        else:
            negotiation_content = """**议价空间分析**：

当前报价处于合理区间，议价空间有限但仍可尝试：

1. 争取免租期或物业费减免
2. 要求房东承担维修责任（书面约定）
3. 协商押金退还条件与流程
4. 如房源优质且竞争激烈，可考虑接受报价快速签约"""
        
        sections.append(ReportSection(
            title="四、议价策略",
            content=negotiation_content,
            highlights=["可执行话术", "让步策略", "底线设定"]
        ))
        
        # Build action items
        action_items = [
            f"{"优先议价：目标价位" + str(int((req.fair_rent_low + req.fair_rent_high) / 2)) + "元" if req.deviation_pct > 10 else "接受报价或小幅议价"}",
            f"{"核查Top风险项" if req.top_risks else "完成标准风险核验"}：{', '.join([r.get('name', '') for r in req.top_risks[:2]]) if req.top_risks else '噪音、采光、合同条款'}",
            f"{"补充证据（当前不足）" if req.evidence_count < 3 else "整理证据包"}：至少采集3-5项关键证据",
            "合同体检：重点核查押金退还、维修责任、提前解约条款",
            "决策时限：基于通勤与到岗时间，设定最终决策 deadline"
        ]
        
        return ReportResponse(
            report_title=f"《{req.title or '房源'}》租房决策分析报告",
            generated_at=now,
            executive_summary=executive_summary,
            sections=sections,
            action_items=action_items,
            confidence_score=confidence
        )
