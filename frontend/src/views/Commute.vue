<template>
  <div class="space-y-6">
    <GlassCard title="通勤-租金边际替代测算沙盘" :hover="false">
      <div class="mb-4 text-sm text-slate-600">
        输入月薪和租房预算上限，系统将计算不同通勤圈的租金中位数和"通勤时间折现"，帮你算清："为了省房租每天多坐地铁，到底亏不亏"。
      </div>

      <div class="grid gap-3 md:grid-cols-3">
        <Field label="月薪（元）" v-model.number="form.monthly_salary" type="number" />
        <Field label="最高月租预算（元）" v-model.number="form.budget_max" type="number" />
        <Field label="每月工作天数" v-model.number="form.work_days_per_month" type="number" />
      </div>

      <div class="mt-4 flex gap-3">
        <NeonButton :loading="loading" @click="run">开始测算</NeonButton>
        <NeonButton variant="ghost" @click="fillDemo">填入演示数据</NeonButton>
        <NeonButton variant="ghost" @click="reset">重置</NeonButton>
      </div>
    </GlassCard>

    <div v-if="loading" class="grid gap-4 lg:grid-cols-2">
      <div v-for="i in 4" :key="i" class="skeleton h-36 rounded-2xl"></div>
    </div>

    <div v-else-if="result" class="space-y-6">
      <!-- 智能摘要 -->
      <div class="rounded-2xl border border-lime-200 bg-lime-50/30 p-4">
        <div class="text-xs tracking-widest text-lime-600 mb-2">📊 测算结论</div>
        <div class="text-sm leading-relaxed text-slate-800">{{ result.summary }}</div>
        <div class="mt-2 text-xs text-slate-500">时薪：{{ result.hourly_wage }} 元/h</div>
      </div>

      <!-- 净成本对比柱状图 -->
      <GlassCard title="各圈层净月度成本对比" :hover="false">
        <div ref="costChartEl" class="h-[280px] w-full"></div>
      </GlassCard>

      <!-- 通勤圈卡片 -->
      <div class="grid gap-4 lg:grid-cols-5">
        <div
          v-for="zone in result.zones"
          :key="zone.zone_name"
          class="rounded-2xl border p-4"
          :class="zone.zone_name === result.best_zone ? 'border-lime-300 bg-lime-50/50' : 'border-slate-200/60 bg-slate-50'"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="text-sm font-semibold truncate text-slate-800">{{ zone.zone_name }}</div>
            <span
              v-if="zone.zone_name === result.best_zone"
              class="rounded-full border border-lime-300 bg-lime-100 px-1.5 py-0.5 text-[10px] text-lime-600"
            >推荐</span>
          </div>

          <div class="text-2xl font-bold" :class="verdictColor(zone.verdict)">
            ¥{{ Math.round(zone.net_monthly_cost) }}
          </div>
          <div class="text-xs text-slate-400 mt-1">净月度成本</div>

          <div class="mt-3 space-y-1 text-xs">
            <div class="flex justify-between">
              <span class="text-slate-500">租金中位数</span>
              <span class="text-slate-800 font-medium">¥{{ Math.round(zone.rent_median) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">通勤时间成本</span>
              <span class="text-sky-600 font-medium">+¥{{ Math.round(zone.monthly_commute_cost) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">通勤区间</span>
              <span class="text-slate-600">{{ zone.commute_min }}-{{ zone.commute_max }}min</span>
            </div>
          </div>

          <div class="mt-3">
            <span
              class="rounded-full px-2 py-0.5 text-[10px] border"
              :class="verdictBadge(zone.verdict)"
            >{{ zone.verdict }}</span>
          </div>
        </div>
      </div>

      <!-- 决策提示 -->
      <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
        <div class="text-xs tracking-widest text-slate-600 mb-3">💡 决策提示</div>
        <div class="space-y-2 text-sm text-slate-700">
          <div>• "净月度成本" = 租金 + 通勤时间折现（将通勤时间按你的时薪换算成钱）</div>
          <div>• 远郊租金虽低，但每天多花1小时通勤 = 每月多"花"{{ Math.round(result.hourly_wage * 22) }}元（按时薪计）</div>
          <div>• 推荐圈层不一定是最便宜的，而是"租金+时间"综合成本最低的</div>
          <div>• 建议结合【估值】和【对比】功能，在推荐圈层内找具体房源</div>
        </div>
      </div>
    </div>

    <EmptyState
      v-else
      icon="🚇"
      title="输入薪资与预算开始测算"
      description="系统将计算不同通勤圈的租金-时间替代关系，找到最优平衡点"
    />
  </div>
</template>

<script setup>
import { nextTick, onUnmounted, ref, reactive } from 'vue'
import * as echarts from 'echarts'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import Field from '../components/Field.vue'
import EmptyState from '../components/EmptyState.vue'
import { analyzeCommute } from '../api/qingju'

const loading = ref(false)
const result = ref(null)
const costChartEl = ref(null)
let costChart = null

const form = reactive({
  monthly_salary: 8000,
  budget_max: 3500,
  work_days_per_month: 22
})

const verdictColor = (v) => {
  const map = { '高性价比': 'text-lime-600', '平衡区间': 'text-sky-600', '偏高': 'text-amber-600', '不经济': 'text-slate-500' }
  return map[v] || 'text-slate-400'
}

const verdictBadge = (v) => {
  const map = {
    '高性价比': 'border-lime-200 bg-lime-100 text-lime-600',
    '平衡区间': 'border-sky-200 bg-sky-100 text-sky-600',
    '偏高': 'border-amber-200 bg-amber-100 text-amber-600',
    '不经济': 'border-slate-200 bg-slate-100 text-slate-500'
  }
  return map[v] || 'border-slate-200 bg-slate-50 text-slate-400'
}

const renderCostChart = () => {
  if (!costChartEl.value || !result.value?.zones?.length) return
  if (!costChart) costChart = echarts.init(costChartEl.value)

  const zones = result.value.zones
  const COLORS = ['#22D3EE', '#8B5CF6', '#EC4899', '#F97316', '#6B7280']

  costChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        let html = `${params[0].name}<br/>`
        params.forEach(p => {
          html += `${p.seriesName}: ¥${Math.round(p.value)}<br/>`
        })
        return html
      }
    },
    legend: { data: ['租金中位数', '通勤时间成本'], bottom: 0, textStyle: { color: 'rgba(0,0,0,0.6)', fontSize: 11 } },
    grid: { left: 50, right: 20, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: zones.map(z => z.zone_name.replace(/（.*）/, '')),
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.1)' } },
      axisLabel: { color: 'rgba(0,0,0,0.6)', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.05)' } },
      axisLabel: { color: 'rgba(0,0,0,0.5)', formatter: '¥{value}' }
    },
    series: [
      {
        name: '租金中位数', type: 'bar', stack: 'total',
        data: zones.map(z => z.rent_median),
        itemStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: '#38bdf8' }, { offset: 1, color: '#8B5CF6' }] }
        },
        barWidth: '45%'
      },
      {
        name: '通勤时间成本', type: 'bar', stack: 'total',
        data: zones.map(z => z.monthly_commute_cost),
        itemStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: '#0ea5e9' }, { offset: 1, color: '#F97316' }] },
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  })
}

const run = async () => {
  loading.value = true
  try {
    console.log('Calling commute API with:', form)
    result.value = await analyzeCommute({ ...form })
    console.log('Commute API response:', result.value)
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '通勤测算完成' } }))
    await nextTick()
    renderCostChart()
  } catch (e) {
    console.error('Commute analysis failed:', e)
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: '通勤测算失败：' + (e.message || '请检查输入数据') } }))
  } finally {
    loading.value = false
  }
}

const fillDemo = () => {
  form.monthly_salary = 8000
  form.budget_max = 3500
  form.work_days_per_month = 22
}

const reset = () => {
  result.value = null
  costChart?.dispose()
  costChart = null
  form.monthly_salary = 0
  form.budget_max = 0
  form.work_days_per_month = 22
}

onUnmounted(() => {
  costChart?.dispose()
})
</script>
