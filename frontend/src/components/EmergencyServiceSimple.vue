<template>
  <div class="emergency-view space-y-6 max-w-7xl mx-auto">
    <!-- Header with gradient - Azul oscuro y gris -->
    <div class="bg-gradient-to-r from-slate-800 to-slate-900 rounded-xl shadow-lg p-6 text-white">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="bg-white bg-opacity-10 rounded-full p-3">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div>
            <h2 class="text-2xl font-bold flex items-center space-x-2">
              <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <span>Sistema de Emergencias</span>
            </h2>
            <p class="text-slate-300 mt-1">Encuentra el hospital más cercano en tiempo real</p>
          </div>
        </div>
        <button
          @click="$emit('close')"
          class="text-white hover:bg-white hover:bg-opacity-10 rounded-lg p-2 transition-all"
          title="Cerrar"
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

    <!-- Modern Tab Navigation with icons - Azul oscuro -->
    <div class="bg-white rounded-xl shadow-md overflow-hidden">
      <div class="flex border-b border-gray-200">
        <button
          @click="activeTab = 'route'"
          :class="[
            'flex-1 px-6 py-4 font-medium text-sm border-b-3 transition-all duration-200 flex items-center justify-center space-x-2',
            activeTab === 'route'
              ? 'border-gray-900 text-gray-900 bg-gray-50'
              : 'border-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          ]"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          <span>Ruta de Emergencia</span>
        </button>
        <button
          @click="activeTab = 'hospitals'"
          :class="[
            'flex-1 px-6 py-4 font-medium text-sm border-b-3 transition-all duration-200 flex items-center justify-center space-x-2',
            activeTab === 'hospitals'
              ? 'border-gray-900 text-gray-900 bg-gray-50'
              : 'border-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          ]"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          <span>Hospitales</span>
        </button>
        <button
          @click="activeTab = 'voronoi'"
          :class="[
            'flex-1 px-6 py-4 font-medium text-sm border-b-3 transition-all duration-200 flex items-center justify-center space-x-2',
            activeTab === 'voronoi'
              ? 'border-gray-900 text-gray-900 bg-gray-50'
              : 'border-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          ]"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          <span>Diagrama Voronoi</span>
        </button>
      </div>
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
          class="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium mb-4"
        >
          <span v-if="loading">Loading...</span>
          <span v-else class="flex items-center space-x-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Refresh Hospital List</span>
          </span>
        </button>

        <div v-if="registeredHospitals.length > 0" class="space-y-4">
          <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <p class="text-green-800 font-semibold">
              <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ registeredHospitals.length }} hospitals registered and ready for emergency routing
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
                  <td class="px-3 py-2 text-gray-700">
                    {{ hospital.name || `Hospital ${idx + 1}` }}
                  </td>
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
              :hospitalInfo="registeredHospitals"
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

        <div v-if="registeredHospitals.length > 0" class="mt-4">
          <VoronoiMap 
            :hospitals="registeredHospitals"
            :graphData="graphData"
          />
        </div>
        <div v-else class="mt-4 p-8 bg-yellow-50 border-2 border-yellow-300 rounded-lg text-center">
          <svg class="w-12 h-12 mx-auto mb-3 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="text-sm text-yellow-800 font-semibold">No hospitals registered yet</p>
          <p class="text-xs text-yellow-600 mt-1">Register hospitals in the "Hospitales" tab to view the Voronoi diagram</p>
        </div>

        <!-- Service Areas Info -->
        <div v-if="serviceAreasInfo && registeredHospitals.length > 0" class="mt-6 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-4">
          <h4 class="font-semibold text-gray-900 mb-3">Información de Áreas de Servicio</h4>
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div class="text-center bg-white rounded-lg p-3 shadow-sm">
              <div class="text-2xl font-bold text-gray-700">{{ serviceAreasInfo.num_hospitals }}</div>
              <div class="text-gray-600 text-xs">Hospitales</div>
            </div>
            <div class="text-center bg-white rounded-lg p-3 shadow-sm">
              <div class="text-2xl font-bold text-gray-700">{{ registeredHospitals.length }}</div>
              <div class="text-gray-600 text-xs">Nodos Asignados</div>
            </div>
          </div>
          <p class="text-xs text-gray-500 mt-3 text-center">
            Cada color representa el área de influencia aproximada de cada hospital
          </p>
        </div>
      </div>
    </div>

    <!-- Find Route Tab - MAIN FEATURE -->
    <div v-if="activeTab === 'route'" class="space-y-6">
      <!-- Quick Start Guide -->
      <div class="bg-gradient-to-r from-gray-50 to-gray-100 border-2 border-gray-300 rounded-xl p-6 shadow-md">
        <div class="flex items-start space-x-4">
          <div class="bg-gray-500 rounded-full p-3 text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-bold text-gray-900 mb-2">¿Cómo usar el Sistema de Emergencias?</h3>
            <ol class="text-sm text-gray-800 space-y-2 list-decimal list-inside">
              <li><strong>Haz clic en cualquier nodo del mapa</strong> para establecer la ubicación de emergencia (hospitales en <svg class="w-3 h-3 inline text-red-600 fill-current" viewBox="0 0 20 20"><circle cx="10" cy="10" r="8"/></svg> rojo)</li>
              <li><strong>Selecciona el algoritmo</strong> de búsqueda que deseas usar (A* es el recomendado)</li>
              <li><strong>Presiona "Encontrar Ruta"</strong> y el sistema calculará automáticamente la ruta al hospital más cercano</li>
            </ol>
          </div>
        </div>
      </div>

      <!-- Two Column Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- LEFT COLUMN: Controls -->
        <div class="space-y-6">
          
          <!-- Location Selection Card -->
          <div class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
            <div class="flex items-center space-x-3 mb-4">
              <div class="bg-gray-100 rounded-lg p-2">
                <svg class="w-6 h-6 text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 class="text-lg font-bold text-gray-900">Paso 1: Ubicación de Emergencia</h3>
            </div>

            <!-- Selected Location Display -->
            <div v-if="selectedNode" class="mb-4 p-4 bg-green-50 border-2 border-green-300 rounded-lg animate-pulse-slow">
              <div class="flex items-center space-x-2 mb-2">
                <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <h4 class="font-bold text-green-900">Ubicación Seleccionada</h4>
              </div>
              <div class="text-sm text-green-800 space-y-1 ml-7">
                <p><strong>Nodo:</strong> <span class="font-mono">{{ selectedNode.id }}</span></p>
                <p><strong>Lat:</strong> {{ emergencyLat?.toFixed(6) }}</p>
                <p><strong>Lon:</strong> {{ emergencyLon?.toFixed(6) }}</p>
              </div>
            </div>

            <div v-else class="mb-4 p-4 bg-yellow-50 border-2 border-yellow-300 rounded-lg">
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                <p class="text-sm font-medium text-yellow-800">Haz clic en un nodo del mapa para continuar</p>
              </div>
            </div>

            <!-- Map Selection -->
            <div class="border-2 border-gray-300 rounded-lg overflow-hidden">
              <MapVisualization 
                ref="mapViz"
                :graphData="graphData"
                :highlightedNodes="hospitalNodes"
                :hospitalInfo="registeredHospitals"
                :selectedEmergencyNode="selectedNode ? selectedNode.id : null"
                :selectionMode="true"
                :singleNodeMode="true"
                @nodes-selected="handleLocationSelected"
              />
            </div>
          </div>

          <!-- Algorithm Selection Card -->
          <div class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
            <div class="flex items-center space-x-3 mb-4">
              <div class="bg-purple-100 rounded-lg p-2">
                <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
              </div>
              <h3 class="text-lg font-bold text-gray-900">Paso 2: Algoritmo de Búsqueda</h3>
            </div>
            
            <label class="block text-sm font-medium text-gray-700 mb-3">Selecciona el algoritmo a usar:</label>
            <select
              v-model="routeAlgorithm"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-600 focus:border-gray-600 text-gray-900 font-medium shadow-sm hover:border-gray-400 transition-all"
            >
              <option value="astar">A* - Óptimo y Eficiente (Recomendado)</option>
              <option value="ucs">UCS - Costo Uniforme</option>
              <option value="bfs">BFS - Búsqueda en Anchura</option>
              <option value="dfs">DFS - Búsqueda en Profundidad</option>
              <option value="iddfs">IDDFS - Profundización Iterativa</option>
            </select>

            <div class="mt-3 p-3 bg-gray-50 rounded-lg flex items-start space-x-2 border border-gray-300">
              <svg class="w-4 h-4 text-gray-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
              </svg>
              <p class="text-xs text-gray-800">
                <strong>Tip:</strong> A* utiliza heurísticas para encontrar la ruta más corta de forma eficiente.
              </p>
            </div>
          </div>

          <!-- Action Button -->
          <button
            @click="findEmergencyRoute"
            :disabled="loading || !selectedNode || registeredHospitals.length === 0"
            :class="[
              'w-full px-8 py-4 rounded-xl font-bold text-lg transition-all duration-200 shadow-lg',
              selectedNode && !loading && registeredHospitals.length > 0
                ? 'bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-600 text-white hover:shadow-xl transform hover:scale-105'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            ]"
          >
            <span v-if="loading" class="flex items-center justify-center space-x-2">
              <svg class="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Buscando Ruta...</span>
            </span>
            <span v-else-if="registeredHospitals.length === 0" class="flex items-center justify-center space-x-2">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>No Hay Hospitales en el Mapa</span>
            </span>
            <span v-else-if="!selectedNode" class="flex items-center justify-center space-x-2">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>Selecciona Ubicación Primero</span>
            </span>
            <span v-else class="flex items-center justify-center space-x-2">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>ENCONTRAR RUTA AL HOSPITAL</span>
            </span>
          </button>
        </div>

        <!-- RIGHT COLUMN: Results -->
        <div class="space-y-6">
          
          <!-- Route Result -->
          <div v-if="routeResult" class="bg-white border-2 border-gray-200 rounded-xl shadow-lg overflow-hidden">
            <div class="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4 text-white">
              <h3 class="text-xl font-bold flex items-center space-x-2">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Resultado de la Ruta</span>
              </h3>
            </div>

            <div v-if="routeResult.success" class="p-6 space-y-6">
              <!-- Summary Cards -->
              <div class="grid grid-cols-2 gap-4">
                <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border-2 border-gray-300">
                  <div class="flex items-center space-x-2 mb-2">
                    <svg class="w-5 h-5 text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    <div class="text-xs font-medium text-gray-900">Hospital Destino</div>
                  </div>
                  <div class="text-lg font-bold text-gray-900">{{ getHospitalName(routeResult.nearest_hospital_id) }}</div>
                </div>

                <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border-2 border-gray-300">
                  <div class="flex items-center space-x-2 mb-2">
                    <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                    </svg>
                    <div class="text-xs font-medium text-gray-700">Distancia</div>
                  </div>
                  <div class="text-lg font-bold text-gray-900">{{ (routeResult.distance_to_hospital / 1000)?.toFixed(2) }} km</div>
                </div>

                <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 border-2 border-green-200">
                  <div class="flex items-center space-x-2 mb-2">
                    <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                    </svg>
                    <div class="text-xs font-medium text-green-700">Nodos en Ruta</div>
                  </div>
                  <div class="text-lg font-bold text-green-900">{{ routeResult.path_length }}</div>
                </div>

                <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border-2 border-gray-300">
                  <div class="flex items-center space-x-2 mb-2">
                    <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div class="text-xs font-medium text-purple-700">Tiempo Estimado</div>
                  </div>
                  <div class="text-lg font-bold text-purple-900">{{ routeResult.travel_time?.toFixed(1) || 'N/A' }} min</div>
                </div>
              </div>

              <!-- Map with Route -->
              <div class="border-2 border-gray-300 rounded-lg overflow-hidden">
                <MapVisualization 
                  :graphData="graphData"
                  :highlightedNodes="[routeResult.nearest_hospital_id]"
                  :highlightedPath="routeResult.path"
                  :hospitalInfo="registeredHospitals"
                  :selectedEmergencyNode="selectedNode ? selectedNode.id : routeResult.start_node"
                  :selectionMode="false"
                />
              </div>

              <!-- Route Details -->
              <div class="bg-gradient-to-r from-gray-50 to-gray-100 p-5 rounded-xl border-2 border-gray-200">
                <h4 class="font-bold text-gray-900 mb-3 flex items-center space-x-2">
                  <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Detalles de la Ruta</span>
                </h4>
                <div class="text-sm text-gray-700 space-y-2">
                  <div class="flex justify-between items-center p-2 bg-white rounded">
                    <strong class="flex items-center space-x-2">
                      <svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
                      </svg>
                      <span>Ubicación de Emergencia:</span>
                    </strong>
                    <span class="font-mono text-xs">({{ emergencyLat?.toFixed(6) }}, {{ emergencyLon?.toFixed(6) }})</span>
                  </div>
                  <div class="flex justify-between items-center p-2 bg-white rounded">
                    <strong class="flex items-center space-x-2">
                      <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                      </svg>
                      <span>Nodo Inicio:</span>
                    </strong>
                    <span class="font-mono">{{ routeResult.start_node }}</span>
                  </div>
                  <div class="flex justify-between items-center p-2 bg-white rounded">
                    <strong class="flex items-center space-x-2">
                      <svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
                      </svg>
                      <span>Hospital Destino:</span>
                    </strong>
                    <span class="font-semibold">{{ getHospitalName(routeResult.nearest_hospital_id) }}</span>
                  </div>
                  <div class="flex justify-between items-center p-2 bg-white rounded">
                    <strong class="flex items-center space-x-2">
                      <svg class="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd"/>
                      </svg>
                      <span>Algoritmo:</span>
                    </strong>
                    <span class="font-semibold">{{ routeAlgorithm.toUpperCase() }}</span>
                  </div>
                  <div class="flex justify-between items-center p-2 bg-white rounded">
                    <strong class="flex items-center space-x-2">
                      <svg class="w-4 h-4 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                      </svg>
                      <span>Tiempo de Cálculo:</span>
                    </strong>
                    <span class="font-semibold">{{ (routeResult.time * 1000).toFixed(2) }} ms</span>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="p-8">
              <div class="text-center text-gray-600">
                <svg class="w-20 h-20 mx-auto mb-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <p class="text-xl font-bold mb-2">No se encontró ruta</p>
                <p class="text-sm text-gray-600">{{ routeResult.error || 'No se pudo encontrar una ruta al hospital más cercano' }}</p>
              </div>
            </div>
          </div>

          <!-- Placeholder when no result yet -->
          <div v-else class="bg-gradient-to-br from-gray-100 to-gray-200 border-2 border-dashed border-gray-400 rounded-xl p-12 text-center">
            <svg class="w-24 h-24 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <h4 class="text-lg font-semibold text-gray-600 mb-2">Resultado de la Ruta</h4>
            <p class="text-sm text-gray-500">
              Selecciona una ubicación y presiona el botón para ver la ruta
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import MapVisualization from './MapVisualization.vue'
import VoronoiMap from './VoronoiMap.vue'

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
const activeTab = ref('route') // Start with route tab as main feature

