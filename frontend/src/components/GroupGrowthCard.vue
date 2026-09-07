<template>
  <section
    class="my-4 rounded-xl border border-green-100 bg-green-50 p-4"
    aria-labelledby="next-group-title"
  >
    <h2 id="next-group-title" class="text-sm font-semibold text-gray-800">Alla prossima uscita?</h2>
    <p class="mt-1 text-sm leading-6 text-gray-600">
      Organizzi tu? Riparti con un nuovo gruppo. Se Equa ti è stata utile, puoi consigliarla agli
      amici.
    </p>
    <div class="mt-3 flex flex-wrap gap-2">
      <RouterLink
        to="/"
        class="min-h-11 rounded-lg bg-green-600 px-4 py-2.5 text-sm font-semibold text-white"
        >Crea un nuovo gruppo</RouterLink
      >
      <button
        type="button"
        :disabled="sharing"
        class="min-h-11 rounded-lg border border-green-300 bg-white px-4 py-2.5 text-sm font-semibold text-green-800 disabled:opacity-50"
        @click="shareApp"
      >
        Consiglia Equa
      </button>
      <a
        :href="whatsAppUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="min-h-11 px-3 py-2.5 text-sm font-medium text-green-800"
        >Consiglia su WhatsApp</a
      >
    </div>
    <p class="mt-2 text-xs text-gray-500">
      Condividi solo l'app, senza link o dati di questo gruppo.
    </p>
    <p v-if="feedback" class="mt-2 text-sm text-green-800" role="status">{{ feedback }}</p>
    <input
      v-if="showManualLink"
      :value="appUrl"
      readonly
      aria-label="Link pubblico di Equa da copiare"
      class="mt-2 w-full rounded-lg border border-green-200 bg-white px-3 py-2 text-sm"
      @focus="selectLink"
    />
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

// Never derive referrals from location.href: it can contain a private group UUID.
const appUrl = new URL('/', window.location.origin).toString()
const message =
  'Con Equa dividi le spese di cene e vacanze, senza account. Provala per la prossima uscita!'
const whatsAppUrl = `https://wa.me/?text=${encodeURIComponent(`${message} ${appUrl}`)}`
const feedback = ref('')
const showManualLink = ref(false)
const sharing = ref(false)

function selectLink(event: FocusEvent): void {
  ;(event.target as HTMLInputElement).select()
}

async function shareApp(): Promise<void> {
  if (sharing.value) return
  sharing.value = true
  feedback.value = ''
  try {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Equa — Dividi le spese, non le amicizie',
          text: message,
          url: appUrl,
        })
        return
      } catch (failure: unknown) {
        if ((failure as { name?: string })?.name === 'AbortError') return
      }
    }
    try {
      await navigator.clipboard.writeText(`${message} ${appUrl}`)
      feedback.value = 'Messaggio copiato: incollalo dove preferisci.'
    } catch {
      showManualLink.value = true
      feedback.value = 'Puoi copiare manualmente il link pubblico qui sotto.'
    }
  } finally {
    sharing.value = false
  }
}
</script>
