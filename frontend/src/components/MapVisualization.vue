<template>
  <div class="map-visualization">
    <div class="controls mb-4 flex items-center justify-between">
      <div class="text-sm text-gray-600">
        <span v-if="graphData">
          {{ graphData.total_nodes?.toLocaleString() }} nodes, 
          {{ graphData.total_edges?.toLocaleString() }} edges
          <span v-if="graphData.sampled" class="text-orange-600">(sampled for performance)</span>
        </span>
        <span v-else class="text-gray-400">No map data</span>
      </div>
      <div class="flex gap-2">
        <select 
          v-model="mapLayer" 
          @change="changeLayer"
          class="px-3 py-1 text-sm border rounded"
          style="border-color: #3b82f6; color: #1e40af;"
        >
          <option value="streets">🗺️ Streets</option>
          <option value="satellite">🛰️ Satellite</option>
        </select>
        <button
          v-if="graphData"
          @click="refreshVisualization"
          class="px-3 py-1 text-white rounded text-sm"
          style="background-color: #2563eb;"
        >
          🔄 Refresh
        </button>
      </div>
    </div>
    
    <div class="map-container border-2 overflow-hidden shadow-inner" style="border-color: #3b82f6; height: 600px;">
      <div ref="mapContainer" style="width: 100%; height: 100%;"></div>
    </div>

    <!-- Selected nodes info -->
    <div v-if="selectedNodes.length > 0" class="mt-2 p-2 rounded" style="background-color: #eff6ff;">
      <div class="text-xs font-semibold mb-1" style="color: #1e40af;">Selected Nodes:</div>
      <div v-for="(node, idx) in selectedNodes" :key="node.id" class="text-xs" style="color: #1e40af;">
        {{ idx + 1 }}. Node {{ node.id }} ({{ node.lat.toFixed(6) }}, {{ node.lon.toFixed(6) }})
      </div>
      <button
        @click="clearSelection"
        class="mt-2 px-2 py-1 text-white text-xs rounded"
        style="background-color: #2563eb;"
      >
        Clear Selection
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  graphData: {
    type: Object,
    default: null
  },
  highlightedNodes: {
    type: Array,
    default: () => []
  },
  highlightedPath: {
    type: Array,
    default: () => []
  },
  selectionMode: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['node-selected', 'nodes-selected'])

const mapContainer = ref(null)
const selectedNodes = ref([])
const mapLayer = ref('satellite')

let map = null
let baseLayer = null
let satelliteLayer = null
let nodeMarkers = []
let edgePolylines = []
let pathPolyline = null

const initMap = () => {
  if (!mapContainer.value || map) return
  
  // Initialize map
  map = L.map(mapContainer.value, {
    center: [20.7339, -103.4587], // Guadalajara default
    zoom: 13,
    zoomControl: true,
    minZoom: 11,
    maxBoundsViscosity: 1.0, // Makes the bounds completely solid - cannot drag outside
    maxBounds: null // Will be set dynamically
  })
  
  // Street layer (OpenStreetMap)
  baseLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  })
  
  // Satellite layer (ESRI World Imagery)
  satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles © Esri',
    maxZoom: 19
  })
  
  // Add default layer
  if (mapLayer.value === 'satellite') {
    satelliteLayer.addTo(map)
  } else {
    baseLayer.addTo(map)
  }
}

const changeLayer = () => {
  if (!map) return
  
  if (mapLayer.value === 'satellite') {
    map.removeLayer(baseLayer)
    satelliteLayer.addTo(map)
  } else {
    map.removeLayer(satelliteLayer)
    baseLayer.addTo(map)
  }
}

const clearLayers = () => {
  nodeMarkers.forEach(marker => map.removeLayer(marker))
  edgePolylines.forEach(polyline => map.removeLayer(polyline))
  if (pathPolyline) map.removeLayer(pathPolyline)
  
  nodeMarkers = []
  edgePolylines = []
  pathPolyline = null
}

