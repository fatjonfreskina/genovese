# Roadmap Equa

> Dividi le spese, non le amicizie.

Questo documento descrive l'evoluzione prevista di Equa con tre obiettivi principali:

1. Rendere il calcolo e la gestione delle spese semplici, affidabili e veloci.
2. Far tornare gli utenti quando il gruppo cambia o quando i pagamenti devono essere chiusi.
3. Aumentare la diffusione dei gruppi condivisi senza snaturare il modello gratuito, leggero e senza registrazione obbligatoria.

La roadmap e ordinata per impatto e dipendenze, non per data rigida. Le funzionalita che richiedono account, email automatiche o pagamenti online verranno affrontate solo dopo aver consolidato il flusso anonimo basato sul link.

---

## 0. Checklist di avanzamento

> Usa `[ ]` per le attivita da fare e `[x]` per quelle completate. Le checkbox di questa sezione sono il riepilogo operativo; i dettagli e i criteri tecnici sono descritti nelle sezioni successive.

### Fondamenta

- [ ] Correggere la validazione degli split lato backend.
- [ ] Uniformare caricamenti, errori, retry e conferme.
- [ ] Uniformare la formattazione di importi e valute.
- [x] Aggiungere test backend e frontend essenziali.
- [ ] Definire il modello di sicurezza dei link.

### Condivisione e ritorno senza account

- [x] Implementare Web Share API e fallback clipboard.
- [x] Aggiungere condivisione WhatsApp.
- [x] Salvare e mostrare i gruppi recenti localmente.
- [ ] Migliorare la pagina di ingresso da link condiviso.
- [ ] Aggiungere titolo dinamico e anteprima del link.

### Bilanci e chiusura dei debiti

- [x] Permettere di identificare il partecipante sul dispositivo.
- [x] Mostrare il riepilogo personale "devi pagare/ricevere".
- [ ] Generare promemoria condivisibili.
- [x] Generare un riepilogo di chiusura condivisibile e versionato.
- [x] Introdurre lo stato dei pagamenti.
- [x] Mostrare lo stato di chiusura del gruppo.
- [x] Gestire spese in più valute nello stesso gruppo.

### Collaborazione

- [ ] Aggiungere aggiornamento automatico leggero.
- [ ] Registrare e mostrare lo storico delle attivita.
- [ ] Completare la modifica dei partecipanti.
- [ ] Aggiungere ricerca, filtri e ordinamento delle spese.

### Notifiche, PWA e uso continuativo

- [ ] Implementare inviti email con consenso esplicito.
- [ ] Aggiungere preferenze e digest delle notifiche.
- [ ] Separare i token di invito dai token di modifica.
- [ ] Rendere Equa installabile come PWA.
- [ ] Gestire cache offline e sincronizzazione.
- [ ] Aggiungere template, date, esportazioni e spese ricorrenti.

### Evoluzione opzionale

- [ ] Validare la domanda per account opzionali.
- [ ] Implementare dashboard personale e recupero multi-dispositivo.
- [ ] Introdurre ruoli e permessi lato backend.
- [ ] Valutare integrazioni con servizi di pagamento.

---

## 1. Principi di prodotto

### 1.1 Nessun account come punto di partenza

La forza di Equa e permettere a chiunque di creare un gruppo in pochi secondi. Le prime funzionalita devono quindi funzionare senza registrazione.

Gli account potranno diventare opzionali in futuro per chi desidera cronologia, notifiche e recupero avanzato dei gruppi. Non devono essere un prerequisito per aggiungere una spesa o vedere un saldo.

### 1.2 Il link deve rimanere centrale

Il link condiviso e il principale canale di acquisizione: ogni partecipante che apre il link e un potenziale nuovo utilizzatore. Condivisione, anteprime, messaggi e accesso da mobile devono essere progettati intorno a questo comportamento.

### 1.3 Privacy prima della crescita

Equa tratta dati finanziari informali e indirizzi email. Ogni nuova funzione deve rispettare questi criteri:

- nessuna vendita dei dati;
- nessuna email inviata senza consenso esplicito;
- raccolta del minimo indispensabile (Law of Least Privilege);
- possibilita di cancellare i dati del gruppo;
- analytics aggregati e, quando possibile, anonimi;
- documentazione chiara di cosa viene salvato e perche.

### 1.4 Correttezza e fiducia

Un saldo sbagliato o una spesa persa distrugge la fiducia piu velocemente di qualsiasi problema estetico. Validazione backend, conferme, storico modifiche e gestione degli errori hanno precedenza sulle funzioni accessorie.

### 1.5 Mobile first

Il caso d'uso principale e un gruppo di persone che usa telefoni diversi durante una cena, una vacanza o una trasferta. Ogni flusso deve essere utilizzabile con una mano, con rete instabile e senza installare un'app.

---

## 2. Stato attuale

### 2.1 Funzionalita gia presenti

- Creazione di gruppi senza registrazione.
- Nome, descrizione, valuta e partecipanti.
- Condivisione tramite URL con UUID.
- Inserimento spese divise tra tutti, tra un sottoinsieme o con importi personalizzati.
- Modifica e cancellazione delle spese.
- Calcolo dei saldi con algoritmo greedy.
- Aggiunta e rimozione dei partecipanti con vincoli sulle spese esistenti.
- Modifica dell'email di un partecipante.
- Totale delle spese nella vista gruppo.
- Donazione PayPal.

### 2.2 Modello tecnico attuale

