# Migrazioni database

Prima di distribuire una versione che usa nuove colonne, esegui ogni file SQL una sola volta sul database di destinazione, nell'ordine numerico.

Per la chiusura dei conti, esegui `001_add_group_status.sql`, `002_create_settlements.sql` e `003_add_group_closing_count.sql` prima di distribuire il backend aggiornato. Le nuove installazioni ricevono le tabelle direttamente da SQLAlchemy durante l'avvio.

I rollback corrispondenti devono essere eseguiti in ordine inverso (`003`, `002`, `001`). Il rollback `002` elimina la tabella dei pagamenti e i relativi dati; eseguilo prima di rimuovere con `001` la colonna di stato.

La migrazione `003` inizializza a `1` i gruppi per cui esistono prove di una chiusura precedente (stato `closing`/`closed` o settlement). I dati precedenti non permettono di ricostruire più cicli storici con precisione. Il rollback rimuove la colonna e il relativo conteggio.

## Multi-valuta (004)

Esegui `004_add_multi_currency.sql` dopo `001`, `002`, `003`, con un backup e prima del deploy del nuovo backend. Ferma le scritture durante migrazione e deploy: MySQL può eseguire commit impliciti delle istruzioni DDL e `create_all()` non aggiorna tabelle esistenti.

La migrazione conserva tutti gli importi precedenti: assegna alle spese e ai pagamenti la valuta del gruppo, ricava la data spesa da `created_at` (data corrente solo se mancante), e registra sulle spese cambio identità `1` con fonte `identity`. La modalità di chiusura preesistente resta `separate`. Le nuove installazioni creano direttamente le nuove colonne tramite SQLAlchemy.

I nuovi campi salvano valuta/data originali, cambio per unità di valuta originale verso quella del gruppo, data effettiva del tasso e fonte (`identity`, `frankfurter`, `manual`). Un cambio mancante è `NULL`: i bilanci separati funzionano, quelli unificati richiedono di completarlo. Le spese in valuta del gruppo hanno sempre cambio `1`. In chiusura le spese sono bloccate e i pagamenti conservano la propria valuta; non si recuperano nuovi tassi durante il calcolo dei saldi.

Il recupero automatico richiede HTTPS in uscita verso `api.frankfurter.dev` (Frankfurter v2), senza chiavi API. Vengono trasmesse solo coppia di valute e data, mai ID del gruppo, partecipanti o importi. La data restituita può precedere la data spesa (weekend/festivi). Un timeout o una coppia/data non disponibile non impediscono il salvataggio della spesa; il cambio può essere completato manualmente. Non è richiesta alcuna nuova variabile d'ambiente.

Il rollback `004_add_multi_currency_rollback.sql` va eseguito prima di `003`, a scritture ferme e con un client MySQL che supporti `DELIMITER`, senza `--force`. È consentito solo se spese e pagamenti restano nella valuta del gruppo e tutti i cambi sono identità. Il controllo interrompe il rollback quando il vecchio backend reinterpretarebbe dati multi-valuta. In quel caso non cancellare né riconvertire automaticamente gli originali: mantieni il backend compatibile oppure ripristina un backup precedente con una procedura concordata. Il rollback consentito rimuove comunque le date spesa e i metadati dei cambi; conserva prima un backup. Se il controllo blocca l'esecuzione, la procedura `equa_rollback_004` può restare nel database: rimuovi solo tale procedura prima di un eventuale nuovo tentativo.

Questi script devono essere verificati sul MySQL di destinazione/staging; i test applicativi SQLite non sostituiscono una prova di migrazione o rollback MySQL.

Le frazioni eventualmente presenti in importi storici di valute ora trattate senza decimali (JPY, KRW, VND, CLP, ISK) non vengono arrotondate dalla migrazione e rimangono esatte nei saldi separati. Le nuove spese e le modifiche agli importi devono rispettare i decimali della valuta. La data spesa è una data di calendario: il client propone oggi nel fuso locale; il backend ammette al massimo domani rispetto a UTC per non rifiutare l'oggi dei client con fuso in anticipo. Il tasso automatico non può mai essere datato dopo la data spesa richiesta.
