Absolutely. Based on the evidence you provided and the final test results we established, here is the **complete corrected `EVIDENCE.md`** ready to replace the current file.

````markdown
# Evidence

This document records evidence for the implemented billing, metering, authentication, quota, webhook, background-processing, and database-migration requirements.

---

## 1. Idempotent Usage Metering

### Test

The same usage request was submitted twice using the same idempotency key:

`final-idempotency-test-001`

### First request

```text
id                  : <event ID from first request>
tenant_id           : 2
usage_type          : api_call
quantity            : 1
idempotency_key     : final-idempotency-test-001
````

### Second request

The same request was submitted again with the same idempotency key.

```text
id                  : <same event ID as first request>
tenant_id           : 2
usage_type          : api_call
quantity            : 1
idempotency_key     : final-idempotency-test-001
```

### Result

Both requests returned the same usage event instead of creating a second event.

### Evidence

The same idempotency key returned the existing usage event, demonstrating idempotent usage recording and preventing duplicate usage events.

---

## 2. Quota Enforcement

### Test

Tenant 2 uses the Pro plan with:

```text
api_call_limit : 10000
```

Before the final quota-boundary test, Tenant 2 had:

```text
api_calls : 5
```

A request attempting to add:

```text
quantity : 9995
```

was submitted.

### Result — Exact Quota Boundary

The request was accepted because:

```text
5 + 9995 = 10000
```

The resulting usage summary showed:

```text
api_calls       : 10000
api_call_limit  : 10000
```

A second request attempting to add:

```text
quantity : 1
```

was then submitted.

### Result — Over Quota

The application rejected the request with:

```text
HTTP 429
api_call quota exceeded
```

The usage summary remained:

```text
api_calls       : 10000
api_call_limit  : 10000
```

### Conclusion

The application allows usage exactly up to the configured quota and rejects the next request that would exceed the limit with HTTP `429`.

---

## 3. Tenant API-Key Authentication

### Test 1 — Missing API Key

A request was made without an `X-Tenant-Key` header.

### Result

The application rejected the request with a validation error indicating:

```text
x-tenant-key
Field required
```

---

### Test 2 — Wrong Tenant API Key

Tenant 1's API key was used while requesting an operation for Tenant 2.

### Result

The application rejected the request with:

```text
HTTP 403
Invalid tenant API key
```

---

### Test 3 — Valid Tenant API Key

A valid Tenant 2 API key was used to access:

```text
GET /usage/2
```

### Result

The application successfully returned Tenant 2's usage information:

```text
tenant_id       : 2
plan            : Pro
period          : 2026-09
api_calls       : 10000
api_call_limit  : 10000
ai_tokens       : 1800
ai_token_limit  : 1000000
api_call_cost   : 100000
ai_cost         : 2250
total_cost      : 102250
```

### Conclusion

Tenant API-key authentication is enforced, and cross-tenant access using another tenant's API key is rejected.

---

## 4. Usage and Cost Calculation

Tenant 2's final usage summary returned:

```text
tenant_id       : 2
plan            : Pro
period          : 2026-09
api_calls       : 10000
api_call_limit  : 10000
ai_tokens       : 1800
ai_token_limit  : 1000000
api_call_cost   : 100000
ai_cost         : 2250
total_cost      : 102250
```

The application calculates:

* API-call usage and cost.
* AI-token usage.
* AI input-token cost.
* Cached input-token cost.
* Output-token cost.
* Reasoning-token cost as billable output.
* Total usage cost.

The configured pricing values are defined in `app/config.py`.

For the tested AI usage:

```text
input tokens          : 1000
cached input tokens   : 200
output tokens         : 500
reasoning tokens      : 100
```

The resulting AI cost was:

```text
input cost            : 1000
cached input cost     : 50
output + reasoning    : 1200
total AI cost         : 2250
```

This matches the application's reported `ai_cost` of `2250`.

---

## 5. Razorpay Webhook Signature Verification

Razorpay Test Mode was used as an organization-approved alternative to the Stripe integration specified in the capstone brief.

### Test 1 — Forged Signature

A webhook request was sent using:

```text
fake_signature
```

instead of a valid signature.

### Result

The application rejected the request with:

```text
Invalid webhook signature
```

No subscription synchronization was performed for the forged request.

---

### Test 2 — Valid Signature

A valid HMAC-SHA256 signature was generated using the configured Razorpay webhook secret and the exact webhook request payload.

The request was then submitted with the generated signature.

### Result

The application processed the webhook successfully.

```text
Webhook processed successfully
```

### Conclusion

Webhook signatures are verified using HMAC-SHA256 before webhook processing.

---

## 6. Webhook Idempotency / Duplicate Event Protection

### Test

A webhook with event ID:

```text
test-valid-event-002
```

was successfully processed.

The same event ID was then submitted again with the same valid signature and payload.

### Result

The second request returned:

```text
Webhook already processed
```

The database contained the processed webhook event:

```text
provider_event_id : test-valid-event-002
event_type        : subscription.activated
```

### Conclusion

Previously processed provider webhook events are detected and are not processed again.

This prevents duplicate processing when the same webhook event is replayed.

---

## 7. Background Job Validation

A usage request was submitted successfully with:

```text
Tenant ID       : 2
Usage type      : api_call
Quantity        : 1
Idempotency key : background-test-001
```

The API created usage event ID `14`.

The background processing log was then checked with:

```powershell
Get-Content usage_background.log
```

### Observed Result

```text
Background usage processing completed: event_id=14, tenant_id=2, usage_type=api_call, quantity=1
```

This confirms that the usage event was successfully processed by the background job after the API request completed.

The background job includes retry handling for failures, with up to 3 attempts and error logging after the final failed attempt.

---

## 8. Subscription and Plan Synchronization

The webhook handler processes the Razorpay:

```text
subscription.activated
```

event.

The implementation:

1. Verifies the Razorpay webhook signature.
2. Checks whether the provider event has already been processed.
3. Extracts the tenant ID from the subscription notes.
4. Locates the tenant.
5. Locates the Pro plan.
6. Updates the tenant's `plan_id` to the Pro plan.
7. Creates a subscription record.
8. Records the processed provider event.

This provides the Free → Pro subscription synchronization flow.

Razorpay Test Mode is used as an organization-approved alternative to the Stripe payment-provider requirement.

---

## 9. Database Migration

Alembic was added and configured for database migrations.

A migration for tenant API keys was generated:

```text
alembic/versions/e584df6fd757_add_tenant_api_keys.py
```

The migration was successfully applied using Alembic.

The migration state was verified with:

```text
e584df6fd757 (head)
```

The resulting tenant records were verified to contain API-key information, and tenant authentication tests passed successfully.

---

## 10. Tenant API-Key Isolation During Usage Recording

A valid Tenant 2 API key was used to record usage through:

```text
POST /usage/
```

The request successfully created a usage event for Tenant 2.

The same authentication mechanism was also tested against invalid tenant credentials and rejected unauthorized requests.

This demonstrates that usage operations are protected by tenant API-key authentication.

---

## 11. Application Compilation

The application was validated using:

```powershell
python -m compileall app
```

The command completed successfully without Python compilation errors.

The application source tree was successfully compiled, including:

```text
app/
app/databases/
app/dependencies/
app/routers/
app/schemas/
app/services/
```

---

## 12. Swagger / OpenAPI Verification

The FastAPI Swagger UI was verified at:

```text
http://127.0.0.1:8000/docs
```

The following endpoints were visible:

```text
GET  /
GET  /health
POST /tenants/
POST /usage/
GET  /usage/{tenant_id}
POST /billing/checkout
POST /billing/webhook
```

This confirms that the main application routers are registered and exposed through FastAPI.

---

## 13. Security / Secrets Check

The real `.env` file is excluded through `.gitignore`:

```text
.env
```

The following command was used to verify that `.env` is not tracked by Git:

```powershell
git ls-files .env
```

The command returned no output.

The repository therefore does not track the real environment file containing Razorpay credentials.

A separate `.env.example` file contains safe placeholder values for the required Razorpay environment variables.

The local SQLite database and generated log files are also excluded from Git.

---

## 14. Requirements / Dependency Check

The project includes a `requirements.txt` file containing the dependencies required by the application, including:

```text
fastapi
uvicorn
SQLAlchemy
razorpay
python-dotenv
pydantic
requests
```

Alembic is also included:

```text
alembic==1.19.2
```

This supports installation of the application's database migration tooling.

---

## 15. Submission Manifest

The repository contains the required root-level manifest:

```text
capstone.yaml
```

The manifest specifies:

```yaml
run: uvicorn app.main:app --host 0.0.0.0 --port 8000
base_url: http://127.0.0.1:8000
seed: python seed.py
test:
  - GET /health
  - GET /
  - POST /tenants/
  - POST /usage/
  - GET /usage/1
  - POST /billing/checkout
  - POST /billing/webhook
```

The project also contains the corresponding `seed.py` script in the repository root.

---

## Summary

The following implemented behaviors have been manually verified:

* Idempotent usage recording.
* API-call quota enforcement.
* Exact quota-boundary handling.
* HTTP 429 when usage exceeds the quota.
* Tenant API-key authentication.
* Cross-tenant API-key rejection.
* Usage and cost calculation.
* AI token pricing including cached input and reasoning tokens.
* Razorpay Test Mode subscription integration.
* Razorpay webhook signature verification.
* Webhook duplicate-event protection.
* Subscription activation and Free → Pro plan synchronization.
* Background usage processing.
* Background-job retry handling.
* Alembic database migration.
* Application compilation.
* FastAPI Swagger/OpenAPI route registration.
* Environment-secret protection through `.gitignore`.
* Required project manifest and seed configuration.

Razorpay Test Mode was used as an organization-approved alternative to the Stripe integration specified in the original capstone brief.

````

