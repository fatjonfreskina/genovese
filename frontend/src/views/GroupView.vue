<template>
  <FeedbackDialog :request="dialog" @respond="respond" />
  <div class="max-w-2xl mx-auto py-8 px-4">
    <div v-if="loading" class="text-center py-20 text-gray-400">Caricamento...</div>
    <div v-else-if="error" class="text-center py-20 text-red-500">
      {{ error }}
    </div>

    <div v-else-if="group">
      <!-- Promemoria mostrato solo subito dopo la creazione del gruppo -->
      <div
        v-if="showShareDialog"
        class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40 p-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="share-reminder-title"
        @click.self="closeShareDialog"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-2xl" aria-hidden="true">🔗</p>
              <h2 id="share-reminder-title" class="mt-2 text-xl font-bold text-gray-800">
                Condividi il link del gruppo
              </h2>
            </div>
            <button
              type="button"
              class="text-2xl leading-none text-gray-400 hover:text-gray-700"
              aria-label="Chiudi promemoria condivisione"
              @click="closeShareDialog"
            >
              ×
            </button>
          </div>
          <p class="mt-3 text-sm leading-6 text-gray-600">
            Invialo ai partecipanti e conservalo in una chat: senza il link non sarà possibile
            ritrovare questo gruppo su un altro dispositivo.
          </p>
          <div class="mt-5 grid gap-2 sm:grid-cols-2">
            <a
              :href="whatsAppShareUrl"
              target="_blank"
              rel="noopener noreferrer"
              @click="trackEvent('share_whatsapp')"
              class="flex items-center justify-center gap-2 rounded-lg bg-green-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-green-700"
            >
              <svg
                aria-hidden="true"
                class="h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="M20.5 11.6a8.4 8.4 0 0 1-12.4 7.3L3.5 20l1.2-4.4A8.4 8.4 0 1 1 20.5 11.6Z"
                />
                <path
                  d="M9.1 7.8c.2-.5.5-.5.8-.5h.4c.3 0 .5.1.6.4l.7 1.7c.1.3.1.5-.1.7l-.5.6c.5.9 1.2 1.6 2.1 2.1l.6-.5c.2-.2.5-.2.7-.1l1.7.7c.3.1.4.3.4.6v.4c0 .3-.1.6-.5.8-.4.2-1 .3-1.5.1-3-.9-5.4-3.3-6.3-6.3-.2-.5-.1-1.1.1-1.5Z"
                />
              </svg>
              WhatsApp
            </a>
            <button
              type="button"
              class="flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-semibold text-gray-700 transition hover:bg-gray-50"
              @click="shareGroup"
            >
              <svg
                aria-hidden="true"
                class="h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <circle cx="18" cy="5" r="2.5" />
                <circle cx="6" cy="12" r="2.5" />
                <circle cx="18" cy="19" r="2.5" />
                <path d="m8.2 10.8 7.5-4.4M8.2 13.2l7.5 4.4" />
              </svg>
              Condividi…
            </button>
            <button
              type="button"
              class="flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-semibold text-gray-700 transition hover:bg-gray-50 sm:col-span-2"
              @click="copyLink"
            >
              <svg
                aria-hidden="true"
                class="h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="9" y="9" width="10" height="10" rx="2" />
                <path d="M15 9V7a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2" />
              </svg>
              {{ copied ? '✓ Link copiato' : 'Copia il link' }}
            </button>
          </div>
          <p class="mt-4 break-all rounded-lg bg-gray-50 p-3 text-xs text-gray-500">
            {{ groupLink }}
          </p>
        </div>
      </div>

      <div
        v-if="showCelebration"
        class="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 sm:items-center"
        role="dialog"
        aria-modal="true"
        aria-labelledby="celebration-title"
        @click.self="showCelebration = false"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 text-center shadow-xl">
          <p class="text-4xl" aria-hidden="true">🎉</p>
          <h2 id="celebration-title" class="mt-3 text-xl font-bold text-gray-800">Conti chiusi!</h2>
          <p class="mt-2 text-sm leading-6 text-gray-600">
            Avete chiuso i conti di {{ group.name }}. Se Equa vi è stata utile, puoi offrirci un
            caffè per mantenerla gratuita.
          </p>
          <a
            href="https://paypal.me/fatjonfreskina"
            target="_blank"
            rel="noopener noreferrer"
            @click="trackEvent('donation_clicked')"
            class="mt-5 block rounded-lg bg-green-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-green-700"
            >☕ Offri un caffè</a
          >
          <button
            type="button"
            class="mt-3 text-sm text-gray-500 hover:text-gray-700"
            @click="showCelebration = false"
          >
            Non ora
          </button>
        </div>
      </div>

      <div
        v-if="showClosingSummary"
        class="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 sm:items-center"
        role="dialog"
        aria-modal="true"
        aria-labelledby="closing-summary-title"
        @click.self="showClosingSummary = false"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
          <div class="flex items-start justify-between gap-4">
            <div>
              <span
                class="inline-block rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-700"
              >
                Beta
              </span>
              <h2 id="closing-summary-title" class="mt-2 text-xl font-bold text-gray-800">
                Condividi il riepilogo
              </h2>
            </div>
            <button
              type="button"
              class="text-2xl leading-none text-gray-400 hover:text-gray-700"
              aria-label="Chiudi riepilogo"
              @click="showClosingSummary = false"
            >
              ×
            </button>
          </div>
          <p class="mt-2 text-sm leading-6 text-gray-600">
            Invia al gruppo le somme da pagare e il link per aggiornare i pagamenti.
          </p>
          <div
            class="mt-4 max-h-64 overflow-y-auto whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-sm leading-6 text-gray-700"
          >
            {{ closingSummaryMessage }}
          </div>
          <a
            :href="closingSummaryWhatsAppUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-4 flex items-center justify-center rounded-lg bg-green-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-green-700"
            @click="trackEvent('closing_summary_whatsapp')"
          >
            Condividi su WhatsApp
          </a>
          <button
            type="button"
            class="mt-3 w-full text-sm text-gray-500 hover:text-gray-700"
            @click="showClosingSummary = false"
          >
            Non ora
          </button>
        </div>
      </div>

      <!-- Link home -->
      <div class="mb-4">
        <RouterLink to="/" class="text-sm text-gray-400 hover:text-green-600 transition">
          ← Torna alla home
        </RouterLink>
      </div>

      <!-- Header -->
      <div class="mb-6 flex items-start justify-between gap-4">
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2 mb-1">
            <img :src="equaLogo" alt="" width="24" height="24" class="flex-shrink-0" />
            <h1 class="break-words text-2xl font-bold text-green-700">{{ group.name }}</h1>
          </div>
          <p v-if="group.description" class="text-gray-500 text-sm">
            {{ group.description }}
          </p>
        </div>
        <button
          @click="openShareDialog"
          class="shrink-0 rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-500 transition hover:text-green-600"
        >
          🔗 Condividi
        </button>
      </div>

      <div
        v-if="!savedLocally"
        class="mb-6 flex items-center justify-between gap-3 rounded-xl border border-green-100 bg-green-50 px-4 py-3"
      >
        <div class="min-w-0">
          <p class="text-sm text-green-800">
            Ritrova questo gruppo dalla home su questo dispositivo.
          </p>
        </div>
        <button
          type="button"
          class="shrink-0 text-sm font-semibold text-green-700 underline underline-offset-2 hover:text-green-800"
          @click="saveGroupLocally"
        >
          Salva gruppo
        </button>
      </div>

      <section
        v-if="group.status !== 'active'"
        :class="[
          'mb-6 rounded-xl border px-4 py-4',
          group.status === 'closing'
            ? 'border-amber-100 bg-amber-50'
            : 'border-green-100 bg-green-50',
        ]"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="font-semibold text-gray-800">{{ groupStatusTitle }}</p>
            <p class="mt-1 text-sm text-gray-600">{{ groupStatusDescription }}</p>
          </div>
          <span
            :class="[
              'shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold',
              group.status === 'closing'
                ? 'bg-amber-100 text-amber-700'
                : 'bg-green-100 text-green-700',
            ]"
          >
            {{ groupStatusLabel }}
          </span>
        </div>
        <p v-if="statusError" class="mt-3 text-sm text-red-600">{{ statusError }}</p>
        <div class="mt-4 flex flex-wrap gap-2">
          <button
            v-if="group.status === 'closing'"
            type="button"
            class="rounded-lg border border-amber-300 bg-white px-3 py-2 text-sm font-semibold text-amber-800 transition hover:bg-amber-100"
            @click="showClosingSummary = true"
          >
            Condividi riepilogo
          </button>
          <button
            v-if="group.status === 'closing'"
            type="button"
            :disabled="statusLoading"
            class="rounded-lg bg-green-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-green-700 disabled:bg-gray-300"
            @click="closeGroup"
          >
            {{ statusLoading ? 'Aggiornamento...' : 'Segna come chiuso' }}
          </button>
          <button
            type="button"
            :disabled="statusLoading"
            class="rounded-lg border border-gray-300 px-3 py-2 text-sm font-semibold text-gray-700 transition hover:bg-white disabled:bg-gray-100"
            @click="reopenGroup"
          >
            Riapri conti
          </button>
        </div>
      </section>

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
              : 'border-transparent text-gray-500 hover:text-gray-700',
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab: Spese -->
      <div v-if="activeTab === 'expenses'">
        <!-- Totale spese -->
        <div
          class="bg-green-50 border border-green-100 rounded-xl px-5 py-3 mb-4 flex flex-wrap items-center justify-between gap-3"
        >
          <span class="text-sm text-green-700 font-medium">Totale spese</span>
          <div class="text-right">
            <p
              v-for="total in totalExpenses"
              :key="total.currency"
              class="text-lg font-bold text-green-700"
            >
              {{ formatCurrency(total.amount, total.currency) }}
              <span v-if="hasForeignExpenses" class="text-xs font-medium">{{
                total.currency
              }}</span>
            </p>
            <p v-if="hasForeignExpenses" class="text-xs text-green-700">
              Importi originali, senza conversioni
            </p>
          </div>
        </div>

        <!-- Bottone aggiungi -->
        <button
          v-if="group.status === 'active'"
          @click="openNewExpenseForm"
          class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg py-2.5 mb-4 transition"
        >
          {{ showExpenseForm && !editingExpenseId ? '✕ Annulla' : '+ Aggiungi spesa' }}
        </button>

        <!-- Form aggiunta / modifica spesa -->
        <div v-if="showExpenseForm" id="expense-form" class="bg-white rounded-2xl shadow p-5 mb-4">
          <h3 class="font-semibold text-gray-800 mb-3">
            {{ editingExpenseId ? 'Modifica spesa' : 'Nuova spesa' }}
          </h3>
          <div class="space-y-3">
            <div>
              <label for="expense-description" class="block text-sm font-medium text-gray-700 mb-1"
                >Descrizione</label
              >
              <input
                id="expense-description"
                v-model="expenseForm.description"
                type="text"
                placeholder="Es. Cena al ristorante"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
              />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label for="expense-amount" class="block text-sm font-medium text-gray-700 mb-1"
                  >Importo</label
                >
                <input
                  id="expense-amount"
                  v-model="expenseForm.amount"
                  type="number"
                  :min="currencyStep(expenseForm.currency)"
                  :step="currencyStep(expenseForm.currency)"
                  :placeholder="currencyDecimals(expenseForm.currency) ? '0.00' : '0'"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                />
              </div>
              <div>
                <label for="expense-currency" class="block text-sm font-medium text-gray-700 mb-1"
                  >Valuta</label
                >
                <select
                  id="expense-currency"
                  v-model="expenseForm.currency"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                >
                  <option
                    v-for="currency in CURRENCIES"
                    :key="currency.code"
                    :value="currency.code"
                  >
                    {{ currency.code }} · {{ currency.name }}
                  </option>
                </select>
              </div>
            </div>
            <div>
              <label for="expense-date" class="block text-sm font-medium text-gray-700 mb-1"
                >Data della spesa</label
              >
              <input
                id="expense-date"
                v-model="expenseForm.expense_date"
                type="date"
                :max="todayDate()"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
              />
            </div>
            <details
              v-if="expenseForm.currency !== group.currency"
              class="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm"
            >
              <summary class="cursor-pointer font-medium text-gray-700">
                Dettagli cambio · {{ exchangeRateCaption }}
              </summary>
              <p class="mt-2 text-xs text-gray-600">
                Il cambio viene salvato con questa spesa e usato solo per unificare i conti in
                {{ group.currency }}.
              </p>
              <p v-if="ratePreview && !manualRateOverride" class="mt-2 text-xs text-gray-600">
                {{
                  ratePreview.source === 'manual'
                    ? 'Cambio manuale salvato'
                    : 'Cambio di riferimento'
                }}
                del {{ formatExpenseDate(ratePreview.date) }}.
                <span v-if="ratePreview.source === 'frankfurter'"
                  >Fonte: Frankfurter. Può differire dall'addebito della banca.</span
                >
              </p>
              <div v-if="manualRateOverride" class="mt-3">
                <label for="expense-exchange-rate" class="block text-xs font-medium text-gray-700"
                  >1 {{ expenseForm.currency }} in {{ group.currency }}</label
                >
                <input
                  id="expense-exchange-rate"
                  v-model="manualRate"
                  type="number"
                  min="0.000000000001"
                  max="1000000000"
                  step="0.000000000001"
                  inputmode="decimal"
                  class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                />
                <p class="mt-1 text-xs text-gray-500">
                  Inserisci il cambio concordato o quello applicato dalla banca.
                </p>
              </div>
              <div class="mt-3 flex flex-wrap gap-3">
                <button
                  v-if="!manualRateOverride"
                  type="button"
                  class="text-xs font-semibold text-green-700 underline"
                  @click="enableManualRate"
                >
                  Modifica cambio
                </button>
                <button
                  type="button"
                  :disabled="rateLoading"
                  class="text-xs font-semibold text-green-700 underline disabled:text-gray-400"
                  @click="refreshAutomaticRate"
                >
                  {{ manualRateOverride ? 'Usa cambio automatico' : 'Aggiorna cambio automatico' }}
                </button>
              </div>
            </details>
            <p
              v-if="expenseConvertedPreview !== null"
              class="text-xs font-medium text-green-700"
              aria-live="polite"
            >
              Controvalore: circa
              {{ formatCurrency(expenseConvertedPreview, group.currency) }}
            </p>
            <p
              v-if="rateError && !manualRateOverride && expenseForm.currency !== group.currency"
              role="status"
              class="text-xs text-amber-800"
            >
              {{ rateError }} Puoi salvare la spesa e completare il cambio più tardi: i bilanci
              separati restano disponibili.
            </p>
            <div>
              <label for="expense-payer" class="block text-sm font-medium text-gray-700 mb-1"
                >Pagato da</label
              >
              <select
                id="expense-payer"
                v-model="expenseForm.paid_by_member_id"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
              >
                <option disabled value="">Seleziona...</option>
                <option v-for="member in group.members" :key="member.id" :value="member.id">
                  {{ member.name }}
                </option>
              </select>
            </div>

            <!-- Tipo di divisione -->
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
                      : 'bg-white text-gray-600 border-gray-300 hover:border-green-400',
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
              <p
                v-if="expenseForm.subsetIds.length > 0 && Number(expenseForm.amount) > 0"
                class="text-xs text-green-600"
              >
                Circa
                {{
                  formatCurrency(
                    Number(expenseForm.amount) / expenseForm.subsetIds.length,
                    expenseForm.currency,
                  )
                }}
                a testa; gli eventuali resti sono distribuiti automaticamente.
              </p>
            </div>

            <!-- Split personalizzato (sempre visibile in modifica) -->
            <div v-if="expenseForm.splitType === 'custom'" class="space-y-2">
              <div v-for="member in group.members" :key="member.id" class="flex items-center gap-2">
                <span class="flex-1 text-sm text-gray-700">{{ member.name }}</span>
                <input
                  v-model="expenseForm.customSplits[member.id]"
                  type="number"
                  min="0"
                  :step="currencyStep(expenseForm.currency)"
                  :placeholder="currencyDecimals(expenseForm.currency) ? '0.00' : '0'"
                  :aria-label="`Quota di ${member.name} in ${expenseForm.currency}`"
                  class="w-24 border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                />
              </div>
              <p :class="splitSumOk ? 'text-green-600' : 'text-red-500'" class="text-xs text-right">
                Totale quote: {{ formatCurrency(splitSum, expenseForm.currency) }} /
                {{ formatCurrency(expenseForm.amount || 0, expenseForm.currency) }}
              </p>
            </div>

            <p v-if="expenseError" class="text-red-500 text-sm">
              {{ expenseError }}
            </p>

            <div class="flex gap-2">
              <button
                @click="cancelExpenseForm"
                class="flex-1 border border-gray-300 text-gray-600 font-semibold rounded-lg py-2.5 transition hover:bg-gray-50"
              >
                Annulla
              </button>
              <button
                @click="saveExpense"
                :disabled="expenseLoading"
                class="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white font-semibold rounded-lg py-2.5 transition"
              >
                {{ expenseLoading ? 'Salvataggio...' : editingExpenseId ? 'Aggiorna' : 'Salva' }}
              </button>
            </div>
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
            :class="[
              'bg-white rounded-2xl shadow px-5 py-4 flex items-center justify-between transition',
              group.status === 'active' ? 'cursor-pointer hover:shadow-md' : '',
            ]"
            @click="openEditExpenseForm(expense)"
          >
            <div>
              <p class="font-medium text-gray-800">{{ expense.description }}</p>
              <p class="text-sm text-gray-500">
                Pagato da
                <span class="font-medium">{{ memberName(expense.paid_by_member_id) }}</span>
              </p>
              <p class="mt-1 text-xs text-gray-400">
                {{ formatExpenseDate(expense.expense_date || expense.created_at.slice(0, 10)) }}
              </p>
              <p
                v-if="(expense.currency || group.currency) !== group.currency"
                class="mt-1 text-xs text-gray-500"
              >
                {{
                  expense.converted_amount !== null && expense.converted_amount !== undefined
                    ? `${formatCurrency(expense.converted_amount, group.currency)} con cambio salvato`
                    : 'Cambio da completare per unificare i conti'
                }}
              </p>
            </div>
            <div class="flex items-center gap-3">
              <span class="font-bold text-green-700"
                >{{ formatCurrency(expense.amount, expense.currency || group.currency) }}
                <span v-if="hasForeignExpenses" class="text-xs">{{
                  expense.currency || group.currency
                }}</span></span
              >
              <button
                v-if="group.status === 'active'"
                @click.stop="deleteExpense(expense.id)"
                :aria-disabled="deletionPending"
                :aria-label="`Elimina spesa ${expense.description}`"
                class="text-gray-300 hover:text-red-400 transition text-lg"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: Bilanci -->
      <div v-if="activeTab === 'balances'">
        <section
          v-if="hasForeignExpenses"
          class="mb-4 rounded-xl border border-gray-200 bg-white p-4"
        >
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 class="font-semibold text-gray-800">
                {{
                  balanceMode === 'unified'
                    ? `Conti unificati in ${group.currency}`
                    : 'Conti per valuta'
                }}
              </h2>
              <p class="mt-1 text-xs text-gray-500">
                {{
                  balanceMode === 'unified'
                    ? 'Usiamo i cambi salvati sulle singole spese, senza aggiornarli.'
                    : 'Ogni pagamento resta nella valuta originale.'
                }}
              </p>
            </div>
            <button
              v-if="group.status === 'active' && hasForeignExpenses"
              type="button"
              class="rounded-lg border border-green-300 px-3 py-2 text-sm font-semibold text-green-700 hover:bg-green-50"
              @click="balanceMode = balanceMode === 'separate' ? 'unified' : 'separate'"
            >
              {{
                balanceMode === 'separate' ? `Unifica in ${group.currency}` : 'Mostra per valuta'
              }}
            </button>
          </div>
          <p v-if="group.status !== 'active'" class="mt-2 text-xs text-gray-500">
            Modalità e pagamenti fissati all'inizio della chiusura. Per cambiarli, riapri i conti.
          </p>
          <p
            v-if="balanceMode === 'unified' && !balancesLoading && !balancesError"
            class="mt-3 text-sm font-medium text-green-700"
          >
            Totale convertito: {{ formatCurrency(unifiedTotal, group.currency) }}
          </p>
        </section>
        <section
          v-if="balancesError && !balancesLoading"
          role="alert"
          class="mb-4 rounded-xl border border-amber-200 bg-amber-50 p-4"
        >
          <p class="font-semibold text-amber-900">{{ balancesError }}</p>
          <p
            v-if="balanceMode === 'unified' && missingRateExpenses.length"
            class="mt-1 text-sm text-amber-800"
          >
            Completa il cambio di queste spese per ottenere un bilancio completo:
          </p>
          <ul v-if="balanceMode === 'unified' && missingRateExpenses.length" class="mt-2 space-y-2">
            <li
              v-for="expense in missingRateExpenses"
              :key="expense.id"
              class="flex flex-wrap items-center justify-between gap-2 text-sm text-amber-900"
            >
              <span>{{ expense.description }} · {{ expense.currency }}</span>
              <button
                v-if="group.status === 'active'"
                type="button"
                class="font-semibold underline"
                @click="completeExpenseRate(expense)"
              >
                Completa cambio
              </button>
            </li>
          </ul>
          <button
            type="button"
            class="mt-3 text-sm font-semibold text-amber-900 underline"
            @click="loadBalances"
          >
            Riprova
          </button>
          <button
            v-if="group.status === 'active' && balanceMode === 'unified'"
            type="button"
            class="mt-3 ml-4 text-sm font-semibold text-amber-900 underline"
            @click="balanceMode = 'separate'"
          >
            Torna ai conti per valuta
          </button>
        </section>
        <div
          v-if="group.status === 'closing'"
          class="mb-4 rounded-xl border border-amber-100 bg-amber-50 p-4"
        >
          <div
            v-if="currentMemberId && !showMemberPicker"
            class="flex items-center justify-between gap-3"
          >
            <p class="text-sm text-amber-900">
              Stai agendo come <strong>{{ currentMemberName }}</strong
              >.
            </p>
            <button
              type="button"
              class="shrink-0 text-sm font-semibold text-amber-800 underline"
              @click="showMemberPicker = true"
            >
              Cambia
            </button>
          </div>
          <template v-else>
            <label class="block text-sm font-medium text-amber-900" for="current-member"
              >Quale partecipante sei?</label
            >
            <select
              id="current-member"
              v-model="currentMemberId"
              class="mt-2 w-full rounded-lg border border-amber-200 bg-white px-3 py-2 text-sm text-gray-700"
              @change="saveCurrentMember"
            >
              <option :value="null">Seleziona il tuo nome per aggiornare un pagamento</option>
              <option v-for="member in group.members" :key="member.id" :value="member.id">
                {{ member.name }}
              </option>
            </select>
          </template>
          <p class="mt-2 text-xs text-amber-800">
            La scelta resta solo su questo dispositivo e non è un'autenticazione.
          </p>
        </div>
        <section
          v-if="!balancesLoading && !balancesError && group.status !== 'closed' && currentMemberId"
          class="mb-4 border-y border-gray-200 bg-white px-4 py-4"
        >
          <div class="flex flex-wrap items-baseline justify-between gap-2">
            <h2 class="font-semibold text-gray-800">Il tuo riepilogo</h2>
            <p class="text-xs text-gray-500">Come {{ currentMemberName }}</p>
          </div>
          <div
            v-for="personalBalance in personalBalances"
            :key="personalBalance.currency"
            class="mt-3 border-t border-gray-100 pt-3"
          >
            <p v-if="hasForeignExpenses" class="mb-2 text-xs font-semibold text-gray-600">
              {{ personalBalance.currency }}
            </p>
            <div class="grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-3">
              <div>
                <p class="text-xs text-gray-500">Devi pagare</p>
                <p class="mt-1 font-semibold text-red-600">
                  {{ formatCurrency(personalBalance.amountToPay, personalBalance.currency) }}
                </p>
                <p class="mt-0.5 text-xs text-gray-400">
                  {{ paymentCountLabel(personalBalance.outgoingPayments) }}
                </p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Devi ricevere</p>
                <p class="mt-1 font-semibold text-green-700">
                  {{ formatCurrency(personalBalance.amountToReceive, personalBalance.currency) }}
                </p>
                <p class="mt-0.5 text-xs text-gray-400">
                  {{ paymentCountLabel(personalBalance.incomingPayments) }}
                </p>
              </div>
              <div
                class="col-span-2 border-t border-gray-100 pt-3 sm:col-span-1 sm:border-t-0 sm:pt-0"
              >
                <p class="text-xs text-gray-500">Saldo netto</p>
                <p
                  :class="[
                    'mt-1 font-semibold',
                    personalBalance.netAmount > 0
                      ? 'text-green-700'
                      : personalBalance.netAmount < 0
                        ? 'text-red-600'
                        : 'text-gray-700',
                  ]"
                >
                  {{ formatSignedAmount(personalBalance.netAmount, personalBalance.currency) }}
                </p>
              </div>
            </div>
          </div>
        </section>
        <div
          v-else-if="!balancesLoading && !balancesError && group.status === 'active'"
          class="mb-4 flex items-center justify-between gap-3 border-y border-gray-200 bg-white px-4 py-3"
        >
          <p class="text-sm text-gray-600">Scegli chi sei per vedere il tuo riepilogo.</p>
          <button
            type="button"
            class="shrink-0 text-sm font-semibold text-green-700 underline underline-offset-2"
            @click="activeTab = 'members'"
          >
            Vai a Partecipanti
          </button>
        </div>
        <section
          v-if="
            !balancesLoading &&
            !balancesError &&
            group.status === 'active' &&
            group.expenses.length > 0
          "
          class="mb-4 rounded-xl border border-blue-100 bg-blue-50 p-4"
        >
          <div class="flex flex-wrap items-center gap-2">
            <p class="font-semibold text-blue-900">Avete finito con le spese?</p>
            <span
              class="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-700"
            >
              Beta
            </span>
          </div>
          <p class="mt-1 text-sm text-blue-800">
            Blocca il gruppo per verificare e chiudere i pagamenti.
          </p>
          <button
            type="button"
            class="mt-3 rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
            @click="startClosing"
          >
            Chiudiamo i conti
          </button>
        </section>
        <div v-if="balancesLoading" class="text-center py-10 text-gray-400">Calcolo...</div>
        <div v-else-if="balancesError"></div>
        <div v-else-if="group.status !== 'active'" class="space-y-3">
          <p v-if="settlementError" class="text-sm text-red-600">{{ settlementError }}</p>
          <p
            v-else-if="group.status === 'closed' && settlements.length > 0"
            class="text-center py-4 text-green-700"
          >
            Tutti i pagamenti sono stati confermati. Conti chiusi 🎉
          </p>
          <p v-if="settlements.length === 0" class="text-center py-6 text-gray-400">
            Nessun pagamento necessario: siete già tutti pari.
          </p>
          <div
            v-for="settlement in settlements"
            :key="settlement.id"
            class="rounded-2xl bg-white px-5 py-4 shadow"
          >
            <div class="flex items-center justify-between gap-3">
              <div class="min-w-0 text-gray-700">
                <span class="font-medium">{{ displayMemberName(settlement.from_member_id) }}</span>
                <span class="mx-2 text-gray-400">→</span>
                <span class="font-medium">{{ displayMemberName(settlement.to_member_id) }}</span>
              </div>
              <span class="shrink-0 font-bold text-red-500"
                >{{ formatCurrency(settlement.amount, settlement.currency || group.currency) }}
                <span v-if="hasForeignExpenses" class="text-xs">{{
                  settlement.currency || group.currency
                }}</span></span
              >
            </div>
            <p class="mt-2 text-sm text-gray-500">{{ settlementLabel(settlement) }}</p>
            <button
              v-if="currentMemberId === settlement.from_member_id && !settlement.reported_at"
              class="mt-3 rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white disabled:bg-gray-300"
              :disabled="settlementLoading"
              @click="reportSettlement(settlement.id)"
            >
              Ho pagato
            </button>
            <button
              v-else-if="
                currentMemberId === settlement.to_member_id &&
                settlement.reported_at &&
                settlement.status === 'pending'
              "
              class="mt-3 rounded-lg bg-green-600 px-3 py-2 text-sm font-semibold text-white disabled:bg-gray-300"
              :disabled="settlementLoading"
              @click="confirmSettlement(settlement.id)"
            >
              Conferma ricezione
            </button>
          </div>
        </div>
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
              <span class="font-medium">{{ displayMemberName(balance.from_member_id) }}</span>
              <span class="text-gray-400">→</span>
              <span class="font-medium">{{ displayMemberName(balance.to_member_id) }}</span>
            </div>
            <span class="shrink-0 font-bold text-red-500"
              >{{ formatCurrency(balance.amount, balance.currency || group.currency) }}
              <span v-if="hasForeignExpenses" class="text-xs">{{
                balance.currency || group.currency
              }}</span></span
            >
          </div>
        </div>
      </div>

      <!-- Tab: Partecipanti -->
      <div v-if="activeTab === 'members'">
        <div
          v-if="group.status === 'active'"
          class="mb-4 rounded-xl border border-green-100 bg-green-50 p-4"
        >
          <div
            v-if="currentMemberId && !showMemberPicker"
            class="flex items-center justify-between gap-3"
          >
            <p class="text-sm text-green-900">
              In questo gruppo sei <strong>{{ currentMemberName }}</strong
              >.
            </p>
            <button
              type="button"
              class="shrink-0 text-sm font-semibold text-green-800 underline"
              @click="showMemberPicker = true"
            >
              Cambia
            </button>
          </div>
          <template v-else>
            <label class="block text-sm font-medium text-green-900" for="active-current-member">
              Tu chi sei nel gruppo?
            </label>
            <select
              id="active-current-member"
              v-model="currentMemberId"
              class="mt-2 w-full rounded-lg border border-green-200 bg-white px-3 py-2 text-sm text-gray-700"
              @change="saveCurrentMember"
            >
              <option :value="null">Seleziona il tuo nome</option>
              <option v-for="member in group.members" :key="member.id" :value="member.id">
                {{ member.name }}
              </option>
            </select>
          </template>
          <p class="mt-2 text-xs text-green-800">
            La scelta resta solo su questo dispositivo e non è un'autenticazione.
          </p>
        </div>

        <p
          v-if="group.status !== 'active'"
          class="mb-4 rounded-xl bg-amber-50 px-4 py-3 text-sm text-amber-800"
        >
          {{
            group.status === 'closed'
              ? 'Il gruppo è chiuso: i partecipanti sono in sola lettura.'
              : 'I partecipanti non possono essere modificati durante la chiusura dei conti.'
          }}
        </p>
        <!-- Bottone toggle, stesso pattern della tab Spese -->
        <button
          v-if="group.status === 'active'"
          @click="toggleAddMemberForm"
          class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg py-2.5 mb-4 transition"
        >
          {{ showAddMemberForm ? '✕ Annulla' : '+ Aggiungi partecipante' }}
        </button>

        <div
          v-if="showAddMemberForm && group.status === 'active'"
          class="bg-white rounded-2xl shadow p-4 mb-4 flex flex-col sm:flex-row gap-2"
        >
          <input
            v-model="newMember.name"
            placeholder="Nome"
            class="min-w-0 flex-1 border rounded-lg px-3 py-2 text-sm"
          />
          <input
            v-if="emailManagementEnabled"
            v-model="newMember.email"
            placeholder="Email (opzionale)"
            class="min-w-0 flex-1 border rounded-lg px-3 py-2 text-sm"
          />
          <button
            @click="addMember"
            class="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm shrink-0 w-full sm:w-auto"
          >
            Aggiungi
          </button>
        </div>
        <p v-if="addMemberError" class="text-xs text-red-400 mb-2">{{ addMemberError }}</p>

        <div class="bg-white rounded-2xl shadow divide-y divide-gray-100">
          <div
            v-for="member in group.members"
            :key="member.id"
            class="px-5 py-3 flex items-center justify-between gap-3"
          >
            <div class="min-w-0 flex-1">
              <span class="font-medium text-gray-800">{{ member.name }}</span>

              <span
                v-if="
                  emailManagementEnabled &&
                  editingEmailId !== member.id &&
                  (member.email || group.status === 'active')
                "
                @click="group.status === 'active' && startEditEmail(member)"
                :class="[
                  'ml-2 text-sm text-gray-400 transition',
                  group.status === 'active' ? 'cursor-pointer hover:text-green-600' : '',
                ]"
              >
                {{ member.email || '+ aggiungi email' }}
              </span>

              <div
                v-else-if="
                  emailManagementEnabled &&
                  editingEmailId === member.id &&
                  group.status === 'active'
                "
                class="flex items-center gap-2 mt-1"
              >
                <input
                  v-model="editingEmailValue"
                  type="email"
                  placeholder="email@esempio.com"
                  class="min-w-0 flex-1 border rounded-lg px-2 py-1 text-sm"
                  @keyup.enter="saveEmail(member.id)"
                  @keyup.esc="cancelEditEmail"
                />
                <button
                  @click="saveEmail(member.id)"
                  class="text-green-600 hover:text-green-700 text-sm font-medium px-1"
                >
                  Salva
                </button>
                <button
                  @click="cancelEditEmail"
                  class="text-gray-400 hover:text-gray-600 text-sm px-1"
                >
                  Annulla
                </button>
              </div>
            </div>

            <!-- il bottone elimina sparisce mentre stai editando l'email di QUESTO membro -->
            <button
              v-if="editingEmailId !== member.id && group.status === 'active'"
              @click="deleteMember(member.id, member.name)"
              :aria-disabled="deletionPending"
              :aria-label="`Rimuovi partecipante ${member.name}`"
              class="text-gray-300 hover:text-red-400 transition text-lg shrink-0"
            >
              ✕
            </button>
          </div>
        </div>
        <p class="text-xs text-gray-400 mt-3 text-center">
          Un partecipante può essere rimosso solo se non è coinvolto in nessuna spesa.
        </p>
      </div>

      <!-- Footer donazione -->
      <div class="mt-10">
        <DonationFooter />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  groupsApi,
  type Group,
  type Balance,
  type BalanceMode,
  type Expense,
  type ExpenseInput,
  type ExchangeRate,
  type Settlement,
  type Split,
} from '../api/groups'
import DonationFooter from '../components/DonationFooter.vue'
import FeedbackDialog from '../components/FeedbackDialog.vue'
import { useFeedbackDialog } from '../composables/useFeedbackDialog'
import { buildClosingSummary } from '../utils/closingSummary'
import {
  calculatePersonalBalancesByCurrency,
  calculatePersonalSettlementsByCurrency,
} from '../utils/personalBalanceSummary'
import {
  CURRENCIES,
  currencyDecimals,
  currencyStep,
  formatCurrency,
  todayDate,
  expenseTotalsByCurrency,
} from '../utils/currency'
import { isRecentGroup, saveRecentGroup } from '../utils/recentGroups'
import equaLogo from '../assets/equa-logo.svg'
import { trackEvent } from '../utils/analytics'

