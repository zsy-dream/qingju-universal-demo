<template>
  <div class="space-y-6">
    <GlassCard title="租后问题记录｜事件时间线 + 证据闭环" :hover="false">
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Field label="关联房源ID" v-model.number="form.listing_id" type="number" />
        <Field label="问题标题" v-model="form.title" placeholder="如：卫生间漏水" />
        <div>
          <div class="mb-2 text-xs tracking-widest text-slate-500">问题分类</div>
          <select v-model="form.category" class="w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 focus:border-lime-400 focus:outline-none">
            <option value="维修">维修</option>
            <option value="噪音">噪音</option>
            <option value="漏水">漏水</option>
            <option value="邻里纠纷">邻里纠纷</option>
            <option value="设备故障">设备故障</option>
            <option value="其他">其他</option>
          </select>
        </div>
        <div>
          <div class="mb-2 text-xs tracking-widest text-slate-500">严重程度</div>
          <select v-model="form.severity" class="w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 focus:border-lime-400 focus:outline-none">
            <option value="轻微">轻微</option>
            <option value="一般">一般</option>
            <option value="严重">严重</option>
            <option value="紧急">紧急</option>
          </select>
        </div>
      </div>

      <div class="mt-4">
        <div class="mb-2 text-xs tracking-widest text-slate-500">问题描述</div>
        <textarea
          v-model="form.description"
          rows="3"
          class="w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-3 text-sm text-slate-800 focus:border-lime-400 focus:outline-none"
          placeholder="详细描述问题发生的时间、频率、影响范围等"
        />
      </div>

      <div class="mt-4 flex gap-3">
        <NeonButton :loading="creating" @click="create">记录问题</NeonButton>
        <NeonButton variant="ghost" @click="fillDemo">填入演示数据</NeonButton>
        <NeonButton variant="ghost" @click="reset">重置</NeonButton>
        <NeonButton size="sm" variant="ghost" @click="loadAll">查看全部</NeonButton>
      </div>
    </GlassCard>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="skeleton h-32 rounded-2xl"></div>
    </div>

    <div v-else-if="issues.length > 0" class="space-y-4">
      <div class="flex items-center justify-between">
        <div class="text-sm text-slate-500">共 {{ issues.length }} 条记录</div>
        <div class="flex gap-2">
          <button
            v-for="filter in ['全部', '处理中', '已解决']"
            :key="filter"
            @click="statusFilter = filter"
            class="rounded-full border px-3 py-1 text-xs"
            :class="statusFilter === filter ? 'border-lime-300 bg-lime-100 text-lime-700' : 'border-slate-200 text-slate-500'"
          >
            {{ filter }}
          </button>
        </div>
      </div>

      <div class="space-y-3">
        <div
          v-for="issue in filteredIssues"
          :key="issue.id"
          class="rounded-2xl border border-slate-200/60 bg-slate-50 p-4"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-center gap-3">
              <span class="flex h-10 w-10 items-center justify-center rounded-full text-lg" :class="categoryIconClass(issue.category)">
                {{ categoryIcon(issue.category) }}
              </span>
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-semibold">{{ issue.title }}</span>
                  <span class="rounded-full border px-2 py-0.5 text-[10px]" :class="severityBadgeClass(issue.severity)">
                    {{ issue.severity }}
                  </span>
                  <span class="rounded-full border px-2 py-0.5 text-[10px]" :class="statusBadgeClass(issue.status)">
                    {{ issue.status }}
                  </span>
                </div>
                <div class="mt-1 flex items-center gap-3 text-xs text-slate-400">
                  <span>{{ issue.category }}</span>
                  <span>•</span>
                  <span>房源#{{ issue.listing_id }}</span>
                  <span>•</span>
                  <span>{{ formatDate(issue.reported_at) }}</span>
                </div>
              </div>
            </div>
            <div class="flex gap-2">
              <button
                v-if="issue.status !== '已解决'"
                @click="resolveIssue(issue.id)"
                class="rounded-lg border border-lime-200 bg-lime-100 px-3 py-1 text-xs text-lime-700 hover:bg-lime-200"
              >
                标记解决
              </button>
              <button
                @click="deleteIssueById(issue.id)"
                class="rounded-lg border border-slate-200 bg-slate-100 px-3 py-1 text-xs text-slate-600 hover:bg-slate-200"
              >
                删除
              </button>
            </div>
          </div>

          <div class="mt-3 text-sm text-slate-800">{{ issue.description }}</div>

          <div v-if="issue.landlord_response || issue.resolution" class="mt-3 rounded-xl border border-slate-200/60 bg-slate-50 p-3">
            <div v-if="issue.landlord_response" class="mb-2">
              <div class="text-[10px] uppercase tracking-wider text-slate-400">房东/中介回应</div>
              <div class="text-sm text-slate-600">{{ issue.landlord_response }}</div>
            </div>
            <div v-if="issue.resolution">
              <div class="text-[10px] uppercase tracking-wider text-slate-400">解决方案</div>
              <div class="text-sm text-slate-600">{{ issue.resolution }}</div>
            </div>
          </div>

          <div v-if="editingId === issue.id" class="mt-3 rounded-xl border border-sky-200 bg-sky-50/30 p-3">
            <div class="mb-2 text-xs text-sky-600">更新处理记录</div>
            <input
              v-model="editForm.landlord_response"
              class="mb-2 w-full rounded-lg border border-slate-200/60 bg-slate-50 px-3 py-2 text-sm text-slate-800"
              placeholder="房东/中介回应"
            />
            <textarea
              v-model="editForm.resolution"
              rows="2"
              class="mb-2 w-full rounded-lg border border-slate-200/60 bg-slate-50 px-3 py-2 text-sm text-slate-800"
              placeholder="解决方案记录"
            />
            <div class="flex gap-2">
              <NeonButton size="sm" @click="saveEdit(issue.id)">保存</NeonButton>
              <NeonButton size="sm" variant="ghost" @click="editingId = null">取消</NeonButton>
            </div>
          </div>
          <button
            v-else
            @click="startEdit(issue)"
            class="mt-3 text-xs text-lime-500 hover:underline"
          >
            编辑处理记录
          </button>
        </div>
      </div>
    </div>

    <div v-else class="py-12 text-center">
      <div class="text-4xl mb-3">📋</div>
      <div class="text-sm text-slate-400">暂无问题记录</div>
      <div class="mt-2 text-xs text-slate-400">建议定期记录维修、噪音等事件，形成完整证据链</div>
    </div>

    <GlassCard v-if="issues.length > 0" title="沟通留痕模板" :hover="false">
      <div class="space-y-3">
        <div class="rounded-xl border border-lime-200 bg-lime-50/30 p-3">
          <div class="mb-2 text-xs text-lime-700">报修通知模板</div>
          <div class="text-sm text-slate-800">您好，我是[房间号]租客。发现[问题描述]，影响正常使用。请于[时间]前安排维修，如无法及时解决，请提供临时方案。谢谢。</div>
        </div>
        <div class="rounded-xl border border-sky-200 bg-sky-50/30 p-3">
          <div class="mb-2 text-xs text-sky-700">跟进催促模板</div>
          <div class="text-sm text-slate-800">关于[问题]的维修，已于[日期]反馈，目前仍未解决。请确认维修进度及预计完成时间。如本周内无法解决，我将寻求第三方协助。</div>
        </div>
        <div class="rounded-xl border border-amber-200 bg-amber-50/30 p-3">
          <div class="mb-2 text-xs text-amber-700">维权留证模板</div>
          <div class="text-sm text-slate-800">由于[问题]长期未解决，已严重影响居住。现正式提出[减租/解约/维修]要求。相关证据已保存，请于[日期]前书面回复处理方案。</div>
        </div>
      </div>
    </GlassCard>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import Field from '../components/Field.vue'
