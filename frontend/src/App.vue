<template>
  <div class="min-h-screen bg-gray-50 text-gray-900 transition-colors">
    <button
      type="button"
      class="theme-toggle fixed bottom-4 right-4 z-40 flex h-11 w-11 items-center justify-center rounded-full border border-gray-200 bg-white text-xl shadow-sm transition hover:bg-gray-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-green-600"
      :aria-label="darkTheme ? 'Attiva tema chiaro' : 'Attiva tema scuro'"
      :title="darkTheme ? 'Tema chiaro' : 'Tema scuro'"
      @click="toggleTheme"
    >
      <span aria-hidden="true">{{ darkTheme ? '☀️' : '🌙' }}</span>
    </button>
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const THEME_STORAGE_KEY = 'equa-theme'
const darkTheme = ref(document.documentElement.classList.contains('dark'))

function toggleTheme() {
  darkTheme.value = !darkTheme.value
  document.documentElement.classList.toggle('dark', darkTheme.value)
  localStorage.setItem(THEME_STORAGE_KEY, darkTheme.value ? 'dark' : 'light')
}
</script>