const route = useRoute()
const router = useRouter()
const { dialog, respond, askConfirmation, showAlert } = useFeedbackDialog()
const deletionPending = ref(false)
const groupId = route.params.id as string
const emailManagementEnabled = false

const group = ref<Group | null>(null)
const balances = ref<Balance[]>([])
const loading = ref(true)
const error = ref('')
const copied = ref(false)
const showShareDialog = ref(route.query.created === '1')
const savedLocally = ref(route.query.created === '1' || isRecentGroup(groupId))
const activeTab = ref('expenses')
const balancesLoading = ref(false)
const balancesError = ref('')
const balanceMode = ref<BalanceMode>('separate')
let balancesRequest = 0
const settlements = ref<Settlement[]>([])
const settlementLoading = ref(false)
const settlementError = ref('')
const currentMemberId = ref<number | null>(getCurrentMember())
const showMemberPicker = ref(!currentMemberId.value)
const showCelebration = ref(false)
const showClosingSummary = ref(false)
const statusLoading = ref(false)
const statusError = ref('')

const newMember = reactive({ name: '', email: '' })
const addMemberError = ref('')

const tabs = [
  { key: 'expenses', label: '💸 Spese' },
  { key: 'balances', label: '⚖️ Bilanci' },
  { key: 'members', label: '👥 Partecipanti' },
]

