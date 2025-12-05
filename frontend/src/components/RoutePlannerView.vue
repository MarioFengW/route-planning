<template>
  <div class="route-planner-view space-y-6 max-w-7xl mx-auto">
    <!-- Header with gradient -->
    <div class="bg-gradient-to-r from-gray-600 to-gray-700 rounded-xl shadow-lg p-6 text-white">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="bg-white bg-opacity-10 rounded-full p-3">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
          </div>
          <div>
            <h2 class="text-2xl font-bold">Route Planning & Algorithm Comparison</h2>
            <p class="text-gray-100 mt-1">Compare BFS, DFS, UCS, IDDFS, and A* algorithms</p>
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

    <!-- Modern Tab Navigation -->
    <div class="bg-white rounded-xl shadow-md overflow-hidden">
      <div class="flex border-b border-gray-200">
        <button
          @click="activeTab = 'single'"
          :class="[
            'flex-1 px-6 py-4 font-medium text-sm border-b-3 transition-all duration-200 flex items-center justify-center space-x-2',
            activeTab === 'single'
              ? 'border-gray-600 text-gray-600 bg-gray-50'
              : 'border-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          ]"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          <span>Single Route</span>
        </button>
        <button
          @click="activeTab = 'evaluation'"
          :class="[
            'flex-1 px-6 py-4 font-medium text-sm border-b-3 transition-all duration-200 flex items-center justify-center space-x-2',
            activeTab === 'evaluation'
              ? 'border-gray-600 text-gray-600 bg-gray-50'
              : 'border-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          ]"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span>Algorithm Evaluation</span>
        </button>
      </div>
    </div>

    <!-- Single Route Tab -->
    <div v-if="activeTab === 'single'" class="space-y-6">
      <!-- Interactive Map for Node Selection -->
      <div class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
        <div class="flex items-center space-x-3 mb-4">
          <div class="bg-gray-100 rounded-lg p-2">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900">Select Start and Goal Nodes</h3>
        </div>
        <p class="text-sm text-gray-600 mb-4">
          Click on the map to select start (green) and goal (red) nodes. 
          <span v-if="selectedNodes.length === 0" class="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">Select start node first</span>
          <span v-else-if="selectedNodes.length === 1" class="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">Now select goal node</span>
          <span v-else class="inline-flex items-center px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">Both nodes selected!</span>
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
      <div class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
        <div class="flex items-center space-x-3 mb-4">
          <div class="bg-gray-100 rounded-lg p-2">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900">Plan Route</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Algorithm</label>
            <select
              v-model="selectedAlgorithm"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500"
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
          :class="[
            'w-full px-8 py-4 rounded-xl font-bold text-lg transition-all duration-200 shadow-lg flex items-center justify-center space-x-2',
            selectedNodes.length >= 2 && !loading
              ? 'bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-600 text-white hover:shadow-xl transform hover:scale-105'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          ]"
        >
          <svg v-if="loading" class="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else-if="selectedNodes.length >= 2" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span v-if="loading">Planning Route...</span>
          <span v-else-if="selectedNodes.length >= 2">Find Route</span>
          <span v-else>Select Both Nodes First</span>
        </button>
      </div>

      <!-- Single Route Results -->
      <div v-if="singleRouteResult" class="bg-white border-2 border-gray-200 rounded-xl shadow-lg overflow-hidden">
        <div class="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4 text-white">
          <h3 class="text-xl font-bold flex items-center space-x-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Route Result</span>
          </h3>
        </div>
        <div class="p-6">

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border-2 border-gray-300">
            <div class="flex items-center space-x-2 mb-2">
              <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
              <div class="text-xs font-medium text-gray-600">Algorithm</div>
            </div>
            <div class="text-lg font-bold text-gray-900 uppercase">{{ singleRouteResult.algorithm }}</div>
          </div>
          <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 border-2 border-green-200">
            <div class="flex items-center space-x-2 mb-2">
              <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <div class="text-xs font-medium text-green-600">Path Length</div>
            </div>
            <div class="text-lg font-bold text-green-900">{{ singleRouteResult.path_length || singleRouteResult.path?.length || 0 }} nodes</div>
          </div>
          <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border-2 border-gray-300">
            <div class="flex items-center space-x-2 mb-2">
              <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
              </svg>
              <div class="text-xs font-medium text-gray-600">Distance</div>
            </div>
            <div class="text-lg font-bold text-gray-900">{{ (singleRouteResult.total_distance || singleRouteResult.cost)?.toFixed(0) || 'N/A' }} m</div>
          </div>
          <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 border-2 border-orange-200">
            <div class="flex items-center space-x-2 mb-2">
              <svg class="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="text-xs font-medium text-orange-600">Time</div>
            </div>
            <div class="text-lg font-bold text-orange-900">{{ ((singleRouteResult.time || singleRouteResult.search_time || 0) * 1000).toFixed(2) }} ms</div>
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
    </div>

    <!-- Evaluation Tab -->
    <div v-if="activeTab === 'evaluation'" class="space-y-6">
      <!-- Evaluation Configuration -->
      <div class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
        <div class="flex items-center space-x-3 mb-4">
          <div class="bg-gray-100 rounded-lg p-2">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900">Evaluation Configuration</h3>
        </div>
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
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500"
          />
          <p class="text-xs text-gray-500 mt-1">
            Total routes to evaluate: {{ numPairsPerRange * 3 }} pairs × 5 algorithms = {{ numPairsPerRange * 15 }} routes
          </p>
        </div>

        <button
          @click="runEvaluation"
          :disabled="loading"
          :class="[
            'mt-4 w-full px-8 py-4 rounded-xl font-bold text-lg transition-all duration-200 shadow-lg flex items-center justify-center space-x-2',
            !loading
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
          <span v-if="loading">Running Evaluation... (this may take a while)</span>
          <span v-else>Run Complete Evaluation</span>
        </button>
      </div>

      <!-- Evaluation Results -->
      <div v-if="evaluationResults" class="space-y-6">
        <!-- Summary by Distance Range -->
        <div class="bg-white border-2 border-gray-200 rounded-lg p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Results by Distance Range
          </h3>

          <div v-for="range in ['short', 'medium', 'long']" :key="range" class="mb-6 last:mb-0">
            <h4 class="font-semibold text-gray-800 mb-3 flex items-center">
              <span class="mr-2">{{ getRangeIcon(range) }}</span>
              {{ getRangeTitle(range) }}
            </h4>

            <!-- Check if this range has data -->
            <div v-if="!evaluationResults.by_range[range] || Object.keys(evaluationResults.by_range[range]).length === 0" class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
              <p class="text-sm text-gray-600">
                <svg class="w-5 h-5 inline mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                No data available for this distance range. The graph may not have node pairs at this distance.
              </p>
            </div>

            <div v-else class="overflow-x-auto">
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
          <h3 class="text-lg font-semibold text-yellow-900 mb-3 flex items-center justify-center">
            <svg class="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            Recommended Algorithm
          </h3>
          <div class="text-center">
            <div class="text-5xl font-bold text-yellow-700 uppercase mb-2">
              {{ evaluationResults.overall_recommendation || 'A*' }}
            </div>
            <p class="text-sm text-yellow-800 mt-3">
              <strong>Based on composite score</strong>
            </p>
            <p class="text-xs text-yellow-700 mt-2">
              Evaluation criteria: Distance (50%), Time (30%), Nodes Expanded (20%)
            </p>
            <p class="text-xs text-yellow-600 mt-1" v-if="['astar', 'ucs'].includes(evaluationResults.overall_recommendation)">
              ✓ Guarantees optimal (shortest) paths
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
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500"
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
                      result.distance_range === 'medium' ? 'bg-gray-100 text-gray-800' :
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
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm font-medium flex items-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export Evaluation Results
          </button>
        </div>
      </div>
    </div>

    <!-- Instructions -->
    <div class="bg-gray-50 border-l-4 border-gray-500 p-4 rounded">
      <h4 class="font-semibold text-gray-900 mb-2 flex items-center">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Instructions
      </h4>
      <div class="text-sm text-gray-800 space-y-2">
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
  if (!evaluationResults.value || !evaluationResults.value.detailed_results) return []
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
  // Clear previous route when selecting new nodes
  currentPath.value = []
  singleRouteResult.value = null
  // Do NOT clear selection - we want to keep the selected nodes visible
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
    
    // Ensure by_range exists with all ranges
    if (!evaluationResults.value.by_range) {
      evaluationResults.value.by_range = {}
    }
    
    const bestAlgo = evaluationResults.value.overall_recommendation?.toUpperCase() || 'A*'
    successMessage.value = `Evaluation completed! Best algorithm: ${bestAlgo} (based on distance, time, and nodes)`

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
    short: '▪',
    medium: '▪▪',
    long: '▪▪▪'
  }
  return icons[range] || '▪'
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
    bfs: 'bg-gray-100 text-gray-800',
    dfs: 'bg-green-100 text-green-800',
    ucs: 'bg-purple-100 text-purple-800',
    iddfs: 'bg-orange-100 text-orange-800',
    astar: 'bg-yellow-100 text-yellow-800'
  }
  return colors[alg] || 'bg-gray-100 text-gray-800'
}

const getTimeColor = (range, alg) => {
  if (!evaluationResults.value || !evaluationResults.value.by_range) return 'text-gray-700'
  if (!evaluationResults.value.by_range[range]) return 'text-gray-700'
  if (!evaluationResults.value.by_range[range][alg]) return 'text-gray-700'
  
  const rangeData = evaluationResults.value.by_range[range]
  const times = Object.entries(rangeData)
    .filter(([_, data]) => data && data.avg_time !== undefined)
    .map(([_, data]) => data.avg_time)
  
  if (times.length === 0) return 'text-gray-700'
  
  const minTime = Math.min(...times)
  const time = rangeData[alg].avg_time
  
  if (time === minTime) return 'text-green-700'
  if (time < minTime * 2) return 'text-gray-700'
  return 'text-orange-700'
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
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

/* Button press effect */
button:active {
  transform: scale(0.98);
}

.route-planner-view {
  scroll-behavior: smooth;
}
</style>
