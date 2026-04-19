<template>
  <div class="text-center text-xs text-gray-400 space-y-2">
    <p>
      Equa è open source e gratis per sempre.
      <a href="https://github.com/fatjonfreskina/equa" target="_blank" class="text-green-600 hover:underline">Vedi il codice →</a>
       <span class="text-gray-300 mx-1">·</span>
      <span>v{{ APP_VERSION }}</span>
    </p>
    <div class="flex items-center justify-center gap-2 flex-wrap">
      <span>Ti è utile? Offrimi un caffè:</span>
      <div class="flex gap-1">
        <a
          v-for="amount in amounts"
          :key="amount.label"
          :href="`https://paypal.me/fatjonfreskina/${amount.value}EUR`"
          target="_blank"
          class="inline-block bg-green-50 hover:bg-green-100 text-green-700 font-medium rounded-lg px-2.5 py-1 transition border border-green-200"
        >{{ amount.label }}</a>
        <a
          href="https://paypal.me/fatjonfreskina"
          target="_blank"
          class="inline-block bg-gray-100 hover:bg-gray-200 text-gray-600 font-medium rounded-lg px-2.5 py-1 transition border border-gray-200"
        >Libero</a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { APP_VERSION } from '../config'
const amounts = [
  { label: '☕ 1€', value: 1 },
  { label: '🍕 2€', value: 2 },
  { label: '🍷 5€', value: 5 },
]
</script>