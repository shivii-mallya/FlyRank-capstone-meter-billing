from app.config import RAZORPAY_PRO_PLAN_ID
from app.services.payment_service import get_razorpay_client
import hmac
import hashlib
from app.config import RAZORPAY_WEBHOOK_SECRET
from app.databases.models import (
    ProcessedWebhookEvent,
    Tenant,
    Plan,
    Subscription
)

def create_pro_subscription(tenant_id: int):
    client = get_razorpay_client()

    subscription_data = {
        "plan_id": RAZORPAY_PRO_PLAN_ID,
        "total_count": 12,
        "quantity": 1,
        "customer_notify": 1,
        "notes": {
            "tenant_id": str(tenant_id)
        }
    }

    subscription = client.subscription.create(subscription_data)

    return subscription
def verify_webhook_signature(payload: bytes, signature: str):
    expected_signature = hmac.new(
        RAZORPAY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


def process_webhook(
    db,
    payload: bytes,
    signature: str,
    event_id: str,
    event_type: str,
    tenant_id: int,
    subscription_id: str
):
    # 1. Verify Razorpay signature
    if not verify_webhook_signature(payload, signature):
        raise ValueError("Invalid webhook signature")

    # 2. Check whether this webhook was already processed
    existing_event = (
        db.query(ProcessedWebhookEvent)
        .filter(
            ProcessedWebhookEvent.provider_event_id == event_id
        )
        .first()
    )

    if existing_event:
        return {
            "message": "Webhook already processed"
        }

    # 3. Find tenant
    tenant = (
        db.query(Tenant)
        .filter(Tenant.id == tenant_id)
        .first()
    )

    if not tenant:
        raise ValueError("Tenant not found")

    # 4. Handle subscription activation
    if event_type == "subscription.activated":
        pro_plan = (
            db.query(Plan)
            .filter(Plan.name == "Pro")
            .first()
        )

        if not pro_plan:
            raise ValueError("Pro plan not found")

        # Upgrade tenant to Pro
        tenant.plan_id = pro_plan.id

    # 5. Record subscription
    subscription = Subscription(
        tenant_id=tenant_id,
        payment_provider="razorpay",
        provider_subscription_id=subscription_id,
        status="active"
    )

    db.add(subscription)

    # 6. Record processed webhook
    processed_event = ProcessedWebhookEvent(
        provider_event_id=event_id,
        event_type=event_type,
        payment_provider="razorpay"
    )

    db.add(processed_event)
    db.commit()

    return {
        "message": "Webhook processed successfully"
    }