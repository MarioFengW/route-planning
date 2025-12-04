<template>
  <div class="emergency-view space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-gray-200 pb-4">
      <div>
        <h2 class="text-xl font-medium text-gray-900">Emergency Service with Voronoi</h2>
        <p class="text-xs text-gray-500 mt-1">Hospital routing with Voronoi partitioning</p>
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

    <div v-if="successMessage" class="bg-gray-50 border-l-2 border-gray-600 p-3">
      <p class="text-sm text-gray-700">{{ successMessage }}</p>
    </div>

    <!-- Tab Selection -->
    <div class="flex border-b border-gray-200">
      <button
        @click="activeTab = 'setup'"
        :class="[
          'px-6 py-2.5 font-normal text-sm border-b-2 transition-colors',
          activeTab === 'setup'
            ? 'border-gray-600 text-gray-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        ]"
      >
        Setup Hospitals
      </button>
      <button
        @click="activeTab = 'voronoi'"
        :class="[
          'px-6 py-2.5 font-normal text-sm border-b-2 transition-colors',
          activeTab === 'voronoi'
            ? 'border-gray-600 text-gray-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        ]"
        :disabled="!hospitalsRegistered"
      >
        Voronoi Diagram
      </button>
      <button
        @click="activeTab = 'route'"
        :class="[
          'px-6 py-2.5 font-normal text-sm border-b-2 transition-colors',
          activeTab === 'route'
            ? 'border-gray-600 text-gray-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        ]"
        :disabled="!hospitalsRegistered"
      >
        Find Route
      </button>
    </div>

    <!-- Setup Hospitals Tab -->
    <div v-if="activeTab === 'setup'" class="space-y-6">
      <!-- Option 1: Manual Hospital Entry -->
      <div class="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Option 1: Manual Hospital Entry</h3>
        <p class="text-sm text-gray-600 mb-4">
          Enter hospital coordinates manually (lat, lon)
        </p>

        <div class="space-y-3 mb-4">
          <div v-for="(hospital, idx) in manualHospitals" :key="idx" class="flex items-center gap-3">
            <input
              v-model.number="hospital.lat"
              type="number"
              step="0.000001"
              placeholder="Latitude"
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            />
            <input
              v-model.number="hospital.lon"
              type="number"
              step="0.000001"
              placeholder="Longitude"
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            />
            <button
              @click="removeHospital(idx)"
              class="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="flex gap-3">
          <button
            @click="addHospital"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm font-medium flex items-center space-x-1"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span>Add Hospital</span>
          </button>
          <button
            @click="registerManualHospitals"
            :disabled="loading || manualHospitals.length === 0"
            class="px-6 py-2 bg-gray-600 text-white hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed font-normal"
          >
            <span v-if="loading">Registering...</span>
            <span v-else>Register Hospitals</span>
          </button>
        </div>

        <!-- Example coordinates -->
        <div class="mt-4 p-3 bg-gray-50 rounded text-xs text-gray-800 border border-gray-300">
          <strong>Example coordinates for Guadalajara:</strong>
          <ul class="mt-1 space-y-1">
            <li>Hospital Civil: 20.6764, -103.3476</li>
            <li>Hospital San Javier: 20.7217, -103.3908</li>
            <li>Hospital Country 2000: 20.6542, -103.4009</li>
          </ul>
        </div>
      </div>

      <!-- Option 2: Auto Search -->
      <div class="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Option 2: Auto Search (OSM)</h3>
        <p class="text-sm text-gray-600 mb-4">
          Automatically search for hospitals in OpenStreetMap within search distance
        </p>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Search Distance (meters)
          </label>
          <input
            v-model.number="searchDistance"
            type="number"
            min="1000"
            max="50000"
            step="1000"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
          />
        </div>

        <button
          @click="searchHospitals"
          :disabled="loading"
          class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          <span v-if="loading">Searching...</span>
          <span v-else>Auto Search Hospitals</span>
        </button>

        <p class=\"text-xs text-orange-600 mt-2 flex items-center\">
          <svg class=\"w-4 h-4 mr-1\" fill=\"currentColor\" viewBox=\"0 0 20 20\">
            <path fill-rule=\"evenodd\" d=\"M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z\" clip-rule=\"evenodd\" />
          </svg>
          Note: Auto search may not find hospitals if none are tagged in OSM within the area
        </p>
      </div>

      <!-- Registered Hospitals Display -->
      <div v-if="registeredHospitals.length > 0" class="bg-white border-2 border-green-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-green-900 mb-4 flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Registered Hospitals ({{ registeredHospitals.length }})
        </h3>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">#</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Node ID</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Latitude</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Longitude</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(hospital, idx) in registeredHospitals" :key="idx" class="hover:bg-gray-50">
                <td class="px-3 py-2 whitespace-nowrap text-gray-900">{{ idx + 1 }}</td>
                <td class="px-3 py-2 whitespace-nowrap font-mono text-xs text-gray-700">{{ hospital.node_id }}</td>
                <td class="px-3 py-2 whitespace-nowrap text-gray-700">{{ hospital.lat.toFixed(6) }}</td>
                <td class="px-3 py-2 whitespace-nowrap text-gray-700">{{ hospital.lon.toFixed(6) }}</td>
                <td class="px-3 py-2 whitespace-nowrap text-gray-600">{{ hospital.name || 'N/A' }}</td>
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
          Enter the location of an emergency to find the nearest hospital and optimal route
        </p>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
          class="mt-4 w-full px-6 py-3 bg-gray-600 text-white hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed font-normal text-base flex items-center justify-center space-x-2"
        >
          <svg v-if="loading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          <span v-if="loading">Finding Route...</span>
          <span v-else>Find Nearest Hospital Route</span>
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
              <div class="text-sm font-semibold text-red-900">{{ routeResult.nearest_hospital_id }}</div>
            </div>
            <div class="bg-gray-50 rounded-lg p-3">
              <div class="text-xs text-gray-600 mb-1">Distance</div>
              <div class="text-sm font-semibold text-gray-900">{{ routeResult.distance_to_hospital.toFixed(0) }} m</div>
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
      <h4 class="font-semibold text-red-900 mb-2 flex items-center">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Instructions
      </h4>
      <ol class="text-sm text-red-800 space-y-1 list-decimal list-inside">
        <li>Register hospitals manually or use auto-search to find them in OSM</li>
        <li>View the Voronoi diagram to see service area partitions</li>
        <li>Enter an emergency location to find the nearest hospital and optimal route</li>
        <li>The system uses Voronoi partitioning to quickly determine the closest hospital</li>
      </ol>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
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
const activeTab = ref('setup')

