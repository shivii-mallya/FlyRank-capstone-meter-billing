````markdown
# FlyRank — SaaS Metering & Billing Backend

A multi-tenant SaaS backend that provides usage metering, plan-based quotas, token-aware pricing, tenant API-key authentication, and subscription billing integration.

The project is built with **FastAPI, SQLAlchemy, SQLite, Alembic, and Razorpay**.

> **Payment provider note:** Razorpay is used as the payment-provider alternative to Stripe, as permitted by the organization.

---

## Features

- Multi-tenant architecture
- Free and Pro plans
- API-call usage metering
- AI-token usage metering
- Idempotent usage recording
- Monthly plan-based quota enforcement
- HTTP `429` when usage quota is exceeded
- Tenant API-key authentication
- Tenant isolation
- API-call cost calculation
- AI input-token pricing
- Cached input-token pricing
- Output-token pricing
- Reasoning-token billing
- Usage and cost summaries
- Razorpay subscription integration
- Signed Razorpay webhook verification
- Webhook event deduplication
- Free → Pro plan synchronization
- SQLAlchemy database models
- Alembic database migrations
- Environment-based secret configuration
- FastAPI Swagger/OpenAPI documentation

---

## Architecture

```text
                         ┌──────────────────────┐
                         │        Client        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │       Routers        │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
          ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
          │ Tenant API  │   │  Usage API  │   │ Billing API │
          └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
                 │                 │                  │
                 │                 ▼                  ▼
                 │          ┌─────────────┐    ┌─────────────┐
                 │          │    Usage    │    │  Razorpay   │
                 │          │   Service   │    │ Subscription│
                 │          └──────┬──────┘    └──────┬──────┘
                 │                 │                  │
                 │                 ▼                  │
                 │          ┌─────────────┐           │
                 │          │ Quota + Cost│           │
                 │          │ Calculation │           │
                 │          └──────┬──────┘           │
                 │                 │                  ▼
                 │                 │          ┌─────────────┐
                 │                 │          │   Webhook   │
                 │                 │          │ Verification│
                 │                 │          └──────┬──────┘
                 │                 │                 │
                 └─────────────────┼─────────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │      SQLite DB       │
                         │                      │
                         │ Tenants              │
                         │ Plans                │
                         │ Usage Events         │
                         │ Subscriptions        │
                         │ Processed Webhooks   │
                         └──────────────────────┘
````

---

## Technology Stack

| Component           | Technology                |
| ------------------- | ------------------------- |
| Backend             | FastAPI                   |
| ORM                 | SQLAlchemy                |
| Database            | SQLite                    |
| Database migrations | Alembic                   |
| Payment provider    | Razorpay                  |
| Authentication      | Tenant API keys           |
| API documentation   | FastAPI Swagger / OpenAPI |
| Configuration       | `python-dotenv`           |
| Language            | Python                    |

---

## Project Structure

```text
FlyRank-capstone-meter-billing/
│
├── app/
│   ├── databases/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── dependencies/
│   │   └── auth.py
│   │
│   ├── routers/
│   │   ├── billing_router.py
│   │   ├── tenant_router.py
│   │   └── usage_router.py
│   │
│   ├── schemas/
│   │   └── usage.py
│   │
│   ├── services/
│   │   ├── billing_service.py
│   │   ├── payment_service.py
│   │   └── usage_service.py
│   │
│   ├── config.py
│   └── main.py
│
├── alembic/
│   ├── versions/
│   └── ...
│
├── tests/
│   ├── capstone.yaml
│   ├── EVIDENCE.md
│   └── BUILDLOG.md
│
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
├── seed.py
└── README.md
```

---

## Plans

### Free

The Free plan has:

* API-call limit: `1000` per month
* AI-token limit: `100000` per month

### Pro

The Pro plan has:

* API-call limit: `10000` per month
* AI-token limit: `1000000` per month

Plan limits are stored in the database and are used by the usage service when enforcing quotas.

---

## Usage Metering

Usage is recorded through:

```text
POST /usage/
```

Supported usage types include:

```text
api_call
ai_tokens
```

Each usage event contains an idempotency key.

If the same tenant submits the same idempotency key again, the existing usage event is returned instead of creating a duplicate billable event.

---

## Quota Enforcement

Before recording usage, the service:

1. Finds the tenant.
2. Loads the tenant's current plan.
3. Calculates the tenant's usage for the current month.
4. Determines the applicable quota.
5. Checks whether the new usage would exceed the quota.
6. Rejects the request if the quota would be exceeded.
7. Records the event only when the quota check succeeds.

Quota-exceeded requests return:

```text
HTTP 429
```

Example response:

```json
{
  "detail": "api_call quota exceeded"
}
```

---

## Pricing

The application calculates usage costs using integer-based pricing values.

Current configured pricing:

```text
API call:
10 micro-dollars per call

AI input:
1,000 micro-dollars per 1,000 tokens

Cached AI input:
250 micro-dollars per 1,000 tokens

