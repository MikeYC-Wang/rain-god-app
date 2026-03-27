<script setup>
import NavBar from './NavBar.vue'
</script>

<template>
  <div class="min-h-screen bg-light-bg">
    <NavBar />
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <slot />
    </main>
  </div>
</template>
