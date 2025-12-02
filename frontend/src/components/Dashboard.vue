<template>
  <div class="min-h-screen" style="background: linear-gradient(to bottom right, #f9fafb, #dbeafe);">
    <!-- Header -->
    <header style="background-color: #1e40af; border-bottom: 2px solid #1e3a8a;">
      <div class="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-light" style="color: #ffffff;">Route Planning System</h1>
            <p class="text-xs mt-1" style="color: #bfdbfe;">KD-Tree · Search Algorithms · Emergency Services</p>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center">
              <div 
                :class="[
                  'w-3 h-3 rounded-full mr-2',
                  apiStatus === 'online' ? 'bg-green-400' : 'bg-red-400'
                ]"
              ></div>
              <span class="text-sm" style="color: #ffffff;">
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
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <!-- Component 1: KD-Tree -->
        <button
          @click="showComponent = 'kdtree'"
          class="bg-white p-5 text-left transition-all group"
          style="border: 3px solid #3b82f6;"
          @mouseenter="$event.currentTarget.style.borderColor='#2563eb'; $event.currentTarget.style.backgroundColor='#eff6ff'"
          @mouseleave="$event.currentTarget.style.borderColor='#3b82f6'; $event.currentTarget.style.backgroundColor='#ffffff'"
        >
          <h2 class="text-lg font-medium mb-1" style="color: #1e40af;">KD-Tree</h2>
          <p class="text-xs mb-3" style="color: #3b82f6;">Spatial Search Optimization</p>
          <p class="text-sm text-gray-600 leading-relaxed">
            Optimized nearest neighbor search using KD-Tree data structure
          </p>
        </button>

        <!-- Component 2: Route Planning -->
        <button
          @click="showComponent = 'routes'"
          class="bg-white p-5 text-left transition-all group"
          style="border: 3px solid #3b82f6;"
          @mouseenter="$event.currentTarget.style.borderColor='#2563eb'; $event.currentTarget.style.backgroundColor='#eff6ff'"
          @mouseleave="$event.currentTarget.style.borderColor='#3b82f6'; $event.currentTarget.style.backgroundColor='#ffffff'"
        >
          <h2 class="text-lg font-medium mb-1" style="color: #1e40af;">Route Planner</h2>
          <p class="text-xs mb-3" style="color: #3b82f6;">Algorithm Comparison</p>
          <p class="text-sm text-gray-600 leading-relaxed">
            Compare BFS, DFS, UCS, IDDFS, and A* algorithms for route planning
          </p>
        </button>

        <!-- Component 3: Emergency Service -->
        <button
          @click="showComponent = 'emergency'"
          class="bg-white p-5 text-left transition-all group"
          style="border: 3px solid #3b82f6;"
          @mouseenter="$event.currentTarget.style.borderColor='#2563eb'; $event.currentTarget.style.backgroundColor='#eff6ff'"
          @mouseleave="$event.currentTarget.style.borderColor='#3b82f6'; $event.currentTarget.style.backgroundColor='#ffffff'"
        >
          <h2 class="text-lg font-medium mb-1" style="color: #1e40af;">Emergency Service</h2>
          <p class="text-xs mb-3" style="color: #3b82f6;">Hospital Routing</p>
          <p class="text-sm text-gray-600 leading-relaxed">
            Find nearest hospital using Voronoi partitioning and optimal routing
          </p>
        </button>
      </div>

      <!-- Map Setup Section -->
      <div class="bg-white p-6 mb-6" style="border: 3px solid #3b82f6;">
        <h2 class="text-lg font-medium mb-4" style="color: #1e40af;">Map Setup</h2>
        
        <div v-if="!mapLoaded" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Load Map by Address
            </label>
            <input
              v-model="mapAddress"
              type="text"
              placeholder="e.g., Tec de Monterrey campus Guadalajara, Zapopan, Jalisco, México"
              class="w-full px-4 py-2 border-2 border-royal-blue-200 focus:ring-2 focus:ring-royal-blue-500 focus:border-royal-blue-500"
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
                class="w-full px-4 py-2 border-2 border-royal-blue-200 focus:ring-2 focus:ring-royal-blue-500 focus:border-royal-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Network Type
              </label>
              <select
                v-model="networkType"
                class="w-full px-4 py-2 border-2 border-royal-blue-200 focus:ring-2 focus:ring-royal-blue-500 focus:border-royal-blue-500"
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
            class="w-full px-6 py-2.5 transition-colors font-normal disabled:opacity-50 disabled:cursor-not-allowed"
            style="background-color: #2563eb; color: #ffffff;"
            @mouseenter="handleButtonHover($event, true)"
            @mouseleave="handleButtonHover($event, false)"
          >
            <span v-if="loading">Loading Map...</span>
            <span v-else>Load Map</span>
          </button>
        </div>

        <div v-else class="space-y-4">
          <div class="p-4" style="background-color: #eff6ff; border-left: 4px solid #2563eb;">
            <h3 class="font-semibold mb-2" style="color: #1e40af;">✓ Map Loaded</h3>
            <div class="text-sm space-y-1" style="color: #1e40af;">
              <p><strong style="color: #1e3a8a;">Nodes:</strong> {{ mapStats.num_nodes?.toLocaleString() }}</p>
              <p><strong style="color: #1e3a8a;">Edges:</strong> {{ mapStats.num_edges?.toLocaleString() }}</p>
            </div>
          </div>

          <!-- Map Visualization -->
          <div class="bg-gradient-to-br from-royal-blue-50 to-gray-50 p-4 border border-royal-blue-200">
            <h3 class="font-medium text-royal-blue-800 mb-3">Map Visualization</h3>
            <MapVisualization 
              :graphData="graphData"
              :selectionMode="false"
            />
          </div>

          <button
            @click="resetMap"
            class="w-full border border-gray-300 text-gray-700 px-6 py-2.5 hover:bg-gray-50 transition-colors font-normal"
          >
            Load Different Map
          </button>
        </div>
      </div>

      <!-- Active Component Display -->
      <div v-if="showComponent && mapLoaded" class="bg-white border-2 border-royal-blue-300 p-6 shadow-lg shadow-royal-blue-100">
        <!-- KD-Tree Component -->
        <KDTreeView
          v-if="showComponent === 'kdtree'"
          :graphData="graphData"
          @close="showComponent = null"
        />

        <!-- Route Planner Component -->
        <RoutePlannerView
          v-else-if="showComponent === 'routes'"
          :graphData="graphData"
          @close="showComponent = null"
        />

        <!-- Emergency Service Component -->
        <EmergencyView
          v-else-if="showComponent === 'emergency'"
          :graphData="graphData"
          @close="showComponent = null"
        />
      </div>

      <!-- Quick Start Guide -->
      <div class="bg-white border-2 border-royal-blue-200 p-6 mt-6">
        <h2 class="text-lg font-medium text-royal-blue-700 mb-4">Quick Start</h2>
        <div class="space-y-2 text-sm text-gray-600">
          <div class="flex items-start">
            <span class="font-medium text-royal-blue-600 mr-2 min-w-[20px]">1.</span>
            <p>Load a map by entering an address and clicking "Load Map"</p>
          </div>
          <div class="flex items-start">
            <span class="font-medium text-royal-blue-600 mr-2 min-w-[20px]">2.</span>
            <p>Choose a component to explore: KD-Tree, Route Planner, or Emergency Service</p>
          </div>
          <div class="flex items-start">
            <span class="font-medium text-royal-blue-600 mr-2 min-w-[20px]">3.</span>
            <p>Run evaluations to compare algorithms and visualize results</p>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="mt-12" style="background-color: #1e40af; border-top: 2px solid #1e3a8a;">
      <div class="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 text-center" style="color: #bfdbfe;">
        <p class="text-xs">Route Planning Project · Tecnológico de Monterrey</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import MapVisualization from './MapVisualization.vue'
import KDTreeView from './KDTreeView.vue'
import RoutePlannerView from './RoutePlannerView.vue'
import EmergencyView from './EmergencyServiceSimple.vue'

const api = useApi()

// State
const apiStatus = ref('offline')
const mapLoaded = ref(false)
const mapStats = ref({})
const graphData = ref(null)
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
    
    // Load graph data for visualization
    graphData.value = await api.getGraphData()
    
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
  graphData.value = null
  showComponent.value = null
}

const handleButtonHover = (event, isHover) => {
  if (!loading.value && mapAddress.value) {
    event.currentTarget.style.backgroundColor = isHover ? '#1e40af' : '#2563eb'
  }
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