const visualizeGraph = () => {
  if (!map || !props.graphData) return
  
  clearLayers()
  
  const nodes = props.graphData.nodes || []
  const edges = props.graphData.edges || []
  
  if (nodes.length === 0) return
  
  // Draw edges (roads)
  edges.forEach(edge => {
    const source = nodes.find(n => n.id === edge.source)
    const target = nodes.find(n => n.id === edge.target)
    
    if (source && target) {
      const polyline = L.polyline(
        [[source.lat, source.lon], [target.lat, target.lon]],
        { color: '#94a3b8', weight: 1, opacity: 0.4 }
      ).addTo(map)
      edgePolylines.push(polyline)
    }
  })
  
  // Draw nodes
  nodes.forEach(node => {
    const isHighlighted = props.highlightedNodes.includes(node.id)
    const isSelected = selectedNodes.value.some(n => n.id === node.id)
    
    let color = '#64748b'
    let radius = 3
    
    if (isSelected) {
      color = selectedNodes.value[0]?.id === node.id ? '#10b981' : '#ef4444'
      radius = 6
    } else if (isHighlighted) {
      color = '#f59e0b'
      radius = 5
    }
    
    const marker = L.circleMarker([node.lat, node.lon], {
      radius: radius,
      fillColor: color,
      color: '#fff',
      weight: 1,
      opacity: 1,
      fillOpacity: 0.8
    }).addTo(map)
    
    // Add click handler for selection
    if (props.selectionMode) {
      marker.on('click', () => {
        handleNodeSelect(node)
      })
    }
    
    // Add popup with node info
    marker.bindPopup(`
      <div style="color: #1e40af; font-size: 12px;">
        <strong>Node:</strong> ${node.id}<br>
        <strong>Lat:</strong> ${node.lat.toFixed(6)}<br>
        <strong>Lon:</strong> ${node.lon.toFixed(6)}
      </div>
    `)
    
    nodeMarkers.push(marker)
  })
  
  // Draw highlighted path
  if (props.highlightedPath.length > 1) {
    const pathCoords = props.highlightedPath.map(nodeId => {
      const node = nodes.find(n => n.id === String(nodeId))
      return node ? [node.lat, node.lon] : null
    }).filter(coord => coord !== null)
    
    if (pathCoords.length > 1) {
      pathPolyline = L.polyline(pathCoords, {
        color: '#2563eb',
        weight: 4,
        opacity: 0.8
      }).addTo(map)
    }
  }
  
  // Fit bounds to show only the loaded area
  if (nodes.length > 0) {
    const bounds = L.latLngBounds(nodes.map(n => [n.lat, n.lon]))
    
    // Add small padding to bounds (5% instead of 10%)
    const paddedBounds = bounds.pad(0.05)
    
    // Set strict max bounds to prevent panning outside the area
    map.setMaxBounds(paddedBounds)
    
    // Fit the map to these bounds
    map.fitBounds(bounds, { 
      padding: [50, 50],
      maxZoom: 18
    })
  }
}

const handleNodeSelect = (node) => {
  if (!props.selectionMode) return
  
  if (selectedNodes.value.length >= 2) {
    selectedNodes.value = []
  }
  
  selectedNodes.value.push(node)
  
  if (selectedNodes.value.length === 1) {
    emit('node-selected', node)
  } else if (selectedNodes.value.length === 2) {
    emit('nodes-selected', selectedNodes.value)
  }
  
  visualizeGraph()
}

const clearSelection = () => {
  selectedNodes.value = []
  visualizeGraph()
}

const refreshVisualization = () => {
  visualizeGraph()
}

// Lifecycle
onMounted(() => {
  nextTick(() => {
    initMap()
    if (props.graphData) {
      visualizeGraph()
    }
  })
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})

watch(() => props.graphData, () => {
  if (map && props.graphData) {
    visualizeGraph()
  }
}, { deep: true })

watch(() => [props.highlightedNodes, props.highlightedPath], () => {
  if (map && props.graphData) {
    visualizeGraph()
  }
}, { deep: true })
</script>

<style scoped>
.map-visualization {
  width: 100%;
}

/* Leaflet overrides */
:deep(.leaflet-container) {
  font-family: inherit;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 8px;
}
</style>
