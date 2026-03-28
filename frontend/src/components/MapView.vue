<script setup>
import { ref, onMounted, computed } from 'vue'
import { setOptions, importLibrary } from '@googlemaps/js-api-loader'

const mapContainer = ref(null)
const map = ref(null)
const loading = ref(true)
const error = ref(null)

const startPoint = ref(null)
const endPoint = ref(null)
const startMarker = ref(null)
const endMarker = ref(null)
const routePolyline = ref(null)
const routeCoords = ref([])

const checkingRain = ref(false)
const rainResult = ref(null)

const TAIWAN_CENTER = { lat: 23.97, lng: 120.97 }
const DEFAULT_ZOOM = 8

const canCheckRain = computed(() => startPoint.value && endPoint.value && routeCoords.value.length > 0)

const pastelMapStyles = [
  { elementType: 'geometry', stylers: [{ color: '#f5f5f5' }] },
  { elementType: 'labels.text.fill', stylers: [{ color: '#616161' }] },
  { elementType: 'labels.text.stroke', stylers: [{ color: '#f5f5f5' }] },
  {
    featureType: 'administrative',
    elementType: 'geometry.stroke',
    stylers: [{ color: '#c9c9c9' }],
  },
  {
    featureType: 'poi',
    elementType: 'geometry',
    stylers: [{ color: '#e8f5e9' }],
  },
  {
    featureType: 'poi.park',
    elementType: 'geometry',
    stylers: [{ color: '#c8e6c9' }],
  },
  {
    featureType: 'road',
    elementType: 'geometry',
    stylers: [{ color: '#ffffff' }],
  },
  {
    featureType: 'road.arterial',
    elementType: 'geometry',
    stylers: [{ color: '#e0e0e0' }],
  },
  {
    featureType: 'road.highway',
    elementType: 'geometry',
    stylers: [{ color: '#dadada' }],
  },
  {
    featureType: 'transit',
    elementType: 'geometry',
    stylers: [{ color: '#e8eaf6' }],
  },
  {
    featureType: 'water',
    elementType: 'geometry',
    stylers: [{ color: '#AEDFF7' }],
  },
  {
    featureType: 'water',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#9e9e9e' }],
  },
]

let mapsLib = null
let markerLib = null
let routesLib = null
let coreLib = null
let directionsService = null

onMounted(async () => {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY
  if (!apiKey) {
    error.value = '缺少 Google Maps API Key，請設定 VITE_GOOGLE_MAPS_API_KEY 環境變數。'
    loading.value = false
    return
  }

  try {
    setOptions({ apiKey, version: 'weekly' })

    const [mapsResult, routesResult, markerResult, , coreResult] = await Promise.all([
      importLibrary('maps'),
      importLibrary('routes'),
      importLibrary('marker'),
      importLibrary('geometry'),
      importLibrary('core'),
    ])

    mapsLib = mapsResult
    markerLib = markerResult
    routesLib = routesResult
    coreLib = coreResult

    const { Map } = mapsResult
    const { DirectionsService } = routesResult

    map.value = new Map(mapContainer.value, {
      center: TAIWAN_CENTER,
      zoom: DEFAULT_ZOOM,
      styles: pastelMapStyles,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
      zoomControl: true,
      mapId: 'raingod_pastel_map',
    })

    directionsService = new DirectionsService()

    map.value.addListener('click', handleMapClick)

    loading.value = false
  } catch (err) {
    error.value = '地圖載入失敗：' + err.message
    loading.value = false
  }
})

function createMarkerContent(color, label) {
  const div = document.createElement('div')
  div.style.width = '20px'
  div.style.height = '20px'
  div.style.borderRadius = '50%'
  div.style.backgroundColor = color
  div.style.border = '2px solid #ffffff'
  div.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)'
  div.title = label
  return div
}

function handleMapClick(event) {
  const latLng = event.latLng
  const { AdvancedMarkerElement } = markerLib

  if (!startPoint.value) {
    startPoint.value = { lat: latLng.lat(), lng: latLng.lng() }
    startMarker.value = new AdvancedMarkerElement({
      position: latLng,
      map: map.value,
      content: createMarkerContent('#22c55e', '起點'),
      title: '起點',
    })
  } else if (!endPoint.value) {
    endPoint.value = { lat: latLng.lat(), lng: latLng.lng() }
    endMarker.value = new AdvancedMarkerElement({
      position: latLng,
      map: map.value,
      content: createMarkerContent('#ef4444', '終點'),
      title: '終點',
    })
    fetchRoute()
  }
}

async function fetchRoute() {
  if (!startPoint.value || !endPoint.value) return

  try {
    const result = await directionsService.route({
      origin: startPoint.value,
      destination: endPoint.value,
      travelMode: routesLib.TravelMode.DRIVING,
    })

    const path = result.routes[0].overview_path
    routeCoords.value = path.map((p) => ({ lat: p.lat(), lng: p.lng() }))

    routePolyline.value = new mapsLib.Polyline({
      path: path,
      geodesic: true,
      strokeColor: '#AEDFF7',
      strokeOpacity: 0.9,
      strokeWeight: 5,
      map: map.value,
    })

    const bounds = new coreLib.LatLngBounds()
    path.forEach((p) => bounds.extend(p))
    map.value.fitBounds(bounds, 60)
  } catch (err) {
    error.value = '路線規劃失敗：' + err.message
  }
}

