# Changelog

Tutte le modifiche rilevanti al progetto sono documentate in questo file.

Il formato segue [Keep a Changelog](https://keepachangelog.com/it/1.0.0/).
Il versionamento segue [Semantic Versioning](https://semver.org/lang/it/).

---

## [1.6.0] Frontend - 2026-09-04

### Aggiunto

- Spese in più valute con valuta di default del gruppo, data effettiva, cambio storico salvato e correzione manuale facoltativa.
- Bilanci separati per valuta e vista unificata su richiesta; la modalità scelta viene congelata nei pagamenti durante la chiusura.
- Supporto per lek albanese, yen e altre valute principali, con precisione e arrotondamenti coerenti con l'unità minima.
- Migrazione `004` con rollback protetto, test backend/frontend e documentazione del flusso multi-valuta.

### Modificato

- Il campo valuta nella creazione del gruppo è ora presentato come “Valuta di default” e le spese mostrano sempre la propria valuta.
- Totali, riepiloghi personali e messaggi di chiusura mantengono separati gli importi in valute diverse.
- Sostituiti alert e conferme native con modali condivise mobile-first, pulsanti touch, semantica accessibile, gestione del focus e annullamento tramite Escape.
- Le conferme di eliminazione indicano la spesa o il partecipante coinvolto; la cancellazione della cronologia chiarisce che non elimina i gruppi remoti.

### Corretto

- Gli errori durante l'eliminazione delle spese mostrano un messaggio recuperabile e le richieste di eliminazione ripetute vengono bloccate mentre l'operazione è in corso.

---

## [1.5.1] Frontend - 2026-08-29

### Corretto

- Le pageview manuali inviate a Umami includono l'identificatore obbligatorio del sito, evitando risposte `400 Bad Request` in produzione.

---

## [1.5.0] Frontend; Backend - 2026-08-29

### Aggiunto

- Setup e manutenzione riproducibili dell'ambiente Codex Cloud con Python 3.12, Node.js 20 e dipendenze di sviluppo.
- Badge `Novità` per gruppi recenti e salvataggio locale, e badge `Beta` per il flusso di chiusura dei conti.
- Riepilogo WhatsApp con emoji generato all'avvio della chiusura, con totale spese, pagamenti richiesti, link al gruppo e versione per i cicli successivi al primo.
- Integrazione Umami Cloud opzionale per pageview anonimizzate e gli eventi aggregati del funnel: gruppi, spese, condivisione, chiusura, pagamenti e donazioni.
- Asset SVG del logo condiviso tra l'app e la testata del README.
- Base di test automatici: pytest per il calcolo dei bilanci, Vitest per le utility frontend e hook pre-commit per le suite interessate dalle modifiche.
- Flusso di chiusura dei conti con stati `In corso`, `Chiusura conti` e `Conti chiusi`, più riapertura esplicita quando serve una correzione.
- Pagamenti persistenti generati dai saldi: chi paga può segnalare il pagamento e chi riceve può confermarlo dal proprio dispositivo.
- Invito alla chiusura visibile nella tab Bilanci solo quando è rilevante, selezione locale del partecipante compatta e popup finale di celebrazione con donazione facoltativa.
- Selezione locale `Tu chi sei nel gruppo?` disponibile nella tab Partecipanti mentre la vacanza è in corso e riutilizzata durante la chiusura dei conti.
- Riepilogo personale nella tab Bilanci con importi da pagare e ricevere, saldo netto e numero di pagamenti per l'identità scelta sul dispositivo.

### Modificato

- Lockfile resi disponibili a Codex e dipendenza `cryptography` fissata a una versione esplicita.
- Il link di donazione mostrato alla chiusura dei conti ora lascia libero l'importo.
- L'azione `Aggiungi email` dei partecipanti viene nascosta quando il gruppo è in chiusura o chiuso.
- La gestione email dei partecipanti resta disponibile nel codice ma viene temporaneamente nascosta nell'interfaccia.

### Corretto

- I gruppi già in pari possono avviare e completare il flusso di chiusura dalla tab Bilanci.
- Nei gruppi chiusi la tab Bilanci mostra lo storico dei pagamenti confermati invece di riproporre i saldi originari come debiti aperti.
- L'eliminazione di un partecipante coinvolto nello storico dei pagamenti viene rifiutata esplicitamente, evitando errori di integrità del database.
- Aggiunti gli script di rollback mancanti per le migrazioni `001` e `002`.
- Il riepilogo personale resta visibile durante la chiusura e considera solo i pagamenti non ancora confermati.
- Suggerimenti di donazione aggiornati a 2 €, 3 € e 5 €.
- Durante la chiusura dei conti il backend rifiuta modifiche a spese e partecipanti, evitando che i saldi cambino involontariamente.
- I messaggi della chiusura distinguono correttamente il gruppo in chiusura dal gruppo già chiuso e indicano quando si attende la conferma del creditore.
- Dopo l'avvio della chiusura, la tab Bilanci ricarica subito i pagamenti da confermare senza richiedere una navigazione o un refresh manuale.

---

## [1.4.2] Frontend - 2026-08-25

### Aggiunto

- Cronologia locale dei gruppi: i gruppi creati vengono salvati sul dispositivo e i gruppi ricevuti possono essere salvati volontariamente.
- Sezione "I tuoi gruppi recenti" nella home, con apertura rapida, rimozione singola e cancellazione completa della cronologia.

---

## [1.4.1] Frontend; Backend - 2026-08-25

### Aggiunto

- Il pulsante "Condividi" nell'header apre il pannello con WhatsApp, condivisione nativa e copia del link.

### Corretto

- Nell'header del gruppo, su mobile i titoli lunghi vanno a capo nello spazio disponibile senza sovrapporsi al pulsante di condivisione, che resta sulla stessa riga.

---

## [1.4.0] Frontend; Backend - 2026-08-25

### Aggiunto

- Dopo la creazione di un gruppo viene mostrato un promemoria per condividere e conservare il link di accesso.
- Il promemoria offre condivisione nativa, messaggio WhatsApp precompilato, copia del link e URL visibile per la copia manuale.

---

## [1.3.0] Frontend; Backend - 2026-08-24

### Aggiunto

- Modifica dell'email dei partecipanti direttamente dalla tab "Partecipanti".
- Form di aggiunta partecipante richiudibile per una visualizzazione piu compatta.
- Configurazione pre-commit con Black, Ruff e Prettier per formattazione e linting automatici.

---

## [1.2.1] Frontend - 2026-08-22

### Corretto

- Form di aggiunta partecipante nella tab "Partecipanti" non era responsive e sfondava lo schermo su mobile. Ora va in colonna sotto i 640px (flex-col sm:flex-row) e gli input possono restringersi correttamente (min-w-0).

---

## [1.2.0] Frontend; Backend - 2026-08-22

### Aggiunto

- Nuovo endpoint `POST /groups/{group_id}/members/` per aggiungere partecipanti a un gruppo già esistente, anche a spese già presenti. I nuovi membri non vengono retroattivamente coinvolti nelle spese precedenti, che mantengono lo split salvato al momento della loro creazione.

---

## [1.1.1] Backend - 2026-04-23

### Corretto

- Aggiunto test della connessione al database prima di avviare l'applicazione (fix #7). Aggiunto inoltre pool_recycle a 1800 secondi per riciclare le connessioni ogni 30 minuti, prevenendo timeout inattesi.

---

## [1.1.0] Frontend; [1.1.0] Backend - 2026-04-19

### Aggiunto

- Totale spese in tempo reale nella vista gruppo
- Modifica spese già inserite (click su una spesa per aprire il form precompilato)
- Rimozione partecipanti dal gruppo (solo se non coinvolti in nessuna spesa)
- Nuovo endpoint `PUT /groups/{group_id}/expenses/{expense_id}`
- Nuovo endpoint `DELETE /groups/{group_id}/members/{member_id}`

---

## [1.0.0] Frontend; [1.0.0] Backend - 2026-04-08

### Aggiunto

- Creazione gruppi con partecipanti
- Aggiunta spese con tre modalità: tutti, sottoinsieme, personalizzato
- Algoritmo greedy per minimizzare il numero di transazioni
- Vista bilanci con chi deve cosa a chi
- Link condivisibile per ogni gruppo
- Donazioni PayPal con cifre rapide (1€, 2€, 5€, libero)
- Logo geometrico SVG
- Deploy self-hosted con Docker + Portainer + Nginx
- CI/CD con GitHub Actions → Docker Hub
