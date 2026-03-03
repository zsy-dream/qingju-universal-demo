<template>
  <div class="flex flex-col items-center justify-center py-16 text-center">
    <div class="relative mb-6 flex h-24 w-24 items-center justify-center">
      <!-- 背景光晕 -->
      <div class="absolute inset-0 rounded-full bg-lime-500/10 blur-xl animate-pulse"></div>
      <!-- 扫描线动画 -->
      <div class="absolute inset-2 overflow-hidden rounded-full border border-slate-200/60">
        <div class="h-[2px] w-full bg-gradient-to-r from-transparent via-lime-400/50 to-transparent" style="animation: scanline 2s ease-in-out infinite"></div>
      </div>
      <!-- 图标 -->
      <div class="relative text-5xl">{{ icon }}</div>
    </div>
    
    <div class="text-lg font-medium text-slate-800">{{ title }}</div>
    <div class="mt-2 max-w-sm text-sm leading-relaxed text-slate-400">{{ description }}</div>
    
    <slot name="action">
      <NeonButton v-if="actionText" class="mt-6" size="sm" @click="$emit('action')">
        {{ actionText }}
      </NeonButton>
    </slot>
    
    <!-- 辅助提示 -->
    <div v-if="hint" class="mt-4 flex items-center gap-2 rounded-full border border-slate-200/60 bg-slate-50 px-4 py-1.5 text-xs text-slate-400">
      <span class="text-lime-500">💡</span> {{ hint }}
    </div>
  </div>
</template>

<script setup>
import NeonButton from './NeonButton.vue'

defineProps({
  icon: { type: String, default: '📭' },
  title: { type: String, default: '暂无数据' },
  description: { type: String, default: '当前没有符合条件的内容' },
  actionText: { type: String, default: '' },
  hint: { type: String, default: '' }
})

defineEmits(['action'])
</script>
