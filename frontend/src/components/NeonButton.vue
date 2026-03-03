<template>
  <button
    :disabled="disabled || loading"
    :class="btnClass"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="mr-2 inline-flex h-3.5 w-3.5 items-center justify-center">
      <span class="h-3.5 w-3.5 rounded-full border-2 border-current/20 border-t-current animate-spin" />
    </span>
    <span class="relative z-10 font-bold"><slot /></span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'primary' }, // primary, secondary, ghost, outline
  size: { type: String, default: 'md' },        // sm, md, lg
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false }
})

const sizeClass = computed(() => {
  if (props.size === 'sm') return 'px-3 py-1.5 text-xs rounded-lg'
  if (props.size === 'lg') return 'px-10 py-3.5 text-base rounded-2xl'
  return 'px-7 py-2.5 text-sm rounded-xl'
})

const variantClass = computed(() => {
  if (props.variant === 'ghost') {
    return 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-800 border-slate-200 transition-all'
  }
  if (props.variant === 'secondary') {
    return 'bg-sky-50 text-sky-600 border-sky-200 hover:bg-sky-100 hover:border-sky-300 shadow-sm transition-all'
  }
  if (props.variant === 'outline') {
    return 'bg-white border-slate-200 text-slate-600 hover:border-lime-400 hover:text-lime-600 hover:bg-lime-50/30 shadow-sm transition-all'
  }
  // Default: Primary (Clean Lime)
  return 'bg-lime-500 text-white border-lime-500 shadow-btn hover:shadow-btnHover hover:bg-lime-600 hover:-translate-y-0.5 active:translate-y-0 active:scale-95 transition-all'
})

const btnClass = computed(() => {
  return [
    'group relative inline-flex items-center justify-center border leading-none tracking-wide text-center',
    'disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100 disabled:-translate-y-0',
    'focus-visible:ring-4 focus-visible:ring-lime-100 focus-visible:outline-none',
    sizeClass.value,
    variantClass.value
  ].join(' ')
})
</script>
