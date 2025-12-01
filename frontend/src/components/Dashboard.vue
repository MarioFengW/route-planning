<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- Header -->
    <header class="bg-white shadow-md">
      <div class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">🗺️ Route Planning System</h1>
            <p class="text-sm text-gray-600 mt-1">KD-Tree, Search Algorithms & Emergency Services</p>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center">
              <div 
                :class="[
                  'w-3 h-3 rounded-full mr-2',
                  apiStatus === 'online' ? 'bg-green-500' : 'bg-red-500'
                ]"
              ></div>
              <span class="text-sm text-gray-600">
                API {{ apiStatus === 'online' ? 'Online' : 'Offline' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <!-- Status Messages -->
      <div v-if="error" class="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>

      <div v-if="successMessage" class="mb-6 bg-green-50 border-l-4 border-green-500 p-4 rounded">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-green-700">{{ successMessage }}</p>
          </div>
        </div>
      </div>

      <!-- Components Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <!-- Component 1: KD-Tree -->
        <div class="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
              <span class="text-2xl">🌳</span>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">KD-Tree</h2>
              <p class="text-sm text-gray-500">Spatial Search</p>
            </div>
          </div>
          <p class="text-gray-600 text-sm mb-4">
            Optimized nearest neighbor search using KD-Tree data structure
          </p>
          <button
            @click="showComponent = 'kdtree'"
            class="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Open KD-Tree
          </button>
        </div>

        <!-- Component 2: Route Planning -->
        <div class="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
              <span class="text-2xl">🚗</span>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">Route Planner</h2>
              <p class="text-sm text-gray-500">Search Algorithms</p>
            </div>
          </div>
          <p class="text-gray-600 text-sm mb-4">
            Compare BFS, DFS, UCS, IDDFS, and A* algorithms for route planning
          </p>
          <button
            @click="showComponent = 'routes'"
            class="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors font-medium"
          >
            Open Planner
          </button>
        </div>

        <!-- Component 3: Emergency Service -->
        <div class="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mr-4">
              <span class="text-2xl">🏥</span>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">Emergency</h2>
              <p class="text-sm text-gray-500">Hospital Routes</p>
            </div>
          </div>
          <p class="text-gray-600 text-sm mb-4">
            Find nearest hospital using Voronoi partitioning and optimal routing
          </p>
          <button
            @click="showComponent = 'emergency'"
            class="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors font-medium"
          >
            Open Emergency
          </button>
        </div>
      </div>

      <!-- Map Setup Section -->
      <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">🗺️ Map Setup</h2>
        
        <div v-if="!mapLoaded" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Load Map by Address
            </label>
            <input
              v-model="mapAddress"
              type="text"
              placeholder="e.g., Tec de Monterrey campus Guadalajara, Zapopan, Jalisco, México"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Distance (meters)
              </label>
              <input
                v-model.number="mapDistance"
                type="number"
                placeholder="10000"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Network Type
              </label>
              <select
                v-model="networkType"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="drive">Drive</option>
                <option value="walk">Walk</option>
                <option value="bike">Bike</option>
                <option value="all">All</option>
              </select>
            </div>
          </div>

          <button
            @click="loadMap"
            :disabled="loading || !mapAddress"
            class="w-full bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading">Loading Map...</span>
            <span v-else>Load Map</span>
          </button>
        </div>

        <div v-else class="space-y-4">
          <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded">
            <h3 class="font-semibold text-green-800 mb-2">✓ Map Loaded Successfully</h3>
            <div class="text-sm text-green-700 space-y-1">
              <p><strong>Nodes:</strong> {{ mapStats.num_nodes?.toLocaleString() }}</p>
              <p><strong>Edges:</strong> {{ mapStats.num_edges?.toLocaleString() }}</p>
            </div>
          </div>

          <button
            @click="resetMap"
            class="w-full bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors font-medium"
          >
            Load Different Map
          </button>
        </div>
      </div>

      <!-- Active Component Display -->
      <div v-if="showComponent && mapLoaded" class="bg-white rounded-lg shadow-lg p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ componentTitle }}
          </h2>
          <button
            @click="showComponent = null"
            class="text-gray-500 hover:text-gray-700"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Component Content Placeholder -->
        <div class="text-center py-12 text-gray-500">
          <p class="text-lg mb-4">{{ componentDescription }}</p>
          <p class="text-sm">Component implementation coming soon...</p>
        </div>
      </div>

      <!-- Quick Start Guide -->
      <div class="bg-white rounded-lg shadow-lg p-6 mt-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">📖 Quick Start Guide</h2>
        <div class="space-y-3 text-gray-600">
          <div class="flex items-start">
            <span class="font-bold text-indigo-600 mr-2">1.</span>
            <p>Load a map by entering an address and clicking "Load Map"</p>
          </div>
          <div class="flex items-start">
            <span class="font-bold text-indigo-600 mr-2">2.</span>
            <p>Choose a component to explore: KD-Tree, Route Planner, or Emergency Service</p>
          </div>
          <div class="flex items-start">
            <span class="font-bold text-indigo-600 mr-2">3.</span>
            <p>Run evaluations to compare algorithms and visualize results</p>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white shadow-md mt-12">
      <div class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 text-center text-gray-600">
        <p class="text-sm">Route Planning Project - Análisis y Diseño de Algoritmos</p>
        <p class="text-xs mt-1">Tecnológico de Monterrey</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'

const api = useApi()

// State
const apiStatus = ref('offline')
const mapLoaded = ref(false)
const mapStats = ref({})
const showComponent = ref(null)
const error = ref(null)
const successMessage = ref(null)
const loading = ref(false)

// Map form data
const mapAddress = ref('Tec de Monterrey campus Guadalajara, Zapopan, Jalisco, 45201, México')
const mapDistance = ref(10000)
const networkType = ref('drive')

// Computed
const componentTitle = computed(() => {
  const titles = {
    kdtree: '🌳 KD-Tree Evaluation',
    routes: '🚗 Route Planning & Algorithm Comparison',
    emergency: '🏥 Emergency Service with Voronoi'
  }
  return titles[showComponent.value] || ''
})

const componentDescription = computed(() => {
  const descriptions = {
    kdtree: 'Evaluate KD-Tree performance vs exhaustive search for nearest neighbor queries',
    routes: 'Compare BFS, DFS, UCS, IDDFS, and A* algorithms across different distance ranges',
    emergency: 'Find optimal routes to nearest hospitals using Voronoi partitioning'
  }
  return descriptions[showComponent.value] || ''
})

// Methods
const checkApiHealth = async () => {
  try {
    await api.checkHealth()
    apiStatus.value = 'online'
  } catch (err) {
    apiStatus.value = 'offline'
  }
}

const loadMap = async () => {
  if (!mapAddress.value) return

  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    const result = await api.loadMap({
      address: mapAddress.value,
      dist: mapDistance.value,
      network_type: networkType.value
    })

    mapLoaded.value = true
    mapStats.value = result.stats
    successMessage.value = 'Map loaded successfully!'
    
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err) {
    error.value = `Failed to load map: ${err.message}`
  } finally {
    loading.value = false
  }
}

const resetMap = () => {
  mapLoaded.value = false
  mapStats.value = {}
  showComponent.value = null
}

// Lifecycle
onMounted(() => {
  checkApiHealth()
  // Check API health every 30 seconds
  setInterval(checkApiHealth, 30000)
})
</script>

<style scoped>
/* Custom animations */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
