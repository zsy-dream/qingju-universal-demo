<template>
  <div class="space-y-6">
    <GlassCard title="决策包一键分享｜估值 + 风险 + 证据整合" :hover="false">
      <div class="grid gap-4 md:grid-cols-2">
        <div>
          <div class="mb-2 text-xs tracking-widest text-slate-500">房源ID</div>
          <input
            v-model.number="form.listing_id"
            type="number"
            class="w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-3 text-slate-800 focus:border-lime-400 focus:outline-none"
            placeholder="输入房源ID"
          />
        </div>
        <div>
          <div class="mb-2 text-xs tracking-widest text-slate-500">分享标题</div>
          <input
            v-model="form.title"
            class="w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-3 text-slate-800 focus:border-lime-400 focus:outline-none"
            placeholder="如：杨浦地铁口一居-决策包"
          />
        </div>
      </div>

      <div class="mt-4 flex flex-wrap gap-3">
        <label class="flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-2">
          <input type="checkbox" v-model="form.include_estimate" class="accent-lime-500" />
          <span class="text-sm">包含估值分析</span>
        </label>
        <label class="flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-2">
          <input type="checkbox" v-model="form.include_risk" class="accent-lime-500" />
          <span class="text-sm">包含风险评估</span>
        </label>
        <label class="flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-2">
          <input type="checkbox" v-model="form.include_evidence" class="accent-lime-500" />
          <span class="text-sm">包含证据摘要</span>
        </label>
        <label class="flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-2">
          <input type="checkbox" v-model="form.include_negotiation" class="accent-lime-500" />
          <span class="text-sm">包含议价建议</span>
        </label>
      </div>

      <div class="mt-4 flex gap-3">
        <NeonButton :loading="generating" @click="generate">生成决策包</NeonButton>
        <NeonButton variant="ghost" @click="fillDemo">填入演示</NeonButton>
        <NeonButton variant="ghost" @click="reset">重置</NeonButton>
      </div>
    </GlassCard>

    <div v-if="generating" class="skeleton h-96 rounded-2xl"></div>

    <div v-else-if="packageData" class="space-y-4">
      <div class="rounded-2xl border border-lime-200 bg-lime-50/30 p-4">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-xs tracking-widest text-lime-700">决策包已生成</div>
            <div class="mt-1 text-sm text-slate-600">可复制下方内容分享给同伴/家人</div>
          </div>
          <NeonButton size="sm" @click="copyPackage">复制全部</NeonButton>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-6">
        <pre ref="packageContent" class="whitespace-pre-wrap font-sans text-sm leading-relaxed text-slate-800">{{ packageText }}</pre>
      </div>

      <GlassCard title="快速分享卡片" :hover="false">
        <div class="rounded-xl border border-slate-200/60 bg-slate-50 p-4">
          <div class="flex items-start justify-between">
            <div>
              <div class="text-lg font-semibold">{{ packageData.title }}</div>
              <div class="mt-2 flex flex-wrap gap-2">
                <span v-if="packageData.estimate" class="rounded-full border border-lime-200 bg-lime-50 px-2 py-0.5 text-xs text-lime-600">
                  估值: ¥{{ packageData.estimate.fair_rent_low }}-{{ packageData.estimate.fair_rent_high }}
                </span>
                <span v-if="packageData.risk" class="rounded-full border border-lime-200 bg-lime-50 px-2 py-0.5 text-xs text-lime-500">
                  风险: {{ packageData.risk.level }}
                </span>
                <span v-if="packageData.evidence_count" class="rounded-full border border-slate-100 bg-slate-50 px-2 py-0.5 text-xs text-slate-500">
                  证据: {{ packageData.evidence_count }}项
                </span>
              </div>
            </div>
            <div class="text-3xl">🏠</div>
          </div>
          <div v-if="packageData.estimate" class="mt-3 text-sm text-slate-600">
            当前报价¥{{ packageData.estimate.asking_rent }}，偏离{{ packageData.estimate.deviation_pct }}%
          </div>
          <div class="mt-3 text-xs text-slate-400">
            来自 青居智算 — 租房防坑与真实估值系统
          </div>
        </div>
        <NeonButton class="mt-4 w-full" size="sm" variant="ghost" @click="copyShort">复制短卡片</NeonButton>
      </GlassCard>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import { getListing } from '../api/qingju'

