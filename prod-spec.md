# CommercePilot Production Spec

## Objective
Build CommercePilot as a production-grade conversational payments platform using:

- React frontend
- FastAPI backend
- AWS Bedrock for LLM inference
- AWS cloud services for security, storage, deployment, and observability
- Pine Labs APIs for real payment operations

This spec assumes:

- no mocks in runtime
- no fake provider fallbacks
- no skipped infra or security-critical components
- all payment state is durable and auditable

## Product Scope

### Phase 1 Production Scope

1. Merchant reserve balance query
2. Merchant payment link generation
3. Payment status lookup
4. Session-aware chat experience
5. Pine Labs webhook ingestion
6. Full production security, logging, persistence, and deployment baseline

### Explicitly Deferred

These are product-phase deferrals, not architecture skips:

- Mood Engine
- Voice Ledger
- Dead Cart Resurrection
- Split-Pay Arbitration
- Native mobile apps

## Production Success Criteria

- Real Pine Labs sandbox or production-compatible API integration only
- No mock providers in deployed environments
- Durable session and payment state in a real database
- Secure secret handling through AWS Secrets Manager
- Role-based AWS access via IAM
- Full request tracing and structured logs
- Verified webhook ingestion and replay protection
- Idempotent payment operations
- Automated tests for critical flows
- Containerized deployable services
- Monitoring, alerting, and rollback plan

## High-Level Architecture

### Frontend

- React + TypeScript + Vite
- Hosted on AWS CloudFront + S3 or Amplify Hosting
- Authenticated merchant UI
- Customer chat entry point through scoped session token

### Backend API

- FastAPI service
- Deployed on ECS Fargate or App Runner
- Stateless application containers
- Uses RDS PostgreSQL for persistence
- Uses Redis/ElastiCache for short-lived session acceleration and rate limiting

### LLM Layer

- AWS Bedrock Runtime
- Model: approved Bedrock chat model suitable for structured extraction and low latency
- LLM used only for:
  - intent classification
  - argument extraction
  - safe response generation

### Payment Layer

- Pine Labs API integration over HTTPS
- Webhook callback ingestion
- Signature verification and replay protection

### AWS Platform Services

- Bedrock Runtime
- Secrets Manager
- IAM
- CloudWatch Logs
- CloudWatch Alarms
- X-Ray or OpenTelemetry-compatible tracing
- RDS PostgreSQL
- ElastiCache Redis
- S3 for artifacts if needed
- WAF on public edge if internet-facing

## Environment Strategy

### Environments

1. `local`
2. `dev`
3. `staging`
4. `prod`

Rules:

- `prod` and `staging` must reject mock providers
- separate Pine Labs credentials per environment
- separate database and Redis per environment
- separate Secrets Manager namespaces per environment

## Core User Flows

### 1. Reserve Balance

1. Merchant opens authenticated chat
2. Merchant asks for reserve balance
3. Backend resolves merchant identity
4. Backend queries Pine Labs reserve endpoint
5. Backend stores request/response audit record
6. Backend returns normalized answer

### 2. Create Payment Link

1. Merchant asks to create payment link
2. Backend uses Bedrock for intent and missing argument extraction
3. Backend validates amount, currency, merchant permissions, and request idempotency key
4. Backend sends create-link request to Pine Labs
5. Backend stores payment intent, provider ref, raw provider metadata, and status
6. Backend returns chat response with link and payment reference

### 3. Check Payment Status

1. Merchant or customer asks status
2. Backend resolves payment reference from message or stored session state
3. Backend checks latest local payment record
4. Backend optionally refreshes from Pine Labs if stale
5. Backend returns normalized current status

### 4. Webhook Update

1. Pine Labs sends webhook
2. Backend verifies signature and timestamp
3. Backend checks replay nonce/event id
4. Backend updates payment state transactionally
5. Backend appends audit event
6. Backend returns ack

## Required Production Components

## 1. Identity and Access

### Merchant Authentication

- Use Cognito or existing merchant identity provider
- JWT-based auth for merchant dashboard
- backend validates issuer, audience, expiry, and scopes

### Customer Session Access

- customer access must be scoped through a short-lived signed token
- no open anonymous session with arbitrary merchant access

### Authorization

- merchant can only view and act on own merchant_id
- backend must never trust merchant_id from raw client input alone
- merchant_id must come from authenticated claims or validated mapping

## 2. Data Model

Use PostgreSQL.

### Tables

#### `merchants`

- `id`
- `external_merchant_id`
- `name`
- `status`
- `created_at`
- `updated_at`

#### `chat_sessions`

- `id`
- `merchant_id`
- `customer_id` nullable
- `channel`
- `status`
- `created_at`
- `updated_at`

#### `chat_messages`

- `id`
- `session_id`
- `role`
- `content`
- `intent`
- `tool_name`
- `tool_args_json`
- `response_json`
- `created_at`

#### `payments`

- `id`
- `merchant_id`
- `session_id`
- `order_id`
- `payment_ref`
- `provider_status`
- `normalized_status`
- `amount`
- `currency`
- `payment_url`
- `provider_payload_json`
- `idempotency_key`
- `created_at`
- `updated_at`

#### `payment_events`

- `id`
- `payment_id`
- `source`
- `event_type`
- `provider_event_id`
- `payload_json`
- `created_at`

#### `webhook_receipts`

- `id`
- `provider`
- `provider_event_id`
- `signature_valid`
- `received_at`
- `processed_at`
- `status`

## 3. Session Management

### Durable State

- source of truth must be PostgreSQL
- Redis may cache recent session context
- session state cannot exist only in memory

### Stored Context

- merchant id
- recent payment refs
- recent order ids
- latest payment status
- last successful tool call

### Session Rules

- session expiration policy defined
- PII minimization applied
- customer data stored only when necessary

