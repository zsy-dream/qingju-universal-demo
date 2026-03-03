<template>
  <div class="min-h-screen text-slate-900 bg-[#f8fafc] selection:bg-lime-200 selection:text-lime-900">
    <!-- 全局微光 (改为极淡的呼吸感，非强制光晕) -->
    <div class="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      <div class="absolute -left-[5%] -top-[10%] h-[600px] w-[800px] rounded-full bg-lime-50/40 blur-[100px]" />
      <div class="absolute -right-[5%] top-[20%] h-[500px] w-[700px] rounded-full bg-sky-50/30 blur-[100px]" />
    </div>

    <!-- 顶部导航: Notion/飞书式纯白边框感 -->
    <header class="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur-md select-none transition-all duration-300">
      <div class="mx-auto flex max-w-[1400px] items-center gap-2 px-4 py-2">
        <!-- Logo区域: 更靠左，更紧凑 -->
        <div class="flex items-center gap-2 shrink-0 mr-1">
          <!-- Logo: 青柠绿呼吸感 -->
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-lime-500 text-white shadow-btn transition-transform hover:scale-105 active:scale-95">
            <span class="text-lg font-bold italic tracking-tighter">Q</span>
          </div>
          <div class="flex flex-col leading-tight">
            <span class="text-[9px] font-bold tracking-[0.15em] text-lime-600">QINGJU</span>
            <span class="text-base font-bold text-slate-900">青居智算</span>
          </div>
        </div>

        <!-- 桌面端导航: 更紧凑的间距 -->
        <nav class="hidden min-w-0 flex-1 items-center gap-0.5 overflow-x-auto md:flex">
          <NavLink to="/dashboard" label="驾驶舱" icon="📊" />
          <NavLink to="/listings" label="房源" icon="🏠" />
          <NavLink to="/favorites" label="收藏" icon="⭐" />
          <NavLink to="/compare" label="对比" icon="⚖️" />
          <NavLink to="/estimate" label="估值" icon="💰" />
          <NavLink to="/risk" label="风控" icon="🛡️" />
          <NavLink to="/commute" label="通勤" icon="🚇" />
          <NavLink to="/evidence" label="证据" icon="📷" />
          <NavLink to="/negotiate" label="议价" icon="🤝" />
          <NavLink to="/contract" label="合同" icon="📝" />
          <NavLink to="/split" label="分摊" icon="⚡" />
          <NavLink to="/report" label="报告" icon="📄" />
          <NavLink to="/share" label="分享" icon="🔗" />
          <NavLink to="/issues" label="问题" icon="⚠️" />
        </nav>

        <!-- 导入数据按钮: 固定可见，左侧加一条竖线分隔 -->
        <div class="flex shrink-0 items-center gap-2 pl-2 border-l border-slate-200 ml-1">
          <button @click="seedDemo" class="group relative flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 transition-all hover:border-lime-300 hover:text-lime-600 hover:shadow-sm active:bg-slate-50">
            <span class="h-1.5 w-1.5 rounded-full bg-lime-500 group-hover:animate-pulse" />
            导入数据
          </button>
        </div>
      </div>

      <!-- 移动端导航: 按正常分析流程排序 -->
      <div class="mx-auto max-w-[1400px] px-4 pb-3 md:hidden">
        <div class="flex overflow-x-auto mobile-nav-scroll gap-2 no-print">
          <NavLink to="/dashboard" label="驾驶舱" icon="📊" />
          <NavLink to="/listings" label="房源" icon="🏠" />
          <NavLink to="/favorites" label="收藏" icon="⭐" />
          <NavLink to="/compare" label="对比" icon="⚖️" />
          <NavLink to="/estimate" label="估值" icon="💰" />
          <NavLink to="/risk" label="风控" icon="🛡️" />
          <NavLink to="/commute" label="通勤" icon="🚇" />
          <NavLink to="/evidence" label="证据" icon="📷" />
          <NavLink to="/negotiate" label="议价" icon="🤝" />
          <NavLink to="/contract" label="合同" icon="📝" />
          <NavLink to="/split" label="分摊" icon="⚡" />
          <NavLink to="/report" label="报告" icon="📄" />
          <NavLink to="/share" label="分享" icon="🔗" />
          <NavLink to="/issues" label="问题" icon="⚠️" />
        </div>
      </div>
    </header>

    <!-- 主体内容: 干净背景 + 轻盈动效 -->
    <main class="mx-auto max-w-[1400px] px-6 py-8 relative z-10">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <ToastHost />

    <footer class="mx-auto max-w-[1400px] border-t border-slate-100 px-6 py-8 text-xs text-slate-400">
      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div class="flex items-center gap-4">
          <span>© Qingju Universal System</span>
          <span class="h-1 w-1 rounded-full bg-slate-200" />
          <span class="hover:text-lime-600 transition-colors cursor-help">数据隐私保护</span>
        </div>
        <div class="max-w-md text-slate-400/80 italic">
          注：估值与风控用于辅助决策，建议结合实地勘察。青居智算致力于为毕业生扫清租房障碍。
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import ToastHost from '../components/ToastHost.vue'
import NavLink from '../components/NavLink.vue'
import { 
  createListing, listListings, 
  estimate, risk, 
  createEvidence, createIssue,
  compareListings, calculateSplit,
  generateNegotiationScript, inspectContract
} from '../api/qingju'

