import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useFavoritesStore = defineStore('favorites', () => {
  // State
  const favorites = ref([])
  const history = ref([])

  // Load from localStorage safely
  if (typeof window !== 'undefined') {
    favorites.value = JSON.parse(localStorage.getItem('qingju_favorites') || '[]')
    history.value = JSON.parse(localStorage.getItem('qingju_history') || '[]')
  }

  // Getters
  const favoriteIds = computed(() => favorites.value.map(f => f.id))
  const isFavorite = computed(() => (id) => favoriteIds.value.includes(id))
  const historyCount = computed(() => history.value.length)

  // Actions
  const saveFavorites = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('qingju_favorites', JSON.stringify(favorites.value))
    }
  }

  const saveHistory = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('qingju_history', JSON.stringify(history.value.slice(0, 50)))
    }
  }

  const addFavorite = (listing) => {
    if (!isFavorite(listing.id)) {
      favorites.value.unshift({
        id: listing.id,
        title: listing.title,
        asking_rent: listing.asking_rent,
        city: listing.city,
        district: listing.district,
        area_sqm: listing.area_sqm,
        added_at: new Date().toISOString()
      })
      saveFavorites()
    }
  }

  const removeFavorite = (id) => {
    favorites.value = favorites.value.filter(f => f.id !== id)
    saveFavorites()
  }

  const toggleFavorite = (listing) => {
    if (isFavorite(listing.id)) {
      removeFavorite(listing.id)
      return false
    } else {
      addFavorite(listing)
      return true
    }
  }

  const addHistory = (action, data) => {
    history.value.unshift({
      action,
      data,
      timestamp: new Date().toISOString()
    })
    if (history.value.length > 50) {
      history.value = history.value.slice(0, 50)
    }
    saveHistory()
  }

  const clearHistory = () => {
    history.value = []
    saveHistory()
  }

  const clearFavorites = () => {
    favorites.value = []
    saveFavorites()
  }

  return {
    favorites,
    history,
    favoriteIds,
    isFavorite,
    historyCount,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    addHistory,
    clearHistory,
    clearFavorites
  }
})