const showExpenseForm = ref(false)
const editingExpenseId = ref<number | null>(null)
const expenseLoading = ref(false)
const expenseError = ref('')
const expenseForm = reactive({
  description: '',
  amount: '',
  currency: 'EUR',
  expense_date: todayDate(),
  paid_by_member_id: '' as number | string,
  splitType: 'equal',
  customSplits: {} as Record<number, string>,
  subsetIds: [] as number[],
})
const originalExpense = ref<Expense | null>(null)
const ratePreview = ref<ExchangeRate | null>(null)
const rateLoading = ref(false)
const rateError = ref('')
const manualRateOverride = ref(false)
const manualRate = ref('')
const refreshRateRequested = ref(false)
const rateContextVersion = ref(0)
let rateRequest = 0

const showAddMemberForm = ref(false)
const editingEmailId = ref<number | null>(null)
const editingEmailValue = ref('')

const splitTypes = [
  { key: 'equal', label: 'Tutti' },
  { key: 'subset', label: 'Seleziona persone' },
  { key: 'custom', label: 'Personalizzato' },
]

const totalExpenses = computed(() =>
  expenseTotalsByCurrency(group.value?.expenses || [], group.value?.currency || 'EUR'),
)
const hasForeignExpenses = computed(
  () =>
    group.value?.expenses.some(
      (expense) => (expense.currency || group.value?.currency) !== group.value?.currency,
    ) || false,
)
const missingRateExpenses = computed(
  () =>
    group.value?.expenses.filter(
      (expense) =>
        (expense.currency || group.value?.currency) !== group.value?.currency &&
        !expense.exchange_rate,
    ) || [],
)
const unifiedTotal = computed(
  () =>
    group.value?.expenses.reduce(
      (sum, expense) =>
        sum +
        Number(
          expense.converted_amount ??
            ((expense.currency || group.value?.currency) === group.value?.currency
              ? expense.amount
              : 0),
        ),
      0,
    ) || 0,
)
const exchangeRateCaption = computed(() => {
  if (manualRateOverride.value)
    return `1 ${expenseForm.currency} = ${manualRate.value || '…'} ${group.value?.currency}`
  if (rateLoading.value) return 'Recupero in corso…'
  if (!ratePreview.value) return 'Da completare'
  return `1 ${expenseForm.currency} = ${ratePreview.value.rate} ${group.value?.currency}`
})
const expenseConvertedPreview = computed(() => {
  if (!group.value || expenseForm.currency === group.value.currency) return null
  const amount = Number(expenseForm.amount)
  const rate = Number(manualRateOverride.value ? manualRate.value : ratePreview.value?.rate)
  if (!validCurrencyAmount(amount) || !Number.isFinite(rate) || rate <= 0) return null
  return amount * rate
})

