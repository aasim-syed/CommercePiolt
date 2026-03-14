# CommercePilot Supermemory

## Purpose
This file is a compact handoff of the work completed in this session so future work can resume quickly without reconstructing context.

## Current Demo Direction
- Build around the fixed 3-flow MVP from `SPEC-DEMO.md`:
  - create payment link
  - check payment status
  - get merchant reserve balance
- Keep frontend/backend response contract stable:
  - `reply`
  - `tool_called`
  - `data`
  - `session_state`
- Use Pine Labs stub/mock mode when live endpoint details are incomplete.
- Use AWS Bedrock live when credentials are available.

## Product / UX Changes Completed

### Frontend shell
- Reworked the frontend from a single-page chat into a sidebar layout with separate views.
- Added these pages:
  - `Overview`
  - `Operator Console`
  - `System Status`

### Status visibility
- Added `frontend/src/components/StatusPanel.tsx`
- Status panel shows:
  - provider mode
  - merchant id
  - session id
  - last payment ref
  - last payment status
  - Bedrock readiness
  - Pine Labs readiness

### Demo trigger UI
- Added manual payment status trigger controls on the System Status page.
- Supported trigger states:
  - `SUCCESS`
  - `FAILED`
  - `EXPIRED`
- This is meant to simulate webhook delivery during the demo.

### Enterprise-style UI pass
- Reduced playful styling.
- Shifted toward a more dashboard / operator-console look.
- Tightened palette, radii, and layout language.

## Backend Changes Completed

### Config cleanup
- Reworked `backend/app/config.py` to use env-driven settings expected by the app.
- Added / aligned fields for:
  - AWS / Bedrock
  - Pine Labs
  - CORS allowed origins
- Removed several misleading hardcoded placeholders.

### Allowed origins parsing fix
- Fixed startup failure caused by `ALLOWED_ORIGINS` being parsed as JSON.
- Current approach:
  - `allowed_origins` is stored as raw env string
  - `allowed_origins_list` is exposed as computed parsed list

### Demo webhook trigger
- Added backend endpoint:
  - `POST /webhooks/demo/payment-status`
- It updates session state by `payment_ref`.

### Pine Labs OAuth token step
- Implemented token generation support in `backend/app/services/pine_labs_client.py`
- Supports env vars:
  - `PINE_LABS_CLIENT_ID`
  - `PINE_LABS_CLIENT_SECRET`
  - `PINE_LABS_GRANT_TYPE`
- Token endpoint assumed:
  - `/api/auth/v1/token`
- Access token is cached in memory until near expiry.
- No retry loop or polling loop was added.

## Files Added or Meaningfully Changed

### Frontend
- `frontend/src/App.tsx`
- `frontend/src/components/StatusPanel.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/OverviewPage.tsx`
- `frontend/src/pages/SystemPage.tsx`
- `frontend/src/styles.css`

### Backend
- `backend/app/config.py`
- `backend/app/main.py`
- `backend/app/routes/webhooks.py`
- `backend/app/schemas/webhook.py`
- `backend/app/services/pine_labs_client.py`
- `backend/app/services/startup_checks.py`
- `backend/app/services/webhook_service.py`

## Important Runtime / Integration Notes

### AWS
- AWS credentials were added by the user to `backend/.env`.
- The assistant never opened `backend/.env`.
- Bedrock health check logic exists, but actual proof of AWS usage is:
  - successful log events from `bedrock_request_started` / `bedrock_request_completed`
  - or successful chat behavior using Bedrock

### Pine Labs
- Initially only mock/stub mode was safe.
- Later Pine Labs OAuth-style credentials became available:
  - `client_id`
  - `client_secret`
  - `grant_type=client_credentials`
- This was enough to implement token generation only.
- It is still not guaranteed that create link / status / reserve balance will work live because exact Pine Labs endpoint contracts are still uncertain.
- Missing / uncertain items:
  - merchant id
  - webhook secret
  - exact payment link endpoint contract
  - exact reserve balance endpoint contract
  - exact payment status endpoint contract

## Known Constraints / Cautions
- Do not read `backend/.env` unless the user explicitly allows it.
- Avoid runaway AWS or Pine Labs costs:
  - no infinite loops found
  - no automatic polling found
  - no retry storm logic added
- The main remaining risk is incorrect live Pine Labs endpoint shape, not billing explosion.

## Validation Performed
- `python -m py_compile backend/app/config.py`
- `python -m py_compile backend/app/config.py backend/app/main.py backend/app/services/startup_checks.py`
- `python -m py_compile backend/app/config.py backend/app/services/pine_labs_client.py`
- `npx.cmd tsc -b` in frontend passed at one point
- Full Vite build had an environment-specific `esbuild` spawn permission issue earlier, not a TypeScript error

## Current Expected Demo Position
- Frontend shell is ready enough for demo.
- System Status view exists and is useful.
- Manual webhook-style status transition exists.
- AWS can be live if Bedrock credentials are valid.
- Pine Labs is partially integrated:
  - token auth path implemented
  - business API compatibility still uncertain
- If Pine Labs live calls remain unstable, safest demo story is:
  - orchestration complete
  - adapter ready
  - live endpoint swap / endpoint contract finalization pending

## Suggested Next Steps
1. Restart backend after config changes.
2. Verify AWS by making one chat request and checking Bedrock logs.
3. Verify whether Pine Labs token auth succeeds.
4. If auth succeeds but business calls fail, inspect Pine Labs endpoint contracts next.
5. Keep demo fallback path available.
6. Rehearse the 3-step judge flow:
   - reserve balance
   - create payment link for 1200
   - trigger status and check payment status

