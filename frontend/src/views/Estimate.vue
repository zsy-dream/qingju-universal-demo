<template>
  <div class="space-y-4">
    <!-- 输入面板 -->
    <GlassCard title="真实估值｜输入面板" :hover="false">
      <div class="grid gap-3 md:grid-cols-4">
        <Field label="报价（元/月）" v-model.number="form.asking_rent" type="number" />
        <Field label="面积（㎡）" v-model.number="form.area_sqm" type="number" />
        <Field label="楼层" v-model.number="form.floor" type="number" />
        <Field label="总楼层" v-model.number="form.total_floors" type="number" />
        <Field label="朝向" v-model="form.orientation" placeholder="南/北/东/西/东南" />
        <Field label="装修" v-model="form.decoration" placeholder="豪装/精装/简装/毛坯" />
        <Field label="地铁距离（m）" v-model.number="form.subway_distance_m" type="number" />
        <Field label="通勤时间（min）" v-model.number="form.commute_minutes" type="number" />
      </div>

      <div class="mt-4 flex flex-wrap items-center gap-3">
        <label class="flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200/60 bg-slate-50/50 px-4 py-2 text-xs text-slate-600">
          <input v-model="form.has_elevator" type="checkbox" class="h-4 w-4 accent-lime-500" />
          有电梯
        </label>

        <NeonButton :loading="loading" @click="run">执行估值</NeonButton>
        <NeonButton variant="ghost" @click="reset">重置</NeonButton>
      </div>

      <div class="mt-4 rounded-xl border border-slate-200/60 bg-slate-50/50 p-3">
        <div class="text-xs text-slate-500 mb-1">输出说明</div>
        <div class="text-xs text-slate-600">基于 Hedonic 特征价格模型，输出合理租金区间 + 偏离度 + 因素贡献瀑布图 + 对标样本，用于理解与议价。</div>
      </div>
    </GlassCard>

    <!-- 估值结论 -->
    <div v-if="loading || result" class="grid gap-4 md:grid-cols-3">
      <!-- 左侧：核心结论 -->
      <div class="space-y-4">
        <GlassCard title="合理租金区间" :hover="false">
          <div v-if="loading" class="skeleton h-16 rounded-xl"></div>
          <div v-else-if="result" class="text-center py-4">
            <div class="text-3xl font-bold text-slate-800">{{ result.fair_rent_low }} ~ {{ result.fair_rent_high }}</div>
            <div class="mt-2 flex items-center justify-center gap-3 text-sm">
              <span :class="result.deviation_pct > 0 ? 'text-sky-500' : 'text-lime-600'">
                偏离：{{ result.deviation_pct }}%
              </span>
              <span class="text-slate-400" v-if="result.deviation_pct > 10">⚠ 报价偏高</span>
              <span class="text-slate-400" v-else-if="result.deviation_pct < -5">✓ 性价比高</span>
            </div>
          </div>
        </GlassCard>

        <GlassCard title="因素贡献 TOP" :hover="false">
          <div v-if="loading" class="space-y-4">
            <div v-for="i in 4" :key="i" class="skeleton h-12 rounded-xl"></div>
          </div>
          <div v-else-if="result" class="space-y-4">
            <div v-for="f in result.factors" :key="f.name" class="group">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-slate-700 group-hover:text-lime-600 transition-colors">{{ f.name }}</span>
                <span class="text-xs font-semibold" :class="f.value >= 0 ? 'text-lime-600' : 'text-sky-500'">
                  {{ f.value > 0 ? '+' : '' }}{{ f.value }} 元
                </span>
              </div>
              <div class="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div 
                  class="h-full transition-all duration-700 ease-out"
                  :style="{ width: Math.min(Math.abs(f.value) / 10, 100) + '%' }"
                  :class="f.value >= 0 ? 'bg-lime-400' : 'bg-sky-400'"
                ></div>
              </div>
            </div>
          </div>
        </GlassCard>
        
        <GlassCard title="同区标杆对比" :hover="false">
          <div class="space-y-3">
            <template v-if="loading">
              <div v-for="i in 3" :key="i" class="skeleton h-10 rounded-xl"></div>
            </template>
            <template v-else-if="result">
              <div v-for="b in result.benchmarks" :key="b.name" class="p-3 rounded-xl border border-slate-100 bg-slate-50/50 flex items-center justify-between hover:border-lime-200 transition-all">
                <div class="text-sm text-slate-600">{{ b.name }}</div>
                <div class="text-sm font-bold text-slate-800">¥{{ b.rent }} <span class="text-[10px] font-normal text-slate-400">/月</span></div>
              </div>
            </template>
            <div class="mt-6 p-4 rounded-xl bg-lime-50/50 border border-lime-100 italic text-xs text-lime-700 leading-relaxed">
              注：估值与风控用于辅助决策，建议结合实地勘察。青居智算致力于为毕业生扫清租房陷阱。
            </div>
          </div>
        </GlassCard>
      </div>

      <!-- 对标样本（全宽） -->
      <GlassCard v-if="result && result.comparable_samples?.length" class="md:col-span-3" title="对标样本" :hover="false">
        <div class="grid gap-3 md:grid-cols-3">
          <div v-for="(c, idx) in result.comparable_samples" :key="idx" class="rounded-xl border border-slate-200/60 bg-slate-50/50 p-3">
            <div class="text-sm font-semibold truncate">{{ c.title }}</div>
            <div class="mt-1 text-xs text-slate-500">租金：{{ c.rent }} ｜相似度：{{ Math.round(c.similarity * 100) }}%</div>
            <div class="mt-1 text-xs text-slate-400">{{ c.note }}</div>
          </div>
        </div>
      </GlassCard>
    </div>

    <!-- 空状态 -->
    <EmptyState
      v-else-if="!listingId"
      icon="🔍"
      title="请先在房源列表选择房源"
      description="估值引擎需要房源的特征数据（位置、面积、装修等）作为输入，点击下方按钮前往。"
      action-text="浏览房源列表"
      @action="$router.push('/listings')"
    />
    <div v-else class="skeleton h-96 rounded-2xl"></div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { useRoute } from 'vue-router'

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

const form = reactive({
  asking_rent: 5200,
  area_sqm: 32,
  floor: 10,
  total_floors: 18,
  orientation: '南',
  decoration: '精装',
  has_elevator: true,
  subway_distance_m: 380,
  commute_minutes: 28
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

const run = async () => {
  loading.value = true
  try {
    result.value = await estimate({ ...form })
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '估值已生成（含因素解释与对标样本）' } }))
  } finally {
    loading.value = false
  }
}

const reset = () => {
  result.value = null
  form.asking_rent = 0
  form.area_sqm = 0
  form.floor = 0
  form.total_floors = 0
  form.orientation = ''
  form.decoration = ''
  form.has_elevator = false
  form.subway_distance_m = 0
  form.commute_minutes = 0
}

onMounted(async () => {
  if (listingId.value) {
    try {
      loading.value = true
      listing.value = await getListing(listingId.value)
      if (listing.value) {
        form.asking_rent = listing.value.asking_rent || 0
        form.area_sqm = listing.value.area_sqm || 0
        form.floor = 10
        form.total_floors = 18
        form.orientation = listing.value.orientation || '南'
        form.decoration = listing.value.decoration || '精装'
        form.has_elevator = listing.value.has_elevator || false
        form.subway_distance_m = listing.value.subway_distance_m || 500
        form.commute_minutes = listing.value.commute_minutes || 30
      }
    } finally {
      loading.value = false
    }
  }
})
</script>
