````markdown
# Build Log

## Overview

This project was developed as a SaaS usage metering and billing backend using FastAPI, SQLAlchemy, SQLite, Alembic, and Razorpay as the payment-provider integration.

AI assistance was used during development for implementation guidance, debugging, code review, and testing support. All suggested changes were reviewed and tested locally before being retained.

---

## 1. Core Usage Metering

Implemented usage recording for:

- API calls
- AI tokens

The usage service calculates monthly usage per tenant and checks the applicable plan quota before recording a usage event.

Idempotency keys were implemented so that retrying the same billable request does not create duplicate usage events.

---

## 2. Pricing and Cost Calculation

Implemented pricing for:

- API calls
- AI input tokens
- Cached input tokens
- AI output tokens
- Reasoning tokens

Reasoning tokens are treated as billable output tokens.

Integer-based pricing is used to avoid floating-point money calculations.

---

## 3. Tenant Authentication and Isolation

Tenant API keys were added to provide tenant-level authentication and isolation.

Alembic was used to create and apply the database migration for tenant API keys.

Authentication was tested with:

- Missing API key
- Invalid API key
- Wrong tenant API key
- Valid tenant API key

Unauthorized requests were rejected, while requests using the correct tenant API key were accepted.

---

## 4. Quota Enforcement

Quota enforcement was implemented at the usage-service level.

When a request would exceed the tenant's configured plan quota, the request is rejected with HTTP `429`.

The quota behavior was manually tested with a Pro tenant. A request attempting to exceed the API-call quota was rejected, and the rejected usage was not recorded.

---

## 5. Razorpay Subscription Integration

Razorpay was integrated as the payment-provider alternative permitted by the organization.

The billing service creates Razorpay subscriptions using the configured Pro plan.

The checkout endpoint is protected by tenant API-key authentication.

---

## 6. Webhook Processing

Razorpay webhook processing was implemented with:

- HMAC-SHA256 signature verification
- Provider event ID deduplication
- Tenant identification through subscription notes
- Subscription record creation
- Free → Pro plan synchronization

Webhook behavior was tested with both invalid and valid signatures.

A replayed webhook event was also tested and correctly returned an already-processed response.

---

## 7. Database Migration

Alembic was configured for database migrations.

A migration was generated to add tenant API-key support and was successfully applied to the database.

The migrated tenant records were subsequently used during API-key authentication testing.

---

## 8. AI-Assisted Development

AI assistance was used during development for:

- Explaining FastAPI and SQLAlchemy implementation details.
- Structuring usage metering and billing services.
- Debugging webhook signature verification.
- Debugging webhook replay and idempotency behavior.
- Implementing tenant API-key authentication.
- Setting up and troubleshooting the Alembic migration.
- Reviewing API routes and Swagger output.
- Creating and checking manual PowerShell test commands.
- Reviewing repository security and submission requirements.

AI suggestions were reviewed and tested rather than being accepted without verification.

---

## 9. Debugging and Iteration

### Webhook Signature Verification

An initial webhook request failed with an invalid signature.

The signature was regenerated using the exact webhook payload and configured webhook secret. The corrected request was successfully processed.

### Webhook Replay

A previously processed webhook event was submitted again using the same provider event ID.

The application correctly detected the duplicate event and returned:

```text
Webhook already processed
````

### Tenant API-Key Authentication

Requests without a tenant API key and requests using an incorrect tenant API key were rejected.

A request using the correct tenant API key successfully accessed the tenant's data.

### Usage Idempotency

The same usage request was submitted twice using the same idempotency key.

Both requests returned the same usage event instead of creating a duplicate record.

### Quota Enforcement

A Pro tenant had 3 API calls recorded against a 10,000-call monthly limit.

A request attempting to add 9,998 additional API calls was rejected with:

```text
api_call quota exceeded
```

and HTTP `429`.

The recorded usage remained at 3 API calls.

---

## 10. Validation

The application was successfully compiled using:

```text
python -m compileall app
```

The FastAPI Swagger/OpenAPI interface was also verified locally.

The following endpoint groups were verified through Swagger:

* Tenants
* Usage
* Billing
* Health check
* Root endpoint

---

## 11. Final Project State

The implemented backend provides:

* Multi-tenant usage metering
* Idempotent usage recording
* Plan-based quotas
* API-call pricing
* AI-token pricing
* Cached-input pricing
* Reasoning-token billing
* Tenant API-key authentication
* Tenant isolation
* Usage and cost summaries
* Razorpay subscription integration
* Signed webhook verification
* Webhook deduplication
* Free → Pro plan synchronization
* Alembic database migrations
* Environment-based secret configuration

```
```
