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
          style="border-color: #6b7280; color: #374151;"
        >
          <option value="streets">Streets</option>
          <option value="satellite">Satellite</option>
        </select>
        <button
          v-if="graphData"
          @click="refreshVisualization"
          class="px-3 py-1 text-white rounded text-sm flex items-center space-x-1"
          style="background-color: #4b5563;"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Refresh</span>
        </button>
      </div>
    </div>
    
    <div class="map-container border-2 overflow-hidden shadow-inner" style="border-color: #6b7280; height: 600px;">
      <div ref="mapContainer" style="width: 100%; height: 100%;"></div>
    </div>

    <!-- Selected nodes info -->
    <div v-if="selectedNodes.length > 0" class="mt-2 p-2 rounded" style="background-color: #f3f4f6;">
      <div class="text-xs font-semibold mb-1" style="color: #374151;">Selected Nodes:</div>
      <div v-for="(node, idx) in selectedNodes" :key="node.id" class="text-xs" style="color: #374151;">
        {{ idx + 1 }}. Node {{ node.id }} ({{ node.lat.toFixed(6) }}, {{ node.lon.toFixed(6) }})
      </div>
      <button
        @click="clearSelection"
        class="mt-2 px-2 py-1 text-white text-xs rounded"
        style="background-color: #4b5563;"
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
import { Delaunay } from 'd3-delaunay'

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
  },
  selectedEmergencyNode: {
    type: [String, Number],
    default: null
  },
  showVoronoiRegions: {
    type: Boolean,
    default: false
  },
  selectedHospitalIndex: {
    type: Number,
    default: -1
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
let voronoiLayers = []

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

const drawVoronoiRegions = () => {
  if (!map || !props.showVoronoiRegions || !props.hospitalInfo || props.hospitalInfo.length < 2) {
    return
  }
  
  // Clear previous Voronoi layers
  voronoiLayers.forEach(layer => map.removeLayer(layer))
  voronoiLayers = []
  
  console.log('Drawing Voronoi regions for hospitals:', props.hospitalInfo)
  
  // Prepare points for Delaunay triangulation
  const hospitals = props.hospitalInfo
  const points = hospitals.map(h => [h.lon, h.lat])
  
  // Calculate bounds - include graph nodes if available for better bounds
  let minLat, maxLat, minLon, maxLon
  
  if (props.graphData && props.graphData.nodes && props.graphData.nodes.length > 0) {
    // Use graph bounds for better coverage
    const nodeLats = props.graphData.nodes.map(n => n.lat)
    const nodeLons = props.graphData.nodes.map(n => n.lon)
    minLat = Math.min(...nodeLats)
    maxLat = Math.max(...nodeLats)
    minLon = Math.min(...nodeLons)
    maxLon = Math.max(...nodeLons)
    console.log('Using graph bounds for Voronoi diagram')
  } else {
    // Fallback to hospital bounds
    const lats = hospitals.map(h => h.lat)
    const lons = hospitals.map(h => h.lon)
    minLat = Math.min(...lats)
    maxLat = Math.max(...lats)
    minLon = Math.min(...lons)
    maxLon = Math.max(...lons)
  }
  
  // Calculate map size (approximate distance in degrees)
  const latRange = maxLat - minLat
  const lonRange = maxLon - minLon
  const mapSize = Math.max(latRange, lonRange)
  
  // Dynamic expansion: 15% of the map size (adapts to map extent)
  // For a 10km map (≈0.09 degrees), expansion ≈ 0.0135 degrees (≈1.5km)
  // For a 100m map (≈0.0009 degrees), expansion ≈ 0.000135 degrees (≈15m)
  const expansionFactor = 0.15
  const latMargin = mapSize * expansionFactor
  const lonMargin = mapSize * expansionFactor
  
  const xmin = minLon - lonMargin
  const ymin = minLat - latMargin
  const xmax = maxLon + lonMargin
  const ymax = maxLat + latMargin
  
  console.log('Voronoi bounds:', { 
    mapSize: mapSize.toFixed(6), 
    expansion: (mapSize * expansionFactor).toFixed(6),
    bounds: { xmin, ymin, xmax, ymax } 
  })
  
  // Create Delaunay triangulation and Voronoi diagram
  const delaunay = Delaunay.from(points)
  const voronoi = delaunay.voronoi([xmin, ymin, xmax, ymax])
  
  // Colors for different regions
  const colors = [
    'rgba(239, 68, 68, 0.15)',   // red
    'rgba(59, 130, 246, 0.15)',  // blue
    'rgba(34, 197, 94, 0.15)',   // green
    'rgba(251, 146, 60, 0.15)',  // orange
    'rgba(168, 85, 247, 0.15)',  // purple
    'rgba(236, 72, 153, 0.15)',  // pink
    'rgba(14, 165, 233, 0.15)',  // sky
    'rgba(234, 179, 8, 0.15)',   // yellow
    'rgba(99, 102, 241, 0.15)',  // indigo
    'rgba(139, 92, 246, 0.15)'   // violet
  ]
  
  const borderColors = [
    '#ef4444', '#3b82f6', '#22c55e', '#fb923c', '#a855f7',
    '#ec4899', '#0ea5e9', '#eab308', '#6366f1', '#8b5cf6'
  ]
  
  // Draw Voronoi cells
  for (let i = 0; i < hospitals.length; i++) {
    const cell = voronoi.cellPolygon(i)
    if (!cell) continue
    
    // Convert to lat/lon coordinates for Leaflet (swap x,y to lat,lon)
    const latLngs = cell.map(([x, y]) => [y, x])
    
    const isSelected = props.selectedHospitalIndex === i
    const color = isSelected ? 'rgba(34, 197, 94, 0.25)' : colors[i % colors.length]
    const borderColor = isSelected ? '#22c55e' : borderColors[i % borderColors.length]
    const weight = isSelected ? 4 : 3
    
    // Draw the polygon
    const polygon = L.polygon(latLngs, {
      fillColor: color,
      color: borderColor,
      weight: weight,
      opacity: 1,
      fillOpacity: isSelected ? 0.35 : 0.2,
      dashArray: isSelected ? '10, 5' : '5, 5'
    }).addTo(map)
    
    polygon.bindPopup(`
      <div style="font-size: 12px;">
        <strong style="color: ${borderColor};">${hospitals[i].name}</strong><br>
        <span style="font-size: 11px;">
          ${isSelected ? '✓ <strong>Hospital Seleccionado</strong><br>' : ''}
          Región ${i + 1} - Área de influencia
        </span>
      </div>
    `)
    
    voronoiLayers.push(polygon)
  }
  
  console.log(`Drew ${voronoiLayers.length} Voronoi regions`)
}

const clearLayers = () => {
  nodeMarkers.forEach(marker => map.removeLayer(marker))
  edgePolylines.forEach(polyline => map.removeLayer(polyline))
  if (pathPolyline) map.removeLayer(pathPolyline)
  voronoiLayers.forEach(layer => map.removeLayer(layer))
  
  nodeMarkers = []
  edgePolylines = []
  pathPolyline = null
  voronoiLayers = []
}

const visualizeGraph = () => {
  if (!map || !props.graphData) return
  
  clearLayers()
  
  const nodes = props.graphData.nodes || []
  const edges = props.graphData.edges || []
  
  if (nodes.length === 0) return
  
  // Debug: Log highlighted nodes
  if (props.highlightedNodes && props.highlightedNodes.length > 0) {
    console.log('Highlighted nodes:', props.highlightedNodes)
    console.log('Total nodes in graph:', nodes.length)
    console.log('Sample node IDs:', nodes.slice(0, 5).map(n => n.id))
  }
  
  // Debug: Log hospital info
  if (props.hospitalInfo && props.hospitalInfo.length > 0) {
    console.log('Hospital Info:', props.hospitalInfo)
    console.log('Sample hospital node IDs:', props.hospitalInfo.map(h => ({
      node_id: h.node_id,
      nearest_node: h.nearest_node,
      name: h.name
    })))
  }
  
  // Draw Voronoi regions first (if enabled) so they appear below other elements
  drawVoronoiRegions()
  
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
    // Convert both to strings for comparison
    const nodeIdStr = String(node.id)
    const isHighlighted = props.highlightedNodes.some(hId => String(hId) === nodeIdStr)
    const isSelected = selectedNodes.value.some(n => n.id === node.id)
    const isEmergencyNode = props.selectedEmergencyNode && 
      (String(props.selectedEmergencyNode) === nodeIdStr || 
       Number(props.selectedEmergencyNode) === Number(node.id))
    
    // Check if this node is a hospital (compare as strings and numbers)
    const nodeIdNum = Number(node.id)
    
    // Find hospital at this node (now only one hospital per node)
    const hospitalAtNode = props.hospitalInfo.find(h => {
      const hospitalNodeId = h.node_id || h.nearest_node
      return hospitalNodeId === node.id || 
             hospitalNodeId === nodeIdStr || 
             hospitalNodeId === nodeIdNum ||
             String(hospitalNodeId) === nodeIdStr
    })
    
    const hasHospital = !!hospitalAtNode
    
    let color = '#64748b'
    let radius = 3
    
    // Priority: selected nodes (local state) or emergency node prop have highest priority
    if (isSelected || isEmergencyNode) {
      // Selected emergency location in green
      color = '#10b981'
      radius = 7
    } else if (hasHospital) {
      // Hospital nodes in red
      color = '#dc2626'
      radius = 7
    } else if (isHighlighted) {
      // KD-Tree selected nodes in purple
      color = '#9333ea'
      radius = 6
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
    const popupContent = (isSelected || isEmergencyNode)
      ? `
        <div style="color: #10b981; font-size: 12px;">
          <strong>
            <svg style="display: inline; width: 14px; height: 14px; margin-right: 4px;" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
            </svg>
            Ubicación de Emergencia
          </strong><br>
          <strong>Node:</strong> ${node.id}<br>
          <strong>Lat:</strong> ${node.lat.toFixed(6)}<br>
          <strong>Lon:</strong> ${node.lon.toFixed(6)}
        </div>
      `
      : hasHospital
      ? `
        <div style="color: #dc2626; font-size: 12px;">
          <strong>
            <svg style="display: inline; width: 14px; height: 14px; margin-right: 4px;" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm2 2V5h1v1H5zM3 13a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1H4a1 1 0 01-1-1v-3zm2 2v-1h1v1H5zM13 3a1 1 0 00-1 1v3a1 1 0 001 1h3a1 1 0 001-1V4a1 1 0 00-1-1h-3zm1 2v1h1V5h-1z" clip-rule="evenodd" />
              <path d="M11 4a1 1 0 10-2 0v1a1 1 0 002 0V4zM10 7a1 1 0 011 1v1h1a1 1 0 110 2h-1v1a1 1 0 11-2 0v-1H8a1 1 0 110-2h1V8a1 1 0 011-1z" />
            </svg>
            ${hospitalAtNode.name}
          </strong><br>
          <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid #fca5a5;">
            <strong>Hospital:</strong> ${hospitalAtNode.lat?.toFixed(5)}, ${hospitalAtNode.lon?.toFixed(5)}<br>
            <strong>Node ID:</strong> ${node.id}<br>
            <strong>Node:</strong> ${node.lat.toFixed(6)}, ${node.lon.toFixed(6)}
          </div>
        </div>
      `
      : `
        <div style="color: #374151; font-size: 12px;">
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

watch(() => props.selectedEmergencyNode, () => {
  if (map && props.graphData) {
    visualizeGraph()
  }
})

watch(() => [props.showVoronoiRegions, props.selectedHospitalIndex], () => {
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
