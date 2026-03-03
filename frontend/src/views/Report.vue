<template>
  <div class="space-y-6">
    <GlassCard title="LLM 综合报告生成｜整合估值 + 风险 + 证据" :hover="false">
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Field label="房源标题" v-model="form.title" placeholder="如：地铁口南向一居" />
        <Field label="当前报价" v-model.number="form.asking_rent" type="number" />
        <Field label="合理区间下限" v-model.number="form.fair_rent_low" type="number" />
        <Field label="合理区间上限" v-model.number="form.fair_rent_high" type="number" />
        <Field label="偏离程度（%）" v-model.number="form.deviation_pct" type="number" />
        <Field label="风险评分（0-200）" v-model.number="form.risk_score" type="number" />
        <Field label="风险等级" v-model="form.risk_level" placeholder="可租/谨慎/不建议" />
        <Field label="证据数量" v-model.number="form.evidence_count" type="number" />
      </div>

      <div class="mt-4 rounded-2xl border border-slate-200/60 bg-slate-50 p-4">
        <div class="text-xs tracking-widest text-slate-500">风险项（JSON，可选）</div>
        <textarea
          v-model="risksJson"
          rows="2"
          class="mt-2 w-full rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-3 text-xs font-mono text-slate-800 focus:border-lime-400 focus:outline-none"
          placeholder='[{"name": "二房东风险", "contribution": 24}]'
        />
      </div>

      <div class="mt-4 flex gap-3">
        <NeonButton :loading="loading" @click="generate">生成综合报告</NeonButton>
        <NeonButton variant="ghost" @click="fillDemo">填入演示数据</NeonButton>
        <NeonButton variant="ghost" @click="reset">重置</NeonButton>
      </div>
    </GlassCard>

    <div v-if="report" class="space-y-4">
      <!-- 报告头部信息 -->
      <GlassCard :title="report.report_title" :hover="false">
        <div class="flex items-center justify-between rounded-xl border border-slate-200/60 bg-slate-50 px-4 py-3 mb-4">
          <div class="text-xs text-slate-500">生成时间：{{ report.generated_at }}</div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-500">置信度</span>
            <span class="text-lg font-semibold" :class="confidenceColor">{{ report.confidence_score }}%</span>
          </div>
        </div>

        <!-- 执行摘要 + 行动清单 并排 -->
        <div class="grid gap-4 md:grid-cols-2">
          <!-- 执行摘要 -->
          <div class="rounded-xl border border-lime-200 bg-lime-50/30 p-4">
            <div class="text-xs tracking-widest text-lime-700 mb-2 font-medium">执行摘要</div>
            <div class="whitespace-pre-wrap text-sm leading-relaxed text-slate-700">{{ report.executive_summary }}</div>
          </div>

          <!-- 行动清单 -->
          <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div class="text-xs tracking-widest text-slate-600 mb-3 font-medium">行动清单</div>
            <div class="space-y-2">
              <div
                v-for="(item, idx) in report.action_items"
                :key="idx"
                class="flex items-start gap-2 text-sm text-slate-700"
              >
                <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-lime-500/20 text-xs text-lime-600">{{ idx + 1 }}</span>
                <span class="leading-relaxed">{{ item }}</span>
              </div>
            </div>
          </div>
        </div>
      </GlassCard>

      <!-- 导出操作栏 -->
      <div class="flex flex-wrap gap-2 rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
        <NeonButton size="sm" @click="exportPDF" :loading="exporting === 'pdf'">📄 导出 PDF</NeonButton>
        <NeonButton size="sm" variant="ghost" @click="exportHTML" :loading="exporting === 'html'">🌐 导出 HTML</NeonButton>
        <NeonButton size="sm" variant="ghost" @click="exportMarkdown" :loading="exporting === 'md'">📝 导出 Markdown</NeonButton>
        <NeonButton size="sm" variant="ghost" @click="copyReport">📋 复制文本</NeonButton>
      </div>

      <!-- 各章节内容 -->
      <div class="grid gap-4 md:grid-cols-2">
        <div
          v-for="(section, idx) in report.sections"
          :key="idx"
          class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div class="flex items-center gap-3 mb-3 pb-3 border-b border-slate-100">
            <span class="flex h-7 w-7 items-center justify-center rounded-full bg-lime-100 text-sm text-lime-700 font-semibold">{{ idx + 1 }}</span>
            <span class="font-semibold text-slate-800">{{ section.title }}</span>
          </div>
          <div class="whitespace-pre-wrap text-sm leading-relaxed text-slate-600">{{ section.content }}</div>
          <div v-if="section.highlights && section.highlights.length" class="flex flex-wrap gap-2 mt-4 pt-3 border-t border-slate-100">
            <span
              v-for="(hl, hidx) in section.highlights"
              :key="hidx"
              class="rounded-full border border-lime-200 bg-lime-50 px-3 py-1 text-xs text-lime-700"
            >
              {{ hl }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <EmptyState
      v-if="!report && !loading"
      icon="📋"
      title="输入房源信息后生成综合报告"
      description="报告将整合估值、风险、证据分析，支持PDF导出与一键复制"
    />
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'

import GlassCard from '../components/GlassCard.vue'
import NeonButton from '../components/NeonButton.vue'
import Field from '../components/Field.vue'
import EmptyState from '../components/EmptyState.vue'
import { generateReport } from '../api/qingju'

const loading = ref(false)
const exporting = ref('') // '' | 'pdf' | 'html' | 'md'
const report = ref(null)

const form = reactive({
  listing_id: 1,
  title: '',
  asking_rent: 0,
  fair_rent_low: 0,
  fair_rent_high: 0,
  deviation_pct: 0,
  risk_score: 0,
  risk_level: '可租',
  evidence_count: 0,
  top_risks: [],
  factors: []
})

const risksJson = computed({
  get: () => JSON.stringify(form.top_risks, null, 2),
  set: (val) => {
    try { form.top_risks = JSON.parse(val) } catch {}
  }
})

const confidenceColor = computed(() => {
  if (!report.value) return 'text-white'
  const s = report.value.confidence_score
  if (s >= 80) return 'text-lime-600'
  if (s >= 60) return 'text-lime-500'
  return 'text-sky-500'
})

const generate = async () => {
  loading.value = true
  try {
    const res = await generateReport({ ...form })
    // 处理后端返回的不同格式
    report.value = res.report || res.data || res
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '综合报告已生成' } }))
  } catch (e) {
    console.error('Generate report failed:', e)
  } finally {
    loading.value = false
  }
}