// Setup state
const manualHospitals = ref([{ lat: null, lon: null }])
const searchDistance = ref(10000)
const hospitalsRegistered = ref(false)
const registeredHospitals = ref([])

// Voronoi state
const voronoiImageUrl = ref(null)
const serviceAreasInfo = ref(null)

// Route state
const emergencyLat = ref(null)
const emergencyLon = ref(null)
const routeAlgorithm = ref('astar')
const routeResult = ref(null)

// Computed
const hospitalNodes = computed(() => {
  return registeredHospitals.value.map(h => h.node_id)
})

// Methods
const addHospital = () => {
  manualHospitals.value.push({ lat: null, lon: null })
}

const removeHospital = (idx) => {
  manualHospitals.value.splice(idx, 1)
}

const registerManualHospitals = async () => {
  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    const validHospitals = manualHospitals.value.filter(h => h.lat && h.lon)
    
    if (validHospitals.length === 0) {
      error.value = 'Please enter at least one valid hospital location'
      return
    }

    const result = await api.registerHospitals(validHospitals)
    registeredHospitals.value = result.hospitals
    hospitalsRegistered.value = true
    successMessage.value = `Successfully registered ${result.num_hospitals} hospitals`

    // Load service areas info
    serviceAreasInfo.value = await api.getServiceAreas()

    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err) {
    error.value = `Failed to register hospitals: ${err.message}`
  } finally {
    loading.value = false
  }
}

const searchHospitals = async () => {
  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    const result = await api.registerHospitals(null, searchDistance.value)
    registeredHospitals.value = result.hospitals
    hospitalsRegistered.value = true
    
    if (result.num_hospitals === 0) {
      error.value = 'No hospitals found in the search area. Try increasing search distance or use manual entry.'
    } else {
      successMessage.value = `Found and registered ${result.num_hospitals} hospitals`
      serviceAreasInfo.value = await api.getServiceAreas()
    }

    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err) {
    error.value = `Failed to search hospitals: ${err.message}`
  } finally {
    loading.value = false
  }
}

const loadVoronoiDiagram = async () => {
  loading.value = true
  error.value = null

  try {
    // Generate URL with timestamp to avoid caching
    const timestamp = Date.now()
    voronoiImageUrl.value = `http://localhost:5000/api/emergency/voronoi?t=${timestamp}`
    
    // Also load service areas info
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

const findEmergencyRoute = async () => {
  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    const result = await api.getEmergencyRoute(emergencyLat.value, emergencyLon.value, routeAlgorithm.value)
    routeResult.value = result

    if (result.success) {
      successMessage.value = `Route found to Hospital ${result.nearest_hospital_id}: ${result.distance_to_hospital.toFixed(0)}m`
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
</script>
