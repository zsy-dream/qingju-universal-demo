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
      <div v-show="loading" class="space-y-3">
        <div class="skeleton h-10 rounded-xl"></div>
        <div class="skeleton h-24 rounded-2xl"></div>
        <div class="skeleton h-24 rounded-2xl"></div>
      </div>

      <div v-show="!loading && result" class="space-y-4">
        <!-- 综合等级 -->
        <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
          <div class="text-xs tracking-widest text-slate-500">综合等级</div>
          <div class="mt-1 flex items-baseline gap-3">
            <div class="text-2xl font-semibold" :class="levelColor">{{ result.risk_level }}</div>
            <div class="text-xs text-slate-500">风险分：{{ result.risk_score }}/200</div>
          </div>
          <!-- 风险分可视化进度条 -->
          <div class="mt-3 h-2 w-full rounded-full bg-slate-200 overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-700"
              :style="{ width: Math.min(result.risk_score / 200 * 100, 100) + '%' }"
              :class="result.risk_score >= 120 ? 'bg-sky-500 shadow-neon' : result.risk_score >= 70 ? 'bg-lime-500 shadow-neon' : 'bg-lime-600 shadow-neon'"
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

      <div v-if="!loading && !result" class="text-sm text-slate-600 py-10 text-center italic">
        请先设置风险信号强度并生成结论
      </div>
    </GlassCard>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import Signal from '../components/Signal.vue'
import { risk } from '../api/qingju'
import { useAppStore } from '../stores/app'

const appStore = useAppStore()
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
  if (!result.value) return 'text-slate-400'
  const score = result.value.risk_score
  if (score >= 120) return 'text-sky-500' // 慎租/不建议
  if (score >= 70) return 'text-lime-500' // 谨慎
  return 'text-lime-600' // 安全
})

/**
 * 渲染六维风险雷达图
 */
const renderRadarChart = () => {
  if (!radarChartEl.value) {
    console.error('Radar element not found')
    return
  }
  
  // 必须重新初始化，因为元素可能由于 v-if/v-else 发生变化
  if (radarChart) {
    radarChart.dispose()
    radarChart = null
  }
  
  radarChart = echarts.init(radarChartEl.value)

  const data = result.value?.radar_data || []
  if (data.length === 0) return

  const indicator = data.map(d => ({
    name: d.name.replace('风险', ''),
    max: 2 * (d.weight || 20)
  }))
  const values = data.map(d => (d.value || 0) * (d.weight || 20))

  radarChart.setOption({
    backgroundColor: 'transparent',
    radar: {
      indicator,
      center: ['50%', '55%'],
      radius: '65%',
      axisName: {
        color: '#64748b',
        fontSize: 11,
        fontWeight: 500
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(132, 204, 22, 0.02)', 'rgba(132, 204, 22, 0.05)']
        }
      },
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.05)' } },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.05)' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '风险信号',
        symbol: 'circle',
        symbolSize: 6,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(14, 165, 233, 0.4)' },
            { offset: 1, color: 'rgba(132, 204, 22, 0.2)' }
          ])
        },
        lineStyle: { color: '#0ea5e9', width: 2 },
        itemStyle: { color: '#0ea5e9', borderColor: '#fff', borderWidth: 1 }
      }]
    }]
  })
}

const handleResize = () => {
  radarChart?.resize()
}

const run = async () => {
  loading.value = true
  try {
    const res = await risk({ ...form })
    result.value = res
    appStore.pushToast({ type: 'success', message: '风控评估完成' })
  } catch (err) {
    appStore.pushToast({ type: 'error', message: '评估失败，请重试' })
  } finally {
    loading.value = false
    await nextTick()
    setTimeout(renderRadarChart, 150)
  }
}

const reset = () => {
  result.value = null
  radarChart?.dispose()
  radarChart = null
  Object.keys(form).forEach(k => form[k] = 0)
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  radarChart?.dispose()
})
</script>
