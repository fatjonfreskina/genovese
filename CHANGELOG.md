# Changelog

Tutte le modifiche rilevanti al progetto sono documentate in questo file.

Il formato segue [Keep a Changelog](https://keepachangelog.com/it/1.0.0/).
Il versionamento segue [Semantic Versioning](https://semver.org/lang/it/).

---

## [1.1.0] - 2026-04-19

### Aggiunto

- Totale spese in tempo reale nella vista gruppo
- Modifica spese già inserite (click su una spesa per aprire il form precompilato)
- Rimozione partecipanti dal gruppo (solo se non coinvolti in nessuna spesa)
- Nuovo endpoint `PUT /groups/{group_id}/expenses/{expense_id}`
- Nuovo endpoint `DELETE /groups/{group_id}/members/{member_id}`

---

## [1.0.0] - 2026-04-08

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