- Frontend: Vue 3, TypeScript, Vite, Tailwind CSS.
- Backend: FastAPI, SQLAlchemy e MySQL.
- Persistenza: gruppi, membri, spese e split.
- API organizzate per gruppi, spese, bilanci e membri.
- Nessun account, ruolo, sessione utente o audit trail.
- Nessun sistema di notifiche o invio email.
- Nessuna cronologia locale dei gruppi visitati.
- Nessun aggiornamento in tempo reale.

Riferimenti principali:

- [HomeView.vue](frontend/src/views/HomeView.vue)
- [GroupView.vue](frontend/src/views/GroupView.vue)
- [groups.ts](frontend/src/api/groups.ts)
- [models.py](backend/app/models.py)
- [schemas.py](backend/app/schemas.py)

### 2.3 Frizioni da risolvere

1. Un gruppo non e recuperabile se l'utente perde il link.
2. La condivisione usa principalmente gli appunti e non sfrutta i canali mobile.
3. Il riepilogo dei bilanci non evidenzia la posizione personale dell'utente.
4. Alcuni errori usano `alert`, altri non mostrano un feedback sufficiente.
5. Non e possibile sapere chi ha modificato una spesa.
6. L'email del partecipante viene salvata ma non attiva alcun flusso.
7. Gli endpoint custom devono validare meglio l'appartenenza dei membri al gruppo.
8. Il possesso dell'UUID consente di leggere e modificare il gruppo.

---

## 3. Metriche di successo

Le metriche devono essere raccolte in modo compatibile con il posizionamento privacy-first. Non serve tracciare ogni azione individuale per capire se il prodotto funziona.

### 3.1 Attivazione

- Tempo mediano dalla home alla creazione del primo gruppo.
- Percentuale di creazioni completate rispetto a quelle iniziate.
- Percentuale di gruppi con almeno una spesa inserita.
- Percentuale di gruppi condivisi dopo la creazione.

### 3.2 Collaborazione

- Numero medio di partecipanti per gruppo.
- Numero medio di spese per gruppo.
- Percentuale di gruppi in cui piu di un partecipante apre il link.
- Percentuale di gruppi in cui viene aperta la tab Bilanci.

### 3.3 Retention

- Percentuale di gruppi riaperti dopo 24 ore, 7 giorni e 30 giorni.
- Percentuale di gruppi con almeno una modifica dopo la prima visita.
- Tempo medio tra ultima spesa e chiusura dei pagamenti.
- Percentuale di gruppi che raggiungono lo stato "tutti pagati".

### 3.4 Crescita

- Condivisioni per gruppo.
- Nuovi ingressi generati da un link condiviso.
- Rapporto tra gruppi creati e gruppi aperti tramite link.
- Quota di traffico da condivisioni rispetto al traffico diretto.

### 3.5 Qualita

- Errori API per endpoint.
- Fallimenti di salvataggio.
- Tempo di risposta del caricamento gruppo.
- Segnalazioni di dati mancanti o saldi errati.

---

## 4. Fase 0: affidabilita e fondamenta

**Priorita: immediata**  
**Obiettivo: rendere Equa degna di fiducia prima di aggiungere meccanismi di crescita.**

### 4.1 Validazione completa delle spese

**Checklist**

- [ ] Validare il pagante e l'appartenenza al gruppo.
- [ ] Validare ogni membro presente negli split.
- [ ] Bloccare split duplicati e importi non validi.
- [ ] Verificare la somma degli split.
- [ ] Aggiungere test per tutte le regole.

#### Comportamento

Il backend deve rifiutare ogni richiesta non coerente con il gruppo:

- il pagante deve essere membro del gruppo;
- ogni `member_id` di uno split deve appartenere al gruppo;
- non devono esserci split duplicati per lo stesso membro;
- gli importi devono essere maggiori o uguali a zero;
- l'importo totale deve essere maggiore di zero;
- la somma degli split deve coincidere con il totale entro la tolleranza prevista;
- una spesa deve avere almeno uno split valido;
- il gruppo deve esistere.

#### API coinvolte

- `POST /groups/{group_id}/expenses/`
- `POST /groups/{group_id}/expenses/equal`
- `POST /groups/{group_id}/expenses/subset`
- `PUT /groups/{group_id}/expenses/{expense_id}`

#### Criteri di completamento

- Test backend per ogni regola di validazione.
- Nessuna spesa puo riferirsi a membri di un altro gruppo.
- Gli errori restituiscono messaggi leggibili e codici HTTP coerenti.

### 4.2 Stati di caricamento, errore e retry

**Checklist**

- [ ] Gestire caricamento gruppo e bilanci.
- [ ] Gestire creazione, modifica e cancellazione delle spese.
- [ ] Gestire aggiunta, modifica e rimozione dei membri.
- [ ] Impedire il doppio invio.
- [ ] Conservare i dati del form dopo un errore di rete.

Aggiungere una gestione uniforme per:

- caricamento gruppo;
- caricamento bilanci;
- creazione e modifica spesa;
- cancellazione spesa;
- aggiunta, modifica e rimozione membro;
- copia e condivisione del link.

Ogni operazione deve avere:

- stato di caricamento;
- pulsante o azione di retry dove possibile;
- messaggio non tecnico;
- prevenzione del doppio invio;
- conservazione dei dati gia inseriti in caso di errore di rete.

### 4.3 Feedback non invasivo

**Checklist**

- [x] Sostituire gli `alert` con notifiche accessibili.
- [ ] Mostrare conferme dopo le operazioni riuscite.
- [ ] Rendere espliciti gli errori recuperabili.
- [x] Confermare le azioni distruttive con il nome dell'elemento.

Sostituire progressivamente gli `alert` con notifiche temporanee accessibili:

