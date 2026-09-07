<template>
  <section
    v-if="enabled"
    class="mt-4 border-t border-gray-100 pt-4"
    :aria-labelledby="`${id}-title`"
  >
    <h3 :id="`${id}-title`" class="text-sm font-semibold text-gray-800">Non perdere il gruppo</h3>
    <p class="mt-1 text-xs leading-5 text-gray-500">
      Conserva il link nella tua email, anche per un altro dispositivo. Facoltativo, senza account o
      newsletter.
    </p>
    <button
      v-if="stage === 'intro'"
      type="button"
      class="mt-2 min-h-11 text-sm font-semibold text-green-700"
      @click="start"
    >
      Conserva via email
    </button>
    <p v-else-if="stage === 'done'" class="mt-3 text-sm text-green-700" role="status">
      Link inviato! Controlla la posta, anche la cartella spam. Puoi continuare a usare il gruppo.
    </p>
    <form v-else class="mt-3 space-y-3" @submit.prevent="submit">
      <div v-if="stage === 'email'">
        <label :for="`${id}-email`" class="block text-sm font-medium text-gray-700"
          >La tua email</label
        >
        <input
          :id="`${id}-email`"
          ref="emailInput"
          v-model="email"
          type="email"
          inputmode="email"
          autocomplete="email"
          autocapitalize="none"
          :spellcheck="false"
          required
          maxlength="254"
          :disabled="busy"
          :aria-describedby="`${id}-privacy`"
          class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm"
        />
      </div>
      <div v-else>
        <p class="text-xs leading-5 text-gray-600" role="status">
          Codice inviato a {{ email }}. Inseriscilo qui entro {{ expiresInMinutes }} minuti;
          controlla anche lo spam.
        </p>
        <label :for="`${id}-code`" class="mt-2 block text-sm font-medium text-gray-700"
          >Codice a 6 cifre</label
        >
        <input
          :id="`${id}-code`"
          ref="codeInput"
          v-model="code"
          type="text"
          inputmode="numeric"
          autocomplete="one-time-code"
          pattern="[0-9]{6}"
          minlength="6"
          maxlength="6"
          required
          :disabled="busy"
          class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm tracking-widest"
        />
        <button
          type="button"
          :disabled="busy"
          class="min-h-11 text-xs font-medium text-green-700 disabled:opacity-50"
          @click="changeAddress"
        >
          Cambia email o richiedi un nuovo codice
        </button>
      </div>
      <p v-if="error" class="text-sm text-red-600" role="alert">{{ error }}</p>
      <p :id="`${id}-privacy`" class="text-xs leading-5 text-gray-500">
        Chiedendo il codice autorizzi l'invio di questa verifica; il link partirà solo dopo la
        conferma. Il recapito non viene salvato nel database né mostrato ai partecipanti. Il
        fornitore email lo tratta per la consegna.
        <a
          v-if="privacyUrl"
          :href="privacyUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="underline"
          >Informativa privacy</a
        >. Nessun ruolo aggiuntivo: chi ha il link può collaborare. Il link non è un backup dei
        dati.
      </p>
      <div class="flex flex-wrap items-center gap-3">
        <button
          type="submit"
          :disabled="busy"
          class="min-h-11 rounded-lg bg-green-600 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50"
        >
          {{
            busy ? 'Invio…' : stage === 'code' ? 'Conferma e inviami il link' : 'Inviami il codice'
          }}
        </button>
        <button
          type="button"
          :disabled="busy"
          class="min-h-11 text-sm text-gray-600 disabled:opacity-50"
          @click="skip"
        >
          Per ora no
        </button>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, useId } from 'vue'
import { groupsApi } from '../api/groups'

const props = defineProps<{ groupId: string }>()
const id = useId()
const enabled = ref(false)
const privacyUrl = ref<string | null>(null)
const stage = ref<'intro' | 'email' | 'code' | 'done'>('intro')
const email = ref('')
const code = ref('')
const token = ref('')
const busy = ref(false)
const error = ref('')
const expiresInMinutes = ref(15)
const emailInput = ref<HTMLInputElement | null>(null)
const codeInput = ref<HTMLInputElement | null>(null)
let mounted = true

onMounted(async () => {
  try {
    const { data } = await groupsApi.emailLinkOptions()
    if (mounted) {
      enabled.value = data.enabled
      privacyUrl.value = data.privacy_url
    }
  } catch {
    // Creation and sharing work even with an old backend or email disabled.
  }
})

function discardChallenge(challenge = token.value): void {
  token.value = ''
  code.value = ''
  if (challenge)
    void groupsApi.cancelEmailLink(props.groupId, challenge).catch(() => {
      // Server-side expiry still invalidates the challenge if the network is unavailable.
    })
}

async function start(): Promise<void> {
  stage.value = 'email'
  await nextTick()
  emailInput.value?.focus()
}

async function changeAddress(): Promise<void> {
  discardChallenge()
  error.value = ''
  await start()
}

function skip(): void {
  discardChallenge()
  email.value = ''
  error.value = ''
  stage.value = 'intro'
}

async function submit(): Promise<void> {
  if (busy.value) return
  error.value = ''
  const confirming = stage.value === 'code'
  if (confirming && !/^[0-9]{6}$/.test(code.value)) {
    error.value = 'Inserisci il codice a 6 cifre ricevuto via email.'
    return
  }
  busy.value = true
  try {
    if (confirming) {
      await groupsApi.confirmEmailLink(props.groupId, token.value, code.value)
      token.value = ''
      code.value = ''
      email.value = ''
      if (mounted) stage.value = 'done'
    } else {
      const { data } = await groupsApi.requestEmailLink(props.groupId, email.value.trim())
      if (!mounted) {
        discardChallenge(data.challenge_token)
        return
      }
      token.value = data.challenge_token
      expiresInMinutes.value = Math.ceil(data.expires_in / 60)
      stage.value = 'code'
    }
  } catch (failure: unknown) {
    if (!mounted) return
    const response = (failure as { response?: { status?: number; data?: { detail?: unknown } } })
      ?.response
    error.value =
      typeof response?.data?.detail === 'string'
        ? response.data.detail
        : 'Invio non riuscito. Controlla i dati e la connessione, poi riprova.'
    if (confirming && (response?.status === 410 || response?.status === 503)) {
      discardChallenge()
      stage.value = 'email'
    }
  } finally {
    busy.value = false
    await nextTick()
    if (mounted && stage.value === 'code') codeInput.value?.focus()
  }
}

onBeforeUnmount(() => {
  mounted = false
  discardChallenge()
  email.value = ''
})
</script>
