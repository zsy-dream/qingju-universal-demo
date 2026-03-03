<template>
  <div class="grid gap-4 lg:grid-cols-3">
    <GlassCard class="lg:col-span-2" title="证据采集｜关联房源" :hover="false">
      <div class="space-y-4">
        <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
          <div class="text-xs tracking-widest text-slate-500">选择房源</div>
          <select
            v-model="selectedListingId"
            class="mt-2 w-full rounded-2xl border border-slate-200/60 bg-slate-50 px-4 py-3 text-sm text-slate-800 focus:border-lime-400 focus:outline-none"
            :disabled="listingsLoading"
          >
            <option value="" class="bg-white text-slate-800">
              {{ listingsLoading ? '加载中...' : (listings.length ? '请选择要采集证据的房源' : '暂无房源，请先导入') }}
            </option>
            <option v-for="l in listings" :key="l.id" :value="l.id" class="bg-white text-slate-800">
              #{{ l.id }} {{ l.title }} ({{ l.city }}{{ l.district }})
            </option>
          </select>
        </div>

        <div v-if="selectedListingId" class="grid gap-3 md:grid-cols-2">
          <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
            <div class="text-xs tracking-widest text-slate-500">风险标签</div>
            <select
              v-model="newEvidence.risk_tag"
              class="mt-2 w-full rounded-xl border border-slate-200/60 bg-slate-50 px-3 py-2 text-sm text-slate-800"
            >
              <option value="" class="bg-white text-slate-800">通用证据</option>
              <option value="noise" class="bg-white text-slate-800">噪音</option>
              <option value="mold" class="bg-white text-slate-800">潮湿/霉变</option>
              <option value="light" class="bg-white text-slate-800">采光</option>
              <option value="appliances" class="bg-white text-slate-800">设备老化</option>
              <option value="contract" class="bg-white text-slate-800">合同条款</option>
              <option value="sublease" class="bg-white text-slate-800">二房东/转租</option>
            </select>
          </div>

          <div class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
            <div class="text-xs tracking-widest text-slate-500">来源类型</div>
            <select
              v-model="newEvidence.source_type"
              class="mt-2 w-full rounded-xl border border-slate-200/60 bg-slate-50 px-3 py-2 text-sm text-slate-800"
            >
              <option value="user" class="bg-white text-slate-800">本人实拍</option>
              <option value="landlord" class="bg-white text-slate-800">房东提供</option>
              <option value="other" class="bg-white text-slate-800">其他来源</option>
            </select>
          </div>
        </div>

        <div v-if="selectedListingId">
          <div class="text-xs tracking-widest text-slate-500">证据备注</div>
          <textarea
            v-model="newEvidence.note"
            rows="2"
            class="mt-2 w-full rounded-2xl border border-slate-200/60 bg-slate-50 px-4 py-3 text-sm text-slate-800 focus:border-lime-400 focus:outline-none"
            placeholder="描述证据内容（如：卧室窗户正对施工工地，噪音约70dB）"
          />
        </div>

        <div v-if="selectedListingId" class="rounded-2xl border border-dashed border-slate-100 bg-slate-50 p-6 text-center">
          <input
            type="file"
            accept="image/*,video/*"
            class="hidden"
            @change="handleFile"
            ref="fileInput"
          />
          <NeonButton variant="ghost" @click="$refs.fileInput.click()">
            {{ previewUrl ? '更换文件' : '选择图片/视频' }}
          </NeonButton>
          <div class="mt-2 text-xs text-slate-400">支持 JPG/PNG/MP4，最大 10MB</div>

          <div v-if="previewUrl" class="mt-4">
            <img
              v-if="isImage"
              :src="previewUrl"
              class="mx-auto max-h-48 rounded-2xl border border-slate-200/60 object-contain"
            />
            <video
              v-else
              :src="previewUrl"
              controls
              class="mx-auto max-h-48 rounded-2xl border border-slate-200/60"
            />
          </div>
        </div>

        <div v-if="selectedListingId" class="flex gap-3">
          <NeonButton :loading="uploading" @click="submitEvidence">提交证据</NeonButton>
          <NeonButton variant="ghost" @click="resetForm">重置</NeonButton>
        </div>
      </div>
    </GlassCard>

    <GlassCard title="已采集证据" :hover="false">
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 3" :key="i" class="skeleton h-20 rounded-2xl"></div>
      </div>

      <div v-else-if="evidenceList.length === 0" class="py-8 text-center text-sm text-slate-400">
        {{ selectedListingId ? '暂无证据，请先采集' : '请先选择房源' }}
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="e in evidenceList"
          :key="e.id"
          class="rounded-2xl border border-slate-200/60 bg-slate-50 p-3 transition-all duration-200 hover:-translate-y-[1px] hover:bg-white/8"
        >
          <div class="flex items-start justify-between gap-2">
            <div>
              <div class="flex items-center gap-2">
                <span
                  class="rounded-full px-2 py-0.5 text-[10px] uppercase tracking-wider"
                  :class="tagColor(e.risk_tag)"
                >
                  {{ e.risk_tag || '通用' }}
                </span>
                <span class="text-[10px] text-slate-400">{{ e.source_type }}</span>
              </div>
              <div class="mt-1 text-xs text-slate-600 line-clamp-2">{{ e.note || '无备注' }}</div>
            </div>
            <button
              @click="deleteItem(e.id)"
              class="rounded-lg p-1 text-slate-400 transition-colors hover:bg-slate-50 hover:text-sky-500"
            >
              ×
            </button>
          </div>
          <div v-if="e.content" class="mt-2">
            <img
              v-if="isImageUrl(e.content)"
              :src="e.content"
              class="h-24 w-full rounded-xl border border-slate-200/60 object-cover"
            />
            <div v-else class="rounded-xl border border-slate-200/60 bg-slate-50 px-3 py-2 text-xs text-slate-400">
              文件已上传
            </div>
          </div>
        </div>
      </div>
    </GlassCard>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import { listListings, createEvidence, listEvidence, deleteEvidence } from '../api/qingju'

