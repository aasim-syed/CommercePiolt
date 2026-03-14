# CommercePilot

CommercePilot is a conversational payments operations assistant built for a hackathon demo. It combines a React operator console, a FastAPI orchestration backend, Pine Labs / Plural integration, session-aware payment state, and a judge-friendly control surface for payment lifecycle workflows.

## What It Does

CommercePilot is centered on three merchant operations:

- Create payment link
- Check payment status
- Get reserve balance

The product goal is to reduce dashboard hopping and let operators manage payment tasks through one conversational workflow.

## Live vs Demo

Current project state is intentionally hybrid:

- Live:
  - Pine Labs / Plural token flow
  - Create payment link flow
  - Backend orchestration contract
  - Session-aware payment state
- Demo / controlled fallback:
  - Reserve balance can be stubbed for reliability
  - Webhook-style status transitions can be manually triggered for the demo
- Partial / environment-dependent:
  - Bedrock model invocation depends on account/model access
  - Pine Labs status and payouts surfaces depend on environment behavior

## Stack

- Frontend: React + TypeScript + Vite
- Backend: FastAPI
- LLM path: AWS Bedrock
- Payments: Pine Labs / Plural
- Hosting target: frontend static hosting + backend container / EC2

## Architecture

```text
Frontend UI
  -> /agent/chat
  -> FastAPI agent orchestration
  -> Pine Labs provider adapter
  -> session state + status controls
```

Stable backend response shape:

```json
{
  "reply": "...",
  "tool_called": {},
  "data": {},
  "session_state": {}
}
```

This contract is intentionally kept stable so provider internals can change without breaking the UI.

## Demo Flow

Recommended judge flow:

1. Ask for reserve balance
2. Create payment link for `1200`
3. Show payment URL and payment ref
4. Check payment status
5. Trigger / reflect status transition

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment

### Frontend

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### Backend

Expected categories:

- app settings
- Pine Labs / Plural auth
- optional payouts host
- AWS Bedrock settings
- CORS origins

Do not commit real secrets.

## Deployment Shape

Current simplest deployment path:

- Frontend: static hosting
- Backend: Docker container on EC2

Frontend should be built with:

```env
VITE_API_BASE_URL=http://<backend-public-ip>:8000
```

## Why This Is Interesting

This is not just a chatbot over a payment API.

CommercePilot combines:

- natural-language payment operations
- session memory across turns
- provider-adapter architecture
- controlled event/status simulation
- operator-visible system readiness

That makes the demo feel like a product surface, not a thin integration wrapper.

## Next Phase Vision

- Payment Mood Engine
- Merchant Voice Ledger
- Dead Cart Resurrection
- Split-Pay Arbitration

## Repo Notes

- `frontend/` contains the operator console
- `backend/` contains the FastAPI agent and provider adapters
- `SUPERMEMORY.md` contains the running build/debug history and handoff context
