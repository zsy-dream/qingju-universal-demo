import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useFavoritesStore = defineStore('favorites', () => {
  // State
  const favorites = ref([])
  const history = ref([])

  // Load from localStorage safely
  if (typeof window !== 'undefined') {
    try {
      favorites.value = JSON.parse(localStorage.getItem('qingju_favorites') || '[]')
      history.value = JSON.parse(localStorage.getItem('qingju_history') || '[]')
    } catch (e) {
      console.error('Failed to load favorites from localStorage', e)
    }
  }

  // Getters
  // 确保 ID 统一为数值进行比较，防止 API 返回数值与前端字符串/数值不匹配
  const favoriteIds = computed(() => favorites.value.map(f => Number(f.id)))

  const isFavorite = computed(() => {
    return (id) => favoriteIds.value.includes(Number(id))
  })

  // Actions
  const saveFavorites = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('qingju_favorites', JSON.stringify(favorites.value))
    }
  }

  const addFavorite = (listing) => {
    const id = Number(listing.id)
    // 使用 .value 访问 computed 返回的函数
    if (!isFavorite.value(id)) {
      favorites.value.unshift({
        id: id,
        title: listing.title,
        asking_rent: listing.asking_rent,
        city: listing.city,
        district: listing.district,
        area_sqm: listing.area_sqm,
        added_at: new Date().toISOString()
      })
      saveFavorites()
      return true
    }
    return false
  }

  const removeFavorite = (id) => {
    const targetId = Number(id)
    favorites.value = favorites.value.filter(f => Number(f.id) !== targetId)
    saveFavorites()
  }

  const toggleFavorite = (listing) => {
    const id = Number(listing.id)
    if (isFavorite.value(id)) {
      removeFavorite(id)
      return false
    } else {
      return addFavorite(listing)
    }
  }

  const clearFavorites = () => {
    favorites.value = []
    saveFavorites()
  }

  return {
    favorites,
    favoriteIds,
    isFavorite,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    clearFavorites
  }
})
