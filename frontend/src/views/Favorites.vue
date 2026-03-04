<template>
  <div class="space-y-6">
    <GlassCard title="我的收藏｜快速查看关注的房源" :hover="false">
      <div class="flex items-center justify-between">
        <div class="text-sm text-slate-500">
          共 <span class="text-sky-500 font-semibold">{{ favoritesStore.favorites.length }}</span> 套收藏房源
        </div>
        <div class="flex gap-2">
          <NeonButton size="sm" variant="ghost" @click="exportFavorites">导出列表</NeonButton>
          <NeonButton size="sm" variant="ghost" @click="clearAll" v-if="favoritesStore.favorites.length > 0">清空</NeonButton>
        </div>
      </div>
    </GlassCard>

    <div v-if="favoritesStore.favorites.length === 0" class="py-16 text-center">
      <EmptyState
        icon="♡"
        title="暂无收藏"
        description="在房源列表中点击收藏按钮，将感兴趣的房源添加到这里"
        action-text="去浏览房源"
        @action="$router.push('/listings')"
      />
    </div>

    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="fav in favoritesStore.favorites"
        :key="fav.id"
        class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4 transition-all hover:-translate-y-1 hover:bg-white/8"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-sky-500">♥</span>
              <span class="truncate font-semibold">{{ fav.title }}</span>
            </div>
            <div class="mt-1 flex flex-wrap gap-2 text-xs text-slate-500">
              <span>{{ fav.city }}·{{ fav.district }}</span>
              <span>•</span>
              <span>{{ fav.area_sqm }}㎡</span>
            </div>
            <div class="mt-1 text-xs text-slate-400">
              收藏于 {{ formatDate(fav.added_at) }}
            </div>
          </div>
          <div class="text-right">
            <div class="text-lg font-semibold text-lime-600">¥{{ fav.asking_rent }}</div>
          </div>
        </div>

        <div class="mt-4 flex gap-2">
          <NeonButton size="sm" variant="ghost" @click="goDetail(fav.id)">查看</NeonButton>
          <NeonButton size="sm" variant="ghost" @click="quickCompare(fav.id)">对比</NeonButton>
          <NeonButton size="sm" variant="ghost" @click="remove(fav.id)">移除</NeonButton>
        </div>
      </div>
    </div>

    <GlassCard title="快捷对比｜选择收藏房源进行横向对比" :hover="false" v-if="favoritesStore.favorites.length >= 2">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="fav in favoritesStore.favorites.slice(0, 6)"
          :key="fav.id"
          @click="toggleCompareSelection(fav.id)"
          class="rounded-full border px-3 py-1.5 text-sm transition-all"
          :class="compareSelection.includes(fav.id) ? 'border-lime-300 bg-lime-50 text-lime-600' : 'border-slate-200/60 bg-slate-50 text-slate-500'"
        >
          #{{ fav.id }} {{ fav.title.slice(0, 10) }}...
        </button>
      </div>
      <div class="mt-4 flex items-center gap-4">
        <div class="text-sm text-slate-500">
          已选择 {{ compareSelection.length }} 套
        </div>
        <NeonButton
          size="sm"
          @click="startCompare"
          :disabled="compareSelection.length < 2"
        >
          开始对比
        </NeonButton>
      </div>
    </GlassCard>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFavoritesStore } from '../stores/favorites'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import EmptyState from '../components/EmptyState.vue'

const router = useRouter()
const favoritesStore = useFavoritesStore()
const compareSelection = ref([])

const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

const remove = (id) => {
  favoritesStore.removeFavorite(id)
  window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'info', message: '已移除收藏' } }))
}

const clearAll = () => {
  if (confirm('确定清空所有收藏？')) {
    favoritesStore.clearFavorites()
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'info', message: '收藏已清空' } }))
  }
}

const goDetail = (id) => {
  router.push({ path: '/estimate', query: { listing_id: id } })
}

const quickCompare = (id) => {
  router.push({ path: '/compare', query: { ids: id } })
}

const toggleCompareSelection = (id) => {
  const idx = compareSelection.value.indexOf(id)
  if (idx > -1) {
    compareSelection.value.splice(idx, 1)
  } else if (compareSelection.value.length < 6) {
    compareSelection.value.push(id)
  } else {
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'warning', message: '最多选择6套对比' } }))
  }
}

const startCompare = () => {
  router.push({ path: '/compare', query: { ids: compareSelection.value.join(',') } })
}

const exportFavorites = () => {
  if (favoritesStore.favorites.length === 0) {
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'warning', message: '收藏列表为空' } }))
    return
  }
  const text = favoritesStore.favorites.map(f =>
    `#${f.id} ${f.title} | ¥${f.asking_rent} | ${f.city}·${f.district} | ${f.area_sqm}㎡`
  ).join('\n')
  
  // 创建下载文件
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `收藏列表_${new Date().toLocaleDateString()}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '收藏列表已导出' } }))
}
</script>
