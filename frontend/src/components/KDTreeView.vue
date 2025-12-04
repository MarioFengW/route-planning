<template>
  <div class="kdtree-view space-y-6 max-w-7xl mx-auto">
    <!-- Header with gradient -->
    <div class="bg-gradient-to-r from-gray-600 to-gray-700 rounded-xl shadow-lg p-6 text-white">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="bg-white bg-opacity-10 rounded-full p-3">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
            </svg>
          </div>
          <div>
            <h2 class="text-2xl font-bold">KD-Tree Evaluation</h2>
            <p class="text-gray-100 mt-1">Optimized vertex search in graph</p>
          </div>
        </div>
        <button
          @click="$emit('close')"
          class="text-white hover:bg-white hover:bg-opacity-10 rounded-lg p-2 transition-all"
          title="Close"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Status Messages with animations -->
    <transition name="slide-down">
      <div v-if="error" class="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg shadow-md">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-red-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
          </svg>
          <p class="text-sm text-red-800 font-medium">{{ error }}</p>
        </div>
      </div>
    </transition>

    <transition name="slide-down">
      <div v-if="successMessage" class="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg shadow-md">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
          <p class="text-sm text-green-800 font-medium">{{ successMessage }}</p>
        </div>
      </div>
    </transition>

    <!-- Step 1: Build KD-Tree -->
    <div class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
      <div class="flex items-center space-x-3 mb-4">
        <div class="bg-gray-100 rounded-lg p-2">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
          </svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900">Step 1: Build KD-Tree</h3>
      </div>
      <p class="text-sm text-gray-600 mb-4">
        Construct a KD-Tree from all graph vertices for optimized spatial search.
      </p>
      
      <button
        @click="buildKDTree"
        :disabled="loading || kdTreeBuilt"
        :class="[
          'px-8 py-4 rounded-xl font-bold text-lg transition-all duration-200 shadow-lg flex items-center justify-center space-x-2',
          !loading && !kdTreeBuilt
            ? 'bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-600 text-white hover:shadow-xl transform hover:scale-105'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        ]"
      >
        <svg v-if="loading" class="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else-if="kdTreeBuilt" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        <span v-if="loading">Building KD-Tree...</span>
        <span v-else-if="kdTreeBuilt">KD-Tree Built Successfully</span>
        <span v-else>Build KD-Tree</span>
      </button>

      <div v-if="buildTime !== null" class="mt-4 p-4 bg-gradient-to-r from-gray-50 to-gray-100 border-2 border-gray-300 rounded-lg">
        <div class="flex items-center space-x-2">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm text-gray-800 font-medium">
            <strong>Build Time:</strong> {{ buildTime?.toFixed(4) || '0.0000' }} seconds
          </p>
        </div>
      </div>
    </div>

    <!-- Step 2: Run Evaluation -->
    <div class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
      <div class="flex items-center space-x-3 mb-4">
        <div class="bg-gray-100 rounded-lg p-2">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900">Step 2: Evaluate Performance</h3>
      </div>
      <p class="text-sm text-gray-600 mb-4">
        Search for random locations within map bounds and compare KD-Tree vs exhaustive search performance.
      </p>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Number of Random Locations
        </label>
        <input
          v-model.number="numLocations"
          type="number"
          min="1"
          max="100"
          class="w-full px-4 py-2 border border-gray-300 focus:ring-1 focus:ring-gray-500 focus:border-gray-500"
          placeholder="Enter number of locations (default: 20)"
        />
        <p class="text-xs text-gray-500 mt-1">
          Random locations will be generated within the map bounds
        </p>
      </div>

      <button
        @click="runEvaluation"
        :disabled="loading || !kdTreeBuilt"
        :class="[
          'px-8 py-4 rounded-xl font-bold text-lg transition-all duration-200 shadow-lg flex items-center justify-center space-x-2',
          !loading && kdTreeBuilt
            ? 'bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-600 text-white hover:shadow-xl transform hover:scale-105'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        ]"
      >
        <svg v-if="loading" class="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <span v-if="loading">Running Evaluation...</span>
        <span v-else>Run Evaluation</span>
      </button>

      <p v-if="!kdTreeBuilt" class="text-xs text-orange-600 mt-2 flex items-center">
        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        Please build the KD-Tree first
      </p>
    </div>

    <!-- Results -->
    <div v-if="evaluationResults" class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-lg">
      <h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
        <svg class="w-6 h-6 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        Evaluation Results
      </h3>

      <!-- Summary Statistics -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- KD-Tree Results -->
        <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 border-2 border-gray-300">
          <h4 class="font-bold text-gray-900 mb-4 flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
            </svg>
            KD-Tree Search
          </h4>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between p-2 bg-white bg-opacity-50 rounded">
              <span class="text-gray-700 font-medium">Average Time:</span>
              <strong class="text-gray-900">{{ ((evaluationResults.kdtree_avg_time || 0) * 1000).toFixed(4) }} ms</strong>
            </div>
            <div class="flex justify-between p-2 bg-white bg-opacity-50 rounded">
              <span class="text-gray-700 font-medium">Total Time:</span>
              <strong class="text-gray-900">{{ (evaluationResults.kdtree_total_time || 0).toFixed(4) }} s</strong>
            </div>
            <div class="flex justify-between p-2 bg-white bg-opacity-30 rounded">
              <span class="text-gray-600">Min Time:</span>
              <span class="text-gray-900">{{ ((evaluationResults.kdtree_min_time || 0) * 1000).toFixed(4) }} ms</span>
            </div>
            <div class="flex justify-between p-2 bg-white bg-opacity-30 rounded">
              <span class="text-gray-600">Max Time:</span>
              <span class="text-gray-900">{{ ((evaluationResults.kdtree_max_time || 0) * 1000).toFixed(4) }} ms</span>
            </div>
          </div>
        </div>

        <!-- Exhaustive Search Results -->
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 border-2 border-orange-200">
          <h4 class="font-bold text-orange-900 mb-4 flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Exhaustive Search
          </h4>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between p-2 bg-white bg-opacity-50 rounded">
              <span class="text-orange-700 font-medium">Average Time:</span>
              <strong class="text-orange-900">{{ ((evaluationResults.exhaustive_avg_time || 0) * 1000).toFixed(4) }} ms</strong>
            </div>
            <div class="flex justify-between p-2 bg-white bg-opacity-50 rounded">
              <span class="text-orange-700 font-medium">Total Time:</span>
              <strong class="text-orange-900">{{ (evaluationResults.exhaustive_total_time || 0).toFixed(4) }} s</strong>
            </div>
            <div class="flex justify-between p-2 bg-white bg-opacity-30 rounded">
              <span class="text-orange-600">Min Time:</span>
              <span class="text-orange-900">{{ ((evaluationResults.exhaustive_min_time || 0) * 1000).toFixed(4) }} ms</span>
            </div>
            <div class="flex justify-between p-2 bg-white bg-opacity-30 rounded">
              <span class="text-orange-600">Max Time:</span>
              <span class="text-orange-900">{{ ((evaluationResults.exhaustive_max_time || 0) * 1000).toFixed(4) }} ms</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Comparison -->
      <div class="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6 mb-6 border-2 border-gray-300">
        <h4 class="font-bold text-gray-900 mb-4 flex items-center justify-center">
          <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Performance Improvement
        </h4>
        <div class="text-center">
          <div class="text-4xl font-bold text-gray-700 mb-2">
            {{ (evaluationResults.speedup_factor || 0).toFixed(2) }}x
          </div>
          <p class="text-sm text-gray-800">
            KD-Tree is {{ (evaluationResults.speedup_factor || 0).toFixed(2) }} times faster than exhaustive search
          </p>
          <p class="text-xs text-gray-700 mt-2">
            ({{ ((1 - 1/(evaluationResults.speedup_factor || 1)) * 100).toFixed(1) }}% time reduction)
          </p>
        </div>
      </div>

      <!-- Detailed Results Table -->
      <div class="overflow-x-auto">
        <h4 class="font-semibold text-gray-900 mb-3">Detailed Search Results</h4>
        <table class="min-w-full divide-y divide-gray-200 text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">#</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Query Location</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Nearest Node</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Distance (m)</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">KD-Tree (ms)</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Exhaustive (ms)</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Speedup</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(result, idx) in evaluationResults.detailed_results" :key="idx" class="hover:bg-gray-50">
              <td class="px-3 py-2 whitespace-nowrap text-gray-900">{{ idx + 1 }}</td>
              <td class="px-3 py-2 whitespace-nowrap text-gray-600 font-mono text-xs">
                ({{ (result.query_location?.[0] || 0).toFixed(5) }}, {{ (result.query_location?.[1] || 0).toFixed(5) }})
              </td>
              <td class="px-3 py-2 whitespace-nowrap text-gray-900 font-mono text-xs">
                {{ result.nearest_node }}
              </td>
              <td class="px-3 py-2 whitespace-nowrap text-gray-700">
                {{ (result.distance || 0).toFixed(2) }}
              </td>
              <td class="px-3 py-2 whitespace-nowrap text-gray-700 font-semibold">
                {{ ((result.kdtree_time || 0) * 1000).toFixed(4) }}
              </td>
              <td class="px-3 py-2 whitespace-nowrap text-gray-700 font-semibold">
                {{ ((result.exhaustive_time || 0) * 1000).toFixed(4) }}
              </td>
              <td class="px-3 py-2 whitespace-nowrap">
                <span :class="[
                  'px-2 py-1 rounded text-xs font-semibold',
                  result.speedup > 10 ? 'bg-green-100 text-green-800' :
                  result.speedup > 5 ? 'bg-gray-100 text-gray-800' :
                  'bg-yellow-100 text-yellow-800'
                ]">
                  {{ (result.speedup || 0).toFixed(1) }}x
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Map Visualization with Highlighted Nodes -->
      <div class="mt-6">
        <h4 class="font-semibold text-gray-900 mb-3">Map Visualization</h4>
        <p class="text-sm text-gray-600 mb-3">Highlighted nodes show the nearest vertices found for query locations.</p>
        <MapVisualization 
          :graphData="graphData"
          :highlightedNodes="highlightedNodes"
          :selectionMode="false"
        />
      </div>

      <!-- Export Results -->
      <div class="mt-6 flex justify-end">
        <button
          @click="exportResults"
          class="px-4 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50 text-sm font-normal flex items-center"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export Results JSON
        </button>
      </div>
    </div>

    <!-- Instructions -->
    <div class="bg-gray-50 border-l-2 border-gray-600 p-4">
      <h4 class="font-medium text-gray-900 mb-2">Instructions</h4>
      <ol class="text-sm text-gray-800 space-y-1 list-decimal list-inside">
        <li>Build the KD-Tree from all graph vertices</li>
        <li>Configure the number of random test locations (default: 20)</li>
        <li>Run evaluation to compare KD-Tree vs exhaustive search</li>
        <li>Random locations will be generated within the map bounds</li>
        <li>Analyze the performance difference and speedup factor</li>
        <li>Export results for your report</li>
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
const kdTreeBuilt = ref(false)
const buildTime = ref(null)
const evaluationResults = ref(null)