- successo: "Spesa aggiornata";
- errore: "Non siamo riusciti a salvare. Riprova";
- informazione: "Il gruppo e stato aggiornato da un altro dispositivo".

Le azioni distruttive devono usare una conferma chiara e distinguere il nome dell'elemento che verra eliminato.

### 4.4 Formati coerenti per importi e valute

**Checklist**

- [ ] Creare un formatter comune basato su `Intl.NumberFormat`.
- [ ] Applicarlo a totale, spese, bilanci e riepilogo personale.
- [ ] Applicarlo ai messaggi di condivisione.

Centralizzare la formattazione degli importi con `Intl.NumberFormat`, usando la valuta del gruppo e due decimali quando servono. Il formato deve essere uguale in:

- totale spese;
- singole spese;
- bilanci;
- riepilogo personale;
- messaggi di condivisione.

### 4.5 Sicurezza minima del link

**Checklist**

- [ ] Documentare cosa permette di fare il link corrente.
- [ ] Valutare token separati per lettura, modifica e gestione.
- [ ] Aggiungere rate limiting agli endpoint pubblici.
- [ ] Validare UUID e input di tutte le route pubbliche.
- [ ] Escludere dati sensibili dai log e dalle anteprime.

Il modello anonimo puo rimanere, ma va chiarito il livello di accesso:

- link corrente per collaborare;
- token separato per operazioni sensibili, se compatibile con l'esperienza;
- possibilita di rigenerare il link di modifica;
- messaggio esplicito: chi possiede il link puo accedere al gruppo;
- rate limiting sugli endpoint pubblici;
- validazione del formato UUID;
- log tecnici senza contenere importi o email in chiaro quando non necessario.

Questa fase non deve introdurre una registrazione obbligatoria.

---

## 5. Fase 1: condivisione e ritorno senza account

**Priorita: molto alta**  
**Obiettivo: aumentare gli ingressi generati da ogni gruppo e permettere agli utenti di tornare.**

### 5.1 Condivisione nativa mobile

**Checklist**

- [x] Usare Web Share API sui dispositivi compatibili.
- [x] Aggiungere WhatsApp e copia link.
- [ ] Aggiungere Telegram ed email.
- [x] Preparare un messaggio con nome gruppo e URL.
- [x] Gestire clipboard e Web Share non disponibili.
- [ ] Mostrare sempre l'esito dell'azione.

Il pulsante "Condividi" deve:

1. usare Web Share API su dispositivi compatibili;
2. offrire WhatsApp e Telegram quando disponibili;
3. offrire email e copia link come fallback;
4. mostrare un messaggio precompilato con nome gruppo e URL;
5. confermare sempre l'esito dell'azione.

Esempio di messaggio:

> Ho creato il gruppo "Vacanza in Sardegna" su Equa. Aprilo qui per aggiungere o controllare le spese: [link]

#### Criteri di completamento

- Condivisione utilizzabile su Android, iOS e desktop.
- Fallback funzionante quando clipboard o Web Share non sono disponibili.
- Il link completo e visibile e copiabile manualmente.
- Nessun errore silenzioso.

### 5.2 Cronologia locale dei gruppi

**Checklist**

- [x] Salvare UUID, nome, valuta e ultimo accesso.
- [x] Mostrare i gruppi recenti nella home.
- [x] Consentire apertura e rimozione singola.
- [x] Consentire cancellazione completa della cronologia.
- [x] Informare che i dati restano sul dispositivo.

Salvare nel browser, senza account:

- UUID del gruppo;
- nome;
- descrizione, se presente;
- valuta;
- data dell'ultimo accesso;
- numero noto di partecipanti e spese.

La home deve mostrare una sezione "I tuoi gruppi recenti" con:

- apertura con un tap;
- rimozione singola;
- eliminazione completa della cronologia locale;
- indicazione che i dati sono salvati solo sul dispositivo.

#### Limiti

La cronologia locale non e un backup. Il gruppo deve continuare a essere recuperabile tramite link condiviso.

### 5.3 Pagina di ingresso condivisa

**Checklist**

- [ ] Mostrare nome, descrizione e partecipanti.
- [ ] Mostrare totale spese e azione principale.
- [x] Offrire il salvataggio tra i gruppi recenti.
- [ ] Stabilizzare il layout durante il caricamento mobile.

Quando un utente apre un link da una chat, la pagina deve rendere immediatamente chiaro:

- nome del gruppo;
- descrizione;
- numero di partecipanti;
- totale spese;
- azione principale per vedere o aggiungere una spesa;
- azione per salvare il gruppo tra i recenti.

Su mobile il caricamento deve mostrare uno stato stabile e non spostare il contenuto quando arrivano i dati.

### 5.4 Titolo e anteprima del link

**Checklist**

- [ ] Aggiornare il titolo del browser con il nome del gruppo.
- [ ] Aggiungere meta description e Open Graph.
- [ ] Escludere importi, email e dati sensibili.

Aggiornare dinamicamente:

- titolo della pagina con il nome del gruppo;
- descrizione meta dove possibile;
- Open Graph title e description;
- testo di condivisione leggibile.

Non includere importi, email o dati sensibili nelle anteprime social.

---

## 6. Fase 2: bilanci comprensibili e chiusura dei debiti

**Priorita: alta**  
**Obiettivo: fare in modo che ogni partecipante capisca subito cosa deve fare.**

### 6.1 Identita locale del partecipante

**Checklist**

- [x] Chiedere quale partecipante rappresenta l'utente.
- [x] Salvare la scelta solo sul dispositivo.
- [x] Permettere di cambiare partecipante in seguito.
- [x] Mantenere accessibile il gruppo senza identificazione.

