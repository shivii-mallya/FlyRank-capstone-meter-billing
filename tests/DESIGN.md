# Design Document — Usage Metering & Billing Engine

## Problem

SaaS applications need to track how much each customer uses, enforce plan limits, calculate usage costs, and keep subscription state synchronized with a payment provider.

## Proposed Solution

Build a FastAPI backend that provides:

- Multi-tenant customer management
- Free and Pro subscription plans
- API-call and AI-token usage metering
- Idempotent usage recording
- Monthly quota enforcement
- Integer-based cost calculation
- Razorpay Test Mode subscription integration as an organization-approved alternative to Stripe
- Signed and deduplicated payment webhooks
- Usage summary and cost reporting

## Data Model

The main entities are:

- `Tenant` — customer organization and current plan
- `Plan` — Free/Pro quotas
- `UsageEvent` — billable usage attributed to a tenant
- `Subscription` — payment-provider subscription state
- `ProcessedWebhookEvent` — prevents duplicate webhook processing

## API Surface

- `POST /tenants/` — create a tenant
- `POST /usage/` — record billable usage
- `GET /usage/{tenant_id}` — retrieve monthly usage and cost summary
- `POST /billing/checkout` — create a Pro subscription
- `POST /billing/webhook` — process signed payment-provider events
- `GET /health` — health check

## Idempotency Strategy

Every usage request contains an idempotency key.

The database enforces uniqueness for:

`tenant_id + idempotency_key`

If the same request is retried with the same key, the existing usage event is returned instead of creating another event.

## Quota Strategy

Before recording usage, the service calculates:

`current monthly usage + requested quantity`

and compares it with the tenant's plan limit.

Requests that exceed the limit return HTTP 429 with a clear quota-exceeded message.

## Cost Calculation

API calls use a fixed integer price.

AI usage tracks:

- input tokens
- cached input tokens
- output tokens
- reasoning tokens

Cached input uses a lower price, while reasoning tokens are billed as output tokens. Pricing constants are stored in configuration using integer units rather than floating-point money calculations.

## Payment Integration

The capstone brief specifies Stripe Test Mode. For this implementation, the organization approved Razorpay as an alternative payment provider.

The payment flow is:

Client
→ FastAPI checkout endpoint
→ Razorpay subscription
→ signed Razorpay webhook
→ signature verification
→ webhook deduplication
→ tenant plan synchronization

## Background Processing

Non-critical usage post-processing runs as a FastAPI background task after the usage event has been committed.

The task retries failed processing up to three times and logs permanent failures.

## Tenant Isolation

Tenant API keys are required for usage operations. A tenant can only access usage associated with its own valid API key.

## Non-Goals

The core implementation does not include:

- Invoicing
- Proration
- Overage billing
- Real AI model calls

AI token counts are simulated for metering and pricing tests.