const groupStatusLabel = computed(() => {
  if (group.value?.status === 'closing') return 'Chiusura conti'
  if (group.value?.status === 'closed') return 'Conti chiusi'
  return 'In corso'
})

const groupStatusTitle = computed(() => {
  if (group.value?.status === 'closing') return 'I conti sono bloccati'
  if (group.value?.status === 'closed') return 'Questo gruppo è chiuso'
  return 'Quando la vacanza è finita, chiudete i conti'
})

const groupStatusDescription = computed(() => {
  if (group.value?.status === 'closing') {
    return 'Spese e partecipanti non possono essere modificati finché state verificando i saldi.'
  }
  if (group.value?.status === 'closed') {
    return 'Il riepilogo resta disponibile in sola lettura. Puoi riaprire i conti se serve una correzione.'
  }
  return 'Blocca spese e partecipanti per verificare i saldi senza modifiche involontarie.'
})

const currentMemberName = computed(() =>
  currentMemberId.value ? memberName(currentMemberId.value) : '',
)

const personalBalances = computed(() =>
  group.value?.status === 'closing'
    ? calculatePersonalSettlementsByCurrency(
        settlements.value,
        currentMemberId.value || 0,
        group.value.currency,
      )
    : calculatePersonalBalancesByCurrency(
        balances.value,
        currentMemberId.value || 0,
        group.value?.currency || 'EUR',
      ),
)

