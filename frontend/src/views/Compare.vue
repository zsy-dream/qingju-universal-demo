<template>
  <div class="space-y-6">
    <GlassCard title="极速选房决策流｜候选池对比收敛" :hover="false">
      <div class="mb-4 text-sm text-slate-500">
        选择2-6套房源进行横向对比，系统将基于价格、通勤、位置、配置、楼层等维度生成综合评分与推荐决策。
      </div>
      
      <div class="grid gap-4 md:grid-cols-6">
        <div v-for="(id, idx) in selectedIds" :key="idx" class="relative">
          <input
            v-model.number="selectedIds[idx]"
            type="number"
            class="w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-3 text-center text-lg font-semibold text-slate-800 focus:border-lime-400 focus:outline-none"
            placeholder="#ID"
          />
          <button
            @click="removeSlot(idx)"
            class="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-sky-500 text-xs text-white"
            v-if="selectedIds.length > 2"
          >
            ×
          </button>
        </div>
        <button
          v-if="selectedIds.length < 6"
          @click="addSlot"
          class="flex items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50 py-3 text-sm text-slate-500 hover:border-lime-400 hover:text-lime-600"
        >
          + 添加房源
        </button>
      </div>

      <div class="mt-4 flex gap-3">
        <NeonButton :loading="loading" @click="runComparison">开始对比分析</NeonButton>
        <NeonButton variant="ghost" @click="fillDemo">填入演示ID</NeonButton>
        <NeonButton variant="ghost" @click="reset">重置</NeonButton>
      </div>
    </GlassCard>

    <div v-if="loading" class="grid gap-4 lg:grid-cols-3">
      <div v-for="i in 3" :key="i" class="skeleton h-64 rounded-2xl"></div>
    </div>

    <div v-else-if="result" class="space-y-6">
      <!-- 智能摘要 -->
      <div class="rounded-2xl border border-lime-200 bg-lime-50/30 p-4">
        <div class="text-sm leading-relaxed text-slate-800">{{ result.summary }}</div>
      </div>

      <!-- 综合得分柱状图 -->
      <GlassCard title="综合得分对比" :hover="false">
        <div ref="scoreBarChartEl" class="h-[260px] w-full"></div>
      </GlassCard>

      <!-- 多维雷达图 -->
      <GlassCard title="多维度雷达对比" :hover="false">
        <div ref="radarChartEl" class="h-[300px] w-full"></div>
      </GlassCard>

      <!-- 房源卡片 -->
      <div class="grid gap-4 lg:grid-cols-3">
        <div
          v-for="score in result.scores"
          :key="score.listing_id"
          class="rounded-2xl border p-4"
          :class="recommendationClass(score.listing_id)"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="text-lg font-semibold truncate text-slate-800" :title="score.title">
              #{{ score.listing_id }} {{ score.title.slice(0, 12) }}...
            </div>
            <div class="text-2xl font-bold" :class="scoreColor(score.total_score)">
              {{ score.total_score.toFixed(1) }}
            </div>
          </div>
          
          <div class="mb-3 text-2xl font-semibold text-lime-600">
            ¥{{ score.asking_rent }}
          </div>

          <div class="space-y-2">
            <div v-for="(val, key) in score.breakdown" :key="key" class="flex items-center justify-between text-xs">
              <span class="text-slate-500">{{ key }}</span>
              <div class="flex items-center gap-2">
                <div class="h-1.5 w-16 rounded-full bg-slate-50 overflow-hidden">
                  <div class="h-full rounded-full bg-lime-500" :style="{ width: val + '%' }"></div>
                </div>
                <span class="w-6 text-right text-slate-600">{{ val }}</span>
              </div>
            </div>
          </div>

          <div class="mt-4 flex gap-2">
            <span
              v-if="isBestChoice(score.listing_id)"
              class="rounded-full border border-lime-300 bg-lime-100 px-2 py-0.5 text-xs text-lime-700 font-semibold"
            >
              🏆 首选推荐
            </span>
            <span
              v-if="isSecondChoice(score.listing_id)"
              class="rounded-full border border-sky-200 bg-sky-100 px-2 py-0.5 text-xs text-sky-700"
            >
              备选
            </span>
            <span
              v-if="isAvoid(score.listing_id)"
              class="rounded-full border border-amber-200 bg-amber-100 px-2 py-0.5 text-xs text-amber-700"
            >
              ⚠ 建议排除
            </span>
          </div>
        </div>
      </div>

      <!-- 分维度对比 -->
      <GlassCard title="分维度对比" :hover="false">
        <div class="space-y-4">
          <div
            v-for="factor in result.factors"
            :key="factor.name"
            class="rounded-xl border border-slate-200/60 bg-slate-50 p-3"
          >
            <div class="mb-2 flex items-center justify-between">
              <span class="font-medium">{{ factor.name }}</span>
              <span v-if="factor.winner_id" class="text-xs text-lime-600">
                优胜: #{{ factor.winner_id }}
              </span>
            </div>
            <div class="grid gap-2" :class="'grid-cols-' + factor.values.length">
              <div
                v-for="val in factor.values"
                :key="val.listing_id"
                class="rounded-lg border p-2 text-center"
                :class="val.listing_id === factor.winner_id ? 'border-lime-300 bg-lime-50/50' : 'border-slate-200/60 bg-slate-50'"
              >
                <div class="text-xs text-slate-500">#{{ val.listing_id }}</div>
                <div class="text-sm font-medium">{{ val.value }}</div>
                <div class="text-xs" :class="val.listing_id === factor.winner_id ? 'text-lime-600' : 'text-slate-400'">
                  得分: {{ val.score }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </GlassCard>

      <!-- 决策理由卡片 -->
      <div class="grid gap-4 lg:grid-cols-2">
        <div class="rounded-2xl border border-lime-200 bg-lime-50/30 p-4">
          <div class="mb-3 text-xs tracking-widest text-lime-700">🏆 首选推荐理由</div>
          <div class="text-sm leading-relaxed text-slate-800">
            {{ result.recommendation.best_choice_reason }}
          </div>
        </div>
        <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
          <div class="mb-3 text-xs tracking-widest text-slate-600">📋 决策建议</div>
          <div class="space-y-2 text-sm text-slate-700">
            <div>• 首选房源综合得分最高，建议优先安排实地看房</div>
            <div>• 对比维度中绿色高亮项为该维度最优</div>
            <div>• 建议结合【证据采集】记录看房实况</div>
            <div>• 使用【合同体检】在签约前排查条款风险</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import { compareListings } from '../api/qingju'

const loading = ref(false)
const result = ref(null)
const selectedIds = ref([1, 2, 3])

const scoreBarChartEl = ref(null)
const radarChartEl = ref(null)
let scoreBarChart = null
let radarChart = null

const NEON_COLORS = ['#84cc16', '#22d3ee', '#f59e0b', '#94a3b8']

const recommendationClass = (id) => {
  if (!result.value) return 'border-slate-200/60 bg-slate-50'
  if (result.value.recommendation.best_choice_id === id) {
    return 'border-lime-300 bg-lime-50/50'
  }
  if (result.value.recommendation.second_choice_id === id) {
    return 'border-sky-200 bg-sky-50/50'
  }
  if (result.value.recommendation.avoid_ids.includes(id)) {
    return 'border-amber-200 bg-amber-50/30'
  }
  return 'border-slate-200/60 bg-slate-50'
}

const scoreColor = (score) => {
  if (score >= 80) return 'text-lime-600'
  if (score >= 60) return 'text-lime-500'
  return 'text-sky-500'
}

const isBestChoice = (id) => result.value?.recommendation.best_choice_id === id
const isSecondChoice = (id) => result.value?.recommendation.second_choice_id === id
const isAvoid = (id) => result.value?.recommendation.avoid_ids.includes(id)

/**
 * 渲染综合得分柱状图
 * NOTE: 横向柱状图，按得分排序，颜色区分首选/备选/排除
 */
const renderScoreBarChart = () => {
  if (!scoreBarChartEl.value || !result.value?.scores?.length) return
  if (!scoreBarChart) scoreBarChart = echarts.init(scoreBarChartEl.value)

  const scores = [...result.value.scores].sort((a, b) => b.total_score - a.total_score)

  scoreBarChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', formatter: p => `#${p[0].name}<br/>综合得分: ${p[0].value}` },
    grid: { left: 80, right: 30, top: 20, bottom: 20 },
    xAxis: {
      type: 'value',
      max: 100,
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.05)' } },
      axisLabel: { color: 'rgba(0,0,0,0.5)' }
    },
    yAxis: {
      type: 'category',
      data: scores.map(s => `#${s.listing_id}`),
      inverse: true,
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.1)' } },
      label: { color: 'rgba(0,0,0,0.6)', fontSize: 12 }
    },
    series: [{
      type: 'bar',
      data: scores.map((s, i) => ({
        value: s.total_score.toFixed(1),
        itemStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: NEON_COLORS[i % NEON_COLORS.length] + '88' },
              { offset: 1, color: NEON_COLORS[i % NEON_COLORS.length] }
            ]
          },
          borderRadius: [0, 6, 6, 0]
        }
      })),
      barWidth: '50%',
      label: {
        show: true,
        position: 'right',
        color: 'rgba(0,0,0,0.6)',
        fontSize: 12,
        formatter: p => p.value
      }
    }]
  })
}

