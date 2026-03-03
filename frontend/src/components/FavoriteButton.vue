<template>
  <button
    @click="toggle"
    class="flex items-center gap-1 rounded-lg border px-3 py-1.5 text-sm transition-all"
    :class="isFav ? 'border-neonPink/50 bg-sky-500/10 text-sky-500' : 'border-slate-200/60 bg-slate-50 text-slate-500 hover:bg-white/8'"
  >
    <span class="text-lg">{{ isFav ? '♥' : '♡' }}</span>
    <span>{{ isFav ? '已收藏' : '收藏' }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useFavoritesStore } from '../stores/favorites'

const props = defineProps({
  listing: { type: Object, required: true }
})

const favoritesStore = useFavoritesStore()
const isFav = computed(() => favoritesStore.isFavorite(props.listing.id))

const toggle = () => {
  const result = favoritesStore.toggleFavorite(props.listing)
  window.dispatchEvent(new CustomEvent('app:toast', {
    detail: { type: result ? 'success' : 'info', message: result ? '已添加到收藏' : '已取消收藏' }
  }))
}
</script>
