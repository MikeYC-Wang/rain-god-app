<template>
  <div class="rounded-3xl bg-white shadow-sm p-6">
    <div class="flex items-center gap-3 mb-4">
      <font-awesome-icon icon="circle-info" class="text-2xl text-pastel-blue" />
      <h1 class="text-2xl font-bold text-slate-700">關於雨神同行</h1>
    </div>

    <div class="space-y-4 text-slate-600 text-sm leading-relaxed">
      <p>
        <span class="font-semibold text-slate-700">雨神同行</span>是一款台灣專屬的通勤路徑氣象提醒應用程式。
        透過比對您的通勤路線與中央氣象署的降雨預報資料，在出門前為您提供沿途降雨風險提醒。
      </p>

      <div class="rounded-3xl bg-light-bg p-4">
        <p class="font-semibold text-slate-700 mb-2">
          <font-awesome-icon icon="gear" class="mr-2 text-pastel-blue" />
          技術說明
        </p>
        <ul class="list-disc list-inside space-y-1 text-slate-500">
          <li>使用 PostGIS 空間資料庫進行路線與降雨網格的交集運算</li>
          <li>串接中央氣象署開放資料 API 取得即時降雨預報</li>
          <li>整合 Google Maps API 提供路線規劃功能</li>
        </ul>
      </div>

      <p class="text-slate-400 text-xs">
        資料來源：中央氣象署開放資料平台
      </p>
    </div>
  </div>
</template>