/**
 * 渲染多维度雷达对比图
 * NOTE: 将每套房源的各维度分数映射到同一个雷达图上进行直观对比
 */
const renderRadarChart = () => {
  if (!radarChartEl.value || !result.value?.scores?.length || !result.value?.factors?.length) return
  if (!radarChart) radarChart = echarts.init(radarChartEl.value)

  const factors = result.value.factors
  const scores = result.value.scores

  const indicator = factors.map(f => ({
    name: f.name,
    max: 100
  }))

  const seriesData = scores.map((s, i) => ({
    value: factors.map(f => {
      const fv = f.values.find(v => v.listing_id === s.listing_id)
      return fv ? fv.score : 0
    }),
    name: `#${s.listing_id}`,
    symbol: 'circle',
    symbolSize: 5,
    lineStyle: { color: NEON_COLORS[i % NEON_COLORS.length], width: 2 },
    itemStyle: { color: NEON_COLORS[i % NEON_COLORS.length] },
    areaStyle: { color: NEON_COLORS[i % NEON_COLORS.length] + '18' }
  }))

  radarChart.setOption({
    backgroundColor: 'transparent',
    legend: {
      data: scores.map(s => `#${s.listing_id}`),
      bottom: 0,
      textStyle: { color: 'rgba(0,0,0,0.6)', fontSize: 11 }
    },
    radar: {
      indicator,
      center: ['50%', '46%'],
      radius: '60%',
      axisName: { color: 'rgba(0,0,0,0.6)', fontSize: 10 },
      splitArea: {
        areaStyle: { color: ['rgba(139,92,246,0.03)', 'rgba(139,92,246,0.06)'] }
      },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.05)' } }
    },
    series: [{ type: 'radar', data: seriesData }]
  })
}

const addSlot = () => {
  if (selectedIds.value.length < 6) {
    selectedIds.value.push(null)
  }
}

const removeSlot = (idx) => {
  if (selectedIds.value.length > 2) {
    selectedIds.value.splice(idx, 1)
  }
}

const runComparison = async () => {
  const validIds = selectedIds.value.filter(id => id && id > 0)
  if (validIds.length < 2) {
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: '请至少选择2个房源进行对比' } }))
    return
  }
  loading.value = true
  try {
    result.value = await compareListings(validIds)
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '对比分析完成' } }))
    await nextTick()
    renderScoreBarChart()
    renderRadarChart()
  } finally {
    loading.value = false
  }
}

const fillDemo = () => {
  selectedIds.value = [1, 2, 3]
}

const reset = () => {
  selectedIds.value = [null, null]
  result.value = null
  scoreBarChart?.dispose()
  radarChart?.dispose()
  scoreBarChart = null
  radarChart = null
}

onUnmounted(() => {
  scoreBarChart?.dispose()
  radarChart?.dispose()
})
</script>