Alla prima apertura del gruppo, proporre in modo leggero:

> Quale partecipante sei?

La scelta viene salvata solo sul dispositivo e puo essere modificata in seguito. Non e un account e non deve impedire l'accesso anonimo.

### 6.2 Riepilogo personale

**Checklist**

- [x] Mostrare totale da pagare.
- [x] Mostrare totale da ricevere.
- [x] Mostrare saldo netto personale.
- [x] Mostrare il numero di pagamenti in entrata e in uscita.
- [x] Lasciare disponibile la lista globale dei bilanci.

In cima alla tab Bilanci mostrare:

- "Devi pagare" con totale;
- "Devi ricevere" con totale;
- saldo netto;
- numero di pagamenti da effettuare;
- numero di pagamenti da ricevere.

La lista globale resta disponibile sotto il riepilogo.

### 6.3 Messaggi di promemoria condivisibili

**Checklist**

- [ ] Aggiungere l'azione "Ricorda" a ogni debito.
- [ ] Generare messaggi con destinatario, importo e gruppo.
- [ ] Aprire la condivisione o copiare il testo senza invio automatico.
- [ ] Usare un tono neutro e non aggressivo.

Per ogni debito offrire un'azione "Ricorda" che genera un messaggio personalizzato. Il primo rilascio deve aprire il sistema di condivisione o copiare il testo, senza invio automatico.

Il messaggio deve contenere:

- nome del destinatario;
- importo;
- nome del gruppo;
- link al gruppo;
- tono neutro e non aggressivo.

### 6.4 Conferma dei pagamenti

**Checklist**

- [x] Definire gli stati `pending`, `confirmed` e `cancelled`.
- [x] Progettare la tabella `settlements`.
- [x] Gestire la rigenerazione dei saldi dopo modifiche alle spese.
- [ ] Conservare lo storico delle conferme precedenti.

Aggiungere lo stato di una transazione:

- `pending`: da pagare;
- `confirmed`: confermata dal creditore o dal gruppo;
- `cancelled`: annullata o corretta.

Per la prima versione puo bastare una conferma locale o condivisa, ma la versione persistente richiedera nuove entita backend.

La prima versione persistente usa l'identità scelta localmente sul dispositivo per attribuire una segnalazione o una conferma. Non costituisce autenticazione: finché non esistono token personali, il gruppo opera su fiducia tra i partecipanti. Riaprire i conti annulla i pagamenti della chiusura corrente, che vengono rigenerati al prossimo avvio della chiusura.

#### Modello dati suggerito

Tabella `settlements`:

- `id`;
- `group_id`;
- `from_member_id`;
- `to_member_id`;
- `amount`;
- `status`;
- `confirmed_at`;
- `created_at`.

Le transazioni dovrebbero essere rigenerate quando cambiano le spese, mantenendo lo storico delle conferme precedenti come eventi separati.

### 6.5 Stato di chiusura del gruppo

**Checklist**

- [x] Mostrare stato "In corso".
- [x] Mostrare stato "Chiusura conti".
- [x] Mostrare stato "Conti chiusi" dopo la conferma dei pagamenti.
- [ ] Creare il riepilogo finale del gruppo.
- [x] Bloccare spese e partecipanti durante la chiusura.
- [x] Consentire la riapertura quando necessario.

Mostrare una sintesi:

- `In corso`;
- `Quasi chiuso`;
- `Tutti i pagamenti confermati`.

La prima versione può bloccare spese e partecipanti durante la chiusura dei conti e consentire una riapertura esplicita. Lo stato "Tutti i pagamenti confermati" richiede invece gli stati persistenti delle singole transazioni.

Quando tutti i saldi sono chiusi, mostrare una schermata breve con:

- totale speso;
- numero partecipanti;
- numero spese;
- data di chiusura;
- azione per riaprire il gruppo se necessario.

### 6.6 Riepilogo condivisibile della chiusura

**Checklist**

- [x] Generare il riepilogo dopo l'avvio riuscito della chiusura.
- [x] Includere totale spese, partecipanti e pagamenti da effettuare.
- [x] Includere il link al gruppo per segnalare e confermare i pagamenti.
- [x] Aprire WhatsApp con il messaggio precompilato senza invio automatico.
- [x] Numerare dal secondo ciclo di chiusura per distinguere i riepiloghi aggiornati.

Il riepilogo globale serve a condividere nella chat del gruppo una fotografia dei conti. Quando un gruppo viene riaperto e chiuso di nuovo, il backend incrementa un contatore persistente e il messaggio mostra `versione 2`, `versione 3` e così via. La prima chiusura non mostra il numero di versione.

Il messaggio deve restare leggibile su mobile e contenere solo dati già accessibili tramite il link del gruppo. Non deve includere email o introdurre invii automatici.

### 6.7 Spese in più valute

**Stato: implementata con la issue #19**

**Checklist**

- [x] Mantenere una valuta di default del gruppo per inserimento e bilanci unificati.
- [x] Consentire di scegliere la valuta originale per ogni spesa.
- [x] Salvare importo originale, valuta originale e tasso di conversione applicato.
- [x] Mostrare prima del salvataggio l'importo convertito nella valuta di default.
- [x] Consentire l'inserimento e la correzione manuale del tasso di cambio.
- [x] Usare un provider opzionale per suggerire i tassi senza renderlo necessario al salvataggio.
- [x] Conservare il tasso usato dalla spesa, evitando che variazioni future cambino i saldi storici.
- [x] Mostrare nel riepilogo gli importi originali per valuta e il totale nella valuta di default.
- [x] Aggiungere migrazione, validazione backend e test su precisione e arrotondamenti.

