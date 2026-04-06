<template>
  <div class="max-w-lg mx-auto py-12 px-4">
    <!-- Header -->
    <div class="text-center mb-10">
      <h1 class="text-4xl font-bold text-green-700 mb-2">🍝 Genovese</h1>
      <p class="text-gray-500">Dividi le spese, non le amicizie</p>
    </div>

    <!-- Form crea gruppo -->
    <div class="bg-white rounded-2xl shadow p-6">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">Crea un nuovo gruppo</h2>

      <div class="space-y-4">
        <!-- Nome gruppo -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nome gruppo</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="Es. Vacanza estate 2025"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
          />
        </div>

        <!-- Descrizione -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Descrizione <span class="text-gray-400">(opzionale)</span></label>
          <input
            v-model="form.description"
            type="text"
            placeholder="Es. Appartamento Barcellona"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
          />
        </div>

        <!-- Valuta -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Valuta</label>
          <select
            v-model="form.currency"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
          >
            <option value="EUR">EUR €</option>
            <option value="USD">USD $</option>
            <option value="GBP">GBP £</option>
            <option value="CHF">CHF ₣</option>
          </select>
        </div>

        <!-- Partecipanti -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Partecipanti</label>
          <div class="space-y-2">
            <div
              v-for="(member, index) in form.members"
              :key="index"
              class="flex gap-2"
            >
              <input
                v-model="member.name"
                type="text"
                :placeholder="`Partecipante ${index + 1}`"
                class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
              />
              <button
                v-if="form.members.length > 2"
                @click="removeMember(index)"
                class="text-red-400 hover:text-red-600 px-2"
              >✕</button>
            </div>
          </div>
          <button
            @click="addMember"
            class="mt-2 text-sm text-green-600 hover:text-green-800 font-medium"
          >
            + Aggiungi partecipante
          </button>
        </div>

        <!-- Errore -->
        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <!-- Submit -->
        <button
          @click="createGroup"
          :disabled="loading"
          class="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white font-semibold rounded-lg py-2.5 transition"
        >
          {{ loading ? 'Creazione...' : 'Crea gruppo' }}
        </button>
      </div>
    </div>

    <!-- Recupera gruppo esistente -->
    <div class="bg-white rounded-2xl shadow p-6 mt-4">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">Hai già un gruppo?</h2>
      <div class="flex gap-2">
        <input
          v-model="existingId"
          type="text"
          placeholder="Incolla il link o l'ID del gruppo"
          class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
        />
        <button
          @click="goToGroup"
          class="bg-gray-700 hover:bg-gray-900 text-white font-semibold rounded-lg px-4 py-2 text-sm transition"
        >
          Vai
        </button>
      </div>
    </div>

    <!-- Footer donazione -->
    <p class="text-center text-xs text-gray-400 mt-8">
      Ti piace Genovese? 
      <a href="https://paypal.me/tuonome" target="_blank" class="text-green-600 hover:underline">Offrimi un caffè ☕</a>
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { groupsApi } from '../api/groups'

const router = useRouter()

const form = reactive({
  name: '',
  description: '',
  currency: 'EUR',
  members: [{ name: '' }, { name: '' }],
})

const existingId = ref('')
const loading = ref(false)
const error = ref('')

function addMember() {
  form.members.push({ name: '' })
}

function removeMember(index: number) {
  form.members.splice(index, 1)
}

async function createGroup() {
  error.value = ''

  if (!form.name.trim()) {
    error.value = 'Inserisci un nome per il gruppo'
    return
  }

  const validMembers = form.members.filter(m => m.name.trim())
  if (validMembers.length < 2) {
    error.value = 'Aggiungi almeno 2 partecipanti'
    return
  }

  loading.value = true
  try {
    const response = await groupsApi.create({
      name: form.name.trim(),
      description: form.description.trim() || undefined,
      currency: form.currency,
      members: validMembers,
    })
    router.push(`/group/${response.data.id}`)
  } catch (e) {
    error.value = 'Errore nella creazione del gruppo. Riprova.'
  } finally {
    loading.value = false
  }
}

function goToGroup() {
  const input = existingId.value.trim()
  if (!input) return

  // Accetta sia l'ID diretto che un URL completo
  const match = input.match(/([a-f0-9-]{36})/)
  if (match) {
    router.push(`/group/${match[1]}`)
  } else {
    error.value = 'ID gruppo non valido'
  }
}
</script>