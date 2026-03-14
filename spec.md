# CommercePilot 2-Hour End-to-End Build Spec

## Goal
Ship a working demo where a user can chat in the frontend, the backend uses AWS Bedrock for intent + response generation, Pine Labs API for payment actions, and AWS for config, hosting support, and observability.

## Demo Scope
Implement only these 3 flows end to end:

1. Create payment link
2. Check payment status
3. Get merchant reserve balance

Everything else is explicitly out of scope for this 2-hour push.

## Success Criteria

- Frontend can send chat messages and render assistant replies
- Backend can classify intent and extract tool args using AWS Bedrock
- Backend can call Pine Labs sandbox APIs for:
  - create payment link
  - payment status
  - reserve balance
- Session context works across turns
- Errors are user-friendly
- Webhook/status update path works for demo
- App can run locally with `.env`

## Architecture

- Frontend: React + Vite single chat page
- Backend: FastAPI
- LLM: AWS Bedrock runtime
- Payments: Pine Labs sandbox APIs
- AWS services:
  - Bedrock Runtime for model inference
  - IAM user/role with Bedrock access
  - CloudWatch-compatible structured logs via backend logging
  - Optional Secrets Manager later, but `.env` for this sprint

## Required Env Vars

Backend:

```env
APP_ENV=dev
USE_MOCK_PINE_LABS=false
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
PINE_LABS_BASE_URL=
PINE_LABS_API_KEY=
PINE_LABS_MERCHANT_ID=
PINE_LABS_WEBHOOK_SECRET=
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Frontend:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## API Contracts

### Frontend -> Backend
`POST /agent/chat`

Request:

```json
{
  "message": "create payment link for 1200",
  "session_id": "s1",
  "merchant_id": "m123"
}
```

Response:

```json
{
  "reply": "Created payment link for Rs 1200.",
  "tool_called": {
    "tool_name": "create_payment_link",
    "arguments": {
      "amount": 1200,
      "merchant_id": "m123"
    }
  },
  "data": {},
  "session_state": {}
}
```

### Pine Labs -> Backend
`POST /webhooks/pine-labs`

Purpose:
- update stored payment status
- make follow-up status checks accurate

## Bedrock Responsibilities

Bedrock does only 2 things:

1. Detect intent:
   - `create_payment_link`
   - `check_payment_status`
   - `get_reserve_balance`
   - `none`
2. Extract missing arguments as strict JSON

Do not let the model call Pine Labs directly.

## Pine Labs Responsibilities

- Create payment link / collect request
- Fetch payment status
- Fetch reserve balance

If Pine Labs reserve balance API is unavailable in sandbox, implement a provider fallback response clearly marked as `sandbox_stub`.

## Backend Work Items

### 1. Config

- Add AWS and Bedrock settings in `backend/app/config.py`
- Add Pine Labs real API settings
- Add toggle `USE_MOCK_PINE_LABS`
- Parse `ALLOWED_ORIGINS`

### 2. Bedrock Client

Create `backend/app/services/bedrock_client.py`

Responsibilities:
- initialize boto3 Bedrock runtime client
- send prompt/messages
- return plain text
- handle AWS errors cleanly

### 3. Replace Ollama LLM Path

Update:
- `backend/app/services/llm_client.py`
- `backend/app/services/llm_router.py`

Requirements:
- remove Ollama dependency from active path
- use Bedrock-backed chat/classification
- enforce strict JSON extraction
- keep same supported intents

### 4. Pine Labs HTTP Provider

Finish `backend/app/providers/pine_labs_http.py`

Methods:
- `create_payment_link(amount, merchant_id)`
- `check_payment_status(payment_ref, current_status=None)`
- `get_reserve_balance(merchant_id)`

Requirements:
- map Pine Labs request/response into internal normalized shape
- include raw response in logs only, not user text
- handle non-200 responses
- handle invalid JSON

### 5. Tool Layer

Keep tool interface stable in:
- `backend/app/tools/payments.py`
- `backend/app/tools/registry.py`

Requirement:
- all tool outputs must return normalized fields:
  - `success`
  - `provider`
  - `payment_ref` if applicable
  - `status` if applicable
  - `amount` if applicable
  - `payment_url` if applicable
  - `currency` if applicable
  - `merchant_id` if applicable
  - `message`

### 6. Agent Orchestration

Update `backend/app/services/agent.py`

Requirements:
- preserve session state
- if user says “check status” after link creation, use last `payment_ref`
- if merchant id missing, use session merchant id or env default
- produce short natural reply after tool result
- never hallucinate payment details

### 7. Webhook Handling

Finish:
- `backend/app/routes/webhooks.py`
- `backend/app/services/webhook_service.py`
- `backend/app/schemas/webhook.py`

Requirements:
- verify webhook secret if Pine Labs supports it
- update session store payment status by `payment_ref`
- return ack response

### 8. Health Endpoint

Ensure `/health` reports:
- app up
- Bedrock config present
- Pine Labs mode (`mock` or `http`)

## Frontend Work Items

### 1. Keep Current Single Chat Page

Use existing chat UI only.

### 2. Tighten UX

- keep starter prompts
- render returned payment URL as clickable link
- show tool name and status
- show backend errors cleanly
- keep merchant/session inputs

### 3. Demo Prompts

- `Create payment link for 1200`
- `What is my reserve balance?`
- `Check payment status`

## Exact 2-Hour Execution Plan

### 0:00-0:15

- wire config for AWS + Pine Labs
- install boto3 if missing
- confirm env variables load

### 0:15-0:40

- implement Bedrock client
- switch intent detection and arg extraction to Bedrock
- test with 3 sample prompts

### 0:40-1:15

- implement Pine Labs HTTP provider
- normalize create/status/balance responses
- connect provider to tool layer

### 1:15-1:35

- complete webhook update flow
- tighten session state reuse
- improve error mapping

### 1:35-1:50

- polish frontend rendering for link/status/errors
- verify all 3 demo flows manually

### 1:50-2:00

- run full local smoke test
- prepare demo script

## Smoke Test Checklist

1. Start backend
2. Start frontend
3. Send `Create payment link for 1200`
4. Confirm reply includes payment URL and payment ref
5. Send `Check payment status`
6. Confirm backend uses last payment ref
7. Send `What is my reserve balance?`
8. Confirm merchant reserve response is returned
9. Send invalid input
10. Confirm graceful error

## Demo Script

1. Merchant asks reserve balance
2. Customer asks to create payment link for order amount
3. Assistant returns Pine Labs link
4. Merchant/customer checks status
5. Optional webhook call updates status and next status check reflects it

## Deliverables

- Bedrock-backed backend
- Pine Labs HTTP integration
- working frontend demo
- webhook endpoint
- local run instructions
- successful manual smoke test

## Non-Goals

- auth
- database
- voice
- mood engine
- split pay
- cart resurrection
- production deployment

## Definition of Done

Project is done when the 3 core flows work from the frontend against FastAPI using Bedrock plus Pine Labs sandbox, without mock mode, and can be demonstrated locally end to end.

4622 9431 2701 3713