Un gruppo continua ad avere una valuta di default. I bilanci sono separati per valuta; su richiesta possono essere unificati nella valuta di default. Ogni spesa conserva una fotografia del tasso applicato al momento del salvataggio. Modificare un tasso è un'azione esplicita e ricalcola i saldi in modo deterministico.

Il salvataggio della spesa deve funzionare anche quando il provider dei cambi non è disponibile. Il cambio manuale resta possibile; il valore usato deve essere visibile e persistito. Non devono essere inviati al provider nomi, descrizioni, partecipanti o importi delle spese.

#### Modello dati proposto

Per ogni spesa sono presenti:

- `amount` e gli split nella valuta originale;
- `currency` come codice dal catalogo supportato;
- `expense_date` come data effettiva della spesa;
- `exchange_rate`, `exchange_rate_date` ed `exchange_rate_source` verso la valuta di default;
- `converted_amount` calcolato dal backend e non salvato come secondo importo modificabile.

#### Criteri di completamento

- [x] Gruppi con una sola valuta continuano a funzionare senza passaggi aggiuntivi.
- [x] I saldi sono riproducibili usando i tassi salvati, anche senza accesso a Internet.
- [x] UI e messaggi distinguono chiaramente importo originale e importo convertito.
- [x] Arrotondamenti e somma degli split rispettano l'unità minima della valuta.
- [x] La migrazione preserva tutte le spese esistenti assegnando loro la valuta del gruppo.

---

## 7. Fase 3: collaborazione trasparente

**Priorita: media-alta**  
**Obiettivo: ridurre conflitti e aggiornamenti persi quando piu persone usano il gruppo.**

### 7.1 Aggiornamento automatico leggero

**Checklist**

- [ ] Implementare polling solo quando la pagina e visibile.
- [ ] Mostrare l'ora dell'ultimo aggiornamento.
- [ ] Non sovrascrivere un form aperto.
- [ ] Avvisare in caso di modifica concorrente.
- [ ] Aggiungere il pulsante "Aggiorna ora".

Prima versione: polling ogni 20-30 secondi solo quando la pagina e visibile.

Comportamento:

- indicare l'ora dell'ultimo aggiornamento;
- non cancellare dati inseriti in un form aperto;
- mostrare un avviso se arrivano modifiche mentre l'utente sta compilando;
- offrire un pulsante "Aggiorna ora";
- sospendere il polling quando la scheda non e visibile.

In futuro valutare Server-Sent Events o WebSocket solo se il polling si dimostra insufficiente.

### 7.2 Storico attivita

**Checklist**

- [ ] Progettare la tabella `activity_events`.
- [ ] Registrare creazione, modifica e cancellazione delle spese.
- [ ] Registrare modifiche a membri e pagamenti.
- [ ] Mostrare una timeline leggibile.
- [ ] Distinguere attore noto e attore sconosciuto.

Mostrare una timeline leggibile:

- partecipante aggiunto;
- spesa aggiunta;
- spesa modificata;
- spesa eliminata;
- email o nome modificato;
- pagamento confermato.

#### Modello dati suggerito

Tabella `activity_events`:

- `id`;
- `group_id`;
- `actor_member_id`, opzionale;
- `event_type`;
- `entity_type`;
- `entity_id`;
- snapshot minimo dei dati rilevanti;
- `created_at`.

L'attore puo essere sconosciuto nel modello senza account. Non bisogna fingere di conoscere l'identita quando non e stata verificata.

### 7.3 Modifica dei partecipanti completa

**Checklist**

- [ ] Esporre la modifica del nome nella UI.
- [ ] Validare il nome non vuoto.
- [ ] Consentire annullamento e ripristino.
- [ ] Aggiornare spese e bilanci dopo il salvataggio.

Esporre in UI anche la modifica del nome, gia compatibile con l'endpoint `PATCH` del backend. Aggiungere:

- modifica inline;
- annullamento;
- validazione del nome vuoto;
- feedback di salvataggio;
- aggiornamento coerente delle spese e dei bilanci.

### 7.4 Filtri e ricerca spese

**Checklist**

- [ ] Cercare per descrizione.
- [ ] Filtrare per pagante.
- [ ] Filtrare per partecipanti coinvolti.
- [ ] Filtrare per intervallo temporale.
- [ ] Ordinare per data o importo.

Quando il gruppo cresce, aggiungere:

- ricerca per descrizione;
- filtro per chi ha pagato;
- filtro per partecipanti coinvolti;
- filtro per intervallo temporale;
- ordinamento piu recenti/piu costose.

La lista deve restare semplice per gruppi piccoli: i filtri appaiono solo quando sono utili.

---

## 8. Fase 4: notifiche e inviti consensuali

**Priorita: media**  
**Obiettivo: creare ritorni automatici senza trasformare Equa in un servizio invasivo.**

### 8.1 Invito via email

**Checklist**

- [ ] Richiedere consenso esplicito prima dell'invio.
- [ ] Inviare nome gruppo e link.
- [ ] Evitare messaggi promozionali non richiesti.
- [ ] Registrare l'esito dell'invio senza dati superflui.
- [ ] Applicare limiti anti-abuso.
- [ ] Consentire la rimozione dell'indirizzo email.

Utilizzare l'email gia presente nel modello solo dopo consenso esplicito.

Prima versione:

- pulsante "Invia invito";
- email con nome gruppo e link;
- nessun messaggio promozionale;
- registrazione dell'esito di invio;
- limite anti-abuso;
- possibilita di rimuovere l'email.

