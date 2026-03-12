# CommercePilot Full Stack

Starter full-stack project for a conversational payments agent.

## Stack

- Frontend: React + TypeScript + Vite + shadcn-style components
- Backend: FastAPI
- API flow: Frontend chat UI -> FastAPI `/agent/chat` -> tool handler

## Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment

Frontend `.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Backend `.env`:

```env
APP_ENV=dev
PINE_LABS_BASE_URL=https://sandbox.example.com
PINE_LABS_API_KEY=demo-key
```
