<template>
  <div class="grid gap-4 lg:grid-cols-3">
    <GlassCard class="lg:col-span-2" title="议价脚本生成器" :hover="false">
      <div class="space-y-4">
        <div class="grid gap-3 md:grid-cols-2">
          <Field label="当前报价（元/月）" v-model.number="form.asking_rent" type="number" />
          <Field label="合理区间下限" v-model.number="form.fair_rent_low" type="number" />
          <Field label="合理区间上限" v-model.number="form.fair_rent_high" type="number" />
          <Field label="偏离程度（%）" v-model.number="form.deviation_pct" type="number" />
        </div>

        <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
          <div class="text-xs tracking-widest text-slate-500 mb-3">风险等级（影响议价策略）</div>
          <div class="flex gap-2">
            <button
              v-for="level in ['可租', '谨慎', '不建议']"
              :key="level"
              @click="form.risk_level = level"
              class="flex-1 rounded-xl border px-3 py-2 text-xs transition-all duration-200"
              :class="form.risk_level === level ? activeClass(level) : 'border-slate-200/60 bg-slate-50 text-slate-500 hover:bg-white/8'"
            >
              {{ level }}
            </button>
          </div>
        </div>

        <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
          <div class="text-xs tracking-widest text-slate-500">因素贡献（JSON格式，可选）</div>
          <textarea
            v-model="factorsJson"
            rows="3"
            class="mt-2 w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-3 text-xs font-mono text-slate-800 focus:border-lime-400 focus:outline-none"
            placeholder='[{&quot;name&quot;: &quot;朝向（北向折价）&quot;, &quot;impact_pct&quot;: -3, &quot;note&quot;: &quot;采光弱&quot;}]'
          />
          <div class="mt-2 text-xs text-slate-400">用于生成更有针对性的议价话术</div>
        </div>

        <div class="flex gap-3">
          <NeonButton :loading="loading" @click="generate">生成议价脚本</NeonButton>
          <NeonButton variant="ghost" @click="fillDemo">填入演示数据</NeonButton>
          <NeonButton variant="ghost" @click="reset">重置</NeonButton>
        </div>
      </div>
    </GlassCard>

    <GlassCard title="脚本结果" :hover="false">
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 4" :key="i" class="skeleton h-24 rounded-2xl"></div>
      </div>

      <div v-else-if="result" class="space-y-4">
        <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
          <div class="text-xs tracking-widest text-slate-500">目标价位</div>
          <div class="mt-2 flex items-baseline gap-2">
            <span class="text-3xl font-semibold text-lime-600">{{ int(result.target_price_low || 0) }}</span>
            <span class="text-slate-400">~</span>
            <span class="text-2xl font-semibold">{{ int(result.target_price_high || 0) }}</span>
          </div>
          <div class="mt-2 text-xs text-slate-500">
            建议报价：<span class="text-lime-500 font-semibold">{{ int(result.recommended_offer || 0) }}</span> 元/月
          </div>
        </div>

        <div v-if="result.script_sections && result.script_sections.length" class="space-y-3">
          <div
            v-for="(section, idx) in result.script_sections"
            :key="idx"
            class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4"
          >
            <div class="flex items-center gap-2">
              <span class="flex h-6 w-6 items-center justify-center rounded-full bg-lime-100 text-xs text-lime-600">{{ idx + 1 }}</span>
              <span class="text-sm font-semibold">{{ section.title }}</span>
            </div>
            <div class="mt-3 text-sm leading-relaxed text-slate-700">{{ section.content }}</div>
            <div v-if="section.tactics && section.tactics.length" class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="(tactic, tidx) in section.tactics"
                :key="tidx"
                class="rounded-full border border-lime-200 bg-lime-100 px-2 py-1 text-[10px] text-lime-700"
              >
                {{ tactic }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="result.fallback_tactics && result.fallback_tactics.length" class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
          <div class="text-xs tracking-widest text-slate-500 mb-3">备选策略</div>
          <div class="space-y-2">
            <div
              v-for="(tactic, idx) in result.fallback_tactics"
              :key="idx"
              class="flex items-start gap-2 text-xs text-slate-600"
            >
              <span class="mt-0.5 text-sky-500">▸</span>
              <span>{{ tactic }}</span>
            </div>
          </div>
        </div>

        <NeonButton size="sm" variant="ghost" @click="copyScript">复制完整脚本</NeonButton>
      </div>

      <div v-else class="py-8 text-center text-sm text-slate-400">
        输入估值信息后生成议价脚本
      </div>
    </GlassCard>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import Field from '../components/Field.vue'
import { generateNegotiationScript } from '../api/qingju'

const loading = ref(false)
const result = ref(null)

const form = reactive({
  asking_rent: 0,
  fair_rent_low: 0,
  fair_rent_high: 0,
  deviation_pct: 0,
  risk_level: '可租',
  factors: []
})

const factorsJson = computed({
  get: () => JSON.stringify(form.factors, null, 2),
  set: (val) => {
    try {
      form.factors = JSON.parse(val)
    } catch {
      // ignore invalid JSON
    }
  }
})

const activeClass = (level) => {
  const map = {
    '可租': 'border-lime-300 bg-lime-100 text-lime-700',
    '谨慎': 'border-sky-200 bg-sky-100 text-sky-700',
    '不建议': 'border-amber-200 bg-amber-100 text-amber-700'
  }
  return map[level]
}

const int = (v) => Math.round(v)

const generate = async () => {
  loading.value = true
  try {
    const res = await generateNegotiationScript({ ...form })
    console.log('Negotiation raw response:', res)
    // 处理不同可能的响应格式
    const data = res.data || res
    console.log('Negotiation processed data:', data)
    if (data && (data.target_price_low !== undefined || data.script_sections)) {
      result.value = data
      window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '议价脚本已生成' } }))
    } else {
      console.error('Invalid response format:', res)
      window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: '脚本生成失败：数据格式错误' } }))
    }
  } catch (e) {
    console.error('Generate script failed:', e)
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: '脚本生成失败：' + (e.message || '未知错误') } }))
  } finally {
    loading.value = false
  }
}

const fillDemo = () => {
  form.asking_rent = 5200
  form.fair_rent_low = 4200
  form.fair_rent_high = 4800
  form.deviation_pct = 15
  form.risk_level = '谨慎'
  form.factors = [
    { name: '朝向（北向折价）', impact_pct: -3, note: '采光弱' },
    { name: '地铁距离（远）', impact_pct: -5, note: '通勤成本上升' },
    { name: '装修（简装折价）', impact_pct: -4, note: '需额外置办' }
  ]
}

const reset = () => {
  form.asking_rent = 0
  form.fair_rent_low = 0
  form.fair_rent_high = 0
  form.deviation_pct = 0
  form.risk_level = '可租'
  form.factors = []
  result.value = null
}

const copyScript = () => {
  if (!result.value) return
  const text = result.value.script_sections.map(s => `${s.title}\n${s.content}`).join('\n\n')
  navigator.clipboard.writeText(text)
  window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '脚本已复制到剪贴板' } }))
}
</script>