## 4. LLM Design with Bedrock

### Allowed LLM Tasks

- classify user intent
- extract structured arguments
- generate concise user-facing response from trusted tool outputs

### Forbidden LLM Behavior

- direct payment decisioning
- inventing amounts, refs, balances, or statuses
- calling external services directly
- bypassing business validation

### Model Interface

Implement a Bedrock client service with:

- timeout controls
- retry with exponential backoff
- request/response logging with redaction
- model fallback support if approved
- strict schema-bound extraction

### Prompting Requirements

- system prompts versioned in code
- prompts stored as templates
- extraction outputs validated by Pydantic
- invalid model outputs treated as failures, not guessed

## 5. Pine Labs Integration

### Provider Design

Implement `PineLabsHttpProvider` as the only allowed provider outside local development.

### Required Endpoints

- create payment link / collect request
- get payment status
- get reserve balance

### Integration Rules

- all requests use explicit timeout
- retries only on safe transient failure classes
- idempotency key used for create-payment operations if Pine Labs supports it
- response mapping to normalized internal model
- preserve provider payload for audit

### Validation

- amount > 0
- currency allowed
- merchant active
- payment ref format verified
- provider error codes mapped to internal typed exceptions

## 6. Webhooks

### Requirements

- verify webhook signature using Pine Labs scheme
- validate event timestamp freshness
- reject replayed event ids
- process transactionally
- return deterministic ack response

### Failure Handling

- failed processing moves receipt to retryable state
- dead-letter workflow defined for poison events
- alert on sustained failures

## 7. API Design

### Merchant Chat API

`POST /agent/chat`

Requirements:

- auth required
- request validation
- correlation id support
- idempotency support where relevant

### Health APIs

- `/health/live`
- `/health/ready`

`ready` must check:

- database reachability
- Redis reachability
- Bedrock client readiness
- Pine Labs connectivity baseline if appropriate

### Admin/Internal APIs

- webhook metrics
- payment lookup by ref
- session inspection for support users only

## 8. Security

### Secrets

- store Pine Labs secrets in AWS Secrets Manager
- store DB credentials in Secrets Manager or IAM auth
- no plaintext prod secrets in `.env`

### Transport

- TLS end to end
- secure headers
- CORS locked to known frontend origins

### App Security

- input validation on all endpoints
- rate limiting per token/IP/session
- request size limits
- dependency scanning
- SAST/secret scanning in CI

### Data Protection

- redact secrets and sensitive payment data from logs
- encrypt data at rest
- encrypt DB and Redis

## 9. Observability

### Logging

- structured JSON logs
- include correlation id, session id, merchant id, payment ref
- redact tokens, secrets, signatures

### Metrics

- chat request count
- intent classification failures
- Pine Labs latency/error rate
- webhook success/failure rate
- payment creation success rate
- Bedrock latency/error rate

### Tracing

- distributed trace for frontend request to backend to Pine Labs

### Alerting

- high 5xx rate
- webhook failure spike
- payment create failure spike
- Bedrock failure spike
- DB connectivity failures

## 10. Frontend Production Requirements

### UX

- merchant login
- session-aware chat
- clear loading and failure states
- clickable payment links
- visible payment status cards

### Security

- no merchant_id trust from manual input in prod UI
- auth token handled securely
- no sensitive data persisted in browser storage unless necessary

### Accessibility

- keyboard navigation
- focus states
- semantic structure

## 11. Deployment

### Backend

- Dockerized FastAPI app
- deploy to ECS Fargate or App Runner
- autoscaling rules
- blue/green or rolling deployment strategy

### Frontend

- build artifact hosted on CloudFront + S3 or Amplify
- environment-specific API base URL

### Infrastructure as Code

- Terraform or AWS CDK required
- provision:
  - VPC
  - ECS/App Runner
  - RDS
  - Redis
  - Secrets Manager
  - IAM roles
  - log groups
  - alarms

## 12. Testing

### Automated Tests

- unit tests for routing, validation, normalization
- integration tests for Pine Labs adapter using contract fixtures
- API tests for chat endpoint
- webhook verification tests
- migration tests for database schema

### End-to-End Tests

- create payment link
- check payment status
- reserve balance query
- webhook updates payment status

### Non-Functional Tests

- load test chat endpoint
- failure injection for Bedrock timeout
- failure injection for Pine Labs timeout

## 13. Rollout Plan

### Stage 1

- local integration against Pine Labs sandbox

### Stage 2

- dev deployment
- internal merchant-only usage

### Stage 3

- staging with UAT
- webhook verification and alert validation

### Stage 4

- production release with feature flag for selected merchants

## 14. Build Sequence

### Workstream 1: Platform

- add AWS config layer
- implement Secrets Manager integration
- add Bedrock client
- add structured logging and tracing

### Workstream 2: Persistence

- add PostgreSQL models and migrations
- add Redis-backed cache/rate limiter
- replace in-memory session store

### Workstream 3: Payments

- complete Pine Labs HTTP provider
- normalize responses
- add idempotency and provider exception mapping

### Workstream 4: Agent

- Bedrock intent classification
- schema-based arg extraction
- trusted response synthesis

### Workstream 5: Security

- auth and authorization
- webhook signature verification
- rate limits and CORS hardening

### Workstream 6: Frontend

- auth-aware chat UI
- payment status cards
- production error handling

### Workstream 7: Ops

- CI/CD
- infra as code
- dashboards and alarms

## 15. Definition of Done

CommercePilot is production-ready only when:

- deployed to AWS with IaC
- uses Bedrock and real Pine Labs APIs only
- stores all critical session and payment state durably
- has auth, authorization, secrets management, observability, and webhook hardening
- has automated coverage for critical flows
- supports rollback and monitored operation in staging and production