/**
 * 导出 PDF 报告
 * NOTE: 使用浏览器原生 print API 将报告内容渲染为 PDF
 */
const exportPDF = () => {
  if (!report.value) return
  exporting.value = 'pdf'

  try {
    const r = report.value
    const riskColor = r.confidence_score >= 80 ? '#22D3EE' : r.confidence_score >= 60 ? '#8B5CF6' : '#EC4899'

    const sectionsHTML = (r.sections || []).map((s, i) => `
      <div style="margin-bottom:24px;padding:16px;border:1px solid #e5e7eb;border-radius:12px;">
        <h3 style="margin:0 0 12px;font-size:16px;color:#1f2937;">
          <span style="display:inline-block;width:28px;height:28px;line-height:28px;text-align:center;border-radius:50%;background:#8B5CF6;color:white;font-size:13px;margin-right:8px;">${i + 1}</span>
          ${s.title || '未命名章节'}
        </h3>
        <div style="font-size:14px;line-height:1.8;color:#374151;white-space:pre-wrap;">${s.content || ''}</div>
        <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap;">
          ${(s.highlights || []).map(h => `<span style="padding:2px 10px;border-radius:12px;background:#F3E8FF;color:#7C3AED;font-size:12px;">${h}</span>`).join('')}
        </div>
      </div>
    `).join('')

    const actionsHTML = (r.action_items || []).map((a, i) => `
      <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:8px;">
        <span style="display:inline-block;min-width:20px;height:20px;line-height:20px;text-align:center;border-radius:50%;background:#ECFDF5;color:#059669;font-size:11px;">${i + 1}</span>
        <span style="font-size:13px;color:#374151;">${a}</span>
      </div>
    `).join('')

    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>${r.report_title || '青居智算报告'}</title>
  <style>
    @page { margin: 20mm; }
    body { font-family: -apple-system, 'Microsoft YaHei', sans-serif; color: #1f2937; margin: 0; padding: 0; }
    .header { text-align: center; margin-bottom: 32px; }
    .header h1 { font-size: 22px; margin: 0 0 8px; }
    .header .meta { display: flex; justify-content: center; gap: 24px; font-size: 12px; color: #6b7280; }
    .summary { background: #F0FDFA; border: 1px solid #99F6E4; border-radius: 12px; padding: 16px; margin-bottom: 24px; }
    .summary h2 { font-size: 14px; color: #0D9488; margin: 0 0 8px; letter-spacing: 2px; }
    .summary pre { margin: 0; white-space: pre-wrap; font-family: inherit; font-size: 14px; line-height: 1.8; }
    .footer { margin-top: 40px; padding-top: 16px; border-top: 1px solid #e5e7eb; text-align: center; font-size: 11px; color: #9ca3af; }
  </style>
</head>
<body>
  <div class="header">
    <h1>${r.report_title || '青居智算报告'}</h1>
    <div class="meta">
      <span>生成时间：${r.generated_at || new Date().toLocaleString()}</span>
      <span>置信度：<strong style="color:${riskColor}">${r.confidence_score || 0}%</strong></span>
    </div>
  </div>
  <div class="summary">
    <h2>执行摘要</h2>
    <pre>${r.executive_summary || '暂无摘要'}</pre>
  </div>
  ${sectionsHTML}
  <div style="margin-top:32px;padding:16px;background:#F9FAFB;border-radius:12px;">
    <h3 style="font-size:15px;margin:0 0 12px;">行动清单</h3>
    ${actionsHTML || '<div style="font-size:13px;color:#6b7280;">暂无行动项</div>'}
  </div>
  <div class="footer">
    青居智算 — 基于 Hedonic 模型的高校毕业生租房防坑与真实估值系统<br/>
    本报告由系统自动生成，仅供参考
  </div>
</body>
</html>`

    // 使用 iframe + print 实现 PDF 导出
    const iframe = document.createElement('iframe')
    iframe.style.cssText = 'position:fixed;left:-9999px;width:800px;height:600px;'
    document.body.appendChild(iframe)

    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document
    iframeDoc.open()
    iframeDoc.write(html)
    iframeDoc.close()

    setTimeout(() => {
      iframe.contentWindow.print()
      setTimeout(() => {
        try { document.body.removeChild(iframe) } catch {}
        exporting.value = ''
      }, 1000)
    }, 500)

    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: 'PDF 导出窗口已打开，请选择"另存为PDF"' } }))
  } catch (err) {
    exporting.value = ''
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: 'PDF 导出失败：' + err.message } }))
  }
}

/**
 * 导出 HTML 报告
 * 生成独立的 HTML 文件供下载
 */
const exportHTML = () => {
  if (!report.value) return
  exporting.value = 'html'

  try {
    const r = report.value
    const htmlContent = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${r.report_title || '青居智算报告'}</title>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
      line-height: 1.6;
      color: #334155;
      max-width: 800px;
      margin: 0 auto;
      padding: 40px 20px;
      background: #f8fafc;
    }
    .container { background: white; border-radius: 16px; padding: 40px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .header { text-align: center; margin-bottom: 32px; padding-bottom: 24px; border-bottom: 2px solid #84cc16; }
    .header h1 { color: #1e293b; font-size: 24px; margin: 0 0 12px; }
    .meta { display: flex; justify-content: center; gap: 24px; font-size: 13px; color: #64748b; }
    .summary { background: #f0fdf4; border-left: 4px solid #84cc16; padding: 20px; margin: 24px 0; border-radius: 0 8px 8px 0; }
    .summary h2 { color: #166534; font-size: 14px; margin: 0 0 12px; text-transform: uppercase; letter-spacing: 1px; }
    .section { margin: 24px 0; padding: 20px; background: #f8fafc; border-radius: 12px; }
    .section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
    .section-number { width: 32px; height: 32px; background: #84cc16; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
    .section h3 { margin: 0; color: #1e293b; font-size: 17px; }
    .section-content { color: #475569; white-space: pre-wrap; }
    .highlights { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
    .highlight { background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
    .actions { background: #f1f5f9; padding: 20px; border-radius: 12px; margin-top: 24px; }
    .actions h3 { color: #1e293b; margin: 0 0 16px; font-size: 15px; }
    .action-item { display: flex; gap: 12px; margin: 8px 0; align-items: flex-start; }
    .action-number { min-width: 24px; height: 24px; background: #84cc16; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }
    .footer { text-align: center; margin-top: 32px; padding-top: 24px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; }
    @media print {
      body { background: white; padding: 0; }
      .container { box-shadow: none; padding: 20px; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>${r.report_title || '青居智算报告'}</h1>
      <div class="meta">
        <span>📅 ${r.generated_at || new Date().toLocaleString()}</span>
        <span>📊 置信度：${r.confidence_score || 0}%</span>
      </div>
    </div>
    
    <div class="summary">
      <h2>执行摘要</h2>
      <div>${r.executive_summary || '暂无摘要'}</div>
    </div>
    
    ${(r.sections || []).map((s, i) => `
      <div class="section">
        <div class="section-header">
          <div class="section-number">${i + 1}</div>
          <h3>${s.title || '未命名章节'}</h3>
        </div>
        <div class="section-content">${(s.content || '').replace(/\n/g, '<br>')}</div>
        ${(s.highlights || []).length ? `
          <div class="highlights">
            ${s.highlights.map(h => `<span class="highlight">${h}</span>`).join('')}
          </div>
        ` : ''}
      </div>
    `).join('')}
    
    <div class="actions">
      <h3>行动清单</h3>
      ${(r.action_items || []).map((a, i) => `
        <div class="action-item">
          <div class="action-number">${i + 1}</div>
          <div>${a}</div>
        </div>
      `).join('') || '<div style="color:#94a3b8">暂无行动项</div>'}
    </div>
    
    <div class="footer">
      青居智算 — 基于 Hedonic 模型的高校毕业生租房防坑与真实估值系统<br>
      本报告由系统自动生成，仅供参考
    </div>
  </div>
</body>
</html>`

    // 创建下载链接
    const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${(r.report_title || 'report').replace(/\s+/g, '_')}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    exporting.value = ''
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: 'HTML 报告已下载' } }))
  } catch (err) {
    exporting.value = ''
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: 'HTML 导出失败：' + err.message } }))
  }
}

