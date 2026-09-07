# Conserva il link via email

Funzione facoltativa e disattivata per default. Il gruppo resta utilizzabile senza email anche se il microservizio non risponde. Non crea account, proprietari, newsletter, rubriche, inviti a terzi o promemoria automatici.

## Esperienza

1. Nel pannello di condivisione compare «Conserva via email» solo quando il backend è configurato. Si può ignorare e continuare subito al gruppo.
2. La persona inserisce il proprio indirizzo, consulta l'informativa e richiede un codice. La prima email non contiene link o dati del gruppo.
3. Il codice a sei cifre va inserito nella stessa pagina entro 15 minuti insieme al token restituito a quel browser.
4. Dopo la verifica il microservizio invia il link collaborativo. La richiesta viene consumata prima dell'invio, quindi non è riutilizzabile. Non ci sono retry automatici.
5. «Per ora no», cambio email o chiusura del pannello annullano la richiesta pendente quando la rete è disponibile.

Il link apre lo stato corrente del gruppo e non è un backup. Chi lo possiede può leggere e collaborare come prima; verificare l'email non assegna identità, ruoli o privilegi. A conti chiusi tutti vedono le azioni per creare un nuovo gruppo e consigliare la sola homepage pubblica di Equa, senza UUID o dati del gruppo.

## Architettura e ordine di rilascio

Il backend Equa gestisce consenso, codice, scadenza, tentativi, consumo singolo e limiti persistenti. Invia al microservizio soltanto uno dei due payload ammessi: `verification` con email e codice oppure `group_link` con email e UUID. Subject, testo e URL sono costruiti dal microservizio, perciò Equa non può usarlo come relay generico.

Il microservizio è condiviso con un altro applicativo. Distribuire in quest'ordine:

1. sul branch dedicato di `python-email-service`, eseguire tutti i test legacy e nuovi;
2. configurare `EQUA_TOKEN`, `EQUA_PUBLIC_URL` ed `EQUA_PRIVACY_URL` nel microservizio e distribuirlo senza modificare `AI_ASSISTANT_TOKEN` e `RECEIVER` dell'altro applicativo;
3. verificare `/health` e i due endpoint storici in staging;
4. applicare `005_email_link_challenges.sql` dopo la migrazione multi-valuta `004`;
5. configurare e distribuire backend e frontend Equa;
6. attivare `EMAIL_LINK_ENABLED=true` solo dopo uno smoke test completo.

Non sono necessarie nuove dipendenze Python in Equa.

## Configurazione backend Equa

| Variabile | Significato |
| --- | --- |
| `EMAIL_LINK_ENABLED` | `true` per abilitare; default `false`. |
| `EMAIL_LINK_SECRET` | Segreto casuale di almeno 32 caratteri, uguale su tutti i worker; cifra i token temporanei e firma i contatori. |
| `EMAIL_SERVICE_URL` | URL base del microservizio, senza `/forward-email-equa`. HTTPS obbligatorio salvo localhost. |
| `EMAIL_SERVICE_TOKEN` | Token dedicato di almeno 32 caratteri; deve coincidere con `EQUA_TOKEN` del microservizio. |
| `EMAIL_SERVICE_TIMEOUT` | Timeout in secondi, da 1 a 30; default `10`. |
| `EMAIL_SERVICE_ALLOW_HTTP` | Opt-in per HTTP su una rete interna fidata; default `false`. Preferire HTTPS anche in LAN. |
| `EMAIL_PRIVACY_URL` | URL HTTPS dell'informativa mostrata dalla UI. Obbligatorio. |

Generare separatamente `EMAIL_LINK_SECRET` e `EMAIL_SERVICE_TOKEN`, ad esempio con `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Non commetterli. La rotazione del primo invalida le richieste esistenti e cambia le chiavi dei contatori; la rotazione del secondo va coordinata con il microservizio.

Il client non segue redirect, ignora i proxy ereditati dall'ambiente per non inoltrare il Bearer token e accetta solo la risposta esatta di successo del servizio. Con configurazione assente o non valida, `GET /email-link/options` restituisce `enabled: false`; gli invii diretti rispondono `503`, senza impedire il normale uso dei gruppi.

## Dati e pulizia

- Nessun indirizzo email viene scritto nelle nuove tabelle, aggiunto ai membri, restituito dalla GET gruppo o scritto nello storage del browser.
- Durante la verifica il recapito è in un token Fernet cifrato e autenticato, mantenuto solo in memoria nella pagina e trasmesso nei body HTTPS. Non mettere token o codici in URL, log, analytics o error reporting.
- `email_link_challenges` contiene hash del token, UUID del gruppo, hash HMAC del codice, tentativi e scadenza.
- `email_link_rate_limits` contiene chiavi HMAC, contatori e scadenze, senza IP o email in chiaro. Sono dati pseudonimi, non anonimi.
- La validità è sempre controllata dal server. Programmare ogni 15 minuti, con lo stesso ambiente DB del backend: `python -m backend.app.cleanup_email_links`.

Il comando rimuove solo record scaduti e non contatta il microservizio. Il microservizio, il provider SMTP e la casella del destinatario trattano necessariamente recapito e contenuto delle due email; conservazione e responsabili vanno descritti nell'informativa. Non abilitare log di body, debug SMTP, tracking di aperture/click, riscrittura link o iscrizioni automatiche.

## Limiti e protezioni

Finestre fisse UTC condivise nel database:

- destinatario, senza distinzione maiuscole/minuscole: 1 richiesta/minuto, 3/ora e 5/giorno;
- IP: 10/minuto e 30/ora;
- gruppo: 10/ora;
- servizio: 200/ora;
- verifica: massimo 5 tentativi entro 15 minuti e un solo utilizzo.

Gli invii falliti consumano il limite. Ogni richiesta può generare al massimo due email. Il backend restituisce `429` con `Retry-After`. Dietro proxy, configurare Uvicorn perché si fidi soltanto dei propri proxy; non fidarsi indiscriminatamente di `X-Forwarded-For`. Aggiungere quote sul reverse proxy e sul provider.

## Verifica del rilascio

- Equa: `python -m pytest backend/tests`, `npm --prefix frontend run test:run`, `npm --prefix frontend run build`.
- Microservizio: `python -m unittest discover -s tests -v`; i test simulano SMTP e includono i contratti dell'altro applicativo.
- Staging: migrazione e rollback MySQL, token errato, codice errato/scaduto, perdita di rete, invio reale verso una casella controllata e job di pulizia.
- UI: controllare mobile, tastiera e focus; «Consiglia Equa» deve condividere la homepage, «Condividi» il gruppo previsto.

I test locali non certificano consegna reale, configurazione del provider, migrazione MySQL o adeguatezza giuridica dell'informativa.
