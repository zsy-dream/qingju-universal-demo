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
    <span v-if="badge" class="absolute -top-1 -right-1 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-sky-500 text-[9px] font-bold text-white shadow-sm ring-2 ring-white animate-pulse-short">
      {{ badge }}
    </span>
  </router-link>
</template>

<script setup>
defineProps({
  to: { type: String, required: true },
  label: { type: String, required: true },
  icon: { type: String, default: '' },
  badge: { type: [String, Number], default: '' }
})
</script>

<style>
.animate-pulse-short {
  animation: pulse-short 1s cubic-bezier(0.4, 0, 0.6, 1) 2;
}
@keyframes pulse-short {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: .7; transform: scale(1.2); }
}
</style>
