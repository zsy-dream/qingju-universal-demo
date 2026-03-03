<template>
  <router-link
    :to="to"
    class="group relative flex items-center gap-1.5 whitespace-nowrap rounded-xl border px-2.5 py-1.5 text-xs font-medium transition-all"
    :class="$route.path.startsWith(to) 
      ? 'border-lime-300 bg-lime-50 text-lime-700 shadow-sm' 
      : 'border-slate-200 bg-white text-slate-600 hover:border-lime-200 hover:bg-lime-50/50 hover:text-lime-600'"
  >
    <span v-if="icon" class="text-sm leading-none">{{ icon }}</span>
    <span class="relative z-10">{{ label }}</span>
  </router-link>
</template>

<script setup>
defineProps({
  to: { type: String, required: true },
  label: { type: String, required: true },
  icon: { type: String, default: '' }
})
</script>
