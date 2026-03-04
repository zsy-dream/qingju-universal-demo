<template>
  <div class="space-y-6">
    <!-- Header & Action -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">真实估值引擎</h1>
        <p class="text-sm text-slate-500 mt-1">基于 Hedonic 特征价格模型，挖掘房源内在价值，揭示报价合理性</p>
      </div>
      <div class="flex items-center gap-2">
        <NeonButton v-if="listing" variant="outline" size="sm" @click="toggleFavorite">
          {{ isFavorite ? '★ 已收藏' : '☆ 收藏房源' }}
        </NeonButton>
        <NeonButton variant="ghost" size="sm" @click="$router.push('/listings')">返回房源列表</NeonButton>
      </div>
    </div>

    <!-- 输入面板 -->
    <GlassCard title="参数录入" :hover="false">
      <div class="grid gap-4 md:grid-cols-4 lg:grid-cols-5">
        <Field label="报价 (元/月)" v-model.number="form.asking_rent" type="number" />
        <Field label="面积 (㎡)" v-model.number="form.area_sqm" type="number" />
        <div class="space-y-2">
          <div class="text-xs tracking-widest text-slate-500">朝向</div>
          <select v-model="form.orientation" class="w-full rounded-xl border border-slate-200/60 bg-white px-4 py-2.5 text-sm text-slate-800 focus:border-lime-400 focus:outline-none">
            <option v-for="o in ['南', '北', '东', '西', '东南', '西北', '南北']" :key="o" :value="o">{{ o }}</option>
          </select>
        </div>
        <div class="space-y-2">
          <div class="text-xs tracking-widest text-slate-500">装修</div>
          <select v-model="form.decoration" class="w-full rounded-xl border border-slate-200/60 bg-white px-4 py-2.5 text-sm text-slate-800 focus:border-lime-400 focus:outline-none">
            <option v-for="d in ['豪装', '精装', '简装', '毛坯']" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
        <div class="md:col-span-4 lg:col-span-1 flex items-end">
          <div class="w-full flex gap-2">
            <NeonButton class="flex-1" :loading="loading" @click="run">更新估值</NeonButton>
            <NeonButton variant="ghost" @click="reset">重置</NeonButton>
          </div>
        </div>
      </div>

      <div class="mt-4 flex flex-wrap gap-6 items-center border-t border-slate-100 pt-4">
        <Field label="楼层" v-model.number="form.floor" type="number" class="w-24" />
        <Field label="总层数" v-model.number="form.total_floors" type="number" class="w-24" />
        <Field label="地铁距 (m)" v-model.number="form.subway_distance_m" type="number" class="w-32" />
        <Field label="通勤 (min)" v-model.number="form.commute_minutes" type="number" class="w-32" />
        <label class="flex cursor-pointer items-center gap-2 text-xs text-slate-600 self-end mb-2">
          <input v-model="form.has_elevator" type="checkbox" class="h-4 w-4 rounded accent-lime-500" />
          有电梯
        </label>
      </div>
    </GlassCard>

    <!-- 核心结论展示区 -->
    <div v-if="loading || result" class="grid gap-6 lg:grid-cols-3">
      <!-- 估值主卡片 -->
      <GlassCard class="lg:col-span-2 relative overflow-hidden" :hover="false">
        <div class="absolute top-0 right-0 w-64 h-64 bg-lime-500/5 blur-3xl rounded-full -mr-32 -mt-32"></div>
        <div class="absolute bottom-0 left-0 w-32 h-32 bg-sky-500/5 blur-2xl rounded-full -ml-16 -mb-16"></div>

        <div class="relative z-10 p-2">
          <div class="flex items-center justify-between mb-8">
            <div>
              <div class="text-xs tracking-widest text-slate-400 uppercase font-semibold">Valuation Report</div>
              <h3 class="text-lg font-bold text-slate-800">合理估值透视</h3>
            </div>
            <div v-if="result" class="text-right">
              <div class="text-xs text-slate-400 mb-1">估值偏离率</div>
              <div class="text-2xl font-bold" :class="result.deviation_pct > 0 ? 'text-amber-500' : 'text-lime-500'">
                {{ result.deviation_pct > 0 ? '+' : '' }}{{ result.deviation_pct }}%
              </div>
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-8">
            <!-- 价格汇总 -->
            <div class="flex flex-col justify-center items-center p-6 rounded-3xl bg-slate-50/50 border border-slate-100/50">
              <div class="text-sm text-slate-500 mb-2">合理估值区间 (月租)</div>
              <div v-if="loading" class="skeleton h-12 w-48 rounded-xl"></div>
              <div v-else class="text-4xl font-black text-slate-800 tracking-tight">
                <span class="text-lg font-normal text-slate-400 mr-1">¥</span>{{ result.fair_rent_low }}<span class="mx-2 text-slate-300 font-light">~</span>{{ result.fair_rent_high }}
              </div>
              <div class="mt-6 w-full space-y-4">
                <div class="flex justify-between text-xs">
                  <span class="text-slate-400">目前报价: ¥{{ form.asking_rent }}</span>
                  <span class="text-slate-800 font-semibold" v-if="result">
                    {{ result.deviation_pct > 10 ? '🔴 明显虚高' : (result.deviation_pct > 3 ? '🟡 略微偏高' : '🟢 价格合理') }}
                  </span>
                </div>
                <div class="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div 
                    class="h-full transition-all duration-1000 ease-out"
                    :style="{ width: result ? Math.max(0, Math.min(100, (form.asking_rent / result.fair_rent_high) * 80)) + '%' : '0%' }"
                    :class="result && result.deviation_pct > 10 ? 'bg-amber-400' : 'bg-lime-400'"
                  ></div>
                </div>
              </div>
            </div>

            <!-- 解释性图表 (瀑布图占位) -->
            <div class="relative min-h-[240px] flex flex-col">
              <div class="text-xs font-semibold text-slate-400 mb-2 flex items-center gap-1">
                <span class="inline-block w-2 h-2 rounded-full bg-lime-400"></span> 价值因子贡献
              </div>
              <div ref="waterfallChartEl" class="flex-1 w-full h-[220px]"></div>
              <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/50 backdrop-blur-sm z-20 rounded-xl">
                 <div class="text-xs text-slate-400 italic">计算中...</div>
              </div>
            </div>
          </div>
        </div>
      </GlassCard>

      <!-- 侧边辅助板块 -->
      <div class="space-y-6">
        <GlassCard title="同片区对标" :hover="false">
          <div class="space-y-3">
            <template v-if="loading">
              <div v-for="i in 3" :key="i" class="skeleton h-12 rounded-xl"></div>
            </template>
            <template v-else-if="result">
              <div v-for="b in result.benchmarks" :key="b.name" class="group p-4 rounded-2xl bg-white border border-slate-100 hover:border-lime-200 hover:shadow-xl hover:shadow-lime-500/5 transition-all cursor-default">
                <div class="flex justify-between items-center">
                  <div>
                    <div class="text-sm font-semibold text-slate-800">{{ b.name }}</div>
                    <div class="text-[10px] text-slate-400 mt-0.5">相似户型成交价</div>
                  </div>
                  <div class="text-right">
                    <div class="text-sm font-bold text-lime-600">¥{{ b.rent }}</div>
                    <div class="text-[9px] text-slate-300">月租参考</div>
                  </div>
                </div>
              </div>
            </template>
            <div v-else class="py-12 text-center text-xs text-slate-400">录入参数后显示对标样本</div>
          </div>
        </GlassCard>

        <GlassCard title="决策建议" :hover="false">
          <div class="space-y-3">
            <div class="flex gap-3 items-start">
              <div class="mt-1 h-5 w-5 flex items-center justify-center rounded-full bg-lime-100 text-[10px] text-lime-600 font-bold shrink-0">1</div>
              <p class="text-[12px] text-slate-600 leading-relaxed">
                <span class="font-bold text-slate-800">议价建议：</span>
                根据估值，该房源存在约 <span class="text-lime-600">{{ result?.deviation_pct || '--' }}%</span> 的议价空间。建议前往 [议价话术] 模块获取对应脚本。
              </p>
            </div>
            <div class="flex gap-3 items-start">
              <div class="mt-1 h-5 w-5 flex items-center justify-center rounded-full bg-sky-100 text-[10px] text-sky-600 font-bold shrink-0">2</div>
              <p class="text-[12px] text-slate-600 leading-relaxed">
                <span class="font-bold text-slate-800">特别提醒：</span>
                {{ form.subway_distance_m > 800 ? '房源距离地铁较远，建议在议价时作为压价理由。' : '房源靠近地铁，溢价属于合理范围。' }}
              </p>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!listingId" class="py-12">
      <EmptyState
        icon="💎"
        title="开始您的估值分析"
        description="您可以手动输入房源特征，或者从房源库选择一套现有房源直接导入。"
        action-text="浏览房源库"
        @action="$router.push('/listings')"
      />
    </div>
    <div v-else-if="loading" class="grid gap-6 lg:grid-cols-3">
       <div class="lg:col-span-2 skeleton h-[400px] rounded-3xl"></div>
       <div class="skeleton h-[400px] rounded-3xl"></div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed, nextTick, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import Field from '../components/Field.vue'
