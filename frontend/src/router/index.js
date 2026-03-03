import { createRouter, createWebHistory } from 'vue-router'

import Dashboard from '../views/Dashboard.vue'
import Listings from '../views/Listings.vue'
import Estimate from '../views/Estimate.vue'
import Risk from '../views/Risk.vue'
import Evidence from '../views/Evidence.vue'
import Negotiate from '../views/Negotiate.vue'
import Report from '../views/Report.vue'
import Contract from '../views/Contract.vue'
import Issues from '../views/Issues.vue'
import Compare from '../views/Compare.vue'
import Share from '../views/Share.vue'
import Favorites from '../views/Favorites.vue'
import Split from '../views/Split.vue'
import Commute from '../views/Commute.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', name: 'dashboard', component: Dashboard },
    { path: '/listings', name: 'listings', component: Listings },
    { path: '/favorites', name: 'favorites', component: Favorites },
    { path: '/estimate', name: 'estimate', component: Estimate },
    { path: '/risk', name: 'risk', component: Risk },
    { path: '/evidence', name: 'evidence', component: Evidence },
    { path: '/negotiate', name: 'negotiate', component: Negotiate },
    { path: '/report', name: 'report', component: Report },
    { path: '/contract', name: 'contract', component: Contract },
    { path: '/issues', name: 'issues', component: Issues },
    { path: '/compare', name: 'compare', component: Compare },
    { path: '/share', name: 'share', component: Share },
    { path: '/split', name: 'split', component: Split },
    { path: '/commute', name: 'commute', component: Commute }
  ]
})

export default router
