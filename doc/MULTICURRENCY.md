# Spese e bilanci multi-valuta

## Comportamento

Come partecipante a un viaggio, posso registrare una spesa nella valuta in cui è stata pagata, vedere i debiti separati per valuta e, quando serve, unificarli nella valuta di default del gruppo usando cambi salvati e verificabili.

- La valuta del gruppo è la **valuta di default**: viene preselezionata sulle nuove spese e usata nel bilancio unificato.
- Importi e quote delle spese restano sempre nella valuta originale. I totali non sommano mai valute diverse.
- La data della spesa parte da oggi ma può essere corretta per una ricevuta inserita in ritardo.
- Per una spesa in valuta diversa, Equa suggerisce un cambio storico di riferimento relativo alla data della spesa. La data del tasso può essere precedente, ad esempio nei giorni senza pubblicazione.
- Il cambio significa sempre **1 unità della valuta della spesa = X unità della valuta di default**. È visibile nei dettagli, insieme al controvalore e alla fonte, e può essere sostituito con un valore manuale.
- Non esiste un selettore tra cambio corrente, storico e medio: la regola automatica è unica. La correzione manuale serve anche per riportare il cambio realmente applicato al pagamento.

## Cambi salvati, non ricalcolati alla lettura

Il backend salva il tasso su ogni spesa. Modificare la descrizione, il pagante, l'importo o la suddivisione non recupera un nuovo cambio quando data e valuta sono invariate. Cambiare valuta o data invalida il precedente tasso; un aggiornamento esplicito del cambio automatico può essere richiesto dai dettagli. Un tasso manuale fornito nella richiesta prevale sull'automatismo.

Leggere gruppi, bilanci e pagamenti non chiama il provider. Non vengono ricalcolati retroattivamente i cambi delle spese, né viene applicata una media tra i tassi.

Se il provider non risponde o non dispone di un tasso per la data richiesta, la spesa viene comunque salvata in valuta originale con cambio mancante. I bilanci separati restano disponibili; quello unificato richiede prima di completare tutti i cambi, senza mostrare totali parziali come completi. Non viene introdotto un salvataggio offline del gruppo: serve comunque il backend Equa.

## Bilanci e chiusura

La vista iniziale è **Per valuta**. Per un gruppo con spese in altre valute, **Unifica in [valuta di default]** mostra i saldi ottenuti usando i tassi salvati sulle singole spese.

La chiusura usa la modalità visualizzata e confermata dall'utente:

- separata: pagamenti distinti per valuta, senza richiedere i cambi;
- unificata: pagamenti nella valuta di default; viene rifiutata se una spesa non ha il cambio.

I pagamenti salvano la propria valuta e il gruppo salva la modalità di chiusura. Spese, tassi e partecipanti non sono modificabili durante la chiusura. I riepiloghi condivisi usano i pagamenti persistiti; per correggere i conti bisogna riaprire esplicitamente il gruppo, annullando i pagamenti del ciclo precedente secondo il flusso esistente.

Il calcolo backend usa `Decimal` e l'unità minima della valuta. Il resto viene distribuito in modo deterministico, mantenendo la somma delle quote uguale al totale; non vengono generati pagamenti di importo zero. JPY, KRW, VND, CLP e ISK non accettano frazioni nelle nuove spese.

## Contratto API

Gli importi decimali nelle risposte sono stringhe JSON. I campi esistenti `amount` e `share_amount` rappresentano gli importi **originali**, non quelli convertiti.

### Spese

Tutti gli endpoint di creazione e modifica accettano, oltre ai campi precedenti:

- `currency`: codice del catalogo supportato; in creazione, se omesso, usa la valuta del gruppo;
- `expense_date`: data ISO `YYYY-MM-DD`, non futura; in creazione il default è oggi;
- `exchange_rate`: tasso manuale positivo, finito e nei limiti accettati dal backend;
- `refresh_exchange_rate`: richiede esplicitamente un nuovo suggerimento automatico.

In modifica, l'omissione di valuta e data conserva i valori della spesa. Omettere il tasso conserva quello salvato quando valuta e data non cambiano.

Le risposte aggiungono `currency`, `expense_date`, `exchange_rate`, `exchange_rate_date`, `exchange_rate_source` (`identity`, `frankfurter`, `manual`, oppure `null`) e `converted_amount`. Per spese nella valuta di default il tasso è `1`; per un cambio mancante, tasso e controvalore sono `null`.

### Suggerimento di cambio

`GET /groups/{group_id}/exchange-rate?currency=ALL&expense_date=2026-09-03`

Risposta: `{currency, target_currency, rate, date, source}`. È una lettura, non salva o aggiorna spese. Un errore è recuperabile inserendo un cambio manuale oppure salvando senza cambio.

### Bilanci e pagamenti

- `GET /groups/{group_id}/balances/?mode=separate` è il default; `mode=unified` usa esclusivamente i tassi salvati. Ogni transazione include `currency`.
- `PATCH /groups/{group_id}/status` con `status: "closing"` accetta `balance_mode: "separate" | "unified"`; se omesso, usa `separate`.
- Il gruppo espone `closing_balance_mode`; ogni settlement espone `currency`.
- La documentazione OpenAPI generata dal backend descrive i vincoli aggiornati.

## Provider e privacy

Il backend usa [Frankfurter v2](https://frankfurter.dev/) e il suo [endpoint storico documentato](https://api.frankfurter.dev/v2/openapi.json): `GET /v2/rate/{currency}/{target_currency}?date={expense_date}`. Il servizio pubblica tassi giornalieri di riferimento, non i cambi o le commissioni effettivamente applicati dalle carte. Non richiede credenziali; la disponibilità del servizio pubblico non è garantita.

Il provider riceve soltanto coppia di valute e data dal server Equa: non riceve UUID del gruppo, nomi, partecipanti, importi, descrizioni, email o IP del browser. Non vengono aggiunti analytics né dati finanziari al salvataggio locale dei gruppi recenti.

## Rilascio e verifiche

La migrazione numerata `004` aggiunge e inizializza le nuove colonne; eseguirla dopo `001`, `002` e `003`, prima del backend aggiornato. Le spese e i pagamenti precedenti mantengono importi e valuta del proprio gruppo. Consultare [le istruzioni di migrazione e rollback](../backend/migrations/README.md) prima di operare su un database esistente.

I test coprono tassi mancanti e manuali, conservazione del cambio, arrotondamenti, valute senza centesimi, chiusura separata/unificata, errori del provider e riepiloghi per valuta. Le suite usano dati isolati e risposte di cambio simulate; non eseguono migrazioni su MySQL né verificano automaticamente il servizio esterno in produzione.