const groupLink = computed(() => new URL(`/group/${groupId}`, window.location.origin).toString())

const shareMessage = computed(() => {
  if (!group.value) return groupLink.value
  return `Ho creato il gruppo "${group.value.name}" su Equa. Aprilo qui per aggiungere o controllare le spese: ${groupLink.value}`
})

const whatsAppShareUrl = computed(
  () => `https://wa.me/?text=${encodeURIComponent(shareMessage.value)}`,
)

const closingSummaryMessage = computed(() => {
  if (!group.value) return ''
  const summaryBalances =
    group.value.status === 'active'
      ? balances.value
      : settlements.value
          .filter((settlement) => settlement.status !== 'cancelled')
          .map((settlement) => ({
            from_member_id: settlement.from_member_id,
            from_member_name: memberName(settlement.from_member_id),
            to_member_id: settlement.to_member_id,
            to_member_name: memberName(settlement.to_member_id),
            amount: settlement.amount,
            currency: settlement.currency || group.value!.currency,
          }))
  return buildClosingSummary(group.value, summaryBalances, groupLink.value)
})

const closingSummaryWhatsAppUrl = computed(
  () => `https://wa.me/?text=${encodeURIComponent(closingSummaryMessage.value)}`,
)

const splitSum = computed(() => {
  return Object.values(expenseForm.customSplits).reduce((acc, v) => acc + (parseFloat(v) || 0), 0)
})

