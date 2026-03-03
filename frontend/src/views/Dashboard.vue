<template>
  <div class="space-y-6">
    <div class="grid gap-4 md:grid-cols-3">
      <GlassCard title="候选房源" :hover="true">
        <template #meta>
          <span class="text-slate-400">Last 12</span>
        </template>
        <div v-if="loading" class="space-y-3">
          <div class="skeleton h-8 rounded-xl"></div>
          <div class="skeleton h-8 rounded-xl"></div>
        </div>
        <div v-else class="text-4xl font-semibold">{{ summary?.listing_count ?? 0 }}</div>
        <div class="mt-2 text-xs text-slate-400">你的候选池越结构化，估值与风险越可解释</div>
      </GlassCard>

      <GlassCard title="平均偏离（%）" :hover="true">
        <template #meta>
          <span class="text-slate-400">Ask vs Fair</span>
        </template>
        <div v-if="loading" class="skeleton h-10 rounded-xl"></div>
        <div v-else class="text-4xl font-semibold" :class="(summary?.avg_deviation_pct ?? 0) > 0 ? 'text-sky-500' : 'text-lime-600'">
          {{ summary?.avg_deviation_pct ?? 0 }}
        </div>
        <div class="mt-2 text-xs text-slate-400">偏离越高，越需要解释与对标样本支撑</div>
      </GlassCard>

      <GlassCard title="平均通勤时间" :hover="true">
        <template #meta>
          <span class="text-slate-400">分钟</span>
        </template>
        <div v-if="loading" class="skeleton h-10 rounded-xl"></div>
        <div v-else class="text-4xl font-semibold text-lime-500">{{ avgCommute }}</div>
        <div class="mt-2 text-xs text-slate-400">通勤-预算-风险三维约束中的硬边界</div>
      </GlassCard>
    </div>

    <div class="grid gap-4 lg:grid-cols-3">
      <GlassCard class="lg:col-span-2" title="估值偏离趋势" :hover="false">
        <div class="h-[280px]">
          <div v-if="loading" class="grid h-full grid-cols-2 gap-3">
            <div class="skeleton rounded-2xl"></div>
            <div class="skeleton rounded-2xl"></div>
          </div>
          <div v-else ref="trendChartEl" class="h-full w-full"></div>
        </div>
      </GlassCard>

      <GlassCard title="价格区间分布" :hover="false">
        <div class="h-[280px]">
          <div v-if="loading" class="skeleton h-full rounded-2xl"></div>
          <div v-else ref="priceChartEl" class="h-full w-full"></div>
        </div>
      </GlassCard>
    </div>

    <div class="grid gap-4 lg:grid-cols-3">
      <GlassCard title="通勤时间分布" :hover="false">
        <div class="h-[260px]">
          <div v-if="loading" class="skeleton h-full rounded-2xl"></div>
          <div v-else ref="commuteChartEl" class="h-full w-full"></div>
        </div>
      </GlassCard>

      <GlassCard title="房源配置占比" :hover="false">
        <div class="h-[260px]">
          <div v-if="loading" class="skeleton h-full rounded-2xl"></div>
          <div v-else ref="configChartEl" class="h-full w-full"></div>
        </div>
      </GlassCard>

      <GlassCard title="最新房源" :hover="false" class="h-full flex flex-col">
        <div v-if="loading" class="space-y-3">
          <div class="skeleton h-16 rounded-2xl"></div>
          <div class="skeleton h-16 rounded-2xl"></div>
          <div class="skeleton h-16 rounded-2xl"></div>
        </div>
        <div v-else class="flex flex-col h-full">
          <div class="space-y-3 flex-1 overflow-y-auto max-h-[260px] pr-1">
            <div
              v-for="l in summary.latest_listings.slice(0, 4)"
              :key="l.id"
              class="rounded-2xl border border-slate-200/60 bg-slate-50 p-3 transition-all duration-200 hover:-translate-y-[1px] hover:bg-white/8"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <div class="text-sm font-semibold">{{ l.title }}</div>
                  <div class="mt-1 text-xs text-slate-500">报价 {{ l.asking_rent }} ｜合理 {{ l.fair_low }}~{{ l.fair_high }}</div>
                </div>
                <div class="text-xs" :class="l.deviation_pct > 0 ? 'text-sky-500' : 'text-lime-600'">
                  {{ l.deviation_pct }}%
                </div>
              </div>
            </div>
          </div>
          <div class="pt-3 mt-auto">
            <NeonButton size="sm" @click="refresh" class="w-full">刷新数据</NeonButton>
          </div>
        </div>
      </GlassCard>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref, computed } from 'vue'
import * as echarts from 'echarts'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import { getDashboardSummary, listListings } from '../api/qingju'

const loading = ref(true)
const summary = ref({ listing_count: 0, avg_deviation_pct: 0, high_risk_count: 0, latest_listings: [] })
const allListings = ref([])

const trendChartEl = ref(null)
const priceChartEl = ref(null)
const commuteChartEl = ref(null)
const configChartEl = ref(null)

let trendChart = null
let priceChart = null
let commuteChart = null
let configChart = null

const avgCommute = computed(() => {
  if (!allListings.value.length) return 0
  const total = allListings.value.reduce((sum, l) => sum + (l.commute_minutes || 0), 0)
  return Math.round(total / allListings.value.length)
})

