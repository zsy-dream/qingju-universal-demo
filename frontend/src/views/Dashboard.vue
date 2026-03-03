<template>
  <div class="space-y-6 pb-12">
    <!-- Top Stats -->
    <div class="grid gap-4 md:grid-cols-3">
      <GlassCard title="候选房源" :hover="true">
        <template #meta>
          <span class="text-slate-400">Total</span>
        </template>
        <div v-if="loading" class="space-y-3">
          <div class="skeleton h-8 w-24 rounded-xl"></div>
          <div class="skeleton h-4 w-32 rounded-xl"></div>
        </div>
        <div v-else>
          <div class="text-4xl font-semibold text-slate-800">{{ summary?.listing_count ?? 0 }}</div>
          <div class="mt-2 text-xs text-slate-400">你的候选池越结构化，估值与风险越可解释</div>
        </div>
      </GlassCard>

      <GlassCard title="平均偏离（%）" :hover="true">
        <template #meta>
          <span class="text-slate-400">Ask vs Fair</span>
        </template>
        <div v-if="loading" class="space-y-3">
          <div class="skeleton h-8 w-24 rounded-xl"></div>
          <div class="skeleton h-4 w-32 rounded-xl"></div>
        </div>
        <div v-else>
          <div class="text-4xl font-semibold" :class="(summary?.avg_deviation_pct ?? 0) > 0 ? 'text-sky-500' : 'text-lime-600'">
            {{ (summary?.avg_deviation_pct ?? 0).toFixed(1) }}%
          </div>
          <div class="mt-2 text-xs text-slate-400">偏离越高，越需要解释与对标样本支撑</div>
        </div>
      </GlassCard>

      <GlassCard title="平均通勤时间" :hover="true">
        <template #meta>
          <span class="text-slate-400">分钟</span>
        </template>
        <div v-if="loading" class="space-y-3">
          <div class="skeleton h-8 w-24 rounded-xl"></div>
          <div class="skeleton h-4 w-32 rounded-xl"></div>
        </div>
        <div v-else>
          <div class="text-4xl font-semibold text-lime-500">{{ avgCommute }}</div>
          <div class="mt-2 text-xs text-slate-400">通勤-预算-风险三维约束中的硬边界</div>
        </div>
      </GlassCard>
    </div>

    <!-- Main Charts Row -->
    <div class="grid gap-4 lg:grid-cols-3">
      <GlassCard class="lg:col-span-2" title="估值偏离分布 (Top 12)" :hover="false">
        <div class="h-[300px] relative">
          <div v-if="loading" class="absolute inset-0 flex items-center justify-center p-8 gap-4">
             <div class="skeleton flex-1 h-full rounded-2xl"></div>
             <div class="skeleton flex-1 h-full rounded-2xl"></div>
          </div>
          <div ref="trendChartEl" class="h-full w-full"></div>
          <div v-if="!loading && (!summary?.latest_listings || summary.latest_listings.length === 0)" class="absolute inset-0 flex items-center justify-center text-slate-400 text-sm">
            暂无趋势数据，请点击右上角导入演示数据
          </div>
        </div>
      </GlassCard>

      <GlassCard title="价格区间分布" :hover="false">
        <div class="h-[300px] relative">
          <div v-if="loading" class="absolute inset-0 p-6">
            <div class="skeleton h-full w-full rounded-full"></div>
          </div>
          <div ref="priceChartEl" class="h-full w-full"></div>
          <div v-if="!loading && allListings.length === 0" class="absolute inset-0 flex items-center justify-center text-slate-400 text-sm">
            暂无价格分布数据
          </div>
        </div>
      </GlassCard>
    </div>

    <!-- Secondary Charts and Latest Listings Row -->
    <div class="grid gap-4 lg:grid-cols-3">
      <GlassCard title="通勤时长分布" :hover="false">
        <div class="h-[280px] relative">
          <div v-if="loading" class="absolute inset-0 p-6">
            <div class="skeleton h-full w-full rounded-2xl"></div>
          </div>
          <div ref="commuteChartEl" class="h-full w-full"></div>
        </div>
      </GlassCard>

      <GlassCard title="房源核心配置占比" :hover="false">
        <div class="h-[280px] relative">
          <div v-if="loading" class="absolute inset-0 p-6">
            <div class="skeleton h-full w-full rounded-2xl"></div>
          </div>
          <div ref="configChartEl" class="h-full w-full"></div>
        </div>
      </GlassCard>

      <GlassCard title="最新导入房源" :hover="false" class="h-full flex flex-col">
        <div v-if="loading" class="space-y-4 p-2">
          <div v-for="i in 3" :key="i" class="skeleton h-16 rounded-2xl"></div>
        </div>
        <div v-else class="flex flex-col h-full">
          <div class="space-y-3 flex-1 overflow-y-auto max-h-[280px] pr-2 scrollbar-thin scrollbar-thumb-slate-200">
            <div
              v-for="l in (summary?.latest_listings || []).slice().reverse().slice(0, 5)"
              :key="l.id"
              class="group rounded-2xl border border-slate-100 bg-white/50 p-3 transition-all duration-300 hover:border-lime-200 hover:bg-white hover:shadow-sm"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0 flex-1">
                  <div class="text-sm font-medium text-slate-700 truncate">{{ l.title }}</div>
                  <div class="mt-1 text-[11px] text-slate-400 flex items-center gap-2">
                    <span>报价: ¥{{ l.asking_rent }}</span>
                    <span class="w-px h-2 bg-slate-200"></span>
                    <span>合理: {{ l.fair_low }}~{{ l.fair_high }}</span>
                  </div>
                </div>
                <div class="text-xs font-semibold px-2 py-1 rounded-lg bg-slate-50" :class="(l.deviation_pct || 0) > 0 ? 'text-sky-500' : 'text-lime-600'">
                  {{ ((l.deviation_pct || 0) > 0 ? '+' : '') + (l.deviation_pct || 0) }}%
                </div>
              </div>
            </div>
            <div v-if="!summary?.latest_listings?.length" class="text-center py-10 text-slate-300 text-sm">
              暂无房源记录
            </div>
          </div>
          <div class="pt-4 mt-auto">
            <NeonButton size="sm" @click="refresh" :loading="loading" class="w-full">
              <template #icon>
                <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              </template>
              刷新数据
            </NeonButton>
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
  if (!allListings.value || allListings.value.length === 0) return 0
  const valid = allListings.value.filter(l => typeof l.commute_minutes === 'number')
  if (valid.length === 0) return 0
  const total = valid.reduce((sum, l) => sum + l.commute_minutes, 0)
  return Math.round(total / valid.length)
})

