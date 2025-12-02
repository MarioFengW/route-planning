<template>
  <div class="kdtree-view space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-gray-200 pb-4">
      <div>
        <h2 class="text-xl font-medium text-gray-900">KD-Tree Evaluation</h2>
        <p class="text-xs text-gray-500 mt-1">Optimized vertex search in graph</p>
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

    <!-- Step 1: Build KD-Tree -->
    <div class="bg-white border border-gray-200 p-5">
      <h3 class="text-base font-medium text-gray-900 mb-3">Step 1: Build KD-Tree</h3>
      <p class="text-sm text-gray-600 mb-4">
        Construct a KD-Tree from all graph vertices for optimized spatial search.
      </p>
      
      <button
        @click="buildKDTree"
        :disabled="loading || kdTreeBuilt"
        class="px-6 py-2.5 bg-royal-blue-600 text-white hover:bg-royal-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-normal"
      >
        <span v-if="loading">Building KD-Tree...</span>
        <span v-else-if="kdTreeBuilt">✓ KD-Tree Built</span>
        <span v-else>Build KD-Tree</span>
      </button>

      <div v-if="buildTime !== null" class="mt-4 p-3 bg-royal-blue-50 border-l-2 border-royal-blue-600">
        <p class="text-sm text-royal-blue-800">
          <strong>Build Time:</strong> {{ buildTime?.toFixed(4) || '0.0000' }} seconds
        </p>
      </div>
    </div>

    <!-- Step 2: Run Evaluation -->
    <div class="bg-white border border-gray-200 p-5">
      <h3 class="text-base font-medium text-gray-900 mb-3">Step 2: Evaluate Performance</h3>
      <p class="text-sm text-gray-600 mb-4">
        Search for 20 locations and compare KD-Tree vs exhaustive search performance.
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Number of Locations
          </label>
          <input
            v-model.number="numLocations"
            type="number"
            min="1"
            max="100"
            class="w-full px-4 py-2 border border-gray-300 focus:ring-1 focus:ring-royal-blue-500 focus:border-royal-blue-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Location Type
          </label>
          <select
            v-model="useRealLocations"
            class="w-full px-4 py-2 border border-gray-300 focus:ring-1 focus:ring-royal-blue-500 focus:border-royal-blue-500"
          >
            <option :value="true">Real locations (from map bounds)</option>
            <option :value="false">Random locations</option>
          </select>
        </div>
      </div>

      <button
        @click="runEvaluation"
        :disabled="loading || !kdTreeBuilt"
        class="px-6 py-2.5 bg-royal-blue-600 text-white hover:bg-royal-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-normal"
      >
        <span v-if="loading">Running Evaluation...</span>
        <span v-else>Run Evaluation</span>
      </button>

      <p v-if="!kdTreeBuilt" class="text-xs text-orange-600 mt-2">
        ⚠️ Please build the KD-Tree first
      </p>
    </div>

    <!-- Results -->
    <div v-if="evaluationResults" class="bg-white border border-gray-200 p-5">
      <h3 class="text-base font-medium text-gray-900 mb-4">Evaluation Results</h3>

      <!-- Summary Statistics -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- KD-Tree Results -->
        <div class="bg-royal-blue-50 border border-royal-blue-200 p-4">
          <h4 class="font-medium text-royal-blue-900 mb-3">KD-Tree Search</h4>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-royal-blue-700">Average Time:</span>
              <strong class="text-royal-blue-900">{{ ((evaluationResults.kdtree_avg_time || 0) * 1000).toFixed(4) }} ms</strong>
            </div>
            <div class="flex justify-between">
              <span class="text-royal-blue-700">Total Time:</span>
              <strong class="text-royal-blue-900">{{ (evaluationResults.kdtree_total_time || 0).toFixed(4) }} s</strong>
            </div>
            <div class="flex justify-between">
              <span class="text-blue-700">Min Time:</span>
              <span class="text-blue-900">{{ ((evaluationResults.kdtree_min_time || 0) * 1000).toFixed(4) }} ms</span>
            </div>
            <div class="flex justify-between">
              <span class="text-blue-700">Max Time:</span>
              <span class="text-blue-900">{{ ((evaluationResults.kdtree_max_time || 0) * 1000).toFixed(4) }} ms</span>
            </div>
          </div>
        </div>

        <!-- Exhaustive Search Results -->
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4">
          <h4 class="font-semibold text-orange-900 mb-3 flex items-center">
            <span class="text-2xl mr-2">🔍</span>
            Exhaustive Search
          </h4>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-orange-700">Average Time:</span>
              <strong class="text-orange-900">{{ ((evaluationResults.exhaustive_avg_time || 0) * 1000).toFixed(4) }} ms</strong>
            </div>
            <div class="flex justify-between">
              <span class="text-orange-700">Total Time:</span>
              <strong class="text-orange-900">{{ (evaluationResults.exhaustive_total_time || 0).toFixed(4) }} s</strong>
            </div>
            <div class="flex justify-between">
              <span class="text-orange-700">Min Time:</span>
              <span class="text-orange-900">{{ ((evaluationResults.exhaustive_min_time || 0) * 1000).toFixed(4) }} ms</span>
            </div>
            <div class="flex justify-between">
              <span class="text-orange-700">Max Time:</span>
              <span class="text-orange-900">{{ ((evaluationResults.exhaustive_max_time || 0) * 1000).toFixed(4) }} ms</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Comparison -->
      <div class="bg-gradient-to-r from-green-50 to-emerald-100 rounded-lg p-4 mb-6">
        <h4 class="font-semibold text-green-900 mb-3">⚡ Performance Improvement</h4>
        <div class="text-center">
          <div class="text-4xl font-bold text-green-700 mb-2">
            {{ (evaluationResults.speedup_factor || 0).toFixed(2) }}x
          </div>
          <p class="text-sm text-green-800">
            KD-Tree is {{ (evaluationResults.speedup_factor || 0).toFixed(2) }} times faster than exhaustive search
          </p>
          <p class="text-xs text-green-700 mt-2">
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
              <td class="px-3 py-2 whitespace-nowrap text-blue-700 font-semibold">
                {{ ((result.kdtree_time || 0) * 1000).toFixed(4) }}
              </td>
              <td class="px-3 py-2 whitespace-nowrap text-orange-700 font-semibold">
                {{ ((result.exhaustive_time || 0) * 1000).toFixed(4) }}
              </td>
              <td class="px-3 py-2 whitespace-nowrap">
                <span :class="[
                  'px-2 py-1 rounded text-xs font-semibold',
                  result.speedup > 10 ? 'bg-green-100 text-green-800' :
                  result.speedup > 5 ? 'bg-blue-100 text-blue-800' :
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
          class="px-4 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50 text-sm font-normal"
        >
          📥 Export Results JSON
        </button>
      </div>
    </div>

    <!-- Instructions -->
    <div class="bg-royal-blue-50 border-l-2 border-royal-blue-600 p-4">
      <h4 class="font-medium text-royal-blue-900 mb-2">Instructions</h4>
      <ol class="text-sm text-blue-800 space-y-1 list-decimal list-inside">
        <li>Build the KD-Tree from all graph vertices</li>
        <li>Configure the number of test locations (default: 20)</li>
        <li>Run evaluation to compare KD-Tree vs exhaustive search</li>
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
const useRealLocations = ref(true)

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
    const result = await api.evaluateKdTree(numLocations.value, useRealLocations.value)
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
