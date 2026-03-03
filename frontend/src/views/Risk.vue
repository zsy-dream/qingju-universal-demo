<template>
  <div class="grid gap-4 lg:grid-cols-3">
    <GlassCard class="lg:col-span-2" title="防坑风控｜信号面板" :hover="false">
      <div class="grid gap-3 md:grid-cols-2">
        <Signal label="噪音风险" v-model.number="form.noise" />
        <Signal label="潮湿/霉变风险" v-model.number="form.mold" />
        <Signal label="采光风险" v-model.number="form.poor_light" />
        <Signal label="设备老化风险" v-model.number="form.old_appliances" />
        <Signal label="二房东/转租风险" v-model.number="form.sublease_risk" />
        <Signal label="合同不公平条款风险" v-model.number="form.contract_unfair" />
      </div>

      <div class="mt-4 flex flex-wrap items-center gap-3">
        <NeonButton :loading="loading" @click="run">生成风控结论</NeonButton>
        <NeonButton variant="ghost" @click="reset">重置</NeonButton>
      </div>

      <div class="mt-5 rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
        <div class="text-xs tracking-widest text-slate-500">规则口径</div>
        <div class="mt-1 text-sm text-slate-600">每个风险信号分为 0/1/2（无/疑似/确认），综合输出可解释的风险等级与建议动作。权重越高的风险项对总分影响越大。</div>
      </div>
    </GlassCard>

    <GlassCard title="风险结论" :hover="false">
      <div v-if="loading" class="space-y-3">
        <div class="skeleton h-10 rounded-xl"></div>
        <div class="skeleton h-24 rounded-2xl"></div>
        <div class="skeleton h-24 rounded-2xl"></div>
      </div>

      <div v-else-if="result" class="space-y-4">
        <!-- 综合等级 -->
        <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
          <div class="text-xs tracking-widest text-slate-500">综合等级</div>
          <div class="mt-1 flex items-baseline gap-3">
            <div class="text-2xl font-semibold" :class="levelColor">{{ result.risk_level }}</div>
            <div class="text-xs text-slate-500">风险分：{{ result.risk_score }}/200</div>
          </div>
          <!-- 风险分可视化进度条 -->
          <div class="mt-3 h-2 w-full rounded-full bg-slate-50 overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-700"
              :style="{ width: Math.min(result.risk_score / 200 * 100, 100) + '%' }"
              :class="result.risk_score >= 120 ? 'bg-sky-500' : result.risk_score >= 70 ? 'bg-lime-500' : 'bg-lime-600'"
            ></div>
          </div>
        </div>

        <!-- 风险雷达图 -->
        <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
          <div class="text-xs tracking-widest text-slate-500">风险信号雷达图</div>
          <div ref="radarChartEl" class="mt-2 h-[260px] w-full"></div>
        </div>

        <!-- 主要风险贡献 -->
        <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
          <div class="text-xs tracking-widest text-slate-500">主要风险贡献</div>
          <div class="mt-3 space-y-2">
            <div v-for="(r, idx) in result.top_risks" :key="idx" class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-2">
                <div class="h-2 w-2 rounded-full" :class="r.signal_level >= 2 ? 'bg-sky-500' : 'bg-lime-500'"></div>
                <div class="text-sm">{{ r.name }}</div>
              </div>
              <div class="flex items-center gap-2">
                <div class="text-xs text-slate-400">权重{{ r.weight }}</div>
                <div class="text-xs text-sky-500 font-medium">+{{ r.contribution }}</div>
              </div>
            </div>
            <div v-if="result.top_risks.length === 0" class="text-sm text-slate-500">当前未选中明显风险信号</div>
          </div>
        </div>

        <!-- 建议动作 -->
        <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
          <div class="text-xs tracking-widest text-slate-600">建议动作</div>
          <div class="mt-3 space-y-2">
            <div v-for="(s, idx) in result.suggestions" :key="idx" class="rounded-xl border border-slate-200/60 bg-slate-50 p-3 text-sm text-slate-700 leading-relaxed">
              <span class="text-lime-600 mr-1">▸</span>{{ s }}
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-sm text-slate-600">请先设置风险信号强度并生成结论</div>
    </GlassCard>
  </div>
</template>

<script setup>
import { computed, nextTick, onUnmounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import Signal from '../components/Signal.vue'
import { risk } from '../api/qingju'

const loading = ref(false)
const result = ref(null)
const radarChartEl = ref(null)
let radarChart = null

const form = reactive({
  noise: 0,
  mold: 0,
  poor_light: 0,
  old_appliances: 0,
  sublease_risk: 0,
  contract_unfair: 0
})

const levelColor = computed(() => {
  if (!result.value) return 'text-white'
  if (result.value.risk_level === '不建议') return 'text-sky-500'
  if (result.value.risk_level === '谨慎') return 'text-lime-500'
  return 'text-lime-600'
})

/**
 * 渲染六维风险雷达图
 * NOTE: 雷达图指标根据权重动态设置 max 值，信号等级越高面积越大
 */
const renderRadarChart = () => {
  if (!radarChartEl.value || !result.value?.radar_data?.length) return
  if (!radarChart) radarChart = echarts.init(radarChartEl.value)

  const data = result.value.radar_data
  // 风险信号值 × 权重 = 加权贡献值
  const indicator = data.map(d => ({
    name: d.name.replace('风险', ''),
    max: d.max_value * d.weight
  }))
  const values = data.map(d => d.value * d.weight)

  radarChart.setOption({
    backgroundColor: 'transparent',
    radar: {
      indicator,
      center: ['50%', '52%'],
      radius: '70%',
      axisName: {
        color: 'rgba(0,0,0,0.6)',
        fontSize: 11
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(139,92,246,0.03)', 'rgba(139,92,246,0.06)', 'rgba(139,92,246,0.09)']
        }
      },
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.1)' } },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '风险信号',
        symbol: 'circle',
        symbolSize: 6,
        areaStyle: {
          color: {
            type: 'radial',
            x: 0.5, y: 0.5, r: 0.5,
            colorStops: [
              { offset: 0, color: 'rgba(236,72,153,0.35)' },
              { offset: 1, color: 'rgba(139,92,246,0.15)' }
            ]
          }
        },
        lineStyle: { color: '#0ea5e9', width: 2 },
        itemStyle: { color: '#0ea5e9', borderColor: '#fff', borderWidth: 1 }
      }]
    }]
  })
}

const run = async () => {
  loading.value = true
  try {
    result.value = await risk({ ...form })
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '风控结论已生成（含Top风险与建议动作）' } }))
    await nextTick()
    // 延迟渲染雷达图，确保DOM已更新且容器有尺寸
    setTimeout(() => {
      renderRadarChart()
    }, 100)
  } finally {
    loading.value = false
  }
}

const reset = () => {
  result.value = null
  radarChart?.dispose()
  radarChart = null
  form.noise = 0
  form.mold = 0
  form.poor_light = 0
  form.old_appliances = 0
  form.sublease_risk = 0
  form.contract_unfair = 0
}

onUnmounted(() => {
  radarChart?.dispose()
})
</script>
