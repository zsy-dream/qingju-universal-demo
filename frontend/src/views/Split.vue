<template>
  <div class="space-y-6">
    <GlassCard title="合租公平分摊计算器" :hover="false">
      <div class="mb-4 text-sm text-slate-500">
        录入各房间面积和权重属性（独卫/阳台/采光/朝向），系统自动计算最公平的租金分摊比例，告别合租纠纷。
      </div>

      <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4 mb-4">
        <Field label="总月租金（元）" v-model.number="totalRent" type="number" />
      </div>

      <div class="space-y-4">
        <div
          v-for="(room, idx) in rooms"
          :key="idx"
          class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4 relative"
        >
          <button
            v-if="rooms.length > 2"
            @click="removeRoom(idx)"
            class="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-sky-500 text-xs text-white hover:bg-sky-500/80"
          >
            ×
          </button>

          <div class="grid gap-3 md:grid-cols-2">
            <Field :label="'房间名称'" v-model="room.name" :placeholder="'如：主卧A'" />
            <Field :label="'面积（㎡）'" v-model.number="room.area_sqm" type="number" />
          </div>

          <div class="mt-3 flex flex-wrap gap-3">
            <label class="flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200/60 bg-slate-50 px-3 py-1.5 text-xs text-slate-600 hover:border-lime-400">
              <input v-model="room.has_private_bathroom" type="checkbox" class="h-4 w-4 accent-lime-500" />
              独卫 (+20%)
            </label>
            <label class="flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200/60 bg-slate-50 px-3 py-1.5 text-xs text-slate-600 hover:border-lime-400">
              <input v-model="room.has_balcony" type="checkbox" class="h-4 w-4 accent-lime-500" />
              阳台 (+10%)
            </label>
            <label class="flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200/60 bg-slate-50 px-3 py-1.5 text-xs text-slate-600 hover:border-lime-400">
              <input v-model="room.has_good_light" type="checkbox" class="h-4 w-4 accent-lime-500" />
              采光好 (+5%)
            </label>
            <Field label="朝向" v-model="room.orientation" placeholder="南/北/东/西" class="w-28" />
          </div>
        </div>
      </div>

      <div class="mt-4 flex flex-wrap gap-3">
        <NeonButton variant="ghost" @click="addRoom" v-if="rooms.length < 8">+ 添加房间</NeonButton>
        <NeonButton :loading="loading" @click="calculate">计算分摊</NeonButton>
        <NeonButton variant="ghost" @click="fillDemo">填入演示数据</NeonButton>
        <NeonButton variant="ghost" @click="reset">重置</NeonButton>
      </div>
    </GlassCard>

    <!-- 分摊结果 -->
    <div v-if="loading" class="grid gap-4 lg:grid-cols-3">
      <div v-for="i in 3" :key="i" class="skeleton h-48 rounded-2xl"></div>
    </div>

    <div v-else-if="result" class="space-y-6">
      <!-- 公式说明 -->
      <div class="rounded-2xl border border-lime-200 bg-lime-50/30 p-4">
        <div class="text-xs tracking-widest text-lime-700 mb-2">📐 计算公式</div>
        <div class="text-sm text-slate-800">{{ result.formula_explanation }}</div>
      </div>

      <!-- 饼图 -->
      <GlassCard title="分摊比例可视化" :hover="false">
        <div ref="pieChartEl" class="h-[280px] w-full"></div>
      </GlassCard>

      <!-- 每间详情 -->
      <div class="grid gap-4" :class="result.rooms.length <= 3 ? 'lg:grid-cols-3' : 'lg:grid-cols-4'">
        <div
          v-for="(room, idx) in result.rooms"
          :key="idx"
          class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4"
        >
          <div class="flex items-center justify-between mb-3">
            <pre ref="packageContent" class="whitespace-pre-wrap font-sans text-sm leading-relaxed text-slate-800">{{ room.name }}</pre>
            <div class="text-2xl font-bold text-lime-600">¥{{ room.monthly_rent }}</div>
          </div>

          <div class="space-y-2 text-xs">
            <div class="flex justify-between">
              <span class="text-slate-400">实际面积</span>
              <span class="text-slate-800">{{ room.area_sqm }}㎡</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">加权面积</span>
              <span class="text-slate-800">{{ room.weighted_area }}㎡</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">占比</span>
              <span class="text-lime-500 font-medium">{{ (room.weight_ratio * 100).toFixed(1) }}%</span>
            </div>
          </div>

          <div v-if="room.weight_details.length" class="mt-3 flex flex-wrap gap-1">
            <span
              v-for="(d, di) in room.weight_details"
              :key="di"
              class="rounded-full border border-lime-200 bg-lime-100 px-2 py-0.5 text-xs text-lime-700"
            >
              {{ d.factor }} {{ d.bonus }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onUnmounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import Field from '../components/Field.vue'
import { calculateSplit } from '../api/qingju'

const loading = ref(false)
const result = ref(null)
const totalRent = ref(6000)
const pieChartEl = ref(null)
let pieChart = null

const NEON_COLORS = ['#22D3EE', '#8B5CF6', '#EC4899', '#10B981', '#F97316', '#6366F1', '#14B8A6', '#F43F5E']

const rooms = reactive([
  { name: '主卧A', area_sqm: 18, has_private_bathroom: true, has_balcony: true, has_good_light: true, orientation: '南' },
  { name: '次卧B', area_sqm: 12, has_private_bathroom: false, has_balcony: false, has_good_light: true, orientation: '北' },
  { name: '小卧C', area_sqm: 9, has_private_bathroom: false, has_balcony: false, has_good_light: false, orientation: '西' }
])

const addRoom = () => {
  if (rooms.length < 8) {
    rooms.push({ name: `房间${String.fromCharCode(65 + rooms.length)}`, area_sqm: 10, has_private_bathroom: false, has_balcony: false, has_good_light: true, orientation: '' })
  }
}

const removeRoom = (idx) => {
  if (rooms.length > 2) {
    rooms.splice(idx, 1)
  }
}

/**
 * 渲染分摊比例饼图
 */
const renderPieChart = () => {
  if (!pieChartEl.value || !result.value?.rooms?.length) return
  if (!pieChart) pieChart = echarts.init(pieChartEl.value)

  pieChart.setOption({
    backgroundColor: 'transparent',
    color: NEON_COLORS,
    tooltip: {
      trigger: 'item',
      formatter: p => `${p.name}<br/>月租: ¥${p.value}<br/>占比: ${p.percent}%`
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      data: result.value.rooms.map(r => ({
        name: r.name,
        value: r.monthly_rent
      })),
      label: {
        color: 'rgba(0,0,0,0.7)',
        fontSize: 12,
        formatter: '{b}\n¥{c}'
      },
      labelLine: { lineStyle: { color: 'rgba(0,0,0,0.3)' } },
      emphasis: {
        itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' }
      }
    }]
  })
}

