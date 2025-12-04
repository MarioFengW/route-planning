<template>
  <div class="voronoi-map">
    <div ref="mapContainer" style="width: 100%; height: 600px; border-radius: 8px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Delaunay } from 'd3-delaunay'

const props = defineProps({
  hospitals: {
    type: Array,
    required: true
  },
  graphData: {
    type: Object,
    default: null
  }
})

const mapContainer = ref(null)
let map = null
let voronoiLayers = []

const initMap = () => {
  if (!mapContainer.value || map) return
  
  // Get center from hospitals
  if (props.hospitals.length === 0) return
  
  const avgLat = props.hospitals.reduce((sum, h) => sum + h.lat, 0) / props.hospitals.length
  const avgLon = props.hospitals.reduce((sum, h) => sum + h.lon, 0) / props.hospitals.length
  
  map = L.map(mapContainer.value, {
    center: [avgLat, avgLon],
    zoom: 13,
    zoomControl: true
  })
  
  // Add satellite layer
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles © Esri',
    maxZoom: 19
  }).addTo(map)
  
  drawVoronoi()
}

const drawVoronoi = () => {
  if (!map) return
  
  // Clear previous layers
  voronoiLayers.forEach(layer => map.removeLayer(layer))
  voronoiLayers = []
  
  if (props.hospitals.length === 0) return
  
  if (props.hospitals.length === 1) {
    // Just show the single hospital
    const h = props.hospitals[0]
    const marker = L.circleMarker([h.lat, h.lon], {
      radius: 10,
      fillColor: '#dc2626',
      color: '#fff',
      weight: 3,
      opacity: 1,
      fillOpacity: 0.9
    }).addTo(map)
    
    marker.bindPopup(`<strong>${h.name}</strong><br>Único hospital en el área`)
    voronoiLayers.push(marker)
    
    map.setView([h.lat, h.lon], 14)
    return
  }
  
  // Prepare points for Delaunay triangulation
  const points = props.hospitals.map(h => [h.lon, h.lat])
  
  // Calculate bounds
  const lats = props.hospitals.map(h => h.lat)
  const lons = props.hospitals.map(h => h.lon)
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  const minLon = Math.min(...lons)
  const maxLon = Math.max(...lons)
  
  // Expand bounds for Voronoi diagram
  const latMargin = (maxLat - minLat) * 0.3 || 0.01
  const lonMargin = (maxLon - minLon) * 0.3 || 0.01
  
  const xmin = minLon - lonMargin
  const ymin = minLat - latMargin
  const xmax = maxLon + lonMargin
  const ymax = maxLat + latMargin
  
  // Create Delaunay triangulation and Voronoi diagram
  const delaunay = Delaunay.from(points)
  const voronoi = delaunay.voronoi([xmin, ymin, xmax, ymax])
  
  // Colors for different regions
  const colors = [
    'rgba(239, 68, 68, 0.25)',   // red
    'rgba(59, 130, 246, 0.25)',  // blue
    'rgba(34, 197, 94, 0.25)',   // green
    'rgba(251, 146, 60, 0.25)',  // orange
    'rgba(168, 85, 247, 0.25)',  // purple
    'rgba(236, 72, 153, 0.25)',  // pink
    'rgba(14, 165, 233, 0.25)',  // sky
    'rgba(234, 179, 8, 0.25)',   // yellow
    'rgba(99, 102, 241, 0.25)',  // indigo
    'rgba(139, 92, 246, 0.25)'   // violet
  ]
  
  const borderColors = [
    '#ef4444', '#3b82f6', '#22c55e', '#fb923c', '#a855f7',
    '#ec4899', '#0ea5e9', '#eab308', '#6366f1', '#8b5cf6'
  ]
  
  // Draw Voronoi cells
  for (let i = 0; i < props.hospitals.length; i++) {
    const cell = voronoi.cellPolygon(i)
    if (!cell) continue
    
    // Convert to lat/lon coordinates for Leaflet (swap x,y to lat,lon)
    const latLngs = cell.map(([x, y]) => [y, x])
    
    const color = colors[i % colors.length]
    const borderColor = borderColors[i % borderColors.length]
    
    // Draw the polygon
    const polygon = L.polygon(latLngs, {
      fillColor: color,
      color: borderColor,
      weight: 3,
      opacity: 1,
      fillOpacity: 0.3,
      dashArray: '5, 5'
    }).addTo(map)
    
    polygon.bindPopup(`
      <div style="font-size: 12px;">
        <strong style="color: ${borderColor};">${props.hospitals[i].name}</strong><br>
        <span style="font-size: 11px;">Área de servicio de este hospital</span>
      </div>
    `)
    
    voronoiLayers.push(polygon)
  }
  
  // Draw hospital markers on top
  props.hospitals.forEach((hospital, idx) => {
    const marker = L.circleMarker([hospital.lat, hospital.lon], {
      radius: 8,
      fillColor: '#dc2626',
      color: '#fff',
      weight: 3,
      opacity: 1,
      fillOpacity: 1,
      zIndexOffset: 1000
    }).addTo(map)
    
    marker.bindPopup(`
      <div style="font-size: 12px;">
        <strong style="color: #dc2626;">
          <svg style="display: inline; width: 14px; height: 14px; margin-right: 4px;" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
          </svg>
          ${hospital.name}
        </strong><br>
        <span style="font-size: 11px;">
          Lat: ${hospital.lat.toFixed(5)}<br>
          Lon: ${hospital.lon.toFixed(5)}<br>
          Node: ${hospital.node_id || hospital.nearest_node}
        </span>
      </div>
    `)
    
    voronoiLayers.push(marker)
  })
  
  // Fit bounds to show all hospitals
  const hospitalBounds = L.latLngBounds(props.hospitals.map(h => [h.lat, h.lon]))
  map.fitBounds(hospitalBounds.pad(0.2))
}

onMounted(() => {
  if (props.hospitals.length > 0) {
    initMap()
  }
})

watch(() => props.hospitals, () => {
  if (map) {
    map.remove()
    map = null
  }
  if (props.hospitals.length > 0) {
    initMap()
  }
}, { deep: true })

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<style scoped>
.voronoi-map {
  width: 100%;
}
</style>