### 8.2 Preferenze di notifica

**Checklist**

- [ ] Consentire di disattivare tutte le email.
- [ ] Configurare notifiche per nuove spese.
- [ ] Configurare notifiche per cambi di saldo.
- [ ] Configurare promemoria e chiusura gruppo.
- [ ] Rendere le preferenze visibili e modificabili.

Ogni partecipante deve poter scegliere:

- nessuna email;
- nuova spesa;
- modifica del saldo;
- promemoria pagamento;
- gruppo chiuso.

Le preferenze devono essere opt-in e visibili nella UI.

### 8.3 Token di invito

**Checklist**

- [ ] Separare token di lettura, collaborazione e gestione.
- [ ] Rendere i token revocabili.
- [ ] Aggiungere scadenza quando appropriato.
- [ ] Evitare token nei log applicativi.

Non usare l'UUID del gruppo come unico identificatore per tutti i casi futuri. Introdurre token separati per:

- invito di sola visualizzazione;
- invito collaborativo;
- gestione del gruppo;
- disiscrizione dalle notifiche.

I token devono essere revocabili e non devono essere mostrati nei log applicativi.

### 8.4 Digest invece di spam

**Checklist**

- [ ] Raggruppare modifiche ravvicinate.
- [ ] Inviare solo cambiamenti utili al destinatario.
- [ ] Mostrare il nuovo saldo nel digest.
- [ ] Consentire di disattivare il digest.

Per ridurre il numero di email, raggruppare piu modifiche in un digest. Esempio:

> Il gruppo "Casa condivisa" ha 3 nuove spese e il tuo saldo e cambiato di 12,40 €.

Inviare solo quando esiste un cambiamento utile per il destinatario.

---

## 9. Fase 5: PWA e connettivita debole

**Priorita: media**  
**Obiettivo: rendere Equa affidabile durante viaggi, cene e situazioni con rete instabile.**

### 9.1 Installazione PWA

**Checklist**

- [ ] Aggiungere manifest web app.
- [ ] Aggiungere icone e colori coerenti.
- [ ] Configurare service worker.
- [ ] Consentire apertura rapida dei gruppi recenti.

Aggiungere:

- manifest web app;
- icone e colori coerenti;
- service worker;
- installazione dalla home;
- apertura diretta degli ultimi gruppi.

### 9.2 Cache offline

**Checklist**

- [ ] Mostrare l'ultimo stato disponibile offline.
- [ ] Accodare una nuova spesa senza connessione.
- [ ] Sincronizzare al ritorno della rete.
- [ ] Mostrare lo stato di sincronizzazione.
- [ ] Confermare il salvataggio solo dopo risposta backend.

La prima versione deve consentire di:

- visualizzare l'ultimo stato caricato;
- compilare una nuova spesa offline;
- mettere la spesa in coda locale;
- sincronizzare quando torna la rete;
- mostrare chiaramente lo stato "in attesa di sincronizzazione".

Non dichiarare una spesa sincronizzata finche il backend non ha risposto con successo.

### 9.3 Conflitti di sincronizzazione

**Checklist**

- [ ] Aggiungere identificatore client alle operazioni offline.
- [ ] Aggiungere versione a gruppo o entita.
- [ ] Definire merge, rifiuto o revisione manuale.
- [ ] Mostrare chiaramente i conflitti all'utente.

Definire una strategia esplicita:

- rifiuto con richiesta di revisione;
- merge quando le entita sono diverse;
- versione del gruppo o dell'entita;
- schermata per scegliere quale dato mantenere.

La sincronizzazione offline non va introdotta prima di avere un identificatore client e una gestione delle versioni.

---

## 10. Fase 6: casi d'uso ricorrenti

**Priorita: media**  
**Obiettivo: estendere l'utilita oltre la singola vacanza o cena.**

### 10.1 Template di gruppo

**Checklist**

- [ ] Creare template vacanza e cena.
- [ ] Creare template regalo, casa e trasferta.
- [ ] Precompilare solo descrizione e suggerimenti utili.
- [ ] Verificare che i template non complichino la creazione libera.

Template iniziali:

- vacanza;
- cena;
- regalo di gruppo;
- casa condivisa;
- trasferta;
- attivita sportiva.

Un template deve solo precompilare descrizione, suggerimenti e impostazioni. Non deve aggiungere complessita al modello dati senza una necessita reale.

### 10.2 Spese ricorrenti

**Checklist**

- [ ] Aggiungere duplicazione rapida di una spesa.
- [ ] Suggerire la spesa precedente.
- [ ] Aggiungere data della spesa.
- [ ] Valutare regole settimanali e mensili.
- [ ] Consentire di saltare un periodo.
- [ ] Notificare prima della generazione automatica.

Supportare spese ripetute per:

- affitto;
- bollette;
- abbonamenti;
- quote settimanali o mensili.

Prima versione manuale:

- duplicazione rapida di una spesa;
- suggerimento della spesa precedente;
- data della spesa;
- nessun addebito automatico.

Seconda versione:

- regola ricorrente;
- generazione automatica;
- possibilita di saltare un periodo;
- notifica prima della creazione.

### 10.3 Date e periodi

**Checklist**

- [ ] Aggiungere data selezionabile alla spesa.
- [ ] Usare la data corrente come default.
- [ ] Ordinare cronologicamente le spese.
- [ ] Filtrare per periodo.
- [ ] Preparare riepiloghi mensili.

Aggiungere alle spese una data selezionabile, mantenendo come default la data corrente. Questo abilita:

