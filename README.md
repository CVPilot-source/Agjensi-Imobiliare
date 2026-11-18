# AlbEstate DEMO — Faqe Demo për Agjenci Pasurish të Paluajtshme

Një aplikacion web demo, **mobile-first** (i përshtatur për telefon dhe desktop), i ndërtuar me **Python Flask** dhe **Google Gemini API** (`google-genai`).

> ⚠️ **Shënim i Rëndësishëm:** Të gjitha pronat dhe çmimet në këtë aplikacion janë **LISTIME SHEMBULL (DEMO)** fiktive vetëm për qëllime demonstrimi dhe testimi. Asistenti AI është i udhëzuar të mos shpikë prona apo çmime jashtë katalogut shembull.

---

## ✨ Veçoritë Kryesore

1. **Dizajn Mobile-First (Për Telefon):**
   - Shirit i sipërm paralajmërues që sqaron se faqja është DEMO.
   - Kartela pronash të optimizuara për ekranet e telefonave dhe meny e poshtme e shpejtë (`sticky bottom nav`).
2. **Listime Shembull & Filtrim Dinamik:**
   - 6 listime shembull të etiketuara qartë me distinktivin `LISTIM SHEMBULL / DEMO` dhe `[SHEMBULL DEMO]`.
   - Filtër i menjëhershëm sipas **Qytetit**, **Llojit të Pronës** dhe **Buxhetit Maksimal (€)** përmes endpoint-it `/api/properties`.
3. **Asistent Virtual AI me Google Gemini (`gemini-2.5-flash`):**
   - Pyet vizitorin për **buxhetin**, **zonën/qytetin** dhe nëse kërkon të **blejë apo të marrë me qira**.
   - Lexon çelësin API **vetëm** nga variabla e mjedisit `GEMINI_API_KEY`.
   - Nuk shpik prona apo çmime: sugjeron vetëm listimet shembull nga katalogu.
   - Ka modalitet rezervë (fallback) nëse `GEMINI_API_KEY` nuk është konfiguruar ende gjatë testimit lokal.
4. **Formular Kontakti & Ruajtje e Lead-eve në Databazë SQLite (`leads.db`):**
   - Çdo kërkesë kontakti ruhet në tabelën `leads` në databazën SQLite (`leads.db`) përmes endpoint-it `POST /api/leads`.
   - Mundësi për të kopjuar kriteret nga biseda me AI direkt te formulari i kontaktit.

---

## 📁 Struktura e Projektit

```text
agjenci-imobiliare-demo/
├── app.py                 # Serveri Flask, API e filtrimit, Gemini AI chat & SQLite DB
├── templates/
│   └── index.html         # Ndërfaqja Mobile-First (HTML5/CSS3/JS)
├── requirements.txt       # Paketa Python (Flask, gunicorn, google-genai)
├── Procfile               # Konfigurimi i nisjes me Gunicorn
├── render.yaml            # Blueprint për publikim të automatizuar në Render
├── .env.example           # Shembull për variablat e mjedisit
└── README.md              # Dokumentacioni dhe udhëzimet për Render
```

---

## 🚀 Si ta Nisni Lokalisht

1. **Krijoni dhe aktivizoni mjedisin virtual:**
   ```bash
   python -m venv .venv
   # Në Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   # Në macOS / Linux:
   source .venv/bin/activate
   ```

2. **Instaloni varësitë:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Vendosni çelësin `GEMINI_API_KEY` në variablën e mjedisit:**
   ```bash
   # Në Windows PowerShell:
   $env:GEMINI_API_KEY="celesi_juaj_nga_google_ai_studio"

   # Në Linux / macOS:
   export GEMINI_API_KEY="celesi_juaj_nga_google_ai_studio"
   ```

4. **Niseni me Flask ose me Gunicorn:**
   ```bash
   # Me Flask:
   python app.py

   # Me Gunicorn (në Linux/macOS/Render; në Windows mbështetet nga gunicorn >= 23/27 ose përmes Render):
   gunicorn app:app --bind 0.0.0.0:5000
   ```
   Pastaj hapni `http://127.0.0.1:5000` në shfletues.

---

## ☁️ Udhëzime për Publikim në Render (Deployment Guide)

Ky projekt është gati për t'u publikuar në [Render](https://render.com/) si një **Web Service** që niset me `gunicorn`.

### Hapi 1: Ngarkoni Kodin në GitHub / GitLab
1. Krijoni një repository të ri në GitHub.
2. Ngarkoni skedarët e projektit (`app.py`, `templates/index.html`, `requirements.txt`, `Procfile`, `render.yaml`, `README.md`).
   *(Mos ngarkoni kurrë skedarë `.env` me çelësa realë!)*

### Hapi 2: Krijoni Shërbimin në Render
Mund ta publikoni në dy mënyra:

#### Opsioni A: Manualisht si Web Service
1. Hyni në [Render Dashboard](https://dashboard.render.com/) dhe klikoni **New +** -> **Web Service**.
2. Lidhni repository-n tuaj të GitHub.
3. Plotësoni fushat kryesore:
   - **Name:** `agjenci-imobiliare-demo`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     gunicorn app:app --bind 0.0.0.0:$PORT
     ```
4. Shkoni te seksioni **Environment Variables** dhe shtoni:
   - **Key:** `GEMINI_API_KEY`
   - **Value:** *(Ngjisni çelësin tuaj të Google Gemini API)*
5. Klikoni **Create Web Service**.

#### Opsioni B: Përmes `render.yaml` (Blueprint)
1. Në Render Dashboard klikoni **New +** -> **Blueprint**.
2. Zgjidhni repository-n që përmban skedarin `render.yaml`.
3. Render do të lexojë automatikisht `buildCommand` (`pip install -r requirements.txt`) dhe `startCommand` (`gunicorn app:app --bind 0.0.0.0:$PORT`) dhe do t'ju kërkojë të plotësoni vlerën e variablës `GEMINI_API_KEY`.