const calculate = async () => {
  if (!totalRent.value || totalRent.value <= 0) {
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: '请输入有效的总月租金' } }))
    return
  }
  loading.value = true
  try {
    result.value = await calculateSplit({
      total_rent: totalRent.value,
      rooms: rooms.map(r => ({ ...r }))
    })
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '分摊计算完成' } }))
    await nextTick()
    renderPieChart()
  } finally {
    loading.value = false
  }
}

const fillDemo = () => {
  totalRent.value = 6000
  rooms.splice(0, rooms.length)
  rooms.push(
    { name: '主卧A（带独卫+阳台）', area_sqm: 18, has_private_bathroom: true, has_balcony: true, has_good_light: true, orientation: '南' },
    { name: '次卧B', area_sqm: 12, has_private_bathroom: false, has_balcony: false, has_good_light: true, orientation: '北' },
    { name: '小卧C', area_sqm: 9, has_private_bathroom: false, has_balcony: false, has_good_light: false, orientation: '西' }
  )
}

const reset = () => {
  result.value = null
  pieChart?.dispose()
  pieChart = null
  totalRent.value = 0
  rooms.splice(0, rooms.length)
  rooms.push(
    { name: '房间A', area_sqm: 0, has_private_bathroom: false, has_balcony: false, has_good_light: true, orientation: '' },
    { name: '房间B', area_sqm: 0, has_private_bathroom: false, has_balcony: false, has_good_light: true, orientation: '' }
  )
}

onUnmounted(() => {
  pieChart?.dispose()
})
</script>
