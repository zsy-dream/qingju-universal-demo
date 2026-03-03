<template>
  <label class="group relative flex flex-col gap-1.5 w-full">
    <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400 pl-1 group-focus-within:text-lime-600 transition-colors">
      {{ label }}
    </span>
    <div class="relative w-full">
      <input
        :type="type"
        :placeholder="placeholder"
        :value="modelValue"
        @input="$emit('update:modelValue', cast($event.target.value))"
        class="w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-[13px] text-slate-900 shadow-sm transition-all placeholder:text-slate-300 hover:border-slate-300 focus:border-lime-500 focus:outline-none focus:ring-4 focus:ring-lime-100"
      />
    </div>
  </label>
</template>

<script setup>
const props = defineProps({
  label: { type: String, required: true },
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' }
})

defineEmits(['update:modelValue'])

const cast = (v) => {
  if (props.type === 'number') {
    const n = Number(v)
    return Number.isFinite(n) ? n : 0
  }
  return v
}
</script>