const renderTrendChart = () => {
  if (!trendChartEl.value) return
  if (!trendChart) trendChart = echarts.init(trendChartEl.value)

  const latest = summary.value?.latest_listings || []
  const data = [...latest].reverse()
  const xs = data.map(x => `#${x.id}`)
  const ys = data.map(x => x.deviation_pct)

  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', formatter: '{b}: {c}%' },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: xs,
      axisLine: { lineStyle: { color: '#E2E8F0' } },
      axisLabel: { color: '#94A3B8', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#F1F5F9' } },
      axisLabel: { color: '#94A3B8', formatter: '{value}%', fontSize: 10 }
    },
    series: [{
      type: 'line',
      data: ys,
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: { width: 3, color: '#84cc16' },
      itemStyle: { color: '#84cc16', borderColor: '#fff', borderWidth: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(132, 204, 22, 0.2)' },
          { offset: 1, color: 'rgba(132, 204, 22, 0)' }
        ])
      }
    }]
  })
}

const renderPriceChart = () => {
  if (!priceChartEl.value) return
  if (!priceChart) priceChart = echarts.init(priceChartEl.value)

  const ranges = [
    { name: '3k以下', value: 0 },
    { name: '3-5k', value: 0 },
    { name: '5-8k', value: 0 },
    { name: '8k+', value: 0 }
  ]
  
  allListings.value.forEach(l => {
    const r = l.asking_rent
    if (r < 3000) ranges[0].value++
    else if (r < 5000) ranges[1].value++
    else if (r < 8000) ranges[2].value++
    else ranges[3].value++
  })

  priceChart.setOption({
    backgroundColor: 'transparent',
    color: ['#84cc16', '#0ea5e9', '#f43f5e', '#fbbf24'],
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['50%', '75%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      data: ranges.filter(r => r.value > 0)
    }]
  })
}

const renderCommuteChart = () => {
  if (!commuteChartEl.value) return
  if (!commuteChart) commuteChart = echarts.init(commuteChartEl.value)

  const labels = ['<30分', '30-45分', '45-60分', '>60分']
  const values = [0, 0, 0, 0]
  
  allListings.value.forEach(l => {
    const m = l.commute_minutes || 0
    if (m < 30) values[0]++
    else if (m < 45) values[1]++
    else if (m < 60) values[2]++
    else values[3]++
  })

  commuteChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: 30, right: 10, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { lineStyle: { color: '#E2E8F0' } },
      axisLabel: { color: '#94A3B8', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#F1F5F9' } },
      axisLabel: { color: '#94A3B8', fontSize: 10 }
    },
    series: [{
      type: 'bar',
      data: values,
      barWidth: '40%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#0ea5e9' },
          { offset: 1, color: '#38bdf8' }
        ]),
        borderRadius: [6, 6, 0, 0]
      }
    }]
  })
}

const renderConfigChart = () => {
  if (!configChartEl.value) return
  if (!configChart) configChart = echarts.init(configChartEl.value)
  if (!allListings.value.length) return

  const total = allListings.value.length
  const elevator = allListings.value.filter(l => l.has_elevator).length
  const south = allListings.value.filter(l => l.orientation?.includes('南')).length
  const quality = allListings.value.filter(l => ['精装', '豪装'].includes(l.decoration)).length
  const subway = allListings.value.filter(l => (l.subway_distance_m || 1500) < 500).length

  configChart.setOption({
    backgroundColor: 'transparent',
    radar: {
      indicator: [
        { name: '电梯', max: total },
        { name: '朝南', max: total },
        { name: '精装', max: total },
        { name: '近地铁', max: total }
      ],
      axisName: { color: '#64748B', fontSize: 11 },
      splitArea: { show: false },
      splitLine: { lineStyle: { color: '#F1F5F9' } },
      axisLine: { lineStyle: { color: '#F1F5F9' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [elevator, south, quality, subway],
        name: '配置分布',
        itemStyle: { color: '#84cc16' },
        areaStyle: { color: 'rgba(132, 204, 22, 0.2)' },
        lineStyle: { width: 2 }
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
    if (summaryData) summary.value = summaryData
    allListings.value = listingsData || []

    await nextTick()
    renderTrendChart()
    renderPriceChart()
    renderCommuteChart()
    renderConfigChart()
  } catch (err) {
    console.error('Dashboard refresh failed:', err)
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

onMounted(() => {
  refresh()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => window.removeEventListener('resize', onResize))
</script>

<style scoped>
.skeleton {
  background: linear-gradient(90deg, #f1f5f9 25%, #f8fafc 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Custom Scrollbar */
.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #f1f5f9;
  border-radius: 10px;
}
.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: #e2e8f0;
}
</style>