import EmptyState from '../components/EmptyState.vue'
import { estimate, getListing } from '../api/qingju'
import { useFavoritesStore } from '../stores/favorites'

const route = useRoute()
const favoritesStore = useFavoritesStore()
const listingId = ref(route.query.listing_id || null)
const listing = ref(null)
const loading = ref(false)
const result = ref(null)
const waterfallChartEl = ref(null)
let waterfallChart = null

const form = reactive({
  asking_rent: 4200,
  area_sqm: 28,
  floor: 6,
  total_floors: 11,
  orientation: '南',
  decoration: '精装',
  has_elevator: true,
  subway_distance_m: 350,
  commute_minutes: 32,
  city: '杭州'
})

const isFavorite = computed(() => listing.value && favoritesStore.isFavorite(listing.value.id))

const toggleFavorite = () => {
  if (!listing.value) return
  const added = favoritesStore.toggleFavorite(listing.value)
  window.dispatchEvent(new CustomEvent('app:toast', { 
    detail: { 
      type: added ? 'success' : 'info', 
      message: added ? '已添加到收藏' : '已取消收藏' 
    } 
  }))
}

const renderWaterfallChart = () => {
  if (!waterfallChartEl.value || !result.value) return
  if (!waterfallChart) waterfallChart = echarts.init(waterfallChartEl.value)

  const factors = result.value.factors || []
  const data = []
  const help = []
  const names = []
  
  let current = 0
  
  // Base
  names.push('初始基准')
  help.push(0)
  data.push(factors[0]?.value || 0)
  current = factors[0]?.value || 0
  
  // Others
  for (let i = 1; i < factors.length; i++) {
    const f = factors[i]
    names.push(f.name)
    if (f.value >= 0) {
      help.push(current)
      data.push(f.value)
      current += f.value
    } else {
      current += f.value
      help.push(current)
      data.push(Math.abs(f.value))
    }
  }
  
  // Result
  names.push('拟合估值')
  help.push(0)
  data.push(current)

  const option = {
    grid: { left: '10%', right: '10%', top: '10%', bottom: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { color: '#94a3b8', fontSize: 10, interval: 0, rotate: 15 },
      axisLine: { lineStyle: { color: '#e2e8f0' } }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } },
      axisLabel: { color: '#94a3b8', fontSize: 10 }
    },
    series: [
      {
        name: 'Placeholder',
        type: 'bar',
        stack: 'total',
        itemStyle: { borderColor: 'transparent', color: 'transparent' },
        emphasis: { itemStyle: { borderColor: 'transparent', color: 'transparent' } },
        data: help
      },
      {
        name: 'Contribution',
        type: 'bar',
        stack: 'total',
        label: { show: false },
        itemStyle: {
          color: (p) => {
            if (p.dataIndex === 0) return '#94a3b8' // Base
            if (p.dataIndex === names.length - 1) return '#22d3ee' // Final
            return factors[p.dataIndex]?.value >= 0 ? '#10b981' : '#f59e0b'
          },
          borderRadius: 2
        },
        data: data
      }
    ]
  }

  waterfallChart.setOption(option)
}