const listings = ref([])
const selectedListingId = ref('')
const evidenceList = ref([])
const loading = ref(false)
const uploading = ref(false)
const listingsLoading = ref(false)

const newEvidence = ref({
  risk_tag: '',
  source_type: 'user',
  note: '',
  content: ''
})

const previewUrl = ref('')
const isImage = ref(true)
const fileInput = ref(null)

const isImageUrl = (url) => {
  return url && !url.endsWith('.mp4') && !url.endsWith('.mov')
}

const tagColor = (tag) => {
  const map = {
    noise: 'bg-sky-100 text-sky-700 border border-sky-200',
    mold: 'bg-amber-100 text-amber-700 border border-amber-200',
    light: 'bg-lime-100 text-lime-700 border border-lime-200',
    appliances: 'bg-slate-100 text-slate-600 border border-slate-200',
    contract: 'bg-sky-100 text-sky-700 border border-sky-200',
    sublease: 'bg-amber-100 text-amber-700 border border-amber-200'
  }
  return map[tag] || 'bg-slate-100 text-slate-500 border border-slate-200'
}

const handleFile = (e) => {
  const file = e.target.files[0]
  if (!file) return

  isImage.value = file.type.startsWith('image/')
  const reader = new FileReader()
  reader.onload = (evt) => {
    previewUrl.value = evt.target.result
    newEvidence.value.content = evt.target.result
  }
  reader.readAsDataURL(file)
}

const submitEvidence = async () => {
  if (!selectedListingId.value) return
  uploading.value = true
  try {
    await createEvidence({
      listing_id: Number(selectedListingId.value),
      ...newEvidence.value
    })
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '证据已保存' } }))
    resetForm()
    loadEvidence()
  } finally {
    uploading.value = false
  }
}

const resetForm = () => {
  newEvidence.value = { risk_tag: '', source_type: 'user', note: '', content: '' }
  previewUrl.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

const loadEvidence = async () => {
  if (!selectedListingId.value) {
    evidenceList.value = []
    return
  }
  loading.value = true
  try {
    evidenceList.value = await listEvidence(Number(selectedListingId.value))
  } finally {
    loading.value = false
  }
}

const deleteItem = async (id) => {
  await deleteEvidence(id)
  window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '证据已删除' } }))
  loadEvidence()
}

watch(selectedListingId, loadEvidence)

onMounted(async () => {
  listingsLoading.value = true
  try {
    listings.value = await listListings(50)
  } catch (e) {
    console.error('Failed to load listings:', e)
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: '房源加载失败' } }))
  } finally {
    listingsLoading.value = false
  }
})
</script>
