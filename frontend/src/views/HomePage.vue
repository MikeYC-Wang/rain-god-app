<script setup>
import MapView from '../components/MapView.vue'
</script>

<template>
  <div>
    <div class="rounded-3xl bg-white shadow-sm p-6 text-center mb-6">
      <font-awesome-icon icon="cloud-rain" class="text-5xl text-pastel-blue mb-3" />
      <h1 class="text-2xl font-bold text-slate-700 mb-1">雨神同行</h1>
      <p class="text-slate-500 text-sm">通勤路徑氣象提醒 - 點擊地圖規劃路線，查詢沿途降雨風險</p>
    </div>

    <MapView />
  </div>
</template>
