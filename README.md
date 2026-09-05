<div align="center">
  <h1 align="center"><img src="frontend/src/assets/equa-logo.svg" width="56" height="56" align="absmiddle" alt="Equa"> equa</h1>
  <p align="center"><strong>Dividi le spese, non le amicizie.</strong></p>
  <p align="center">
    <a href="http://equa.fatjonfreskina.com/"><strong>Prova Equa online →</strong></a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Senza_account-16a34a?style=flat-square" alt="Senza account">
    <img src="https://img.shields.io/badge/Privacy_first-16a34a?style=flat-square" alt="Privacy first">
    <img src="https://img.shields.io/badge/Gratis_per_sempre-16a34a?style=flat-square" alt="Gratis per sempre">
  </p>
</div>

Equa è un'app italiana per dividere le spese di una vacanza, una cena o una casa condivisa. Crea un gruppo, condividi un link e lasciate che Equa calcoli chi deve cosa a chi — senza registrazione, abbonamenti o pubblicità.

## Perché usarla

| Vantaggio | Descrizione |
|---|---|
| 🔗 **Un link, tutto il gruppo** | Chi riceve il link può vedere e collaborare subito. |
| ⚖️ **Conti semplici** | Split equi, per sottoinsieme o personalizzati; meno pagamenti possibili per pareggiare. |
| 📱 **Pensata per il telefono** | Condivisione WhatsApp, copia link e gruppi recenti salvati sul dispositivo. |
| ✅ **Chiudete davvero i conti** | Blocca il gruppo quando finite, segnala i pagamenti e conferma le ricezioni. |

## Inizia in pochi secondi

1. Crea un gruppo e aggiungi almeno due partecipanti.
2. Condividi il link nella chat della vacanza o della cena.
3. Inserite le spese man mano che arrivano.
4. Aprite **Bilanci** per sapere subito chi deve pagare chi.
5. A fine evento, avviate **Chiudiamo i conti** e confermate i pagamenti.

> Il link è la chiave del gruppo: condividilo e conservalo. Equa salva i gruppi recenti solo sul dispositivo, ma questa cronologia non è un backup.

## Sviluppo locale

### Prerequisiti

- Node.js 20+
- Python 3.12+
- MySQL 8+

### 1. Database e backend

Crea un database MySQL e il file `backend/.env`:

```env
DB_USER=equa
DB_PASS=la-tua-password
HOST_NAME=localhost
HOST_PORT=3306
DB_NAME=equa
SECRET_KEY=una-stringa-random-lunga
ALLOW_ORIGINS=http://localhost:5173
```

Poi avvia l’API:

```bash
cd backend
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows PowerShell
# .\venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API e documentazione: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend

In un secondo terminale:

```bash
cd frontend
npm install
npm run dev
```

App locale: [http://localhost:5173](http://localhost:5173)

### 3. Test e controlli

```bash
# Backend, dalla root del repository
pip install -r backend/requirements-dev.txt
python -m pytest backend/tests

# Frontend
cd frontend
npm run test:run
npm run build
```

Per attivare i controlli automatici prima di ogni commit:

```bash
python -m pre_commit install
```

## Migrazioni database

`Base.metadata.create_all()` crea le tabelle mancanti, ma non modifica quelle già esistenti. Prima di distribuire una nuova versione su un database già in uso, esegui le migrazioni SQL in [`backend/migrations/`](backend/migrations/README.md) nell’ordine indicato.

## Stack

Vue 3 · TypeScript · Vite · Tailwind CSS · FastAPI · SQLAlchemy · MySQL

## Documentazione

- [Roadmap di prodotto](doc/ROADMAP.md)
- [Changelog](doc/CHANGELOG.md)
- [Strategia e comandi di test](doc/TESTING.md)
- [Spese, cambi e bilanci multi-valuta](doc/MULTICURRENCY.md)
- [Migrazioni database](backend/migrations/README.md)
- [Metriche anonime](doc/ANALYTICS.md)

## Supporta Equa

Equa è gratuita e open source. Se ti ha evitato una discussione sui conti, puoi offrirci un caffè.

[![Offrimi un caffè su PayPal](https://img.shields.io/badge/PayPal-Offrimi_un_caffè-00457C?style=for-the-badge&logo=paypal)](https://paypal.me/fatjonfreskina)

## Licenza

MIT — usala, adattala e migliorala. I contributi sono benvenuti.
