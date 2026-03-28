<script setup>
import { ref } from 'vue'

const menuOpen = ref(false)

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}
</script>

<template>
  <nav class="bg-pastel-blue shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo / App Name -->
        <RouterLink to="/" class="flex items-center gap-3">
          <font-awesome-icon icon="cloud-rain" class="text-2xl text-white" />
          <span class="text-xl font-bold text-white tracking-wide">雨神同行</span>
        </RouterLink>

        <!-- Desktop Nav -->
        <div class="hidden md:flex items-center gap-6">
          <RouterLink to="/" class="flex items-center gap-2 text-white/90 hover:text-white transition-colors">
            <font-awesome-icon icon="house" class="text-sm" />
            <span>首頁</span>
          </RouterLink>
          <RouterLink to="/route" class="flex items-center gap-2 text-white/90 hover:text-white transition-colors">
            <font-awesome-icon icon="route" class="text-sm" />
            <span>路線規劃</span>
          </RouterLink>
          <RouterLink to="/about" class="flex items-center gap-2 text-white/90 hover:text-white transition-colors">
            <font-awesome-icon icon="circle-info" class="text-sm" />
            <span>關於</span>
          </RouterLink>
        </div>

        <!-- Mobile Menu Button -->
        <button
          class="md:hidden text-white text-xl p-2"
          @click="toggleMenu"
          aria-label="選單"
        >
          <font-awesome-icon :icon="menuOpen ? 'xmark' : 'bars'" />
        </button>
      </div>
    </div>

    <!-- Mobile Menu -->
    <div v-if="menuOpen" class="md:hidden bg-pastel-blue border-t border-white/20 pb-3">
      <RouterLink to="/" class="flex items-center gap-3 px-4 py-3 text-white/90 hover:text-white hover:bg-white/10 transition-colors" @click="menuOpen = false">
        <font-awesome-icon icon="house" class="w-5 text-center" />
        <span>首頁</span>
      </RouterLink>
      <RouterLink to="/route" class="flex items-center gap-3 px-4 py-3 text-white/90 hover:text-white hover:bg-white/10 transition-colors" @click="menuOpen = false">
        <font-awesome-icon icon="route" class="w-5 text-center" />
        <span>路線規劃</span>
      </RouterLink>
      <RouterLink to="/about" class="flex items-center gap-3 px-4 py-3 text-white/90 hover:text-white hover:bg-white/10 transition-colors" @click="menuOpen = false">
        <font-awesome-icon icon="circle-info" class="w-5 text-center" />
        <span>關於</span>
      </RouterLink>
    </div>
  </nav>
</template>
