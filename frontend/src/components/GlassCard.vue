<template>
  <div :class="wrapClass">
    <div class="relative h-full rounded-card border border-slate-200 bg-white shadow-card transition-all duration-300 group-hover:shadow-cardHover group-hover:border-lime-100 overflow-hidden">
      <!-- 极度克制的顶部标识线 -->
      <div v-if="accent" class="absolute left-0 right-0 top-0 h-[3px] bg-gradient-to-r from-lime-400 to-sky-400 opacity-60" />
      
      <!-- 极微弱的背景纹理 (仅在非常大面积时可见，营造Notion感) -->
      <div class="pointer-events-none absolute left-0 top-0 h-32 w-32 opacity-[0.03]" 
        style="background: radial-gradient(circle at 10% 10%, #84cc16, transparent 60%);" 
      />

      <div v-if="title" class="flex items-start justify-between border-b border-slate-50 px-6 py-5">
        <div>
          <div class="text-[10px] font-bold uppercase tracking-[0.18em] text-lime-500 mb-0.5">QINGJU SYSTEM</div>
          <div class="text-lg font-bold tracking-tight text-slate-800">{{ title }}</div>
        </div>
        <div class="mt-1 flex items-center gap-2 text-xs text-slate-400">
          <slot name="meta" />
        </div>
      </div>

      <div class="px-6 py-6 h-full">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  hover: { type: Boolean, default: true },
  accent: { type: Boolean, default: false } // 是否在顶部显示彩色细线
})

const wrapClass = computed(() => {
  return [
    'relative group flex flex-col h-full',
    props.hover ? 'transition-all duration-300' : ''
  ].join(' ')
})
</script>