const splitSumOk = computed(() => {
  const factor = 10 ** currencyDecimals(expenseForm.currency)
  return (
    validCurrencyAmount(Number(expenseForm.amount)) &&
    Object.values(expenseForm.customSplits).every((value) =>
      validCurrencyAmount(Number(value), true),
    ) &&
    Math.round(splitSum.value * factor) === Math.round(Number(expenseForm.amount) * factor)
  )
})

async function loadGroup() {
  try {
    const res = await groupsApi.get(groupId)
    group.value = res.data
    if (res.data.status !== 'active')
      balanceMode.value = res.data.closing_balance_mode || 'separate'
    if (
      currentMemberId.value &&
      !res.data.members.some((member) => member.id === currentMemberId.value)
    ) {
      currentMemberId.value = null
      saveCurrentMember()
    }
    if (route.query.created === '1' || savedLocally.value) {
      saveRecentGroup(res.data)
      savedLocally.value = true
    }
  } catch {
    error.value = 'Gruppo non trovato.'
  } finally {
    loading.value = false
  }
}

async function loadBalances() {
  const request = ++balancesRequest
  balancesLoading.value = true
  balancesError.value = ''
  balances.value = []
  settlements.value = []
  try {
    if (group.value?.status !== 'active') {
      const settlementsResponse = await groupsApi.getSettlements(groupId)
      if (request === balancesRequest)
        settlements.value = settlementsResponse.data.filter(
          (settlement) => settlement.status !== 'cancelled',
        )
    } else {
      const res = await groupsApi.getBalances(groupId, balanceMode.value)
      if (request === balancesRequest) balances.value = res.data
    }
  } catch (cause: unknown) {
    if (request !== balancesRequest) return
    balancesError.value =
      balanceMode.value === 'unified' && missingRateExpenses.value.length
        ? 'Mancano alcuni cambi: il bilancio unificato non è ancora disponibile.'
        : apiErrorMessage(cause, 'Non è stato possibile caricare i bilanci. Riprova.')
  } finally {
    if (request === balancesRequest) balancesLoading.value = false
  }
}

watch(activeTab, (tab) => {
  if (tab === 'balances') loadBalances()
})

watch(balanceMode, () => {
  if (activeTab.value === 'balances') loadBalances()
})

function memberName(id: number) {
  return group.value?.members.find((m) => m.id === id)?.name || 'Sconosciuto'
}

function displayMemberName(id: number) {
  return currentMemberId.value === id ? 'Tu' : memberName(id)
}

function formatSignedAmount(amount: number, currency: string) {
  if (amount === 0) return formatCurrency(amount, currency)
  return `${amount > 0 ? '+' : '-'}${formatCurrency(Math.abs(amount), currency)}`
}

function formatExpenseDate(date: string) {
  return new Intl.DateTimeFormat('it-IT', { dateStyle: 'medium' }).format(
    new Date(`${date}T12:00:00`),
  )
}

