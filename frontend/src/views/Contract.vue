<template>
  <div class="space-y-6">
    <GlassCard title="合同条款体检｜红线提醒 + 替代建议" :hover="false">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-sm text-slate-500">预置7项高频风险条款模板，一键检测</div>
        <div class="flex gap-2">
          <NeonButton size="sm" @click="runQuickInspect">一键体检</NeonButton>
          <NeonButton size="sm" variant="ghost" @click="showCustom = !showCustom">
            {{ showCustom ? '收起' : '自定义条款' }}
          </NeonButton>
        </div>
      </div>

      <div v-if="showCustom" class="mb-4 rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
        <div class="text-xs tracking-widest text-slate-500 mb-2">自定义条款检查（JSON格式）</div>
        <textarea
          v-model="customClausesJson"
          rows="4"
          class="w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-3 text-xs font-mono text-slate-800 focus:border-lime-400 focus:outline-none"
          placeholder='[{&quot;clause_name&quot;: &quot;押金退还&quot;, &quot;severity&quot;: &quot;critical&quot;, &quot;current_text&quot;: &quot;...&quot;, ...}]'
        />
        <div class="mt-2 flex gap-2">
          <NeonButton size="sm" @click="runCustomInspect">执行自定义检查</NeonButton>
          <NeonButton size="sm" variant="ghost" @click="loadExample">载入示例</NeonButton>
        </div>
      </div>
    </GlassCard>

    <div v-if="loading" class="grid gap-4 lg:grid-cols-2">
      <div v-for="i in 4" :key="i" class="skeleton h-48 rounded-2xl"></div>
    </div>

    <div v-else-if="result" class="space-y-4">
      <div class="grid gap-4 md:grid-cols-3">
        <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4 text-center">
          <div class="text-xs tracking-widest text-slate-500">总体风险</div>
          <div class="mt-2 text-2xl font-semibold" :class="riskColor">{{ riskText }}</div>
        </div>
        <div class="rounded-2xl border border-lime-200/60 bg-sky-50/30 p-4 text-center">
          <div class="text-xs tracking-widest text-sky-500">红线项</div>
          <div class="mt-2 text-2xl font-semibold text-sky-500">{{ result.critical_count }}</div>
        </div>
        <div class="rounded-2xl border border-lime-300/60 bg-lime-50/30 p-4 text-center">
          <div class="text-xs tracking-widest text-lime-500">警告项</div>
          <div class="mt-2 text-2xl font-semibold text-lime-500">{{ result.warning_count }}</div>
        </div>
      </div>

      <div v-if="result.red_flags.length > 0 && result.red_flags[0] !== '暂未发现明显高风险条款，仍需逐项核对'" class="rounded-2xl border border-sky-200 bg-sky-50/50 p-4">
        <div class="text-xs tracking-widest text-sky-600 mb-2">红线警示（必须修改）</div>
        <div class="space-y-2">
          <div v-for="(flag, idx) in result.red_flags" :key="idx" class="flex items-start gap-2 text-sm text-slate-800">
            <span class="mt-0.5 text-sky-500">⚠</span>
            <span>{{ flag }}</span>
          </div>
        </div>
      </div>

      <div class="grid gap-4 lg:grid-cols-2">
        <div
          v-for="(clause, idx) in result.checked_clauses"
          :key="idx"
          class="rounded-2xl border p-4"
          :class="clauseBorderColor(clause.severity)"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="text-lg">{{ severityIcon(clause.severity) }}</span>
              <span class="font-semibold text-slate-800">{{ clause.clause_name }}</span>
            </div>
            <span class="rounded-full border px-2 py-0.5 text-[10px]" :class="severityBadgeClass(clause.severity)">
              {{ severityText(clause.severity) }}
            </span>
          </div>

          <div class="mb-3 rounded-xl border border-slate-200/60 bg-slate-50 p-3">
            <div class="text-[10px] uppercase tracking-wider text-slate-400 mb-1">合同原文（风险点）</div>
            <div class="text-sm text-slate-600">{{ clause.current_text }}</div>
          </div>

          <div class="mb-3 rounded-xl border border-lime-200 bg-lime-50/30 p-3">
            <div class="text-[10px] uppercase tracking-wider text-lime-600 mb-1">建议替代方案</div>
            <div class="text-sm text-slate-800">{{ clause.suggested_alternative }}</div>
          </div>

          <div class="flex items-start gap-2 text-xs text-slate-500">
            <span class="text-lime-500">ℹ</span>
            <span>{{ clause.why_it_matters }}</span>
          </div>
        </div>
      </div>

      <GlassCard title="通用签约建议" :hover="false">
        <div class="grid gap-3 md:grid-cols-2">
          <div
            v-for="(advice, idx) in result.general_advice"
            :key="idx"
            class="flex items-start gap-3 rounded-xl border border-slate-200/60 bg-slate-50 p-3"
          >
            <span class="flex h-6 w-6 items-center justify-center rounded-full bg-lime-500/20 text-xs text-lime-600">{{ idx + 1 }}</span>
            <span class="text-sm text-slate-800">{{ advice }}</span>
          </div>
        </div>
      </GlassCard>

      <GlassCard title="签约前交接清单" :hover="false">
        <div class="grid gap-3 md:grid-cols-3">
          <label v-for="(item, idx) in checkList" :key="idx" class="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200/60 bg-slate-50 p-3 transition-colors hover:bg-white/8">
            <input type="checkbox" v-model="item.checked" class="h-4 w-4 accent-lime-500" />
            <span class="text-sm" :class="item.checked ? 'text-lime-600 line-through' : 'text-slate-800'">{{ item.label }}</span>
          </label>
        </div>
      </GlassCard>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import { inspectContract } from '../api/qingju'

