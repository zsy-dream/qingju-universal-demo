<template>
  <div class="fixed right-4 top-20 z-50 flex w-[320px] flex-col gap-2">
    <div
      v-for="t in store.toasts"
      :key="t.id"
      class="rounded-2xl border border-slate-200/60 bg-panel/70 p-3 backdrop-blur-xl shadow-neon"
    >
      <div class="flex items-start gap-3">
        <div class="mt-0.5 h-2.5 w-2.5 rounded-full" :class="dotClass(t.type)"></div>
        <div>
          <div class="text-xs tracking-widest text-slate-500">SYSTEM</div>
          <div class="text-sm leading-snug">{{ t.message }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useAppStore } from '../stores/app'

const store = useAppStore()

const onToast = (e) => {
  store.pushToast(e.detail || {})
}

onMounted(() => window.addEventListener('app:toast', onToast))
onUnmounted(() => window.removeEventListener('app:toast', onToast))

const dotClass = (type) => {
  if (type === 'success') return 'bg-lime-500 animate-glow'
  if (type === 'error') return 'bg-sky-500 animate-glow'
  return 'bg-brandAccent animate-glow'
}
</script>