/**
 * 导出 Markdown 报告
 * 生成 Markdown 格式供下载
 */
const exportMarkdown = () => {
  if (!report.value) return
  exporting.value = 'md'

  try {
    const r = report.value
    let md = `# ${r.report_title || '青居智算报告'}\n\n`
    md += `> 📅 生成时间：${r.generated_at || new Date().toLocaleString()}  \n`
    md += `> 📊 置信度：${r.confidence_score || 0}%\n\n`
    md += `---\n\n`
    
    // 执行摘要
    md += `## 执行摘要\n\n${r.executive_summary || '暂无摘要'}\n\n`
    
    // 各章节
    (r.sections || []).forEach((s, i) => {
      md += `## ${i + 1}. ${s.title || '未命名章节'}\n\n`
      md += `${s.content || ''}\n\n`
      if ((s.highlights || []).length > 0) {
        md += `**要点：** ${s.highlights.join('、')}\n\n`
      }
    })
    
    // 行动清单
    md += `## 行动清单\n\n`
    if ((r.action_items || []).length > 0) {
      r.action_items.forEach((a, i) => {
        md += `${i + 1}. ${a}\n`
      })
    } else {
      md += `> 暂无行动项\n`
    }
    md += `\n---\n\n`
    md += `*青居智算 — 基于 Hedonic 模型的高校毕业生租房防坑与真实估值系统*  \n`
    md += `*本报告由系统自动生成，仅供参考*`

    // 创建下载链接
    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${(r.report_title || 'report').replace(/\s+/g, '_')}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    exporting.value = ''
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: 'Markdown 报告已下载' } }))
  } catch (err) {
    exporting.value = ''
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: 'Markdown 导出失败：' + err.message } }))
  }
}