function resetRoute() {
  if (startMarker.value) {
    startMarker.value.map = null
    startMarker.value = null
  }
  if (endMarker.value) {
    endMarker.value.map = null
    endMarker.value = null
  }
  if (routePolyline.value) {
    routePolyline.value.setMap(null)
    routePolyline.value = null
  }
  startPoint.value = null
  endPoint.value = null
  routeCoords.value = []
  rainResult.value = null
  error.value = null
}

function toGeoJSON(coords) {
  return {
    type: 'LineString',
    coordinates: coords.map((c) => [c.lng, c.lat]),
  }
}

async function checkRain() {
  if (!canCheckRain.value) return

  checkingRain.value = true
  rainResult.value = null

  try {
    const geojson = toGeoJSON(routeCoords.value)
    const response = await fetch('/api/routes/check-rain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ route: geojson }),
    })

    if (!response.ok) {
      throw new Error(`伺服器回應錯誤 (${response.status})`)
    }

    const data = await response.json()
    rainResult.value = data
  } catch (err) {
    rainResult.value = { error: true, message: err.message }
  } finally {
    checkingRain.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <!-- Instruction Banner -->
    <div class="rounded-3xl bg-white shadow-sm p-4 flex items-center gap-3">
      <font-awesome-icon icon="map-location-dot" class="text-xl text-pastel-blue" />
      <p class="text-slate-600 text-sm" v-if="!startPoint">
        請在地圖上點擊選擇<span class="font-semibold text-green-600">起點</span>
      </p>
      <p class="text-slate-600 text-sm" v-else-if="!endPoint">
        請在地圖上點擊選擇<span class="font-semibold text-red-500">終點</span>
      </p>
      <p class="text-slate-600 text-sm" v-else>
        路線已規劃完成，可以查詢降雨風險
      </p>
    </div>

    <!-- Map -->
    <div class="rounded-3xl overflow-hidden shadow-sm bg-white relative" style="min-height: 500px;">
      <!-- Loading State -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-mist-gray/30 z-10">
        <div class="text-center">
          <font-awesome-icon icon="cloud-rain" class="text-4xl text-pastel-blue animate-pulse mb-3" />
          <p class="text-slate-500">地圖載入中...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="error && !map" class="absolute inset-0 flex items-center justify-center bg-mist-gray/30 z-10">
        <div class="text-center px-6">
          <font-awesome-icon icon="triangle-exclamation" class="text-4xl text-warm-yellow mb-3" />
          <p class="text-slate-600">{{ error }}</p>
        </div>
      </div>

      <!-- Map Container -->
      <div ref="mapContainer" class="w-full h-full" style="min-height: 500px;" />
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-wrap gap-3" v-if="!loading && map">
      <button
        @click="checkRain"
        :disabled="!canCheckRain || checkingRain"
        class="bg-warm-yellow hover:bg-warm-yellow-dark text-slate-700 font-semibold px-6 py-3 rounded-3xl shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <font-awesome-icon
          :icon="checkingRain ? 'spinner' : 'cloud-rain'"
          :class="{ 'animate-spin': checkingRain }"
          class="mr-2"
        />
        {{ checkingRain ? '查詢中...' : '查詢降雨風險' }}
      </button>

      <button
        @click="resetRoute"
        :disabled="!startPoint && !endPoint"
        class="bg-mist-gray hover:bg-slate-300 text-slate-600 font-semibold px-6 py-3 rounded-3xl shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <font-awesome-icon icon="rotate-left" class="mr-2" />
        重置路線
      </button>
    </div>

    <!-- Route Error -->
    <div v-if="error && map" class="rounded-3xl bg-warm-yellow/20 border border-warm-yellow p-4 flex items-start gap-3">
      <font-awesome-icon icon="triangle-exclamation" class="text-warm-yellow mt-0.5" />
      <p class="text-slate-700 text-sm">{{ error }}</p>
    </div>

    <!-- Rain Result -->
    <div v-if="rainResult && !rainResult.error" class="rounded-3xl shadow-sm p-5"
      :class="rainResult.has_rain_risk ? 'bg-warm-yellow/20 border border-warm-yellow' : 'bg-green-50 border border-green-300'"
    >
      <div class="flex items-start gap-3">
        <font-awesome-icon
          :icon="rainResult.has_rain_risk ? 'triangle-exclamation' : 'check'"
          :class="rainResult.has_rain_risk ? 'text-warm-yellow' : 'text-green-500'"
          class="text-xl mt-0.5"
        />
        <div>
          <p class="font-semibold text-slate-700">
            {{ rainResult.has_rain_risk ? '注意！路線有降雨風險' : '路線安全，目前無降雨風險' }}
          </p>
          <p v-if="rainResult.message" class="text-slate-600 text-sm mt-1">
            {{ rainResult.message }}
          </p>
        </div>
      </div>
    </div>

    <!-- Rain Check Error -->
    <div v-if="rainResult && rainResult.error" class="rounded-3xl bg-red-50 border border-red-300 p-4 flex items-start gap-3">
      <font-awesome-icon icon="triangle-exclamation" class="text-red-400 mt-0.5" />
      <p class="text-slate-700 text-sm">查詢失敗：{{ rainResult.message }}</p>
    </div>
  </div>
</template>
