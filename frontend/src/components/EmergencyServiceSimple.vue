<template>
  <div class="emergency-view space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-gray-200 pb-4">
      <div>
        <h2 class="text-xl font-medium text-gray-900">Emergency Service with Voronoi</h2>
        <p class="text-xs text-gray-500 mt-1">Automatic hospital detection and routing</p>
      </div>
      <button
        @click="$emit('close')"
        class="text-gray-500 hover:text-gray-700"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Status Messages -->
    <div v-if="error" class="bg-red-50 border-l-2 border-red-500 p-3">
      <p class="text-sm text-red-700">{{ error }}</p>
    </div>

    <div v-if="successMessage" class="bg-royal-blue-50 border-l-2 border-royal-blue-600 p-3">
      <p class="text-sm text-royal-blue-700">{{ successMessage }}</p>
    </div>

    <!-- Tab Selection -->
    <div class="flex border-b border-gray-200">
      <button
        @click="activeTab = 'hospitals'"
        :class="[
          'px-6 py-2.5 font-normal text-sm border-b-2 transition-colors',
          activeTab === 'hospitals'
            ? 'border-royal-blue-600 text-royal-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        ]"
      >
        Registered Hospitals
      </button>
      <button
        @click="activeTab = 'voronoi'"
        :class="[
          'px-6 py-2.5 font-normal text-sm border-b-2 transition-colors',
          activeTab === 'voronoi'
            ? 'border-royal-blue-600 text-royal-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        ]"
      >
        Voronoi Diagram
      </button>
      <button
        @click="activeTab = 'route'"
        :class="[
          'px-6 py-2.5 font-normal text-sm border-b-2 transition-colors',
          activeTab === 'route'
            ? 'border-royal-blue-600 text-royal-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        ]"
      >
        Find Route
      </button>
    </div>

    <!-- Registered Hospitals Tab -->
    <div v-if="activeTab === 'hospitals'" class="space-y-6">
      <div class="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Auto-Registered Hospitals</h3>
        <p class="text-sm text-gray-600 mb-4">
          Hospitals were automatically detected and registered when you loaded the map.
          These are actual hospitals found in OpenStreetMap within the map area.
        </p>

        <button
          @click="loadHospitals"
          :disabled="loading"
          class="px-6 py-3 bg-royal-blue-600 text-white rounded-lg hover:bg-royal-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium mb-4"
        >
          <span v-if="loading">Loading...</span>
          <span v-else>🔄 Refresh Hospital List</span>
        </button>

        <div v-if="registeredHospitals.length > 0" class="space-y-4">
          <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <p class="text-green-800 font-semibold">
              ✓ {{ registeredHospitals.length }} hospitals registered and ready for emergency routing
            </p>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 text-sm">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">#</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Node ID</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Latitude</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Longitude</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(hospital, idx) in registeredHospitals" :key="idx" class="hover:bg-gray-50">
                  <td class="px-3 py-2 whitespace-nowrap text-gray-900">{{ idx + 1 }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-gray-700">{{ hospital.name || `Hospital ${idx + 1}` }}</td>
                  <td class="px-3 py-2 whitespace-nowrap font-mono text-xs text-gray-700">{{ hospital.node_id || hospital.nearest_node }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-gray-700">{{ hospital.lat?.toFixed(6) }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-gray-700">{{ hospital.lon?.toFixed(6) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Map visualization with hospitals -->
          <div class="mt-4">
            <h4 class="font-semibold text-gray-900 mb-3">Hospital Locations on Map</h4>
            <MapVisualization 
              :graphData="graphData"
              :highlightedNodes="hospitalNodes"
              :selectionMode="false"
            />
          </div>
        </div>

        <div v-else class="text-center py-8 text-gray-500">
          <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          <p class="text-lg font-semibold">No hospitals registered yet</p>
          <p class="text-sm mt-2">Hospitals should be automatically detected when loading the map.</p>
          <p class="text-xs mt-2 text-orange-600">If none were found, the map area may not have hospitals registered in OpenStreetMap.</p>
        </div>
      </div>
    </div>

    <!-- Voronoi Diagram Tab -->
    <div v-if="activeTab === 'voronoi'" class="space-y-6">
      <div class="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Voronoi Diagram</h3>
        <p class="text-sm text-gray-600 mb-4">
          Voronoi partitioning shows the service areas for each hospital. Each region represents the area 
          closest to a particular hospital.
        </p>

        <button
          @click="loadVoronoiDiagram"
          :disabled="loading"
          class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium mb-4"
        >
          <span v-if="loading">Loading Diagram...</span>
          <span v-else>Generate Voronoi Diagram</span>
        </button>

        <div v-if="voronoiImageUrl" class="mt-4">
          <div class="border-2 border-gray-300 rounded-lg overflow-hidden bg-white">
            <img :src="voronoiImageUrl" alt="Voronoi Diagram" class="w-full h-auto" />
          </div>
        </div>

        <!-- Service Areas Info -->
        <div v-if="serviceAreasInfo" class="mt-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4">
          <h4 class="font-semibold text-purple-900 mb-3">Service Areas Information</h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-700">{{ serviceAreasInfo.num_hospitals }}</div>
              <div class="text-purple-600">Hospitals</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-700">{{ serviceAreasInfo.num_regions }}</div>
              <div class="text-purple-600">Regions</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-700">{{ serviceAreasInfo.avg_region_size?.toFixed(0) || 'N/A' }}</div>
              <div class="text-purple-600">Avg Region Size</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-700">{{ serviceAreasInfo.total_area?.toFixed(0) || 'N/A' }}</div>
              <div class="text-purple-600">Total Area</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Find Route Tab -->
    <div v-if="activeTab === 'route'" class="space-y-6">
      <!-- Location Input -->
      <div class="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Emergency Location</h3>
        <p class="text-sm text-gray-600 mb-4">
          Click on the map or enter coordinates to set an emergency location. The system will automatically 
          find the nearest hospital using Voronoi partitioning and calculate the optimal route.
        </p>

        <!-- Interactive Map Selection -->
        <div class="mb-4">
          <h4 class="font-semibold text-gray-900 mb-2">Select Location on Map</h4>
          <p class="text-xs text-gray-600 mb-3">Click anywhere on the map to set emergency location</p>
          <MapVisualization 
            ref="mapViz"
            :graphData="graphData"
            :highlightedNodes="hospitalNodes"
            :selectionMode="true"
            :singleNodeMode="true"
            @nodes-selected="handleLocationSelected"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Latitude</label>
            <input
              v-model.number="emergencyLat"
              type="number"
              step="0.000001"
              placeholder="20.xxx"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Longitude</label>
            <input
              v-model.number="emergencyLon"
              type="number"
              step="0.000001"
              placeholder="-103.xxx"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Algorithm</label>
            <select
              v-model="routeAlgorithm"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            >
              <option value="astar">A* (Recommended)</option>
              <option value="ucs">UCS</option>
              <option value="bfs">BFS</option>
              <option value="dfs">DFS</option>
              <option value="iddfs">IDDFS</option>
            </select>
          </div>
        </div>

        <button
          @click="findEmergencyRoute"
          :disabled="loading || !emergencyLat || !emergencyLon"
          class="w-full px-6 py-3 bg-royal-blue-600 text-white hover:bg-royal-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-normal text-base"
        >
          <span v-if="loading">Finding Route...</span>
          <span v-else">🚨 Find Nearest Hospital Route</span>
        </button>
      </div>

      <!-- Route Result -->
      <div v-if="routeResult" class="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Emergency Route Result</h3>

        <div v-if="routeResult.success" class="space-y-4">
          <!-- Summary Cards -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-red-50 rounded-lg p-3">
              <div class="text-xs text-red-600 mb-1">Nearest Hospital</div>
              <div class="text-sm font-semibold text-red-900">Hospital {{ routeResult.nearest_hospital_id }}</div>
            </div>
            <div class="bg-blue-50 rounded-lg p-3">
              <div class="text-xs text-blue-600 mb-1">Distance</div>
              <div class="text-sm font-semibold text-blue-900">{{ routeResult.distance_to_hospital?.toFixed(0) }} m</div>
            </div>
            <div class="bg-green-50 rounded-lg p-3">
              <div class="text-xs text-green-600 mb-1">Path Length</div>
              <div class="text-sm font-semibold text-green-900">{{ routeResult.path_length }} nodes</div>
            </div>
            <div class="bg-purple-50 rounded-lg p-3">
              <div class="text-xs text-purple-600 mb-1">Travel Time</div>
              <div class="text-sm font-semibold text-purple-900">{{ routeResult.travel_time?.toFixed(1) || 'N/A' }} min</div>
            </div>
          </div>

          <!-- Map with Route -->
          <div>
            <h4 class="font-semibold text-gray-900 mb-3">Route Visualization</h4>
            <MapVisualization 
              :graphData="graphData"
              :highlightedNodes="[routeResult.start_node, routeResult.nearest_hospital_id]"
              :highlightedPath="routeResult.path"
              :selectionMode="false"
            />
          </div>

          <!-- Route Details -->
          <div class="bg-gray-50 p-4 rounded">
            <h4 class="font-semibold text-gray-900 mb-2">Route Details</h4>
            <div class="text-sm text-gray-700 space-y-1">
              <p><strong>Emergency Location:</strong> ({{ emergencyLat }}, {{ emergencyLon }})</p>
              <p><strong>Start Node:</strong> {{ routeResult.start_node }}</p>
              <p><strong>Destination Hospital:</strong> Node {{ routeResult.nearest_hospital_id }}</p>
              <p><strong>Algorithm Used:</strong> {{ routeAlgorithm.toUpperCase() }}</p>
              <p><strong>Computation Time:</strong> {{ (routeResult.time * 1000).toFixed(2) }} ms</p>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-8 text-red-600">
          <svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="text-lg font-semibold">No route found</p>
          <p class="text-sm mt-2">{{ routeResult.error || 'Unable to find a route to the nearest hospital' }}</p>
        </div>
      </div>
    </div>

    <!-- Instructions -->
    <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded">
      <h4 class="font-semibold text-red-900 mb-2">📝 How It Works</h4>
      <ol class="text-sm text-red-800 space-y-1 list-decimal list-inside">
        <li>Hospitals are automatically detected from OpenStreetMap when you load the map</li>
        <li>The system creates a Voronoi diagram to partition service areas for each hospital</li>
        <li>When you enter an emergency location, it uses Voronoi partitioning to instantly identify the nearest hospital</li>
        <li>The optimal route is calculated using your chosen pathfinding algorithm</li>
      </ol>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import MapVisualization from './MapVisualization.vue'

const props = defineProps({
  graphData: {
    type: Object,
    required: false,
    default: null
  }
})

defineEmits(['close'])

const api = useApi()

// State
const loading = ref(false)
const error = ref(null)
const successMessage = ref(null)
const activeTab = ref('hospitals')

// Hospitals state
const registeredHospitals = ref([])

// Voronoi state
const voronoiImageUrl = ref(null)
const serviceAreasInfo = ref(null)

// Route state
const emergencyLat = ref(null)
const emergencyLon = ref(null)
const routeAlgorithm = ref('astar')
const routeResult = ref(null)
const mapViz = ref(null)

// Computed
const hospitalNodes = computed(() => {
  return registeredHospitals.value.map(h => h.node_id || h.nearest_node)
})

// Methods
const loadHospitals = async () => {
  loading.value = true
  error.value = null

  try {
    const result = await api.getServiceAreas()
    if (result.hospitals) {
      registeredHospitals.value = result.hospitals
      serviceAreasInfo.value = result
      successMessage.value = `Loaded ${result.hospitals.length} hospitals`
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
    }
  } catch (err) {
    error.value = `Failed to load hospitals: ${err.message}`
  } finally {
    loading.value = false
  }
}

const loadVoronoiDiagram = async () => {
  loading.value = true
  error.value = null

  try {
    const timestamp = Date.now()
    voronoiImageUrl.value = `http://localhost:5000/api/emergency/voronoi?t=${timestamp}`
    
    serviceAreasInfo.value = await api.getServiceAreas()
    
    successMessage.value = 'Voronoi diagram generated successfully'
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  } catch (err) {
    error.value = `Failed to load Voronoi diagram: ${err.message}`
  } finally {
    loading.value = false
  }
}

const handleLocationSelected = (nodes) => {
  if (nodes && nodes.length > 0) {
    const node = nodes[0]
    emergencyLat.value = node.lat
    emergencyLon.value = node.lon
  }
}

const findEmergencyRoute = async () => {
  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    const result = await api.getEmergencyRoute(emergencyLat.value, emergencyLon.value, routeAlgorithm.value)
    routeResult.value = result

    if (result.success) {
      successMessage.value = `Route found to Hospital: ${result.distance_to_hospital?.toFixed(0)}m`
      setTimeout(() => {
        successMessage.value = null
      }, 5000)
    }
  } catch (err) {
    error.value = `Failed to find route: ${err.message}`
  } finally {
    loading.value = false
  }
}

// Load hospitals on mount
onMounted(() => {
  loadHospitals()
})
</script>
