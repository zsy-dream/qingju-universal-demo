<template>
  <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
    <div class="flex items-center justify-between">
      <div class="text-sm font-semibold">{{ label }}</div>
      <div class="text-xs text-slate-400">0/1/2</div>
    </div>

    <div class="mt-3 flex items-center gap-2">
      <button
        v-for="n in [0,1,2]"
        :key="n"
        @click="$emit('update:modelValue', n)"
        class="group relative flex-1 rounded-2xl border px-3 py-2 text-xs tracking-widest transition-all duration-200 hover:-translate-y-[1px]"
        :class="modelValue === n ? activeClass(n) : 'border-slate-200 bg-slate-100 text-slate-500 hover:bg-slate-200 hover:text-slate-700'"
      >
        <span class="relative z-10">{{ n === 0 ? '无' : n === 1 ? '疑似' : '确认' }}</span>
        <span class="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          style="background: radial-gradient(500px 120px at 20% 0%, rgba(236,72,153,0.18), transparent 60%), radial-gradient(520px 120px at 80% 100%, rgba(34,211,238,0.12), transparent 55%);"
        />
      </button>
    </div>

    <div class="mt-2 text-xs" :class="hintColor">
      {{ hint }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  modelValue: { type: Number, default: 0 }
})

defineEmits(['update:modelValue'])

const hint = computed(() => {
  if (props.modelValue === 0) return '无明显信号：仍建议按清单核验'
  if (props.modelValue === 1) return '疑似信号：建议补充证据与二次确认'
  return '确认信号：建议形成证据链并在签约前谈判/整改'
})

const hintColor = computed(() => {
  if (props.modelValue === 0) return 'text-slate-400'
  if (props.modelValue === 1) return 'text-lime-500'
  return 'text-sky-500'
})

const activeClass = (n) => {
  if (n === 0) return 'border-slate-300 bg-slate-200 text-slate-700'
  if (n === 1) return 'border-lime-300 bg-lime-100 text-lime-700'
  return 'border-amber-300 bg-amber-100 text-amber-700'
}
</script>