// Hospitals state
const registeredHospitals = ref([])

// Service areas state
const serviceAreasInfo = ref(null)

// Route state
const selectedNode = ref(null)
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
      console.log('Loaded hospitals:', result.hospitals)
      console.log('Hospital nodes:', hospitalNodes.value)
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

const handleLocationSelected = (nodes) => {
  if (nodes && nodes.length > 0) {
    const node = nodes[0]
    selectedNode.value = node
    emergencyLat.value = node.lat
    emergencyLon.value = node.lon
    // Clear previous route result when selecting new location
    routeResult.value = null
    // Clear map visualization by refreshing it
    if (mapViz.value) {
      mapViz.value.clearSelection()
    }
    successMessage.value = `Emergency location selected: Node ${node.id}`
    setTimeout(() => {
      successMessage.value = null
    }, 2000)
  }
}

const getHospitalName = (hospitalNodeId) => {
  // Find hospital by node_id or nearest_node
  const hospital = registeredHospitals.value.find(h => 
    (h.node_id && h.node_id === hospitalNodeId) || 
    (h.nearest_node && h.nearest_node === hospitalNodeId)
  )
  
  if (hospital) {
    return hospital.name || `Hospital ${hospitalNodeId}`
  }
  return `Hospital en Nodo ${hospitalNodeId}`
}

