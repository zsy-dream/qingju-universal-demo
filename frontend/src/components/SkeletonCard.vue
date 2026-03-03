<template>
  <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-6" :class="className">
    <div class="flex items-start justify-between">
      <div class="space-y-3 flex-1">
        <div class="skeleton h-4 w-1/3 rounded"></div>
        <div class="skeleton h-8 w-1/2 rounded-xl"></div>
        <div class="skeleton h-3 w-2/3 rounded"></div>
      </div>
      <div class="skeleton h-10 w-10 rounded-full"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  className: { type: String, default: '' }
})
</script>
