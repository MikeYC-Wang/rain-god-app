<script setup>
import MapView from '../components/MapView.vue'
</script>

<template>
  <div>
    <div class="rounded-3xl bg-white shadow-sm p-6 mb-6">
      <div class="flex items-center gap-3 mb-2">
        <font-awesome-icon icon="route" class="text-2xl text-pastel-blue" />
        <h1 class="text-2xl font-bold text-slate-700">路線規劃</h1>
      </div>
      <p class="text-slate-500 text-sm">在地圖上點擊起點與終點，系統將為您規劃路線並分析沿途降雨風險。</p>
    </div>

    <MapView />
  </div>
</template>
