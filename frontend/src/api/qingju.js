import http from './http'

export const getDashboardSummary = async () => {
  const { data } = await http.get('/api/v1/dashboard/summary')
  return data
}

export const createListing = async (payload) => {
  const { data } = await http.post('/api/v1/listings/', payload)
  return data
}

export const getListing = async (id) => {
  const { data } = await http.get(`/api/v1/listings/${id}`)
  return data
}

export const deleteListing = async (id) => {
  const { data } = await http.delete(`/api/v1/listings/${id}`)
  return data
}

export const listListings = async (limit = 20) => {
  const { data } = await http.get('/api/v1/listings/', { params: { limit } })
  return data
}

export const estimate = async (payload) => {
  const { data } = await http.post('/api/v1/assessments/estimate', payload)
  return data
}

export const risk = async (payload) => {
  const { data } = await http.post('/api/v1/assessments/risk', payload)
  return data
}

// Evidence APIs
export const createEvidence = async (payload) => {
  const { data } = await http.post('/api/v1/evidence/', payload)
  return data
}

export const listEvidence = async (listingId) => {
  const { data } = await http.get('/api/v1/evidence/', { params: { listing_id: listingId } })
  return data
}

export const deleteEvidence = async (id) => {
  const { data } = await http.delete(`/api/v1/evidence/${id}`)
  return data
}

// Negotiation APIs
export const generateNegotiationScript = async (payload) => {
  const { data } = await http.post('/api/v1/negotiation/script', payload)
  return data
}

// Report APIs
export const generateReport = async (payload) => {
  const { data } = await http.post('/api/v1/report/generate', payload)
  return data
}

export const inspectContract = async (payload) => {
  const { data } = await http.post('/api/v1/contract/inspect', payload)
  return data
}

// Issue APIs
export const createIssue = async (payload) => {
  const { data } = await http.post('/api/v1/issues/', payload)
  return data
}

export const listIssues = async (listingId) => {
  const params = listingId ? { listing_id: listingId } : {}
  const { data } = await http.get('/api/v1/issues/', { params })
  return data
}

export const updateIssue = async (id, payload) => {
  const { data } = await http.put(`/api/v1/issues/${id}`, payload)
  return data
}

export const deleteIssue = async (id) => {
  const { data } = await http.delete(`/api/v1/issues/${id}`)
  return data
}

// Comparison APIs
export const compareListings = async (listingIds) => {
  const { data } = await http.post('/api/v1/comparison/compare', { listing_ids: listingIds })
  return data
}

// Split APIs
export const calculateSplit = async (payload) => {
  const { data } = await http.post('/api/v1/split/calculate', payload)
  return data
}

// Commute APIs
export const analyzeCommute = async (payload) => {
  const { data } = await http.post('/api/v1/commute/analyze', payload)
  return data
}
