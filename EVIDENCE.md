````markdown
# Evidence

This document records evidence for the implemented billing, metering, authentication, quota, webhook, and database-migration requirements.

---

## 1. Idempotent Usage Metering

### Test

The same usage request was submitted twice using the same idempotency key:

`idempotency-test-002`

### First request

```text
id                  : 13
tenant_id           : 2
usage_type          : api_call
quantity            : 1
idempotency_key     : idempotency-test-002
````

### Second request

The same request was submitted again with the same idempotency key.

```text
id                  : 13
tenant_id           : 2
usage_type          : api_call
quantity            : 1
idempotency_key     : idempotency-test-002
```

### Result

Both requests returned the same usage event ID (`13`) instead of creating a second event.

**Evidence:** The same idempotency key returned the existing usage event, demonstrating idempotent usage recording.

---

## 2. Quota Enforcement

### Test

Tenant 2 uses the Pro plan with:

```text
api_call_limit : 10000
```

Before the quota test, the usage summary showed:

```text
api_calls : 3
```

A request attempting to add `9998` additional API calls was submitted.

### Result

The application rejected the request with:

```text
HTTP 429
api_call quota exceeded
```

The usage summary subsequently remained at:

```text
api_calls : 3
```

### Conclusion

The application prevents usage from exceeding the configured plan quota and returns HTTP `429` when the quota is exceeded.

---

## 3. Tenant API-Key Authentication

### Test 1 — Missing API key

A request was made to:

```text
GET /billing/checkout?tenant_id=2
```

without an `X-Tenant-Key` header.

### Result

The application rejected the request with a validation error indicating that:

```text
x-tenant-key
Field required
```

---

### Test 2 — Wrong tenant API key

Tenant 1's API key was used while requesting an operation for Tenant 2.

### Result

The application rejected the request with:

```text
HTTP 403
Invalid tenant API key
```

---

### Test 3 — Valid tenant API key

A valid Tenant 2 API key was used to access:

```text
GET /usage/2
```

### Result

The application successfully returned Tenant 2's usage information:

```text
tenant_id      : 2
plan           : Pro
period         : 2026-09
api_calls      : 3
api_call_limit : 10000
ai_tokens      : 1800
ai_token_limit : 1000000
api_call_cost  : 30
ai_cost        : 2250
total_cost     : 2280
```

### Conclusion

Tenant API-key authentication is enforced and cross-tenant access using another tenant's key is rejected.

---

## 4. Usage and Cost Calculation

Tenant 2's usage summary returned:

```text
tenant_id      : 2
plan           : Pro
period         : 2026-09
api_calls      : 3
api_call_limit : 10000
ai_tokens      : 1800
ai_token_limit : 1000000
api_call_cost  : 30
ai_cost        : 2250
total_cost     : 2280
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

---

## 5. Razorpay Webhook Signature Verification

### Test 1 — Forged signature

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

---

### Test 2 — Valid signature

A signature was generated using the configured Razorpay webhook secret and the exact webhook request payload.

The request was then submitted with the generated signature.

### Result

The application returned:

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

````markdown
## Background Job Validation

A usage request was submitted successfully with:

- Tenant ID: 2
- Usage type: `api_call`
- Quantity: `1`
- Idempotency key: `background-test-001`

The API created usage event ID `14`.

The background processing log was then checked with:

```text
Get-Content usage_background.log
````

Observed result:

```text
Background usage processing completed: event_id=14, tenant_id=2, usage_type=api_call, quantity=1
```

This confirms that the usage event was successfully processed by the background job after the API request completed.

The background job also includes retry handling for failures, with up to 3 attempts and error logging after the final failed attempt.

```
```
### Conclusion

Previously processed provider webhook events are detected and are not processed again.

---

## 7. Subscription and Plan Synchronization

The webhook handler processes the `subscription.activated` event.

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

Razorpay is used as the payment provider alternative permitted by the organization.

---

## 8. Database Migration

Alembic was added and configured for database migrations.

A migration for tenant API keys was generated:

```text
alembic/versions/e584df6fd757_add_tenant_api_keys.py
```

The migration was successfully applied using Alembic.

The resulting tenant records were verified to contain API-key information, and tenant authentication tests passed successfully.

---

## 9. Tenant API-Key Isolation During Usage Recording

A valid Tenant 2 API key was used to record usage:

```text
POST /usage/
```

The request successfully created a usage event for Tenant 2.

The same authentication mechanism was also tested against invalid tenant credentials and rejected unauthorized requests.

This demonstrates that usage operations are protected by tenant API-key authentication.

---

## 10. Application Compilation

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

## 11. Swagger / OpenAPI Verification

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

## 12. Security / Secrets Check

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

---

## 13. Requirements / Dependency Check

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

Alembic is also installed and included as:

```text
alembic==1.19.2
```

This supports installation of the application's database migration tooling.

---

## 14. Submission Manifest

The repository contains:

```text
tests/capstone.yaml
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
* HTTP 429 on quota exhaustion.
* Tenant API-key authentication.
* Cross-tenant API-key rejection.
* Usage and cost calculation.
* Razorpay subscription integration.
* Razorpay webhook signature verification.
* Webhook duplicate-event protection.
* Subscription activation and Free → Pro plan synchronization.
* Alembic database migration.
* Application compilation.
* FastAPI Swagger/OpenAPI route registration.
* Environment-secret protection through `.gitignore`.

```
```