import { createIssue, listIssues, updateIssue, deleteIssue } from '../api/qingju'

const creating = ref(false)
const loading = ref(false)
const issues = ref([])
const statusFilter = ref('全部')

const form = ref({
  listing_id: 1,
  title: '',
  category: '维修',
  severity: '一般',
  description: ''
})

const editingId = ref(null)
const editForm = ref({
  status: '处理中',
  landlord_response: '',
  resolution: ''
})

const filteredIssues = computed(() => {
  if (statusFilter.value === '全部') return issues.value
  return issues.value.filter(i => i.status === statusFilter.value)
})

const categoryIcon = (cat) => {
  const map = { '维修': '🔧', '噪音': '🔊', '漏水': '💧', '邻里纠纷': '👥', '设备故障': '⚡', '其他': '📝' }
  return map[cat] || '📝'
}

const categoryIconClass = (cat) => {
  const map = {
    '维修': 'bg-lime-500/10 text-lime-600',
    '噪音': 'bg-sky-500/10 text-sky-500',
    '漏水': 'bg-blue-400/10 text-blue-400',
    '邻里纠纷': 'bg-amber-400/10 text-amber-600',
    '设备故障': 'bg-yellow-400/10 text-yellow-400',
    '其他': 'bg-slate-50 text-slate-500'
  }
  return map[cat] || 'bg-slate-50 text-slate-500'
}