const run = async () => {
  loading.value = true
  try {
    result.value = await estimate({ ...form })
    await nextTick()
    renderWaterfallChart()
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '估值已生成' } }))
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const reset = () => {
  result.value = null
  Object.assign(form, {
     asking_rent: 0,
     area_sqm: 0,
     floor: 0,
     total_floors: 0,
     subway_distance_m: 0,
     commute_minutes: 0,
     decoration: '精装',
     orientation: '南',
     has_elevator: false
  })
  if (waterfallChart) {
    waterfallChart.dispose()
    waterfallChart = null
  }
}

onMounted(async () => {
  if (listingId.value) {
    try {
      loading.value = true
      listing.value = await getListing(listingId.value)
      if (listing.value) {
        Object.assign(form, {
          asking_rent: listing.value.asking_rent || 0,
          area_sqm: listing.value.area_sqm || 0,
          floor: listing.value.floor || 10,
          total_floors: listing.value.total_floors || 18,
          orientation: listing.value.orientation || '南',
          decoration: listing.value.decoration || '精装',
          has_elevator: !!listing.value.has_elevator,
          subway_distance_m: listing.value.subway_distance_m || 500,
          commute_minutes: listing.value.commute_minutes || 30
        })
        await run()
      }
    } finally {
      loading.value = false
    }
  }
})

onUnmounted(() => {
  if (waterfallChart) {
    waterfallChart.dispose()
  }
})
</script>