- ordinamento cronologico reale;
- filtri per giorno o periodo;
- riepiloghi mensili;
- migliore ricostruzione del gruppo dopo settimane.

### 10.4 Esportazione

**Checklist**

- [ ] Esportare CSV.
- [ ] Generare riepilogo PDF.
- [ ] Generare testo pronto da condividere.
- [ ] Generare localmente quando possibile.
- [ ] Evitare invii automatici a servizi esterni.

Offrire esportazione volontaria in:

- CSV;
- PDF riepilogativo;
- testo pronto da condividere.

L'esportazione deve essere disponibile anche senza account e generata localmente quando possibile.

---

## 11. Fase 7: identita opzionale e dashboard personale

**Priorita: strategica, dopo la validazione del modello anonimo**  
**Obiettivo: recuperare i gruppi da piu dispositivi senza imporre un account a tutti.**

### 11.1 Account opzionale

**Checklist**

- [ ] Validare la domanda prima di introdurre account.
- [ ] Consentire recupero gruppi e sincronizzazione.
- [ ] Mantenere la creazione anonima.
- [ ] Rendere chiari i vantaggi dell'account.

L'account deve offrire vantaggi chiari:

- recupero dei gruppi;
- sincronizzazione tra dispositivi;
- preferenze di notifica;
- ruolo di amministratore;
- storico personale.

Non deve bloccare l'accesso a un gruppo condiviso.

### 11.2 Collegamento di un gruppo a un account

**Checklist**

- [ ] Collegare un gruppo anonimo con un'azione esplicita.
- [ ] Spiegare cosa cambia dopo il collegamento.
- [ ] Consentire di scollegare il gruppo.
- [ ] Gestire correttamente gruppi gia condivisi.

Un utente anonimo deve poter collegare un gruppo al proprio account con un'azione esplicita. Il sistema deve spiegare cosa cambia e consentire di scollegarlo.

### 11.3 Dashboard

**Checklist**

- [ ] Mostrare gruppi recenti, attivi e chiusi.
- [ ] Mostrare notifiche pendenti.
- [ ] Mostrare saldi solo quando il partecipante e associato.
- [ ] Evitare associazioni automatiche basate solo sul nome.

La dashboard personale puo mostrare:

- gruppi recenti;
- gruppi attivi;
- gruppi chiusi;
- saldo complessivo, solo se l'identita del partecipante e stata associata;
- notifiche pendenti.

Non mostrare un saldo personale dedotto solo dal nome del partecipante, per evitare associazioni errate.

### 11.4 Ruoli

**Checklist**

- [ ] Definire ruoli partecipante, collaboratore e amministratore.
- [ ] Implementare autorizzazioni lato backend.
- [ ] Testare ogni permesso indipendentemente dalla UI.
- [ ] Gestire cambio e revoca dei ruoli.

Ruoli minimi:

- partecipante;
- collaboratore;
- amministratore.

Le autorizzazioni devono essere esplicite e testate sul backend. La UI non e una misura di sicurezza.

---

## 12. Fase 8: pagamenti integrati

**Priorita: opzionale e da validare**  
**Obiettivo: aiutare a chiudere i conti senza trasformare Equa in una piattaforma finanziaria.**

**Checklist**

- [ ] Validare la domanda per i pagamenti integrati.
- [ ] Valutare deep link verso app di pagamento.
- [ ] Aggiungere copia di importo e causale.
- [ ] Aggiungere conferma manuale del pagamento.
- [ ] Completare analisi legale e di sicurezza.
- [ ] Evitare custodia di denaro e gestione diretta di carte o IBAN.

Possibili integrazioni:

- deep link verso app di pagamento;
- copia automatica di importo e causale;
- conferma manuale del pagamento;
- QR code del riepilogo;
- link a servizi gia usati dagli utenti.

Da evitare nella prima versione:

- custodia di denaro;
- gestione di carte o IBAN;
- commissioni obbligatorie;
- onboarding finanziario complesso;
- promessa di pagamento garantito.

Prima di procedere servono analisi legale, sicurezza, costi e domanda reale degli utenti.

---

## 13. Backlog tecnico trasversale

### Backend

**Checklist**

- [ ] Aggiungere test per gruppi, membri, spese, split e bilanci.
- [ ] Introdurre migrazioni database invece di affidarsi solo a `create_all`.
- [ ] Validare tutti gli input Pydantic con limiti e valori minimi.
- [ ] Aggiungere rate limiting agli endpoint pubblici.
- [ ] Uniformare gli error response.
- [ ] Aggiungere logging strutturato senza dati sensibili.
- [ ] Introdurre versioning o timestamp di aggiornamento per i gruppi.
- [ ] Preparare cancellazione e anonimizzazione dei dati.

### Frontend

**Checklist**

- [ ] Centralizzare toast, dialog e formattazione valuta.
- [ ] Centralizzare gli stati di rete.
- [ ] Aggiungere accessibilita a pulsanti icon-only, tab e form.
- [ ] Sostituire caratteri testuali come `X` con icone accessibili e label.
- [x] Evitare sovrapposizioni tra titoli lunghi e azioni nell'header del gruppo.
- [ ] Gestire focus dopo apertura e chiusura dei form.
- [ ] Aggiornare il titolo della pagina per ogni gruppo.
- [ ] Aggiungere test dei componenti e dei flussi principali.
- [ ] Verificare mobile a 320px, 375px, 768px e desktop.

### Operativita

**Checklist**