const severityBadgeClass = (s) => {
  const map = {
    '轻微': 'border-slate-200 bg-slate-100 text-slate-600',
    '一般': 'border-lime-200 bg-lime-100 text-lime-700',
    '严重': 'border-sky-200 bg-sky-100 text-sky-700',
    '紧急': 'border-amber-200 bg-amber-100 text-amber-700'
  }
  return map[s] || 'border-slate-200 bg-slate-100'
}

const statusBadgeClass = (s) => {
  const map = {
    '处理中': 'border-lime-200 bg-lime-100 text-lime-700',
    '已解决': 'border-slate-200 bg-slate-100 text-slate-600'
  }
  return map[s] || 'border-slate-200 bg-slate-100'
}

const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

const create = async () => {
  if (!form.value.title || !form.value.description) {
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: '请填写标题和描述' } }))
    return
  }
  creating.value = true
  try {
    await createIssue({ ...form.value, evidence_ids: [] })
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '问题已记录' } }))
    reset()
    await loadAll()
  } finally {
    creating.value = false
  }
}

const loadAll = async () => {
  loading.value = true
  try {
    issues.value = await listIssues()
  } finally {
    loading.value = false
  }
}

const resolveIssue = async (id) => {
  await updateIssue(id, { status: '已解决', landlord_response: '', resolution: '' })
  window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '已标记为已解决' } }))
  await loadAll()
}

const deleteIssueById = async (id) => {
  await deleteIssue(id)
  window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '记录已删除' } }))
  await loadAll()
}

const startEdit = (issue) => {
  editingId.value = issue.id
  editForm.value = {
    status: issue.status,
    landlord_response: issue.landlord_response || '',
    resolution: issue.resolution || ''
  }
}

const saveEdit = async (id) => {
  await updateIssue(id, editForm.value)
  editingId.value = null
  window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '处理记录已更新' } }))
  await loadAll()
}

const fillDemo = () => {
  form.value = {
    listing_id: 1,
    title: '卫生间洗手台下水慢',
    category: '维修',
    severity: '一般',
    description: '入住后发现洗手台下水明显比看房时慢，疑似管道堵塞。已尝试自行疏通无效，需要房东安排专业维修。'
  }
}

const reset = () => {
  form.value = {
    listing_id: 1,
    title: '',
    category: '维修',
    severity: '一般',
    description: ''
  }
}

onMounted(() => {
  loadAll()
})
</script>