function apiErrorMessage(cause: unknown, fallback: string) {
  const detail = (cause as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  return typeof detail === 'string' ? detail : fallback
}

function paymentCountLabel(count: number) {
  return count === 1 ? '1 pagamento' : `${count} pagamenti`
}

function toggleAddMemberForm() {
  showAddMemberForm.value = !showAddMemberForm.value
  if (!showAddMemberForm.value) {
    newMember.name = ''
    newMember.email = ''
    addMemberError.value = ''
  }
}

function startEditEmail(member: { id: number; email?: string | null }) {
  editingEmailId.value = member.id
  editingEmailValue.value = member.email || ''
}

function cancelEditEmail() {
  editingEmailId.value = null
  editingEmailValue.value = ''
}

async function saveEmail(memberId: number) {
  try {
    await groupsApi.updateMember(groupId, memberId, { email: editingEmailValue.value.trim() })
    editingEmailId.value = null
    await loadGroup()
  } catch (e: any) {
    await showAlert({
      title: 'Email non aggiornata',
      message:
        typeof e?.response?.data?.detail === 'string'
          ? e.response.data.detail
          : "Errore durante l'aggiornamento dell'email. Riprova.",
    })
  }
}

function resetExpenseForm() {
  ++rateRequest
  ++rateContextVersion.value
  expenseForm.description = ''
  expenseForm.amount = ''
  expenseForm.currency = group.value?.currency || 'EUR'
  expenseForm.expense_date = todayDate()
  expenseForm.paid_by_member_id = ''
  expenseForm.splitType = 'equal'
  expenseForm.customSplits = {}
  expenseForm.subsetIds = []
  expenseError.value = ''
  editingExpenseId.value = null
  originalExpense.value = null
  ratePreview.value = null
  rateLoading.value = false
  rateError.value = ''
  manualRateOverride.value = false
  manualRate.value = ''
  refreshRateRequested.value = false
}

async function loadExchangeRate() {
  const request = ++rateRequest
  ratePreview.value = null
  rateError.value = ''
  rateLoading.value = false
  if (
    !showExpenseForm.value ||
    !group.value ||
    expenseForm.currency === group.value.currency ||
    !expenseForm.expense_date
  )
    return
  const expense = originalExpense.value
  const sameRateContext =
    expense &&
    (expense.currency || group.value.currency) === expenseForm.currency &&
    (expense.expense_date || expense.created_at.slice(0, 10)) === expenseForm.expense_date
  if (sameRateContext && expense.exchange_rate && !refreshRateRequested.value) {
    ratePreview.value = {
      currency: expenseForm.currency,
      target_currency: group.value.currency,
      rate: expense.exchange_rate,
      date: expense.exchange_rate_date || expenseForm.expense_date,
      source: expense.exchange_rate_source || 'manual',
    }
    return
  }
  // Completing a saved expense with no rate is an explicit refresh on update.
  if (sameRateContext && !expense.exchange_rate) refreshRateRequested.value = true
  rateLoading.value = true
  try {
    const response = await groupsApi.getExchangeRate(
      groupId,
      expenseForm.currency,
      expenseForm.expense_date,
    )
    if (request === rateRequest) ratePreview.value = response.data
  } catch {
    if (request === rateRequest) rateError.value = 'Cambio automatico non disponibile.'
  } finally {
    if (request === rateRequest) rateLoading.value = false
  }
}

watch(
  [() => expenseForm.currency, () => expenseForm.expense_date, showExpenseForm, rateContextVersion],
  () => {
    manualRateOverride.value = false
    manualRate.value = ''
    refreshRateRequested.value = false
    void loadExchangeRate()
  },
)

function enableManualRate() {
  manualRate.value = ratePreview.value?.rate || ''
  manualRateOverride.value = true
}

function refreshAutomaticRate() {
  manualRateOverride.value = false
  manualRate.value = ''
  refreshRateRequested.value = true
  void loadExchangeRate()
}

function openNewExpenseForm() {
  if (group.value?.status !== 'active') return
  if (showExpenseForm.value && !editingExpenseId.value) {
    showExpenseForm.value = false
    resetExpenseForm()
    return
  }
  resetExpenseForm()
  showExpenseForm.value = true
}

function openEditExpenseForm(expense: Expense) {
  if (group.value?.status !== 'active') return
  resetExpenseForm()
  editingExpenseId.value = expense.id
  originalExpense.value = expense
  expenseForm.description = expense.description
  expenseForm.amount = String(expense.amount)
  expenseForm.currency = expense.currency || group.value.currency
  expenseForm.expense_date = expense.expense_date || expense.created_at.slice(0, 10)
  expenseForm.paid_by_member_id = expense.paid_by_member_id
  expenseForm.splitType = 'custom'
  expense.splits.forEach((s) => {
    expenseForm.customSplits[s.member_id] = String(s.share_amount)
  })
  showExpenseForm.value = true
}

async function completeExpenseRate(expense: Expense) {
  activeTab.value = 'expenses'
  openEditExpenseForm(expense)
  await nextTick()
  document.getElementById('expense-form')?.scrollIntoView?.({ block: 'start', behavior: 'smooth' })
}

function cancelExpenseForm() {
  showExpenseForm.value = false
  resetExpenseForm()
}

function validCurrencyAmount(amount: number, allowZero = false) {
  const minorUnits = amount * 10 ** currencyDecimals(expenseForm.currency)
  return (
    Number.isFinite(amount) &&
    (allowZero ? amount >= 0 : amount > 0) &&
    Math.abs(minorUnits - Math.round(minorUnits)) < 0.000001
  )
}

function expenseSplits(): Split[] {
  if (expenseForm.splitType === 'custom') {
    return Object.entries(expenseForm.customSplits)
      .filter(([, value]) => Number(value) > 0)
      .map(([id, value]) => ({ member_id: Number(id), share_amount: Number(value) }))
  }
  const ids =
    expenseForm.splitType === 'subset'
      ? expenseForm.subsetIds
      : group.value!.members.map((member) => member.id)
  const factor = 10 ** currencyDecimals(expenseForm.currency)
  const units = Math.round(Number(expenseForm.amount) * factor)
  const share = Math.floor(units / ids.length)
  const remainder = units % ids.length
  return ids.map((id, index) => ({
    member_id: id,
    share_amount: (share + (index < remainder ? 1 : 0)) / factor,
  }))
}

async function saveExpense() {
  if (expenseLoading.value) return
  expenseError.value = ''
  if (!expenseForm.description.trim()) {
    expenseError.value = 'Inserisci una descrizione'
    return
  }
  if (
    !validCurrencyAmount(Number(expenseForm.amount)) ||
    Number(expenseForm.amount) > 99_999_999.99
  ) {
    expenseError.value = `Inserisci un importo positivo con al massimo ${currencyDecimals(expenseForm.currency)} decimali per ${expenseForm.currency}.`
    return
  }
  if (
    !/^\d{4}-\d{2}-\d{2}$/.test(expenseForm.expense_date) ||
    expenseForm.expense_date > todayDate()
  ) {
    expenseError.value = 'Inserisci la data effettiva della spesa, non successiva a oggi.'
    return
  }
  if (
    manualRateOverride.value &&
    (!/^\d+(\.\d{1,12})?$/.test(String(manualRate.value)) ||
      !Number.isFinite(Number(manualRate.value)) ||
      Number(manualRate.value) < 0.000000000001 ||
      Number(manualRate.value) > 1_000_000_000)
  ) {
    expenseError.value = 'Inserisci un cambio positivo con al massimo 12 decimali.'
    return
  }
  if (!expenseForm.paid_by_member_id) {
    expenseError.value = 'Seleziona chi ha pagato'
    return
  }
  if (expenseForm.splitType === 'custom' && !splitSumOk.value) {
    expenseError.value =
      'Le quote devono essere valide per questa valuta e la loro somma deve corrispondere esattamente al totale.'
    return
  }
  if (expenseForm.splitType === 'subset' && !expenseForm.subsetIds.length) {
    expenseError.value = 'Seleziona almeno una persona'
    return
  }

  expenseLoading.value = true
  try {
    const data: ExpenseInput = {
      paid_by_member_id: Number(expenseForm.paid_by_member_id),
      description: expenseForm.description.trim(),
      amount: Number(expenseForm.amount),
      currency: expenseForm.currency,
      expense_date: expenseForm.expense_date,
      ...(manualRateOverride.value ? { exchange_rate: String(manualRate.value) } : {}),
      ...(refreshRateRequested.value && !manualRateOverride.value
        ? { refresh_exchange_rate: true }
        : {}),
    }
    if (editingExpenseId.value) {
      await groupsApi.updateExpense(groupId, editingExpenseId.value, {
        ...data,
        splits: expenseSplits(),
      })
    } else if (expenseForm.splitType === 'equal') {
      await groupsApi.addExpenseEqual(groupId, data)
    } else if (expenseForm.splitType === 'subset') {
      await groupsApi.addExpenseSubset(groupId, {
        ...data,
        member_ids: expenseForm.subsetIds,
      })
    } else {
      await groupsApi.addExpense(groupId, {
        ...data,
        splits: expenseSplits(),
      })
    }
    await loadGroup()
    if (!editingExpenseId.value) trackEvent('expense_created')
    showExpenseForm.value = false
    resetExpenseForm()
  } catch (cause: unknown) {
    expenseError.value = apiErrorMessage(
      cause,
      'Errore nel salvataggio. Controlla i dati e riprova.',
    )
  } finally {
    expenseLoading.value = false
  }
}

async function deleteExpense(expenseId: number) {
  if (group.value?.status !== 'active' || deletionPending.value) return
  const expense = group.value.expenses.find((item) => item.id === expenseId)
  if (!expense) return
  deletionPending.value = true
  try {
    if (
      !(await askConfirmation({
        title: 'Eliminare la spesa?',
        message: `La spesa “${expense.description}” verrà eliminata e i saldi saranno ricalcolati. Questa azione non può essere annullata.`,
        confirmLabel: 'Elimina spesa',
        destructive: true,
      }))
    )
      return
    await groupsApi.deleteExpense(groupId, expenseId)
    await loadGroup()
  } catch {
    await showAlert({
      title: 'Spesa non eliminata',
      message: 'Non è stato possibile eliminare la spesa. Riprova.',
    })
  } finally {
    deletionPending.value = false
  }
}

async function deleteMember(memberId: number, name: string) {
  if (group.value?.status !== 'active' || deletionPending.value) return
  deletionPending.value = true
  try {
    if (
      !(await askConfirmation({
        title: 'Rimuovere il partecipante?',
        message: `Vuoi rimuovere “${name}” dal gruppo? Questa azione non può essere annullata.`,
        confirmLabel: 'Rimuovi partecipante',
        destructive: true,
      }))
    )
      return
    await groupsApi.deleteMember(groupId, memberId)
    await loadGroup()
  } catch (e: any) {
    await showAlert({
      title: 'Partecipante non rimosso',
      message:
        typeof e?.response?.data?.detail === 'string'
          ? e.response.data.detail
          : 'Impossibile rimuovere il partecipante. Riprova.',
    })
  } finally {
    deletionPending.value = false
  }
}

async function addMember() {
  if (group.value?.status !== 'active') return
  addMemberError.value = ''
  if (!newMember.name.trim()) {
    addMemberError.value = 'Inserisci un nome'
    return
  }
  try {
    await groupsApi.addMember(groupId, {
      name: newMember.name.trim(),
      email: newMember.email.trim() || undefined,
    })
    newMember.name = ''
    newMember.email = ''
    showAddMemberForm.value = false
    await loadGroup()
  } catch (e: any) {
    addMemberError.value = e?.response?.data?.detail || "Errore durante l'aggiunta"
  }
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(groupLink.value)
    copied.value = true
    trackEvent('share_copied')
    setTimeout(() => (copied.value = false), 2000)
  } catch {
    // Il link resta visibile nel promemoria e può essere copiato manualmente.
  }
}