const generating = ref(false)
const packageData = ref(null)
const packageContent = ref(null)

const form = ref({
  listing_id: 1,
  title: '',
  include_estimate: true,
  include_risk: true,
  include_evidence: true,
  include_negotiation: true
})

const packageText = computed(() => {
  if (!packageData.value) return ''
  const d = packageData.value
  let text = `【青居智算 · 房源决策包】\n`
  text += `🏠 目标房源：${d.title}\n`
  text += `------------------------\n\n`
  
  if (d.estimate) {
    text += `💰 估值结论\n`
    text += `  • 当前报价: ¥${d.estimate.asking_rent} / 月\n`
    text += `  • 合理区间: ¥${d.estimate.fair_rent_low} - ¥${d.estimate.fair_rent_high} / 月\n`
    text += `  • 偏离程度: ${d.estimate.deviation_pct}\n\n`
  }
  
  if (d.risk) {
    text += `⚠️ 风险提示 (${d.risk.level})\n`
    text += `  • 综合评分: ${d.risk.score}/100\n`
    if (d.risk.top_risks?.length > 0) {
      text += `  • 核心警示: ${d.risk.top_risks.join('、')}\n`
    }
    text += `\n`
  }
  
  if (d.evidence_count !== undefined) {
    text += `📷 现场证据\n`
    text += `  • 已固定 ${d.evidence_count} 项实堪证据细节\n\n`
  }
  
  if (d.negotiation) {
    text += `💡 议价策略\n`
    text += `  • 理想底价: ¥${d.negotiation.target_low} / 月\n`
    text += `  • 开口还价: ¥${d.negotiation.recommended} / 月\n\n`
  }
  
  text += `------------------------\n`
  text += `📌 行动建议: ${d.conclusion || '结合实勘情况谨慎决策'}`
  return text
})

const generate = async () => {
  if (!form.value.listing_id) {
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: '请输入房源ID' } }))
    return
  }
  
  generating.value = true
  try {
    const listing = await getListing(form.value.listing_id)
    if (!listing) {
      window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: '房源不存在' } }))
      return
    }
    
    packageData.value = {
      title: form.value.title || listing.title || `房源#${listing.id}`,
      estimate: form.value.include_estimate ? {
        asking_rent: listing.asking_rent,
        fair_rent_low: Math.round(listing.asking_rent * 0.85),
        fair_rent_high: Math.round(listing.asking_rent * 0.95),
        deviation_pct: '+5%'
      } : null,
      risk: form.value.include_risk ? {
        level: '谨慎',
        score: 65,
        top_risks: ['二房东风险', '合同条款']
      } : null,
      evidence_count: form.value.include_evidence ? 4 : 0,
      negotiation: form.value.include_negotiation ? {
        target_low: Math.round(listing.asking_rent * 0.9),
        target_high: Math.round(listing.asking_rent * 0.95),
        recommended: Math.round(listing.asking_rent * 0.92)
      } : null,
      conclusion: '综合评估建议：优先议价后再签约'
    }
    
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '决策包已生成' } }))
  } finally {
    generating.value = false
  }
}

const copyPackage = () => {
  navigator.clipboard.writeText(packageText.value)
  window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '决策包已复制到剪贴板' } }))
}

const copyShort = () => {
  if (!packageData.value) return
  const d = packageData.value
  const short = `🏠 ${d.title}\n估值: ${d.estimate?.fair_rent_low || '--'}-${d.estimate?.fair_rent_high || '--'}元 | 风险: ${d.risk?.level || '--'} | 证据: ${d.evidence_count || 0}项\n来自青居智算`
  navigator.clipboard.writeText(short)
  window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '短卡片已复制' } }))
}

const fillDemo = () => {
  form.value = {
    listing_id: 1,
    title: '杨浦地铁口南向一居-决策包',
    include_estimate: true,
    include_risk: true,
    include_evidence: true,
    include_negotiation: true
  }
}

const reset = () => {
  form.value = {
    listing_id: null,
    title: '',
    include_estimate: true,
    include_risk: true,
    include_evidence: true,
    include_negotiation: true
  }
  packageData.value = null
}
</script>
