import { setOptions, importLibrary } from '@googlemaps/js-api-loader'

let initialized = false
let loadPromise = null

function initAndLoad() {
  const apiKey = import.meta.env.GOOGLE_MAPS_API_KEY
  if (!apiKey) {
    return Promise.reject(new Error('缺少 Google Maps API Key，請設定 GOOGLE_MAPS_API_KEY 環境變數。'))
  }

  if (!initialized) {
    setOptions({ apiKey, version: 'weekly' })
    initialized = true
  }

  return Promise.all([
    importLibrary('maps'),
    importLibrary('routes'),
    importLibrary('marker'),
    importLibrary('geometry'),
    importLibrary('core'),
  ]).then(([maps, routes, marker, , core]) => ({
    maps,
    routes,
    marker,
    core,
  }))
}

export function useGoogleMaps() {
  if (!loadPromise) {
    loadPromise = initAndLoad()
  }
  return loadPromise
}
