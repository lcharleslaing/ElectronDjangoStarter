## Django + Electron Starter (Tailwind + DaisyUI)

Traditional Django project with Electron desktop wrapper. Includes auth, preferences, projects CRUD, and a full DaisyUI theme switcher.

### Prerequisites
- Python 3.11+
- Node.js 20+
- pip, npm

### Setup
1. Copy env
```
cp .env.example .env
```
2. Setup Django
```
cd backend && python -m venv .venv && \
  (. .venv/bin/activate || source .venv/Scripts/activate) && \
  pip install -r requirements.txt && \
  python manage.py migrate
```
3. Build CSS (optional, for development)
```
cd backend/static/js && npm i && npm run build
```
4. Install Electron deps
```
cd ../electron && npm i
```

### Run (Desktop Dev)
From `electron/`:
```
npm run dev
```
This runs Django and starts Electron once `/api/health` is ready.

### Run (Web Dev)
From `backend/`:
```
python manage.py runserver
```
Visit http://127.0.0.1:8000

### Build Desktop App
From `electron/`:
```
npm run pack
```
Uses electron-builder. Relies on system Python to run Django.

### Environment
See `.env.example`. `OPENAI_API_KEY` is optional and server-side only.

### Structure
- `backend/` Traditional Django project (apps, templates, static)
- `electron/` Electron TS app (spawns Django, opens window)

### Security
- CSRF enabled, HTTPOnly session cookie, env via `python-dotenv`

### License
MIT
