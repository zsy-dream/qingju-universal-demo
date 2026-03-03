<template>
  <div class="space-y-6">
    <GlassCard title="房源管理｜搜索 · 筛选 · 排序" :hover="false">
      <div class="grid gap-4 md:grid-cols-4">
        <div>
          <div class="mb-2 text-xs tracking-widest text-slate-500">搜索</div>
          <input
            v-model="filters.keyword"
            class="w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 focus:border-lime-400 focus:outline-none"
            placeholder="标题/区域/户型"
          />
        </div>
        <div>
          <div class="mb-2 text-xs tracking-widest text-slate-500">城市</div>
          <select v-model="filters.city" class="w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 focus:border-lime-400 focus:outline-none">
            <option value="">全部城市</option>
            <option value="北京">北京</option>
            <option value="上海">上海</option>
            <option value="广州">广州</option>
            <option value="深圳">深圳</option>
            <option value="杭州">杭州</option>
          </select>
        </div>
        <div>
          <div class="mb-2 text-xs tracking-widest text-slate-500">价格区间</div>
          <select v-model="filters.priceRange" class="w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 focus:border-lime-400 focus:outline-none">
            <option value="">全部价格</option>
            <option value="0-3000">3000以下</option>
            <option value="3000-5000">3000-5000</option>
            <option value="5000-8000">5000-8000</option>
            <option value="8000+">8000以上</option>
          </select>
        </div>
        <div>
          <div class="mb-2 text-xs tracking-widest text-slate-500">排序</div>
          <select v-model="sortBy" class="w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 focus:border-lime-400 focus:outline-none">
            <option value="newest">最新添加</option>
            <option value="price_asc">价格从低到高</option>
            <option value="price_desc">价格从高到低</option>
            <option value="area_asc">面积从小到大</option>
            <option value="commute">通勤时间</option>
          </select>
        </div>
      </div>

      <div class="mt-4 flex flex-wrap gap-2">
        <button
          v-for="tag in filterTags"
          :key="tag.key"
          @click="toggleTag(tag.key)"
          class="rounded-full border px-3 py-1 text-xs transition-all"
          :class="activeTags.includes(tag.key) ? 'border-lime-300 bg-lime-100 text-lime-700' : 'border-slate-200 bg-slate-50 text-slate-500'"
        >
          {{ tag.label }}
        </button>
      </div>

      <div class="mt-4 flex gap-3">
        <NeonButton @click="applyFilters">应用筛选</NeonButton>
        <NeonButton variant="ghost" @click="resetFilters">重置</NeonButton>
        <NeonButton size="sm" variant="ghost" @click="showAddModal = true">+ 新增房源</NeonButton>
      </div>
    </GlassCard>

    <div class="flex items-center justify-between">
      <div class="text-sm text-slate-500">
        共 <span class="text-lime-600 font-semibold">{{ filteredListings.length }}</span> 套房源
      </div>
      <div class="flex gap-2">
        <button
          @click="viewMode = 'grid'"
          class="rounded-lg border p-2"
          :class="viewMode === 'grid' ? 'border-lime-300 bg-lime-100 text-lime-700' : 'border-slate-200/60'"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
        </button>
        <button
          @click="viewMode = 'list'"
          class="rounded-lg border p-2"
          :class="viewMode === 'list' ? 'border-lime-300 bg-lime-100 text-lime-700' : 'border-slate-200 text-slate-500'"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
      </div>
    </div>

    <div v-if="loading" class="grid gap-4" :class="viewMode === 'grid' ? 'md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'">
      <div v-for="i in 6" :key="i" class="skeleton h-48 rounded-2xl"></div>
    </div>

    <div v-else-if="filteredListings.length === 0" class="py-16 text-center">
      <div class="text-4xl mb-3">🔍</div>
      <div class="text-sm text-slate-400">没有找到符合条件的房源</div>
      <div class="mt-2 text-xs text-slate-400">试试调整筛选条件</div>
    </div>

    <div v-else class="grid gap-4" :class="viewMode === 'grid' ? 'md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'">
      <div
        v-for="listing in filteredListings"
        :key="listing.id"
        class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4 transition-all hover:-translate-y-1 hover:bg-white/8"
        :class="{ 'opacity-50': listing.is_archived }"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-400">#{{ listing.id }}</span>
              <span class="truncate font-semibold">{{ listing.title }}</span>
            </div>
            <div class="mt-1 flex flex-wrap gap-2 text-xs text-slate-500">
              <span>{{ listing.city }}·{{ listing.district }}</span>
              <span>•</span>
              <span>{{ listing.area_sqm }}㎡</span>
              <span>•</span>
              <span>{{ listing.layout }}</span>
            </div>
          </div>
          <div class="text-right">
            <div class="text-lg font-semibold text-lime-600">¥{{ listing.asking_rent }}</div>
            <div class="text-xs text-slate-400">{{ Math.round(listing.asking_rent / listing.area_sqm) }}元/㎡</div>
          </div>
        </div>

        <div class="mt-3 flex flex-wrap gap-1">
          <span class="rounded-full border border-slate-200/60 bg-slate-50 px-2 py-0.5 text-[10px] text-slate-500">{{ listing.orientation }}</span>
          <span class="rounded-full border border-slate-200/60 bg-slate-50 px-2 py-0.5 text-[10px] text-slate-500">{{ listing.decoration }}</span>
          <span v-if="listing.has_elevator" class="rounded-full border border-lime-200 bg-lime-100 px-2 py-0.5 text-[10px] text-lime-700">电梯</span>
          <span class="rounded-full border border-slate-200/60 bg-slate-50 px-2 py-0.5 text-[10px] text-slate-500">{{ listing.commute_minutes }}分钟通勤</span>
        </div>

        <div class="mt-3 flex gap-2">
          <NeonButton size="sm" variant="ghost" @click="goEstimate(listing.id)">估值</NeonButton>
          <NeonButton size="sm" variant="ghost" @click="goRisk(listing.id)">风控</NeonButton>
          <NeonButton 
            size="sm" 
            variant="ghost" 
            @click="handleToggleFavorite(listing)"
            :class="favoritesStore.isFavorite(listing.id) ? 'text-amber-500 bg-amber-50 border-amber-200' : ''"
          >
            {{ favoritesStore.isFavorite(listing.id) ? '★ 已收藏' : '☆ 收藏' }}
          </NeonButton>
          <NeonButton size="sm" variant="ghost" @click="deleteListing(listing.id)">删除</NeonButton>
        </div>
      </div>
    </div>

    <div v-if="allListings.length > pageSize" class="flex justify-center gap-2">
      <NeonButton size="sm" variant="ghost" :disabled="page === 1" @click="page--">上一页</NeonButton>
      <span class="flex items-center px-3 text-sm text-slate-500">{{ page }} / {{ totalPages }}</span>
      <NeonButton size="sm" variant="ghost" :disabled="page >= totalPages" @click="page++">下一页</NeonButton>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFavoritesStore } from '../stores/favorites'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import { listListings, deleteListing as apiDeleteListing } from '../api/qingju'