const findEmergencyRoute = async () => {
  // Validate hospitals are registered
  if (!registeredHospitals.value || registeredHospitals.value.length === 0) {
    error.value = 'No hospitals registered in the map area. Please load a larger map or manually register hospitals.'
    setTimeout(() => {
      error.value = null
    }, 5000)
    return
  }

  if (!emergencyLat.value || !emergencyLon.value) {
    error.value = 'Please select a location on the map first'
    setTimeout(() => {
      error.value = null
    }, 3000)
    return
  }

  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    const result = await api.getEmergencyRoute(emergencyLat.value, emergencyLon.value, routeAlgorithm.value)
    routeResult.value = result

    if (result.success) {
      successMessage.value = `Route found to nearest hospital: ${result.distance_to_hospital?.toFixed(0)}m away`
      setTimeout(() => {
        successMessage.value = null
      }, 5000)
    } else {
      error.value = result.error || 'No route found to nearest hospital'
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

/* Pulse animation for selected location */
@keyframes pulse-slow {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.animate-pulse-slow {
  animation: pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Hover effects for cards */
.hover\\:shadow-lg:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.hover\\:shadow-xl:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Custom border width for tabs */
.border-b-3 {
  border-bottom-width: 3px;
}

/* Gradient text */
.text-gradient {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Smooth scroll behavior */
.emergency-view {
  scroll-behavior: smooth;
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
  outline: 2px solid #1e3a8a;
  outline-offset: 2px;
}

/* Button press effect */
button:active {
  transform: scale(0.98);
}
</style>