// Form data
const numLocations = ref(20)

// Computed
const highlightedNodes = computed(() => {
  if (!evaluationResults.value) return []
  return evaluationResults.value.detailed_results.map(r => r.nearest_node)
})

// Methods
const buildKDTree = async () => {
  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    const result = await api.buildKdTree()
    kdTreeBuilt.value = true
    buildTime.value = result.build_time
    successMessage.value = `KD-Tree built successfully in ${(result.build_time || 0).toFixed(4)} seconds`
    
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err) {
    error.value = `Failed to build KD-Tree: ${err.message}`
  } finally {
    loading.value = false
  }
}

const runEvaluation = async () => {
  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    // Always use random locations (use_real_locations = false)
    const result = await api.evaluateKdTree(numLocations.value, false)
    evaluationResults.value = result
    successMessage.value = `Evaluation completed! KD-Tree is ${(result.speedup_factor || 0).toFixed(2)}x faster`
    
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err) {
    error.value = `Failed to run evaluation: ${err.message}`
  } finally {
    loading.value = false
  }
}

const exportResults = () => {
  if (!evaluationResults.value) return

  const dataStr = JSON.stringify(evaluationResults.value, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `kdtree_evaluation_${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
/* Smooth transitions and animations */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Custom border width for tabs */
.border-b-3 {
  border-bottom-width: 3px;
}

/* Hover effects for cards */
.hover\:shadow-lg:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.hover\:shadow-xl:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Loading spinner enhancement */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Focus ring for accessibility */
*:focus-visible {
  outline: 2px solid #9333ea;
  outline-offset: 2px;
}

/* Button press effect */
button:active {
  transform: scale(0.98);
}

.kdtree-view {
  scroll-behavior: smooth;
}
</style>
