<script setup>
import { ref } from 'vue'
import Sidebar from '@/components/Sidebar.vue'
import HeaderChat from '@/components/HeaderChat.vue'
import MainChat from '@/components/MainChat.vue'
import InputChat from '@/components/InputChat.vue'
// Drawer untuk mobile
const isDrawerOpen = ref(false)
</script>

<template>
  <div
    class="bg-bg-base text-text-base font-display w-full h-screen flex flex-col lg:flex-row overflow-hidden"
  >
    <!-- Sidebar (Responsive for Mobile and Desktop) -->
    <Sidebar :is-open="isDrawerOpen" @close="isDrawerOpen = false" />

    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Header -->
      <HeaderChat @menu-click="isDrawerOpen = true" />

      <!-- Chat Area (Scrollable) -->
      <MainChat />

      <!-- Input Area -->
      <InputChat />
    </main>
  </div>
</template>
