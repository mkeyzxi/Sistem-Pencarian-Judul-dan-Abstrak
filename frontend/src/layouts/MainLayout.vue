<script setup>
import { ref } from 'vue'
import Header from '@/components/Header.vue'
import Drawer from '@/components/Drawer.vue'
import ChatArea from '@/components/ChatArea.vue'
import InputArea from '@/components/InputArea.vue'

const isDrawerOpen = ref(false)
</script>

<template>
  <div
    class="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 font-display flex flex-col min-h-screen">
    <!-- Header -->
    <Header @toggle-drawer="isDrawerOpen = !isDrawerOpen" />

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto relative flex flex-col max-w-2xl mx-auto w-full pb-32">
      <!-- Chat Area -->
      <ChatArea />
    </main>

    <!-- Input Area -->
    <InputArea />

    <!-- Drawer -->
    <Drawer :is-open="isDrawerOpen" @close="isDrawerOpen = false" />
  </div>
</template>