## Quick Resume Prompt
If resuming later, start with:
"Read `SUPERMEMORY.md`, do not read `backend/.env`, and continue from the current AWS-live / Pine-Labs-partial state."

## Session Continuation: Latest Updates

### AWS / Bedrock findings
- Bedrock integration path was exercised through backend logs.
- Result:
  - request path is wired correctly
  - but AWS returned `UnrecognizedClientException`
- Meaning:
  - the Bedrock client is being used
  - credentials/token/session are invalid or incomplete
- Important note:
  - if AWS creds are temporary workshop creds, `AWS_SESSION_TOKEN` may still be needed

### Pine Labs auth and live calls
- Pine Labs OAuth token flow was implemented in the backend.
- Live create-payment-link flow now works against Pine Labs UAT.
- This is currently the strongest live provider proof in the project.

### Pine Labs payment status
- Initial route guesses failed.
- A narrow fallback was added:
  - `/api/pay/v1/payment/{payment_ref}`
  - fallback: `/api/pay/v1/paymentlink/{payment_ref}`
- Status is still not fully confirmed live.
- Current likely issue:
  - route and/or identifier mismatch between payment link id and actual payment id

### Pine Labs reserve balance
- Earlier balance route guesses were wrong.
- New doc file `acoountbalance` showed a different payouts endpoint:
  - `https://plural-uat.v2.pinepg.in/payouts/v3/payments/funding-account`
- Backend was updated to support a separate payouts host using:
  - `PINE_LABS_PAYOUTS_BASE_URL`
- Runtime findings:
  - `pluraluat.v2...` host gave auth/route style failures
  - `plural-uat.v2...` host produced DNS/network failure (`Name or service not known`)
- User was informed that payouts is currently unusable / unreliable for the demo and mock data is acceptable.
- Conclusion:
  - reserve balance should fall back to deterministic mock/stub mode for demo reliability

### Health / status panel alignment
- The UI originally showed `Pine Labs pending` based on outdated readiness logic.
- This was corrected.
- Backend `/health` now exposes:
  - `pine_labs_auth_configured`
- Frontend status badge now reflects:
  - `Pine Labs auth ready` in HTTP mode when OAuth config is present
  - `Pine Labs stub mode` in mock mode
  - `Pine Labs pending` only when auth truly is missing

### Current reality snapshot
- Working live:
  - Pine Labs OAuth token generation
  - Pine Labs create payment link
  - sidebar UI / system panel / chat shell
  - demo trigger for payment status transitions
- Partial / uncertain:
  - payment status live endpoint
  - AWS Bedrock live auth validity
- Not viable live right now:
  - reserve balance payouts endpoint

### Current recommended demo story
- Live:
  - create payment link via Pine Labs
- Controlled demo mode:
  - reserve balance via merchant-aware stub
  - payment status via session + manual event trigger
- Positioning:
  - operator workflow and orchestration are complete
  - provider adapter is real
  - one live payment action is proven
  - remaining provider surfaces are partially blocked by Pine Labs environment behavior

### Immediate next step after this memory update
- Implement deterministic stub fallback for reserve balance
- Then polish assistant replies / UI result presentation for judges

## Session Continuation: AWS Deployment Notes

### Workshop deployment reality
- The AWS workshop menus visible to the user do not expose modern managed deployment paths like Amplify or App Runner.
- The practical deployment path from the available workshop options is:
  - frontend via S3 static hosting or container
  - backend via Docker on EC2
- Later, the user clarified the workshop expectation is to push Docker images.

### Agreed deployment direction
- Full deploy should use Docker images for both services.
- Required AWS resources for this workshop-style deploy:
  - 2 ECR repositories
    - one for backend image
    - one for frontend image
  - 1 EC2 instance to run containers
- Public endpoints will be needed for:
  - frontend
  - backend

### Bedrock status
- AWS credentials are now valid enough to reach Bedrock.
- Latest failure is no longer credential-related.
- Current Bedrock blocker:
  - model invocation failed with `ValidationException`
  - the configured model id requires an inference profile / ARN rather than on-demand invocation
- If the workshop account does not expose Bedrock inference-profile setup, Bedrock should be treated as partially blocked for the demo.

### Pine Labs status at this point
- Live:
  - token generation
  - create payment link
- Partial / unresolved:
  - payment status live verification
- Blocked / unreliable:
  - reserve balance payouts endpoint
- Demo-safe fallback chosen:
  - reserve balance mocked in frontend

### Current live vs demo split
- Live:
  - Pine Labs create payment link
  - backend orchestration shell
  - token-based Pine Labs auth path
- Demo / simulated:
  - reserve balance frontend mock
  - webhook-style manual status trigger
- Partial:
  - payment status live endpoint path/id mapping
  - Bedrock account/model configuration

### Immediate next plans
1. Update memory before any further changes. Completed.
2. Keep reserve balance mocked and stable for demo.
3. Continue working on live payment status verification if time remains.
4. Prepare Docker images for both frontend and backend.
5. Create:
   - backend ECR repo
   - frontend ECR repo
   - EC2 instance
6. Push both Docker images and run them on EC2.
7. If Bedrock inference profile cannot be obtained in time, keep the LLM path non-blocking for the demo story.
