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
  },
  singleNodeMode: {
    type: Boolean,
    default: false
  },
  hospitalInfo: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['node-selected', 'nodes-selected'])

const mapContainer = ref(null)
const selectedNodes = ref([])
const mapLayer = ref('streets') // Default to Streets view

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
  
  // Debug: Log hospital info
  if (props.hospitalInfo && props.hospitalInfo.length > 0) {
    console.log('Hospital Info:', props.hospitalInfo)
    console.log('Sample hospital node IDs:', props.hospitalInfo.map(h => ({
      node_id: h.node_id,
      nearest_node: h.nearest_node,
      name: h.name
    })))
  }
  
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
    
    // Check if this node is a hospital (compare as strings and numbers)
    const nodeIdStr = String(node.id)
    const nodeIdNum = Number(node.id)
    const hospitalData = props.hospitalInfo.find(h => {
      const hospitalNodeId = h.node_id || h.nearest_node
      return hospitalNodeId === node.id || 
             hospitalNodeId === nodeIdStr || 
             hospitalNodeId === nodeIdNum ||
             String(hospitalNodeId) === nodeIdStr
    })
    
    let color = '#64748b'
    let radius = 3
    
    if (isSelected) {
      color = selectedNodes.value[0]?.id === node.id ? '#10b981' : '#ef4444'
      radius = 6
    } else if (hospitalData) {
      // Hospital nodes in red
      console.log('Found hospital node:', node.id, hospitalData.name)
      color = '#dc2626'
      radius = 7
    } else if (isHighlighted) {
      color = '#f59e0b'
      radius = 5
    }
    
    const marker = L.circleMarker([node.lat, node.lon], {
      radius: radius,
      fillColor: color,
      color: '#fff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.9
    }).addTo(map)
    
    // Add click handler for selection
    if (props.selectionMode) {
      marker.on('click', () => {
        handleNodeSelect(node)
      })
    }
    
    // Add popup with node info
    const popupContent = hospitalData 
      ? `
        <div style="color: #dc2626; font-size: 12px;">
          <strong>🏥 ${hospitalData.name}</strong><br>
          <strong>Node:</strong> ${node.id}<br>
          <strong>Lat:</strong> ${node.lat.toFixed(6)}<br>
          <strong>Lon:</strong> ${node.lon.toFixed(6)}
        </div>
      `
      : `
        <div style="color: #1e40af; font-size: 12px;">
          <strong>Node:</strong> ${node.id}<br>
          <strong>Lat:</strong> ${node.lat.toFixed(6)}<br>
          <strong>Lon:</strong> ${node.lon.toFixed(6)}
        </div>
      `
    
    marker.bindPopup(popupContent)
    
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
  
  // In single node mode, always replace the selection with the new node
  if (props.singleNodeMode) {
    selectedNodes.value = [node]
    // Clear any existing path when selecting a new emergency location
    if (pathPolyline) {
      map.removeLayer(pathPolyline)
      pathPolyline = null
    }
    emit('nodes-selected', [node])
    visualizeGraph()
    return
  }
  
  // Normal mode: allow selecting 2 nodes for route planning
  // Check if the node is already selected
  const existingIndex = selectedNodes.value.findIndex(n => n.id === node.id)
  
  if (existingIndex >= 0) {
    // If the node is already selected, remove it
    selectedNodes.value.splice(existingIndex, 1)
  } else {
    // If we already have 2 nodes, reset and start fresh
    if (selectedNodes.value.length >= 2) {
      selectedNodes.value = [node]
    } else {
      // Add the new node
      selectedNodes.value.push(node)
    }
  }
  
  // Emit the appropriate event
  if (selectedNodes.value.length === 2) {
    emit('nodes-selected', selectedNodes.value)
  } else {
    emit('nodes-selected', selectedNodes.value)
  }
  
  visualizeGraph()
}

const clearSelection = () => {
  selectedNodes.value = []
  // Explicitly clear the path polyline
  if (pathPolyline) {
    map.removeLayer(pathPolyline)
    pathPolyline = null
  }
  visualizeGraph()
}

const refreshVisualization = () => {
  visualizeGraph()
}

// Expose methods to parent component
defineExpose({
  clearSelection,
  refreshVisualization
})

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
