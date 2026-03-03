from app.schemas.contract import ContractInspectionRequest, ContractInspectionResponse


class ContractService:
    # Built-in clause templates for quick inspection
    STANDARD_CLAUSES = [
        {
            "clause_name": "押金退还",
            "severity": "critical",
            "description": "押金退还条件与时限",
            "current_text": "退房时无息退还，如有损坏从押金中扣除",
            "suggested_alternative": "正常磨损除外，房屋无结构性损坏且费用结清后，退房后7个工作日内全额退还。押金扣除需有书面清单与双方签字确认。",
            "why_it_matters": "模糊条款是押金纠纷的主要来源。必须明确'正常磨损'范围与时限。"
        },
        {
            "clause_name": "提前解约",
            "severity": "critical",
            "description": "租客提前退租的条件与违约金",
            "current_text": "租客提前解约需支付2个月租金作为违约金",
            "suggested_alternative": "租客提前30日书面通知，支付1个月租金作为违约金；如房东在同期内找到新租客，违约金可降至半个月。",
            "why_it_matters": "过高的违约金限制了租客的流动性，也可能被法院认定为显失公平。"
        },
        {
            "clause_name": "维修责任",
            "severity": "warning",
            "description": "房屋维修责任归属",
            "current_text": "房屋及设施的日常维修由租客负责",
            "suggested_alternative": "自然老化与结构性损坏由房东负责；人为损坏由租客负责。电器故障24小时内通知，房东3日内修复或更换。",
            "why_it_matters": "将全部维修责任推给租客不合理，应区分自然老化与人为损坏。"
        },
        {
            "clause_name": "转租/分租",
            "severity": "warning",
            "description": "是否允许转租或分租",
            "current_text": "未经房东书面同意，不得转租或分租",
            "suggested_alternative": "租客因工作变动需转租，应提前30日书面通知房东，房东应在7日内回复；无正当理由不得拒绝。",
            "why_it_matters": "过于严格的转租限制可能违反当地租赁法规，应保留合理转租权利。"
        },
        {
            "clause_name": "租金调整",
            "severity": "warning",
            "description": "续租时租金调整机制",
            "current_text": "续租时房东有权根据市场情况调整租金",
            "suggested_alternative": "续租时租金调整幅度不超过上年度CPI+3%，且需提前60日书面通知。",
            "why_it_matters": "无限涨租权让租客面临不确定性，应设定合理涨幅上限与提前通知期。"
        },
        {
            "clause_name": "房屋用途",
            "severity": "normal",
            "description": "房屋使用用途限制",
            "current_text": "仅限居住使用，不得用于商业或其他用途",
            "suggested_alternative": "仅限居住使用，不得用于违法违规活动。居家办公（不产生客流）不在此限。",
            "why_it_matters": "过于宽泛的限制可能影响正常工作需求，应明确合理边界。"
        },
        {
            "clause_name": "钥匙与门禁",
            "severity": "normal",
            "description": "钥匙交接与门禁权限",
            "current_text": "租客应妥善保管钥匙，丢失需赔偿",
            "suggested_alternative": "入住时交接全部钥匙（共__把）与门禁卡（共__张）。丢失一把配钥匙费由租客承担，换锁费用需视责任归属。",
            "why_it_matters": "明确交接数量与责任归属，避免退租时扯皮。"
        }
    ]

    def inspect(self, req: ContractInspectionRequest) -> ContractInspectionResponse:
        if req.quick_mode:
            clauses_to_check = self.STANDARD_CLAUSES
        else:
            clauses_to_check = [item.model_dump() for item in req.user_clauses]

        critical = 0
        warning = 0
        checked = []
        red_flags = []

        for clause in clauses_to_check:
            severity = clause.get("severity", "normal")
            if severity == "critical":
                critical += 1
                red_flags.append(f"【{clause['clause_name']}】存在高风险条款，必须修改")
            elif severity == "warning":
                warning += 1

            checked.append({
                "clause_name": clause["clause_name"],
                "severity": severity,
                "description": clause.get("description", ""),
                "current_text": clause.get("current_text", ""),
                "suggested_alternative": clause.get("suggested_alternative", ""),
                "why_it_matters": clause.get("why_it_matters", "")
            })

        # Determine overall risk
        if critical >= 2:
            overall = "high"
        elif critical >= 1 or warning >= 2:
            overall = "medium"
        else:
            overall = "low"

        general_advice = [
            "签约前逐条核对合同与口头承诺是否一致，不一致处要求书面补充",
            "要求房东出示身份证、房产证（或转租授权书），拍照留存",
            "水电气表读数、家具设备清单拍照签字确认，作为交房/退房依据",
            "所有费用约定（物业费、网费、维修费）必须写入合同，拒绝口头承诺",
            "保留合同原件（或双方签字扫描件），不要只留照片"
        ]

        return ContractInspectionResponse(
            overall_risk=overall,
            critical_count=critical,
            warning_count=warning,
            checked_clauses=checked,
            red_flags=red_flags if red_flags else ["暂未发现明显高风险条款，仍需逐项核对"],
            general_advice=general_advice
        )