async function shareGroup() {
  if (!navigator.share) {
    await copyLink()
    return
  }

  try {
    await navigator.share({
      title: group.value?.name || 'Gruppo Equa',
      text: shareMessage.value,
      url: groupLink.value,
    })
  } catch {
    // La chiusura del foglio di condivisione non è un errore da mostrare all'utente.
  }
}

function openShareDialog() {
  trackEvent('share_opened')
  showShareDialog.value = true
}

function closeShareDialog() {
  showShareDialog.value = false
  if (route.query.created === '1') {
    router.replace({ query: { ...route.query, created: undefined } })
  }
}

function saveGroupLocally() {
  if (!group.value) return
  saveRecentGroup(group.value)
  savedLocally.value = true
}

function getCurrentMember() {
  try {
    const value = localStorage.getItem(`equa.current-member.${groupId}`)
    return value ? Number(value) : null
  } catch {
    return null
  }
}

function saveCurrentMember() {
  try {
    if (currentMemberId.value)
      localStorage.setItem(`equa.current-member.${groupId}`, String(currentMemberId.value))
    else localStorage.removeItem(`equa.current-member.${groupId}`)
  } catch {
    // L'app resta utilizzabile se lo storage locale non è disponibile.
  }
  showMemberPicker.value = !currentMemberId.value
}

function settlementLabel(settlement: Settlement) {
  if (settlement.status === 'confirmed')
    return `Ricezione confermata da ${memberName(settlement.confirmed_by_member_id!)}`
  if (settlement.reported_at)
    return `Pagamento segnalato da ${memberName(settlement.reported_by_member_id!)}. In attesa che ${memberName(settlement.to_member_id)} confermi la ricezione.`
  return 'Da pagare'
}

async function reportSettlement(settlementId: number) {
  if (!currentMemberId.value) return
  settlementLoading.value = true
  settlementError.value = ''
  try {
    await groupsApi.reportSettlement(groupId, settlementId, currentMemberId.value)
    trackEvent('settlement_reported')
    await loadBalances()
  } catch (e: any) {
    settlementError.value =
      e?.response?.data?.detail || 'Non è stato possibile segnalare il pagamento.'
  } finally {
    settlementLoading.value = false
  }
}

async function confirmSettlement(settlementId: number) {
  if (!currentMemberId.value) return
  settlementLoading.value = true
  settlementError.value = ''
  try {
    await groupsApi.confirmSettlement(groupId, settlementId, currentMemberId.value)
    trackEvent('settlement_confirmed')
    await loadBalances()
  } catch (e: any) {
    settlementError.value =
      e?.response?.data?.detail || 'Non è stato possibile confermare il pagamento.'
  } finally {
    settlementLoading.value = false
  }
}

async function updateGroupStatus(status: Group['status']) {
  statusError.value = ''
  statusLoading.value = true
  try {
    const response =
      status === 'closing'
        ? await groupsApi.updateStatus(groupId, status, balanceMode.value)
        : await groupsApi.updateStatus(groupId, status)
    group.value = response.data
    balanceMode.value =
      status === 'active' ? 'separate' : response.data.closing_balance_mode || balanceMode.value
    if (status === 'closing') trackEvent('closing_started')
    if (status === 'closed') {
      showCelebration.value = true
      trackEvent('group_closed')
    }
    showExpenseForm.value = false
    showAddMemberForm.value = false
    cancelEditEmail()
    if (activeTab.value === 'balances' || status === 'closing') await loadBalances()
    return true
  } catch (e: any) {
    statusError.value =
      e?.response?.data?.detail || 'Non è stato possibile aggiornare lo stato del gruppo.'
    return false
  } finally {
    statusLoading.value = false
  }
}

async function startClosing() {
  if (statusLoading.value || balancesLoading.value || balancesError.value) return
  if (
    !(await askConfirmation({
      title: 'Iniziare la chiusura dei conti?',
      message: `${balanceMode.value === 'unified' ? `I pagamenti saranno fissati in ${group.value?.currency}, usando i cambi salvati sulle spese.` : 'I pagamenti saranno fissati separatamente per ogni valuta, senza conversioni.'} Spese e partecipanti saranno bloccati. Potrai riaprire i conti se serve una correzione.`,
      confirmLabel: 'Inizia chiusura',
    }))
  )
    return
  if (await updateGroupStatus('closing')) showClosingSummary.value = true
}

async function closeGroup() {
  if (statusLoading.value) return
  if (
    !(await askConfirmation({
      title: 'Chiudere il gruppo?',
      message: 'Segnerai il gruppo come chiuso. Potrai riaprirlo se serve una correzione.',
      confirmLabel: 'Chiudi gruppo',
    }))
  )
    return
  await updateGroupStatus('closed')
}

async function reopenGroup() {
  if (statusLoading.value) return
  if (
    !(await askConfirmation({
      title: 'Riaprire i conti?',
      message: 'Spese e partecipanti torneranno modificabili.',
      confirmLabel: 'Riapri conti',
    }))
  )
    return
  await updateGroupStatus('active')
}

onMounted(loadGroup)
</script>