AI output:
2,000 micro-dollars per 1,000 tokens
```

Reasoning tokens are added to output tokens when calculating billable AI output.

This avoids floating-point calculations for monetary values.

---

## Usage Summary

Current monthly usage can be retrieved using:

```text
GET /usage/{tenant_id}
```

Example response:

```json
{
  "tenant_id": 2,
  "plan": "Pro",
  "period": "2026-09",
  "api_calls": 3,
  "api_call_limit": 10000,
  "ai_tokens": 1800,
  "ai_token_limit": 1000000,
  "api_call_cost": 30,
  "ai_cost": 2250,
  "total_cost": 2280
}
```

---

## Tenant Authentication

Protected tenant operations use the following header:

```text
X-Tenant-Key: <tenant-api-key>
```

The API key is associated with a specific tenant.

Requests using:

* no API key
* an invalid API key
* another tenant's API key

are rejected.

This prevents one tenant from accessing another tenant's protected usage information.

---

## Razorpay Subscription Billing

Razorpay is used as the payment-provider alternative to Stripe.

The billing flow is:

```text
Client
  │
  ▼
POST /billing/checkout
  │
  ▼
Create Razorpay Subscription
  │
  ▼
Razorpay
  │
  ▼
subscription.activated webhook
  │
  ▼
Verify webhook signature
  │
  ▼
Check provider event ID
  │
  ▼
Find tenant
  │
  ▼
Update tenant to Pro
  │
  ▼
Create subscription record
  │
  ▼
Record processed webhook event
```

The Razorpay subscription contains the tenant ID in its subscription notes so that the webhook can associate the subscription with the correct tenant.

---

## Webhook Security

Webhook requests are verified using HMAC-SHA256.

The application:

1. Receives the raw webhook payload.
2. Uses the configured webhook secret.
3. Calculates the expected signature.
4. Compares it with the Razorpay signature.
5. Rejects the request if the signature is invalid.
6. Processes the event only after successful verification.

Invalid signatures are rejected with:

```text
Invalid webhook signature
```

---

## Webhook Idempotency

Razorpay webhook events are deduplicated using the provider event ID.

If an event has already been processed, the application returns:

```json
{
  "message": "Webhook already processed"
}
```

This prevents replayed webhook events from creating duplicate subscription records or repeating plan changes.

---

## Database

The application uses SQLite with SQLAlchemy.

Main entities include:

```text
Plan
Tenant
Subscription
UsageEvent
ProcessedWebhookEvent
```

Alembic is used for schema migrations.

The repository contains migration files under:

```text
alembic/versions/
```

---

## Environment Variables

Create a local `.env` file using the safe placeholders from:

```text
.env.example
```

Required Razorpay configuration:

```env
RAZORPAY_KEY_ID=your_razorpay_test_key_id
RAZORPAY_KEY_SECRET=your_razorpay_test_key_secret
RAZORPAY_PRO_PLAN_ID=your_razorpay_test_plan_id
RAZORPAY_WEBHOOK_SECRET=your_razorpay_test_webhook_secret
```

Never commit real credentials.

The `.env` file is excluded through `.gitignore`.

---

## Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd FlyRank-capstone-meter-billing
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables using `.env`.

---

## Database Setup

Apply Alembic migrations:

```bash
alembic upgrade head
```

Seed the database:

```bash
python seed.py
```

---

## Running the Application

Start the FastAPI application with:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```

---

## API Endpoints

### Health

```text
GET /health
```

### Root

```text
GET /
```

### Create Tenant

```text
POST /tenants/
```

### Record Usage

```text
POST /usage/
```

Requires:

```text
X-Tenant-Key
```

### Get Usage Summary

```text
GET /usage/{tenant_id}
```

Requires:

```text
X-Tenant-Key
```

### Create Razorpay Subscription

```text
POST /billing/checkout
```

Requires:

```text
X-Tenant-Key
```

### Razorpay Webhook

```text
POST /billing/webhook
```

Requires Razorpay webhook signature and event ID headers.

---

## Testing and Evidence

Manual acceptance testing was performed for:

* Usage idempotency
* Quota enforcement
* HTTP `429` quota responses
* Tenant API-key authentication
* Tenant isolation
* Usage and cost calculation
* Webhook signature verification
* Webhook replay protection
* Subscription activation
* Free → Pro plan synchronization
* Database migrations
* Application compilation
* Swagger/OpenAPI route registration

Detailed evidence is available in:

```text
tests/EVIDENCE.md
```

The development process and AI-assisted development/debugging record is available in:

```text
tests/BUILDLOG.md
```

The capstone submission manifest is available in:

```text
tests/capstone.yaml
```

---

## Security Notes

The repository does not contain real payment-provider credentials.

Sensitive configuration is loaded from environment variables.

The following files are excluded from Git:

```text
.env
*.db
__pycache__/
*.pyc
venv/
.venv/
```

Use Razorpay test credentials during development and testing.

---

## Current Scope

This project focuses on the core SaaS billing and metering workflow:

```text
Tenant
  ↓
API Authentication
  ↓
Usage Event
  ↓
Idempotency Check
  ↓
Quota Check
  ↓
Cost Calculation
  ↓
Usage Summary
```

and:

```text
Tenant
  ↓
Razorpay Subscription
  ↓
Signed Webhook
  ↓
Webhook Deduplication
  ↓
Plan Synchronization
  ↓
Subscription Record
```

The implementation intentionally keeps the architecture compact so that the core billing, metering, authentication, and webhook behaviors remain easy to understand and demonstrate.

````