- [ ] Monitorare disponibilita API e database.
- [ ] Aggiungere health check che verifichi anche la connessione al database.
- [ ] Documentare backup e ripristino.
- [ ] Definire retention dei log.
- [ ] Verificare periodicamente i link condivisi e la gestione degli UUID.

---

## 14. Piano di rilascio consigliato

### Release A: Fondamenta

- [ ] Validazione completa degli split.
- [ ] Errori e retry uniformi.
- [ ] Formattazione valuta.
- [x] Test backend e frontend essenziali.
- [ ] Sicurezza minima del link.

**Risultato atteso:** meno errori e maggiore fiducia nel calcolo.

### Release B: Il gruppo si diffonde

- [x] Web Share API.
- [x] WhatsApp e clipboard.
- [ ] Telegram ed email.
- [ ] Anteprima e titolo dinamico.
- [x] Cronologia locale.
- [x] Link di ingresso piu chiaro.

**Risultato atteso:** piu aperture condivise e meno gruppi persi.

### Release C: Il gruppo si chiude

- [x] Selezione "chi sono".
- [x] Riepilogo personale.
- [ ] Promemoria condivisibili.
- [x] Riepilogo WhatsApp della chiusura.
- [x] Stato dei pagamenti.
- [x] Schermata di gruppo chiuso.
- [x] Spese in più valute con conversione tracciabile.

**Risultato atteso:** piu ritorni nei giorni successivi e meno pagamenti dimenticati.

### Release D: Collaborazione

- [ ] Refresh automatico.
- [ ] Storico attivita.
- [ ] Modifica completa dei partecipanti.
- [ ] Ricerca e filtri.

**Risultato atteso:** migliore uso multi-dispositivo e meno incomprensioni.

### Release E: Ritorno automatico

- [ ] Inviti email consensuali.
- [ ] Preferenze notifiche.
- [ ] Digest.
- [ ] Token di invito separati.

**Risultato atteso:** retention piu alta senza spam.

### Release F: Uso continuativo

- [ ] PWA.
- [ ] Cache offline.
- [ ] Spese ricorrenti.
- [ ] Template.
- [ ] Date ed esportazioni.

**Risultato atteso:** Equa diventa utile anche oltre l'evento occasionale.

### Release G: Account opzionali

- [ ] Account e dashboard.
- [ ] Collegamento dei gruppi.
- [ ] Ruoli.
- [ ] Recupero multi-dispositivo.

**Risultato atteso:** maggiore retention per utenti abituali, mantenendo l'ingresso anonimo.

---

## 15. Decisioni da validare prima dello sviluppo

Prima di iniziare ogni fase conviene rispondere a queste domande:

- [ ] Verificare se gli utenti perdono davvero i link.
- [ ] Misurare quale canale di condivisione genera piu aperture.
- [ ] Verificare se serve confermare i pagamenti dentro Equa.
- [ ] Validare l'utilita delle email rispetto al modello senza account.
- [ ] Testare la comprensibilita della selezione "chi sono".
- [ ] Verificare il valore della PWA rispetto al link mobile.
- [ ] Validare la domanda per le spese ricorrenti.
- [ ] Valutare se l'account opzionale aumenta davvero il valore.

Le risposte dovrebbero arrivare da feedback osservabili: conversazioni con utenti, richieste ricevute, dati aggregati e test dei flussi. Non introdurre un sistema di account o notifiche solo per imitare prodotti piu grandi.

---

## 16. Definizione di completamento di una feature

Una feature e pronta quando:

- [ ] Il comportamento principale e descritto in una user story.
- [ ] Gli errori e gli stati vuoti sono progettati.
- [ ] Il backend valida i dati indipendentemente dalla UI.
- [ ] Esistono test per il caso felice e per gli errori rilevanti.
- [ ] Il flusso e utilizzabile da mobile.
- [ ] Non introduce raccolta dati non necessaria.
- [ ] La documentazione API e aggiornata.
- [ ] Il changelog contiene una voce quando la modifica viene rilasciata.
- [ ] E stata verificata la compatibilita con i gruppi gia esistenti.

---

## 17. Sintesi delle priorita

| Priorita | Feature | Impatto UX | Retention | Crescita | Complessita |
|---|---|---:|---:|---:|---:|
| P0 | Validazione e affidabilita | Molto alto | Medio | Indiretto | Media |
| P1 | Condivisione mobile | Alto | Medio | Molto alto | Bassa |
| P1 | Cronologia locale | Alto | Alto | Basso | Bassa |
| P1 | Riepilogo personale | Molto alto | Alto | Medio | Media |
| P1 | Promemoria condivisibili | Alto | Alto | Medio | Bassa |
| P2 | Stato pagamenti | Molto alto | Molto alto | Basso | Media |
| P2 | Refresh e storico attivita | Alto | Alto | Basso | Media |
| P2 | Inviti e notifiche consensuali | Medio | Molto alto | Alto | Alta |
| P3 | PWA e offline | Medio | Medio | Basso | Alta |
| P3 | Spese ricorrenti | Alto | Molto alto | Medio | Alta |
| P4 | Account opzionali | Medio | Molto alto | Medio | Molto alta |
| P4 | Pagamenti integrati | Variabile | Variabile | Medio | Molto alta |

### Direzione raccomandata

La sequenza con il miglior rapporto valore/complessita e:

**condivisione migliore -> cronologia locale -> riepilogo personale -> stato dei pagamenti -> notifiche consensuali -> PWA e spese ricorrenti -> account opzionali**.

Questa direzione conserva il vantaggio competitivo di Equa, migliora il flusso principale e costruisce la retention attorno a un bisogno reale: sapere chi deve cosa e arrivare davvero alla chiusura dei conti.