const router = useRouter()
const favoritesStore = useFavoritesStore()
const loading = ref(false)
const allListings = ref([])
const viewMode = ref('grid')
const page = ref(1)
const pageSize = 12

const filters = ref({
  keyword: '',
  city: '',
  priceRange: '',
  hasElevator: false,
  nearSubway: false
})

const sortBy = ref('newest')
const activeTags = ref([])

const filterTags = [
  { key: 'elevator', label: '有电梯' },
  { key: 'subway', label: '近地铁(<500m)' },
  { key: 'south', label: '朝南' },
  { key: 'decorated', label: '精装' }
]

const toggleTag = (key) => {
  const idx = activeTags.value.indexOf(key)
  if (idx > -1) activeTags.value.splice(idx, 1)
  else activeTags.value.push(key)
}

const filteredListings = computed(() => {
  let result = [...allListings.value]

  if (filters.value.keyword) {
    const kw = filters.value.keyword.toLowerCase()
    result = result.filter(l => 
      l.title?.toLowerCase().includes(kw) ||
      l.city?.includes(kw) ||
      l.district?.includes(kw) ||
      l.layout?.includes(kw)
    )
  }

  if (filters.value.city) {
    result = result.filter(l => l.city === filters.value.city)
  }

  if (filters.value.priceRange) {
    const [min, max] = filters.value.priceRange.split('-').map(x => x === '8000+' ? 8000 : parseInt(x))
    result = result.filter(l => {
      if (filters.value.priceRange === '8000+') return l.asking_rent >= 8000
      return l.asking_rent >= min && l.asking_rent <= max
    })
  }

  if (activeTags.value.includes('elevator')) {
    result = result.filter(l => l.has_elevator)
  }
  if (activeTags.value.includes('subway')) {
    result = result.filter(l => l.subway_distance_m < 500)
  }
  if (activeTags.value.includes('south')) {
    result = result.filter(l => l.orientation?.includes('南'))
  }
  if (activeTags.value.includes('decorated')) {
    result = result.filter(l => l.decoration === '精装' || l.decoration === '豪装')
  }

  switch (sortBy.value) {
    case 'price_asc':
      result.sort((a, b) => a.asking_rent - b.asking_rent)
      break
    case 'price_desc':
      result.sort((a, b) => b.asking_rent - a.asking_rent)
      break
    case 'area_asc':
      result.sort((a, b) => a.area_sqm - b.area_sqm)
      break
    case 'commute':
      result.sort((a, b) => a.commute_minutes - b.commute_minutes)
      break
    case 'newest':
    default:
      result.sort((a, b) => b.id - a.id)
  }

  const start = (page.value - 1) * pageSize
  return result.slice(start, start + pageSize)
})

const totalPages = computed(() => Math.ceil(allListings.value.length / pageSize))

const loadListings = async () => {
  loading.value = true
  try {
    allListings.value = await listListings(100)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  page.value = 1
}

const resetFilters = () => {
  filters.value = { keyword: '', city: '', priceRange: '', hasElevator: false, nearSubway: false }
  activeTags.value = []
  sortBy.value = 'newest'
  page.value = 1
}

const goEstimate = (id) => {
  router.push({ path: '/estimate', query: { listing_id: id } })
}

const goRisk = (id) => {
  router.push({ path: '/risk', query: { listing_id: id } })
}

const handleToggleFavorite = (listing) => {
  const isNowFavorite = favoritesStore.toggleFavorite(listing)
  const message = isNowFavorite ? '已加入收藏夹' : '已取消收藏'
  const type = isNowFavorite ? 'success' : 'info'
  window.dispatchEvent(new CustomEvent('app:toast', { detail: { type, message } }))
}

const deleteListing = async (id) => {
  if (!confirm('确定删除此房源？')) return
  await apiDeleteListing(id)
  window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '已删除' } }))
  await loadListings()
}

onMounted(() => {
  loadListings()
})
</script>
