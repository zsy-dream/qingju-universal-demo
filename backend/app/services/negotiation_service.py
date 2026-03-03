"""
议价话术生成服务（增强版）

NOTE: 基于估值偏离度、因素贡献和风险等级动态生成结构化议价脚本，
      包含"开场-因素拆解-风险对冲-报价锚点-备选策略"五阶段完整流程。
"""

from __future__ import annotations

import logging
from app.schemas.negotiation import NegotiationRequest, NegotiationResponse

logger = logging.getLogger("app")


class NegotiationService:
    """议价话术生成核心服务"""

    def generate_script(self, req: NegotiationRequest) -> NegotiationResponse:
        """
        生成结构化议价脚本

        Args:
            req: 包含报价、合理区间、偏离度、因素列表和风险等级的请求

        Returns:
            包含目标价位、分阶段话术和备选策略的完整议价方案
        """
        deviation = req.deviation_pct
        asking = req.asking_rent
        fair_mid = (req.fair_rent_low + req.fair_rent_high) / 2

        # NOTE: 根据偏离程度动态设定议价目标区间
        if deviation > 15:
            # 显著溢价 → 激进策略
            target_low = min(fair_mid * 0.95, asking * 0.88)
            target_high = fair_mid
            intensity = "激进"
        elif deviation > 5:
            # 中度溢价 → 温和策略
            target_low = fair_mid * 0.95
            target_high = min(fair_mid * 1.02, asking * 0.95)
            intensity = "温和"
        elif deviation < -10:
            # 低价房 → 防御策略（低价可能有隐患）
            target_low = asking * 0.98
            target_high = asking
            intensity = "防御"
        else:
            # 公允价 → 微调策略
            target_low = min(fair_mid * 0.97, asking * 0.97)
            target_high = asking
            intensity = "微调"

        recommended = round((target_low + target_high) / 2, 0)

        # 构建分阶段话术
        sections = []

        # 阶段一：开场——建立信息对等
        sections.append({
            "title": "第一步：开场——建立信息对等",
            "content": (
                f"「我对这套房做了些研究。类似户型在附近商圈的市场行情大概在"
                f"{int(req.fair_rent_low)}-{int(req.fair_rent_high)}元/月。"
                f"我使用的是基于面积、区位、装修等多因素的 Hedonic 特征定价模型，有数据支撑。"
                f"想听听您的定价思路。」"
            ),
            "tactics": [
                "先展示专业数据依据，掌握话语权",
                "留出空间让对方解释，避免对抗",
                "提到模型名称增强专业感和可信度"
            ]
        })

        # 阶段二：因素拆解——客观折价依据
        negative_factors = [f for f in req.factors if f.get("impact_pct", 0) < 0]
        positive_factors = [f for f in req.factors if f.get("impact_pct", 0) > 0]

        if negative_factors:
            neg_names = "、".join([f["name"].split("（")[0] for f in negative_factors[:3]])
            neg_total = sum(abs(f.get("impact_pct", 0)) for f in negative_factors)
            neg_amount = sum(abs(f.get("amount", 0)) for f in negative_factors)

            content = (
                f"「在估值因素中，这套房在 {neg_names} 方面存在折价因素，"
                f"合计影响约 {neg_total:.0f}%"
            )
            if neg_amount > 0:
                content += f"（约 {int(neg_amount)} 元/月）"
            content += "。"

            if positive_factors:
                pos_names = "、".join([f["name"].split("（")[0] for f in positive_factors[:2]])
                content += f" 当然，{pos_names}是溢价因素，我也考虑在内了。"

            content += "所以综合来看，这个定价存在一定调整空间。」"

            sections.append({
                "title": "第二步：因素拆解——客观折价依据",
                "content": content,
                "tactics": [
                    "用因素贡献数据解释折价，而非主观压价",
                    "先认可正面因素再提折价，避免引起对方防御心理",
                    "量化金额影响更有说服力"
                ]
            })
        else:
            sections.append({
                "title": "第二步：因素拆解——确认公允性",
                "content": (
                    "「从各维度因素来看，这套房综合评分还不错，"
                    "不过价格仍有小幅商量空间。毕竟市场在波动，最终成交价和挂牌价通常有一定差距。」"
                ),
                "tactics": [
                    "正面评价是建立信任的基础",
                    "暗示市场交易习惯存在议价空间"
                ]
            })

        # 阶段三：风险对冲——将风险转化为筹码
        if req.risk_level in ["谨慎", "不建议"]:
            risk_content = "「另外，我在看房过程中注意到一些风险点"
            if req.risk_level == "不建议":
                risk_content += "（多项较为显著）"
            risk_content += (
                "。考虑到合同条款、转租链路等不确定性，"
                "我需要在价格中预留一部分风险对冲空间。"
                "当然，如果能提供产权证明/原房东授权、签署更规范的合同，"
                "我可以在价格上放宽一些。」"
            )
            sections.append({
                "title": "第三步：风险对冲——将风险转化为筹码",
                "content": risk_content,
                "tactics": [
                    "将风险量化为议价理由",
                    "提供'风险降低→价格可谈'的交换条件",
                    "给对方'配合=互利'的正向激励"
                ]
            })

        # 阶段四：报价锚点——给出精准区间
        sections.append({
            "title": f"第{'四' if req.risk_level in ['谨慎', '不建议'] else '三'}步：报价锚点——给出区间",
            "content": (
                f"「综合以上分析，我的心理价位在 {int(target_low)}-{int(target_high)} 元/月。"
                f"如果咱们能在 {int(recommended)} 元左右达成一致，我可以尽快签约"
                f"{'，资料齐全的话今天就能定' if deviation > 10 else ''}。」"
            ),
            "tactics": [
                "给出区间降低对方抵触心理",
                f"推荐值 {int(recommended)} 放在区间{'中低位' if intensity in ['激进', '温和'] else '中高位'}",
                "用'尽快签约'增加吸引力，降低对方的机会成本感知"
            ]
        })

        # 阶段五：收尾——限时+替代方案
        sections.append({
            "title": "最后一步：收尾——限时决策 + 替代方案",
            "content": (
                f"「我这边还有{'2' if intensity == '激进' else '3'}个在看的房源，"
                "这周末前需要定下来。如果价格合适今天就能签。"
                "另外，如果价格完全谈不拢的话，我们是否可以考虑其他让步方式？"
                "比如减免一个月物业费、降低押金比例、或者赠送一周免租期？」"
            ),
            "tactics": [
                "制造温和的时间压力",
                "提供非价格维度的替代让步方案",
                "保持友好态度，留下回旋余地"
            ]
        })

        # 备选策略——按优先级排序
        fallbacks = [
            f"【价格不动时】要求书面承诺：设备维修责任（写入合同）、提前解约条件（违约金上限）、押金退还时限（7个工作日）",
            f"【小幅让步时】接受不超过 {int(fair_mid * 1.03)} 元，但换取：产权证明核验、规范合同模板、设备清单签字",
            "【免租期策略】要求赠送1-2周免租期作为签约优惠，实际等效于1-3%的租金折扣",
            "【押金策略】协商押一付一（替代押二付三），减少沉没成本。或约定押金存入第三方账户",
            "【二房东场景】要求出示原租赁合同、房东授权书，核实收款账户与合同主体一致性",
            f"【底线设定】如果最终报价超过 {int(fair_mid * 1.08)} 元（超出合理区间上限8%），建议放弃本房源"
        ]

        return NegotiationResponse(
            target_price_low=round(target_low, 0),
            target_price_high=round(target_high, 0),
            recommended_offer=recommended,
            script_sections=sections,
            fallback_tactics=fallbacks
        )