const fillDemo = () => {
  form.title = '地铁口南向精装一居'
  form.asking_rent = 5200
  form.fair_rent_low = 4200
  form.fair_rent_high = 4800
  form.deviation_pct = 15
  form.risk_score = 65
  form.risk_level = '谨慎'
  form.evidence_count = 4
  form.top_risks = [
    { name: '二房东/转租风险', contribution: 24 },
    { name: '合同不公平条款', contribution: 18 },
    { name: '噪音风险', contribution: 12 }
  ]
  form.factors = [
    { name: '朝向（南向溢价）', impact_pct: 5, note: '采光好' },
    { name: '地铁距离（近）', impact_pct: 6, note: '通勤便利' },
    { name: '装修（简装折价）', impact_pct: -4, note: '需置办' }
  ]
}

const reset = () => {
  form.title = ''
  form.asking_rent = 0
  form.fair_rent_low = 0
  form.fair_rent_high = 0
  form.deviation_pct = 0
  form.risk_score = 0
  form.risk_level = '可租'
  form.evidence_count = 0
  form.top_risks = []
  form.factors = []
  report.value = null
}

const copyReport = () => {
  if (!report.value) return
  const text = `${report.value.report_title}\n\n执行摘要：\n${report.value.executive_summary}\n\n${report.value.sections.map(s => `${s.title}\n${s.content}`).join('\n\n')}\n\n行动清单：\n${report.value.action_items.join('\n')}`
  navigator.clipboard.writeText(text)
  window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'success', message: '报告已复制' } }))
}
</script>