const renderTrendChart = () => {
  if (!trendChartEl.value) return
  if (!trendChart) trendChart = echarts.init(trendChartEl.value)

  const xs = (summary.value.latest_listings || []).slice().reverse().map((x) => `#${x.id}`)
  const ys = (summary.value.latest_listings || []).slice().reverse().map((x) => x.deviation_pct)

  trendChart.setOption({
    backgroundColor: 'transparent',
    grid: { left: 32, right: 16, top: 20, bottom: 26 },
    xAxis: {
      type: 'category',
      data: xs,
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.1)' } },
      axisLabel: { color: 'rgba(0,0,0,0.6)' }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.05)' } },
      axisLabel: { color: 'rgba(0,0,0,0.6)', formatter: '{value}%' }
    },
    series: [
      {
        type: 'line',
        data: ys,
        smooth: true,
        symbol: 'circle',
        symbolSize: 9,
        lineStyle: { width: 3, color: '#8B5CF6' },
        itemStyle: {
          color: '#38bdf8',
          borderColor: 'rgba(236,72,153,0.75)',
          borderWidth: 2
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(139,92,246,0.28)' },
              { offset: 1, color: 'rgba(34,211,238,0.02)' }
            ]
          }
        }
      }
    ]
  })
}

const renderPriceChart = () => {
  if (!priceChartEl.value || !allListings.value.length) return
  if (!priceChart) priceChart = echarts.init(priceChartEl.value)

  const ranges = { '3000以下': 0, '3000-5000': 0, '5000-8000': 0, '8000以上': 0 }
  allListings.value.forEach(l => {
    if (l.asking_rent < 3000) ranges['3000以下']++
    else if (l.asking_rent < 5000) ranges['3000-5000']++
    else if (l.asking_rent < 8000) ranges['5000-8000']++
    else ranges['8000以上']++
  })

  priceChart.setOption({
    backgroundColor: 'transparent',
    color: ['#22D3EE', '#8B5CF6', '#EC4899', '#10B981'],
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      data: Object.entries(ranges).map(([name, value]) => ({ name, value })),
      label: { color: 'rgba(0,0,0,0.7)', fontSize: 11 },
      labelLine: { lineStyle: { color: 'rgba(0,0,0,0.3)' } },
      emphasis: {
        itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' }
      }
    }]
  })
}

const renderCommuteChart = () => {
  if (!commuteChartEl.value || !allListings.value.length) return
  if (!commuteChart) commuteChart = echarts.init(commuteChartEl.value)

  const ranges = { '<30分': 0, '30-45分': 0, '45-60分': 0, '>60分': 0 }
  allListings.value.forEach(l => {
    const m = l.commute_minutes || 0
    if (m < 30) ranges['<30分']++
    else if (m < 45) ranges['30-45分']++
    else if (m < 60) ranges['45-60分']++
    else ranges['>60分']++
  })

  commuteChart.setOption({
    backgroundColor: 'transparent',
    grid: { left: 16, right: 16, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: Object.keys(ranges),
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.1)' } },
      axisLabel: { color: 'rgba(0,0,0,0.6)', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.05)' } },
      axisLabel: { color: 'rgba(0,0,0,0.6)' }
    },
    series: [{
      type: 'bar',
      data: Object.values(ranges),
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#8B5CF6' },
            { offset: 1, color: '#38bdf8' }
          ]
        },
        borderRadius: [4, 4, 0, 0]
      },
      barWidth: '50%'
    }]
  })
}

const renderConfigChart = () => {
  if (!configChartEl.value || !allListings.value.length) return
  if (!configChart) configChart = echarts.init(configChartEl.value)

  const elevatorCount = allListings.value.filter(l => l.has_elevator).length
  const southCount = allListings.value.filter(l => l.orientation?.includes('南')).length
  const decoratedCount = allListings.value.filter(l => ['精装', '豪装'].includes(l.decoration)).length
  const subwayCount = allListings.value.filter(l => l.subway_distance_m < 500).length

  configChart.setOption({
    backgroundColor: 'transparent',
    radar: {
      indicator: [
        { name: '有电梯', max: allListings.value.length },
        { name: '朝南', max: allListings.value.length },
        { name: '近地铁', max: allListings.value.length },
        { name: '精装', max: allListings.value.length }
      ],
      axisName: { color: 'rgba(0,0,0,0.6)' },
      splitArea: { areaStyle: { color: ['rgba(139,92,246,0.05)', 'rgba(139,92,246,0.1)'] } },
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.1)' } },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [elevatorCount, southCount, subwayCount, decoratedCount],
        name: '配置占比',
        areaStyle: { color: 'rgba(139,92,246,0.3)' },
        lineStyle: { color: '#8B5CF6', width: 2 },
        itemStyle: { color: '#38bdf8' }
      }]
    }]
  })
}

const refresh = async () => {
  loading.value = true
  try {
    const [summaryData, listingsData] = await Promise.all([
      getDashboardSummary(),
      listListings(100)
    ])
    summary.value = summaryData
    allListings.value = listingsData
    await nextTick()
    renderTrendChart()
    renderPriceChart()
    renderCommuteChart()
    renderConfigChart()
  } finally {
    loading.value = false
  }
}

const onResize = () => {
  trendChart?.resize()
  priceChart?.resize()
  commuteChart?.resize()
  configChart?.resize()
}

onMounted(async () => {
  await refresh()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => window.removeEventListener('resize', onResize))
</script>