const loading = ref(false)
const result = ref(null)
const showCustom = ref(false)
const customClausesJson = ref('')

const checkList = ref([
  { label: '水表读数拍照记录', checked: false },
  { label: '电表读数拍照记录', checked: false },
  { label: '燃气表读数拍照记录', checked: false },
  { label: '所有钥匙（含门禁卡）清点交接', checked: false },
  { label: '家具家电清单签字确认', checked: false },
  { label: '房东身份证+房产证（或授权书）拍照', checked: false },
  { label: '房屋现状视频录制', checked: false },
  { label: 'WiFi/网络测试正常', checked: false },
  { label: '所有电器开关测试', checked: false }
])

const riskText = computed(() => {
  if (!result.value) return ''
  const map = { low: '低风险', medium: '中风险', high: '高风险' }
  return map[result.value.overall_risk] || '未知'
})

const riskColor = computed(() => {
  if (!result.value) return ''
  const map = { low: 'text-lime-600', medium: 'text-lime-500', high: 'text-sky-500' }
  return map[result.value.overall_risk] || 'text-white'
})

const severityIcon = (s) => {
  const map = { critical: '🔴', warning: '🟡', normal: '🟢' }
  return map[s] || '⚪'
}

const severityText = (s) => {
  const map = { critical: '红线', warning: '警告', normal: '正常' }
  return map[s] || '未知'
}

const clauseBorderColor = (s) => {
  const map = {
    critical: 'border-sky-200 bg-sky-50/30',
    warning: 'border-lime-200 bg-lime-50/30',
    normal: 'border-slate-200/60 bg-slate-50'
  }
  return map[s] || 'border-slate-200/60 bg-slate-50'
}

const severityBadgeClass = (s) => {
  const map = {
    critical: 'border-sky-200 bg-sky-100 text-sky-600',
    warning: 'border-lime-200 bg-lime-100 text-lime-600',
    normal: 'border-slate-100 bg-slate-50 text-slate-500'
  }
  return map[s] || 'border-slate-100 bg-slate-50'
}

const runQuickInspect = async () => {
  loading.value = true
  try {
    result.value = await inspectContract({ quick_mode: true, user_clauses: [] })
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '合同体检完成' } }))
  } finally {
    loading.value = false
  }
}

const runCustomInspect = async () => {
  try {
    const clauses = JSON.parse(customClausesJson.value)
    loading.value = true
    result.value = await inspectContract({ quick_mode: false, user_clauses: clauses })
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '自定义检查完成' } }))
  } catch (e) {
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: 'JSON格式错误，请检查输入' } }))
  } finally {
    loading.value = false
  }
}

const loadExample = () => {
  customClausesJson.value = JSON.stringify([
    {
      clause_name: "押金退还",
      severity: "critical",
      description: "押金退还条件与时限",
      current_text: "退房时无息退还，如有损坏从押金中扣除",
      suggested_alternative: "正常磨损除外，房屋无结构性损坏且费用结清后，退房后7个工作日内全额退还。",
      why_it_matters: "模糊条款是押金纠纷的主要来源"
    }
  ], null, 2)
}
</script>
