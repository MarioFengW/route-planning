/**
 * Composable for API communication with backend
 */
import { ref } from 'vue'

const API_BASE_URL = 'http://localhost:5000/api'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const request = async (endpoint, options = {}) => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Request failed')
      }

      return await response.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Health check
  const checkHealth = () => request('/health')

  // Map operations
  const loadMap = (data) => request('/map/load', {
    method: 'POST',
    body: JSON.stringify(data),
  })

  const getMapStats = () => request('/map/stats')

  // KD-Tree operations
  const buildKdTree = () => request('/kdtree/build', { method: 'POST' })

  const searchKdTree = (lat, lon) => request('/kdtree/search', {
    method: 'POST',
    body: JSON.stringify({ lat, lon }),
  })

  const evaluateKdTree = (numLocations = 20, useRealLocations = true) => request('/kdtree/evaluate', {
    method: 'POST',
    body: JSON.stringify({ num_locations: numLocations, use_real_locations: useRealLocations }),
  })

  // Route planning
  const planRoute = (startLat, startLon, goalLat, goalLon, algorithm = 'astar') => request('/route/plan', {
    method: 'POST',
    body: JSON.stringify({
      start_lat: startLat,
      start_lon: startLon,
      goal_lat: goalLat,
      goal_lon: goalLon,
      algorithm,
    }),
  })

  const evaluateSearchAlgorithms = (numPairs = 5) => request('/route/evaluate', {
    method: 'POST',
    body: JSON.stringify({ num_pairs_per_range: numPairs }),
  })

  // Emergency service
  const registerHospitals = (hospitals) => request('/emergency/register-hospitals', {
    method: 'POST',
    body: JSON.stringify({ hospitals }),
  })

  const findNearestHospital = (lat, lon) => request('/emergency/nearest-hospital', {
    method: 'POST',
    body: JSON.stringify({ lat, lon }),
  })

  const getEmergencyRoute = (lat, lon, algorithm = 'astar') => request('/emergency/route', {
    method: 'POST',
    body: JSON.stringify({ lat, lon, algorithm }),
  })

  const getServiceAreas = () => request('/emergency/service-areas')

  return {
    loading,
    error,
    // Health
    checkHealth,
    // Map
    loadMap,
    getMapStats,
    // KD-Tree
    buildKdTree,
    searchKdTree,
    evaluateKdTree,
    // Routes
    planRoute,
    evaluateSearchAlgorithms,
    // Emergency
    registerHospitals,
    findNearestHospital,
    getEmergencyRoute,
    getServiceAreas,
  }
}