const router = useRouter()

const seedDemo = async () => {
  // 第1步：创建8套演示房源
  const demoListings = [
    // 类型1: 杨浦溢价型
    { title: '杨浦·互联宝地地铁口精装一居', city: '上海', district: '杨浦', area_sqm: 35, layout: '1室1厅', floor: 12, total_floors: 24, orientation: '南', decoration: '精装', has_elevator: true, subway_distance_m: 180, commute_minutes: 18, asking_rent: 4800 },
    // 类型2: 浦东均衡型
    { title: '浦东·张江高科新小区一居', city: '上海', district: '浦东', area_sqm: 40, layout: '1室1厅', floor: 8, total_floors: 20, orientation: '东南', decoration: '精装', has_elevator: true, subway_distance_m: 400, commute_minutes: 32, asking_rent: 5200 },
    // 类型3: 静安情怀型
    { title: '静安·南京西路老洋房改造LOFT', city: '上海', district: '静安', area_sqm: 28, layout: '1室0厅', floor: 2, total_floors: 4, orientation: '北', decoration: '豪装', has_elevator: false, subway_distance_m: 120, commute_minutes: 12, asking_rent: 5500 },
    // 类型4: 徐汇改善型
    { title: '徐汇·漕河泾公园旁电梯两居', city: '上海', district: '徐汇', area_sqm: 65, layout: '2室1厅', floor: 14, total_floors: 26, orientation: '南', decoration: '精装', has_elevator: true, subway_distance_m: 550, commute_minutes: 28, asking_rent: 7800 },
    // 类型5: 闵行省钱型
    { title: '闵行·莘庄北广场简装一居', city: '上海', district: '闵行', area_sqm: 42, layout: '1室1厅', floor: 5, total_floors: 14, orientation: '西', decoration: '简装', has_elevator: true, subway_distance_m: 350, commute_minutes: 48, asking_rent: 3600 },
    // 类型6: 普陀实用型
    { title: '普陀·真如副中心电梯两居', city: '上海', district: '普陀', area_sqm: 58, layout: '2室1厅', floor: 18, total_floors: 28, orientation: '东南', decoration: '精装', has_elevator: true, subway_distance_m: 260, commute_minutes: 22, asking_rent: 6200 },
    // 类型7: 虹口风险型
    { title: '虹口·鲁迅公园旁老小区低楼层', city: '上海', district: '虹口', area_sqm: 32, layout: '1室1厅', floor: 2, total_floors: 6, orientation: '南', decoration: '简装', has_elevator: false, subway_distance_m: 750, commute_minutes: 42, asking_rent: 3500 },
    // 类型8: 长宁高端型
    { title: '长宁·虹桥商务区精装公寓', city: '上海', district: '长宁', area_sqm: 45, layout: '1室1厅', floor: 16, total_floors: 30, orientation: '东', decoration: '豪装', has_elevator: true, subway_distance_m: 320, commute_minutes: 25, asking_rent: 6800 }
  ]

  let successCount = 0
  const createdListings = []
  
  for (const listing of demoListings) {
    try {
      const created = await createListing(listing)
      createdListings.push(created)
      successCount++
    } catch (e) {
      console.error('Failed to create demo listing:', e)
    }
  }

  // 第2步：为房源生成估值记录（选择前4套进行估值）
  const listingsToEstimate = createdListings.slice(0, 4)
  for (const listing of listingsToEstimate) {
    try {
      await estimate({ listing_id: listing.id })
    } catch (e) {
      console.error('Failed to estimate listing:', e)
    }
  }

  // 第3步：为房源生成风控评估（选择特定房源展示不同风险等级）
  const riskAssessments = [
    { listing: createdListings[6], level: '不建议' }, // 虹口老小区 - 高风险
    { listing: createdListings[1], level: '可租' },   // 浦东均衡 - 低风险
    { listing: createdListings[7], level: '可租' },   // 长宁高端 - 低风险
    { listing: createdListings[4], level: '谨慎' },   // 闵行省钱 - 中风险
  ]
  for (const { listing, level } of riskAssessments) {
    if (listing) {
      try {
        await risk({ 
          listing_id: listing.id,
          roommate_count: listing.id % 3 + 1,
          is_second_landlord: listing.district === '虹口' || listing.district === '静安',
          has_noise_issue: listing.district === '虹口',
          equipment_age: listing.decoration === '简装' ? 'old' : 'new',
          has_damp_issue: listing.orientation === '北' || listing.floor <= 3,
          contract_clause_risk: level === '不建议' ? 'high' : level === '谨慎' ? 'medium' : 'low'
        })
      } catch (e) {
        console.error('Failed to assess risk:', e)
      }
    }
  }

  // 第4步：创建看房证据（为3套房源添加照片证据）
  const evidenceTemplates = [
    { title: '客厅全景照片', type: 'image', description: '采光良好，南向落地窗', listingIndex: 0 },
    { title: '卫生间检查', type: 'image', description: '热水器品牌海尔，2022年生产', listingIndex: 0 },
    { title: '卧室墙面', type: 'image', description: '墙面有轻微霉斑，需注意通风', listingIndex: 6 },
    { title: '地铁距离实拍', type: 'image', description: '步行到地铁站实测4分30秒', listingIndex: 1 },
    { title: '小区环境', type: 'image', description: '绿化率较高，有儿童游乐区', listingIndex: 7 },
    { title: '厨房设备', type: 'image', description: '燃气灶+油烟机，需检查能否正常使用', listingIndex: 4 },
  ]
  for (const ev of evidenceTemplates) {
    const listing = createdListings[ev.listingIndex]
    if (listing) {
      try {
        await createEvidence({
          listing_id: listing.id,
          title: ev.title,
          type: ev.type,
          description: ev.description,
          file_url: `https://example.com/demo/${ev.title}.jpg`
        })
      } catch (e) {
        console.error('Failed to create evidence:', e)
      }
    }
  }

  // 第5步：创建问题记录（为2套房源添加待解决问题）
  const issues = [
    { title: '押金退还条款不清晰', severity: 'critical', description: '合同中写明"根据房屋状况扣除"，未明确标准', listingIndex: 6 },
    { title: '空调制冷效果差', severity: 'warning', description: '试机时发现制冷慢，需确认维修责任', listingIndex: 4 },
    { title: '网络宽带未安装', severity: 'minor', description: '房东承诺入住前安装，需确认具体时间', listingIndex: 0 },
    { title: '二房东身份存疑', severity: 'critical', description: '签约人非房产证持有人，需核实转租权限', listingIndex: 6 },
  ]
  for (const issue of issues) {
    const listing = createdListings[issue.listingIndex]
    if (listing) {
      try {
        await createIssue({
          listing_id: listing.id,
          title: issue.title,
          severity: issue.severity,
          description: issue.description,
          status: 'open'
        })
      } catch (e) {
        console.error('Failed to create issue:', e)
      }
    }
  }

  // 第6步：创建对比分析记录（选择3套热门房源对比）
  if (createdListings.length >= 3) {
    try {
      await compareListings([
        createdListings[1].id, // 浦东
        createdListings[0].id, // 杨浦
        createdListings[7].id  // 长宁
      ])
    } catch (e) {
      console.error('Failed to create comparison:', e)
    }
  }

  // 第7步：创建分摊计算记录（模拟合租场景）
  if (createdListings[3]) { // 徐汇两居适合合租
    try {
      await calculateSplit({
        total_rent: 7800,
        rooms: [
          { name: '主卧', area: 22, has_balcony: true, has_bathroom: false },
          { name: '次卧', area: 18, has_balcony: false, has_bathroom: false }
        ],
        common_area: 25,
        utilities: { wifi: 100, cleaning: 80, others: 50 },
        roommates: [
          { name: '小张', room: '主卧', income_ratio: 1.2 },
          { name: '小李', room: '次卧', income_ratio: 1.0 }
        ]
      })
    } catch (e) {
      console.error('Failed to calculate split:', e)
    }
  }

  // 第8步：创建议价脚本记录（为高价房源生成议价脚本）
  const negotiateListings = [createdListings[2], createdListings[3]].filter(Boolean) // 静安、徐汇
  for (const listing of negotiateListings) {
    try {
      await generateNegotiationScript({
        asking_rent: listing.asking_rent,
        fair_rent_low: Math.round(listing.asking_rent * 0.85),
        fair_rent_high: Math.round(listing.asking_rent * 0.95),
        deviation_pct: 8,
        risk_level: listing.district === '静安' ? '谨慎' : '可租',
        factors: [
          { name: '朝向折价', impact_pct: -5, note: listing.orientation === '北' ? '北向采光弱' : '无明显折价' },
          { name: '装修溢价', impact_pct: 10, note: listing.decoration === '豪装' ? '精装修品质高' : '标准装修' },
          { name: '楼层因素', impact_pct: listing.floor <= 3 ? -3 : 0, note: listing.floor <= 3 ? '低楼层潮湿风险' : '楼层适中' }
        ]
      })
    } catch (e) {
      console.error('Failed to generate negotiation script:', e)
    }
  }

  // 第9步：创建合同审查记录（模拟合同体检）
  try {
    await inspectContract({
      clauses: [
        { clause_name: '押金退还', severity: 'critical', current_text: '退房时根据房屋状况扣除相应费用', suggested_alternative: '明确扣除标准：自然损耗不扣，人为损坏按维修发票扣除', why_it_matters: '避免房东随意扣押金' },
        { clause_name: '提前解约', severity: 'warning', current_text: '租户提前退租需支付2个月租金作为违约金', suggested_alternative: '违约金不超过1个月租金，或提前30天通知可免违约金', why_it_matters: '保护租户因工作变动等合理退租需求' },
        { clause_name: '维修责任', severity: 'warning', current_text: '房屋设施维修由租户负责', suggested_alternative: '非人为损坏的设施维修由房东负责，人为损坏由租户负责', why_it_matters: '明确责任边界，避免推诿' }
      ]
    })
  } catch (e) {
    console.error('Failed to inspect contract:', e)
  }

  // 最终提示
  const totalModules = 9
  window.dispatchEvent(new CustomEvent('app:toast', { 
    detail: { 
      type: 'success', 
      message: `✅ 演示数据初始化完成！\n🏠 房源：${successCount}套 | 📊 估值：${listingsToEstimate.length}套 | 🛡️ 风控：${riskAssessments.length}套\n📷 证据：${evidenceTemplates.length}条 | ⚠️ 问题：${issues.length}条 | ⚖️ 对比：1组\n⚡ 分摊：1组 | 🤝 议价：${negotiateListings.length}套 | 📝 合同：1份` 
    } 
  }))
  router.push('/listings')
}
</script>

<style scoped>
.page-fade-enter-active {
  transition: all 0.25s ease-out;
}
.page-fade-leave-active {
  transition: all 0.15s ease-in;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
