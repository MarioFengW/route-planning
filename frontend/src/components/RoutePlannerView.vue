<template>
  <div class="route-planner-view space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-gray-200 pb-4">
      <div>
        <h2 class="text-xl font-medium text-gray-900">Route Planning & Algorithm Comparison</h2>
        <p class="text-xs text-gray-500 mt-1">Compare BFS, DFS, UCS, IDDFS, and A* algorithms</p>
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
        @click="activeTab = 'single'"
        :class="[
          'px-6 py-2.5 font-normal text-sm border-b-2 transition-colors',
          activeTab === 'single'
            ? 'border-royal-blue-600 text-royal-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        ]"
      >
        Single Route
      </button>
      <button
        @click="activeTab = 'evaluation'"
        :class="[
          'px-6 py-2.5 font-normal text-sm border-b-2 transition-colors',
          activeTab === 'evaluation'
            ? 'border-royal-blue-600 text-royal-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        ]"
      >
        Algorithm Evaluation
      </button>
    </div>

    <!-- Single Route Tab -->
    <div v-if="activeTab === 'single'" class="space-y-6">
      <!-- Interactive Map for Node Selection -->
      <div class="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Select Start and Goal Nodes</h3>
        <p class="text-sm text-gray-600 mb-4">
          Click on the map to select start (green) and goal (red) nodes. 
          <span v-if="selectedNodes.length === 0" class="text-blue-600">Select start node first.</span>
          <span v-else-if="selectedNodes.length === 1" class="text-orange-600">Now select goal node.</span>
          <span v-else class="text-green-600">Both nodes selected!</span>
        </p>

        <MapVisualization 
          ref="mapViz"
          :graphData="graphData"
          :highlightedPath="currentPath"
          :selectionMode="true"
          @nodes-selected="handleNodesSelected"
        />
      </div>

      <!-- Algorithm Selection and Route Planning -->
      <div class="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Plan Route</h3>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Algorithm</label>
            <select
              v-model="selectedAlgorithm"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="bfs">BFS (Breadth-First Search)</option>
              <option value="dfs">DFS (Depth-First Search)</option>
              <option value="ucs">UCS (Uniform Cost Search)</option>
              <option value="iddfs">IDDFS (Iterative Deepening DFS)</option>
              <option value="astar">A* (A-Star)</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Start Node</label>
            <input
              :value="selectedNodes[0]?.id || 'Not selected'"
              readonly
              class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Goal Node</label>
            <input
              :value="selectedNodes[1]?.id || 'Not selected'"
              readonly
              class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
            />
          </div>
        </div>

        <button
          @click="planSingleRoute"
          :disabled="loading || selectedNodes.length < 2"
          class="w-full px-6 py-2.5 bg-royal-blue-600 text-white hover:bg-royal-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-normal"
        >
          <span v-if="loading">Planning Route...</span>
          <span v-else>Find Route</span>
        </button>
      </div>

      <!-- Single Route Results -->
      <div v-if="singleRouteResult" class="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Route Result</h3>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div class="bg-blue-50 rounded-lg p-3">
            <div class="text-xs text-blue-600 mb-1">Algorithm</div>
            <div class="text-lg font-semibold text-blue-900 uppercase">{{ singleRouteResult.algorithm }}</div>
          </div>
          <div class="bg-green-50 rounded-lg p-3">
            <div class="text-xs text-green-600 mb-1">Path Length</div>
            <div class="text-lg font-semibold text-green-900">{{ singleRouteResult.path_length || singleRouteResult.path?.length || 0 }} nodes</div>
          </div>
          <div class="bg-purple-50 rounded-lg p-3">
            <div class="text-xs text-purple-600 mb-1">Distance</div>
            <div class="text-lg font-semibold text-purple-900">{{ (singleRouteResult.total_distance || singleRouteResult.cost)?.toFixed(0) || 'N/A' }} m</div>
          </div>
          <div class="bg-orange-50 rounded-lg p-3">
            <div class="text-xs text-orange-600 mb-1">Time</div>
            <div class="text-lg font-semibold text-orange-900">{{ ((singleRouteResult.time || singleRouteResult.search_time || 0) * 1000).toFixed(2) }} ms</div>
          </div>
        </div>

        <div v-if="singleRouteResult.path && singleRouteResult.path.length > 0" class="text-sm text-gray-600 bg-gray-50 p-3 rounded">
          <strong>Path:</strong> 
          <span class="font-mono">{{ singleRouteResult.path.slice(0, 10).join(' → ') }}</span>
          <span v-if="singleRouteResult.path.length > 10" class="text-gray-400"> ... ({{ singleRouteResult.path.length - 10 }} more nodes)</span>
        </div>
        <div v-else class="text-sm text-red-600 bg-red-50 p-3 rounded">
          <strong>Error:</strong> No path found between selected nodes.
        </div>
      </div>
    </div>

    <!-- Evaluation Tab -->
    <div v-if="activeTab === 'evaluation'" class="space-y-6">
      <!-- Evaluation Configuration -->
      <div class="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Evaluation Configuration</h3>
        <p class="text-sm text-gray-600 mb-4">
          Compare all 5 algorithms across three distance ranges: &lt;1km, 1-5km, and &gt;5km
        </p>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Number of node pairs per range
          </label>
          <input
            v-model.number="numPairsPerRange"
            type="number"
            min="1"
            max="20"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <p class="text-xs text-gray-500 mt-1">
            Total routes to evaluate: {{ numPairsPerRange * 3 }} pairs × 5 algorithms = {{ numPairsPerRange * 15 }} routes
          </p>
        </div>

        <button
          @click="runEvaluation"
          :disabled="loading"
          class="mt-4 w-full px-6 py-2.5 bg-royal-blue-600 text-white hover:bg-royal-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-normal"
        >
          <span v-if="loading">Running Evaluation... (this may take a while)</span>
          <span v-else>Run Complete Evaluation</span>
        </button>
      </div>

      <!-- Evaluation Results -->
      <div v-if="evaluationResults" class="space-y-6">
        <!-- Summary by Distance Range -->
        <div class="bg-white border-2 border-gray-200 rounded-lg p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">📊 Results by Distance Range</h3>

          <div v-for="range in ['short', 'medium', 'long']" :key="range" class="mb-6 last:mb-0">
            <h4 class="font-semibold text-gray-800 mb-3 flex items-center">
              <span class="mr-2">{{ getRangeIcon(range) }}</span>
              {{ getRangeTitle(range) }}
            </h4>

            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 text-sm">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Algorithm</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Avg Time (ms)</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Avg Path Length</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Avg Distance (m)</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Success Rate</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="alg in ['bfs', 'dfs', 'ucs', 'iddfs', 'astar']" :key="alg" class="hover:bg-gray-50">
                    <td class="px-3 py-2 whitespace-nowrap">
                      <span :class="[
                        'px-2 py-1 rounded text-xs font-semibold uppercase',
                        getAlgorithmColor(alg)
                      ]">
                        {{ alg }}
                      </span>
                    </td>
                    <td class="px-3 py-2 whitespace-nowrap font-semibold" :class="getTimeColor(range, alg)">
                      {{ evaluationResults.by_range[range]?.[alg]?.avg_time ? ((evaluationResults.by_range[range][alg].avg_time || 0) * 1000).toFixed(2) : 'N/A' }}
                    </td>
                    <td class="px-3 py-2 whitespace-nowrap text-gray-700">
                      {{ evaluationResults.by_range[range]?.[alg]?.avg_path_length ? (evaluationResults.by_range[range][alg].avg_path_length || 0).toFixed(1) : 'N/A' }}
                    </td>
                    <td class="px-3 py-2 whitespace-nowrap text-gray-700">
                      {{ evaluationResults.by_range[range]?.[alg]?.avg_distance ? (evaluationResults.by_range[range][alg].avg_distance || 0).toFixed(0) : 'N/A' }}
                    </td>
                    <td class="px-3 py-2 whitespace-nowrap">
                      <span :class="[
                        'px-2 py-1 rounded text-xs font-semibold',
                        (evaluationResults.by_range[range]?.[alg]?.success_rate || 0) === 1
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      ]">
                        {{ evaluationResults.by_range[range]?.[alg]?.success_rate !== undefined ? ((evaluationResults.by_range[range][alg].success_rate || 0) * 100).toFixed(0) : '0' }}%
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Overall Best Algorithm -->
        <div class="bg-gradient-to-r from-yellow-50 to-amber-100 border-2 border-yellow-300 rounded-lg p-6">
          <h3 class="text-lg font-semibold text-yellow-900 mb-3">🏆 Recommended Algorithm</h3>
          <div class="text-center">
            <div class="text-5xl font-bold text-yellow-700 uppercase mb-2">
              {{ evaluationResults.best_overall_algorithm }}
            </div>
            <p class="text-sm text-yellow-800">
              Best overall performance considering speed, path quality, and success rate
            </p>
          </div>
        </div>

        <!-- Detailed Results Table -->
        <div class="bg-white border-2 border-gray-200 rounded-lg p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Detailed Route Results</h3>
          
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Range</label>
            <select
              v-model="detailedFilterRange"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Ranges</option>
              <option value="short">Short Distance (&lt; 1km)</option>
              <option value="medium">Medium Distance (1-5km)</option>
              <option value="long">Long Distance (&gt; 5km)</option>
            </select>
          </div>

          <div class="overflow-x-auto max-h-96 overflow-y-auto">
            <table class="min-w-full divide-y divide-gray-200 text-xs">
              <thead class="bg-gray-50 sticky top-0">
                <tr>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Range</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Start → Goal</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Algorithm</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Time (ms)</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Path Length</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Distance (m)</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(result, idx) in filteredDetailedResults" :key="idx" class="hover:bg-gray-50">
                  <td class="px-2 py-2 whitespace-nowrap">
                    <span :class="[
                      'px-2 py-1 rounded text-xs',
                      result.distance_range === 'short' ? 'bg-green-100 text-green-800' :
                      result.distance_range === 'medium' ? 'bg-blue-100 text-blue-800' :
                      'bg-purple-100 text-purple-800'
                    ]">
                      {{ result.distance_range }}
                    </span>
                  </td>
                  <td class="px-2 py-2 whitespace-nowrap font-mono text-xs">
                    {{ result.start_node }} → {{ result.goal_node }}
                  </td>
                  <td class="px-2 py-2 whitespace-nowrap">
                    <span class="font-semibold uppercase">{{ result.algorithm }}</span>
                  </td>
                  <td class="px-2 py-2 whitespace-nowrap text-gray-700">
                    {{ ((result.time || 0) * 1000).toFixed(2) }}
                  </td>
                  <td class="px-2 py-2 whitespace-nowrap text-gray-700">
                    {{ result.path_length }}
                  </td>
                  <td class="px-2 py-2 whitespace-nowrap text-gray-700">
                    {{ (result.total_distance || 0).toFixed(0) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Export Results -->
        <div class="flex justify-end">
          <button
            @click="exportResults"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm font-medium"
          >
            📥 Export Evaluation Results
          </button>
        </div>
      </div>
    </div>

    <!-- Instructions -->
    <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
      <h4 class="font-semibold text-blue-900 mb-2">📝 Instructions</h4>
      <div class="text-sm text-blue-800 space-y-2">
        <p><strong>Single Route:</strong> Select two nodes on the map, choose an algorithm, and find the optimal route.</p>
        <p><strong>Evaluation:</strong> Run a comprehensive comparison of all 5 algorithms across different distance ranges to determine the best algorithm for your use case.</p>
      </div>
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
const activeTab = ref('single')

// Single route state
const selectedNodes = ref([])
const selectedAlgorithm = ref('astar')
const singleRouteResult = ref(null)
const currentPath = ref([])
const mapViz = ref(null)

// Evaluation state
const numPairsPerRange = ref(5)
const evaluationResults = ref(null)
const detailedFilterRange = ref('all')

// Computed
const filteredDetailedResults = computed(() => {
  if (!evaluationResults.value) return []
  if (detailedFilterRange.value === 'all') {
    return evaluationResults.value.detailed_results
  }
  return evaluationResults.value.detailed_results.filter(
    r => r.distance_range === detailedFilterRange.value
  )
})

// Methods
const handleNodesSelected = (nodes) => {
  selectedNodes.value = nodes
}

const planSingleRoute = async () => {
  if (selectedNodes.value.length < 2) return

  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    const startNode = selectedNodes.value[0]
    const goalNode = selectedNodes.value[1]

    const result = await api.planRoute(
      startNode.lat,
      startNode.lon,
      goalNode.lat,
      goalNode.lon,
      selectedAlgorithm.value
    )

    singleRouteResult.value = result

    // Check if route was successfully found
    if (result.success && result.path && result.path.length > 0) {
      currentPath.value = result.path
      const distance = result.total_distance || result.cost || 0
      const pathLen = result.path_length || result.path.length || 0
      successMessage.value = `Route found! ${pathLen} nodes, ${distance.toFixed(0)}m`

      setTimeout(() => {
        successMessage.value = null
      }, 5000)
    } else {
      currentPath.value = []
      error.value = result.error || 'No path found between the selected nodes. Try selecting different nodes or using a different algorithm.'
    }
  } catch (err) {
    error.value = `Failed to plan route: ${err.message}`
  } finally {
    loading.value = false
  }
}

const runEvaluation = async () => {
  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    const result = await api.evaluateSearchAlgorithms(numPairsPerRange.value)
    
    // Handle the response structure
    if (result.by_range) {
      evaluationResults.value = result
    } else if (result.results) {
      // Old format - transform it
      evaluationResults.value = result.results
    } else {
      throw new Error('Invalid evaluation results format')
    }
    
    const bestAlgo = evaluationResults.value.best_overall_algorithm || 'unknown'
    successMessage.value = `Evaluation completed! Best algorithm: ${bestAlgo.toUpperCase()}`

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
  link.download = `search_algorithms_evaluation_${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(url)
}

const getRangeIcon = (range) => {
  const icons = {
    short: '🏃',
    medium: '🚴',
    long: '🚗'
  }
  return icons[range] || '📍'
}

const getRangeTitle = (range) => {
  const titles = {
    short: 'Short Distance (< 1000m)',
    medium: 'Medium Distance (1000-5000m)',
    long: 'Long Distance (> 5000m)'
  }
  return titles[range] || range
}

const getAlgorithmColor = (alg) => {
  const colors = {
    bfs: 'bg-blue-100 text-blue-800',
    dfs: 'bg-green-100 text-green-800',
    ucs: 'bg-purple-100 text-purple-800',
    iddfs: 'bg-orange-100 text-orange-800',
    astar: 'bg-yellow-100 text-yellow-800'
  }
  return colors[alg] || 'bg-gray-100 text-gray-800'
}

const getTimeColor = (range, alg) => {
  if (!evaluationResults.value) return 'text-gray-700'
  
  const times = Object.entries(evaluationResults.value.by_range[range])
    .map(([_, data]) => data.avg_time)
  const minTime = Math.min(...times)
  const time = evaluationResults.value.by_range[range][alg].avg_time
  
  if (time === minTime) return 'text-green-700'
  if (time < minTime * 2) return 'text-blue-700'
  return 'text-orange-700'
}
</script>
