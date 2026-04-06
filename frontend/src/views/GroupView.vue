<template>
  <div class="max-w-2xl mx-auto py-8 px-4">

    <!-- Loading -->
    <div v-if="loading" class="text-center py-20 text-gray-400">Caricamento...</div>

    <!-- Errore -->
    <div v-else-if="error" class="text-center py-20 text-red-500">{{ error }}</div>

    <div v-else-if="group">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold text-green-700">🍝 {{ group.name }}</h1>
          <p v-if="group.description" class="text-gray-500 text-sm mt-1">{{ group.description }}</p>
        </div>
        <button @click="copyLink" class="text-sm text-gray-500 hover:text-green-600 border border-gray-300 rounded-lg px-3 py-1.5 transition">
          {{ copied ? '✓ Copiato!' : '🔗 Condividi' }}
        </button>
      </div>

      <!-- Tabs -->
      <div class="flex gap-2 mb-6 border-b border-gray-200">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'pb-2 px-1 text-sm font-medium border-b-2 transition',
            activeTab === tab.key
              ? 'border-green-600 text-green-700'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab: Spese -->
      <div v-if="activeTab === 'expenses'">
        <!-- Bottone aggiungi -->
        <button
          @click="showExpenseForm = !showExpenseForm"
          class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg py-2.5 mb-4 transition"
        >
          {{ showExpenseForm ? '✕ Annulla' : '+ Aggiungi spesa' }}
        </button>

        <!-- Form aggiungi spesa -->
        <div v-if="showExpenseForm" class="bg-white rounded-2xl shadow p-5 mb-4">
          <h3 class="font-semibold text-gray-800 mb-3">Nuova spesa</h3>
          <div class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Descrizione</label>
              <input
                v-model="expenseForm.description"
                type="text"
                placeholder="Es. Cena al ristorante"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Importo ({{ group.currency }})</label>
              <input
                v-model="expenseForm.amount"
                type="number"
                min="0"
                step="0.01"
                placeholder="0.00"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Pagato da</label>
              <select
                v-model="expenseForm.paid_by_member_id"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
              >
                <option disabled value="">Seleziona...</option>
                <option v-for="member in group.members" :key="member.id" :value="member.id">
                  {{ member.name }}
                </option>
              </select>
            </div>

            <!-- Tipo split -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Divisione</label>
              <div class="flex gap-2 flex-wrap">
                <button
                  v-for="type in splitTypes"
                  :key="type.key"
                  @click="expenseForm.splitType = type.key"
                  :class="[
                    'flex-1 py-2 rounded-lg text-sm font-medium border transition',
                    expenseForm.splitType === type.key
                      ? 'bg-green-600 text-white border-green-600'
                      : 'bg-white text-gray-600 border-gray-300 hover:border-green-400'
                  ]"
                >
                  {{ type.label }}
                </button>
              </div>
            </div>

            <!-- Split: seleziona persone -->
            <div v-if="expenseForm.splitType === 'subset'" class="space-y-2">
              <p class="text-xs text-gray-500">Seleziona tra chi dividere equamente:</p>
              <div v-for="member in group.members" :key="member.id" class="flex items-center gap-2">
                <input
                  type="checkbox"
                  :id="`subset-${member.id}`"
                  :value="member.id"
                  v-model="expenseForm.subsetIds"
                  class="accent-green-600"
                />
                <label :for="`subset-${member.id}`" class="text-sm text-gray-700 cursor-pointer">
                  {{ member.name }}
                </label>
              </div>
              <p v-if="expenseForm.subsetIds.length > 0" class="text-xs text-green-600">
                {{ (parseFloat(expenseForm.amount) / expenseForm.subsetIds.length).toFixed(2) }} {{ group.currency }} a testa
              </p>
            </div>

            <!-- Split personalizzato -->
            <div v-if="expenseForm.splitType === 'custom'" class="space-y-2">
              <div v-for="member in group.members" :key="member.id" class="flex items-center gap-2">
                <span class="flex-1 text-sm text-gray-700">{{ member.name }}</span>
                <input
                  v-model="expenseForm.customSplits[member.id]"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  class="w-24 border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                />
              </div>
              <p :class="splitSumOk ? 'text-green-600' : 'text-red-500'" class="text-xs text-right">
                Totale split: {{ splitSum.toFixed(2) }} / {{ expenseForm.amount || 0 }}
              </p>
            </div>

            <p v-if="expenseError" class="text-red-500 text-sm">{{ expenseError }}</p>

            <button
              @click="addExpense"
              :disabled="expenseLoading"
              class="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white font-semibold rounded-lg py-2.5 transition"
            >
              {{ expenseLoading ? 'Salvataggio...' : 'Salva spesa' }}
            </button>
          </div>
        </div>

        <!-- Lista spese -->
        <div v-if="group.expenses.length === 0" class="text-center py-10 text-gray-400">
          Nessuna spesa ancora. Aggiungine una!
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="expense in [...group.expenses].reverse()"
            :key="expense.id"
            class="bg-white rounded-2xl shadow px-5 py-4 flex items-center justify-between"
          >
            <div>
              <p class="font-medium text-gray-800">{{ expense.description }}</p>
              <p class="text-sm text-gray-500">
                Pagato da <span class="font-medium">{{ memberName(expense.paid_by_member_id) }}</span>
              </p>
            </div>
            <div class="flex items-center gap-3">
              <span class="font-bold text-green-700">{{ expense.amount }} {{ group.currency }}</span>
              <button @click="deleteExpense(expense.id)" class="text-gray-300 hover:text-red-400 transition text-lg">✕</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: Bilanci -->
      <div v-if="activeTab === 'balances'">
        <div v-if="balancesLoading" class="text-center py-10 text-gray-400">Calcolo...</div>
        <div v-else-if="balances.length === 0" class="text-center py-10 text-gray-400">
          Nessun debito! Siete tutti pari 🎉
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="(balance, i) in balances"
            :key="i"
            class="bg-white rounded-2xl shadow px-5 py-4 flex items-center justify-between"
          >
            <div class="flex items-center gap-2 text-gray-700">
              <span class="font-medium">{{ balance.from_member_name }}</span>
              <span class="text-gray-400">→</span>
              <span class="font-medium">{{ balance.to_member_name }}</span>
            </div>
            <span class="font-bold text-red-500">{{ balance.amount }} {{ group.currency }}</span>
          </div>
        </div>
      </div>

      <!-- Tab: Partecipanti -->
      <div v-if="activeTab === 'members'">
        <div class="bg-white rounded-2xl shadow divide-y divide-gray-100">
          <div v-for="member in group.members" :key="member.id" class="px-5 py-3 flex items-center justify-between">
            <span class="font-medium text-gray-800">{{ member.name }}</span>
            <span class="text-sm text-gray-400">{{ member.email || '' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { groupsApi, type Group, type Balance } from '../api/groups'

const route = useRoute()
const groupId = route.params.id as string

const group = ref<Group | null>(null)
const balances = ref<Balance[]>([])
const loading = ref(true)
const error = ref('')
const copied = ref(false)
const activeTab = ref('expenses')
const balancesLoading = ref(false)

const tabs = [
  { key: 'expenses', label: '💸 Spese' },
  { key: 'balances', label: '⚖️ Bilanci' },
  { key: 'members', label: '👥 Partecipanti' },
]

const showExpenseForm = ref(false)
const expenseLoading = ref(false)
const expenseError = ref('')
const expenseForm = reactive({
  description: '',
  amount: '',
  paid_by_member_id: '' as number | string,
  splitType: 'equal',
  customSplits: {} as Record<number, string>,
  subsetIds: [] as number[],
})

const splitTypes = [
  { key: 'equal', label: 'Tutti' },
  { key: 'subset', label: 'Seleziona persone' },
  { key: 'custom', label: 'Personalizzato' },
]

const splitSum = computed(() => {
  return Object.values(expenseForm.customSplits)
    .reduce((acc, v) => acc + (parseFloat(v) || 0), 0)
})

const splitSumOk = computed(() => {
  const amount = parseFloat(expenseForm.amount)
  return Math.abs(splitSum.value - amount) < 0.02
})

async function loadGroup() {
  try {
    const res = await groupsApi.get(groupId)
    group.value = res.data
  } catch {
    error.value = 'Gruppo non trovato.'
  } finally {
    loading.value = false
  }
}

async function loadBalances() {
  balancesLoading.value = true
  try {
    const res = await groupsApi.getBalances(groupId)
    balances.value = res.data
  } finally {
    balancesLoading.value = false
  }
}

watch(activeTab, (tab) => {
  if (tab === 'balances') loadBalances()
})

function memberName(id: number) {
  return group.value?.members.find(m => m.id === id)?.name || 'Sconosciuto'
}

async function addExpense() {
  expenseError.value = ''
  if (!expenseForm.description.trim()) { expenseError.value = 'Inserisci una descrizione'; return }
  if (!expenseForm.amount || parseFloat(expenseForm.amount) <= 0) { expenseError.value = 'Inserisci un importo valido'; return }
  if (!expenseForm.paid_by_member_id) { expenseError.value = 'Seleziona chi ha pagato'; return }
  if (expenseForm.splitType === 'custom' && !splitSumOk.value) {
    expenseError.value = 'La somma degli split non corrisponde al totale'
    return
  }

  expenseLoading.value = true
  try {
    if (expenseForm.splitType === 'equal') {
      await groupsApi.addExpenseEqual(groupId, {
        paid_by_member_id: expenseForm.paid_by_member_id as number,
        description: expenseForm.description.trim(),
        amount: parseFloat(expenseForm.amount),
      })
    } else if (expenseForm.splitType === 'subset') {
      if (expenseForm.subsetIds.length === 0) {
        expenseError.value = 'Seleziona almeno una persona'
        expenseLoading.value = false
        return
      }
      await groupsApi.addExpenseSubset(groupId, {
        paid_by_member_id: expenseForm.paid_by_member_id as number,
        description: expenseForm.description.trim(),
        amount: parseFloat(expenseForm.amount),
        member_ids: expenseForm.subsetIds,
      })
    } else {
      const splits = Object.entries(expenseForm.customSplits)
        .filter(([, v]) => parseFloat(v) > 0)
        .map(([id, v]) => ({ member_id: parseInt(id), share_amount: parseFloat(v) }))
      await groupsApi.addExpense(groupId, {
        paid_by_member_id: expenseForm.paid_by_member_id as number,
        description: expenseForm.description.trim(),
        amount: parseFloat(expenseForm.amount),
        splits,
      })
    }
    await loadGroup()
    showExpenseForm.value = false
    expenseForm.description = ''
    expenseForm.amount = ''
    expenseForm.paid_by_member_id = ''
    expenseForm.customSplits = {}
    expenseForm.subsetIds = []
  } catch {
    expenseError.value = 'Errore nel salvataggio. Riprova.'
  } finally {
    expenseLoading.value = false
  }
}

async function deleteExpense(expenseId: number) {
  if (!confirm('Eliminare questa spesa?')) return
  await groupsApi.deleteExpense(groupId, expenseId)
  await loadGroup()
}

function copyLink() {
  navigator.clipboard.writeText(window.location.href)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

onMounted(loadGroup)
</script>