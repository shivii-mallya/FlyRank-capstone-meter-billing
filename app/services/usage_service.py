from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.databases.models import Tenant, UsageEvent


def record_usage(
    db: Session,
    tenant_id: int,
    usage_type: str,
    quantity: int,
    idempotency_key: str
):
    # 1. Check if this request was already processed
    existing_event = (
        db.query(UsageEvent)
        .filter(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.idempotency_key == idempotency_key
        )
        .first()
    )

    if existing_event:
        return existing_event

    # 2. Find the tenant
    tenant = (
        db.query(Tenant)
        .filter(Tenant.id == tenant_id)
        .first()
    )

    if not tenant:
        raise ValueError("Tenant not found")

    # 3. Get the tenant's plan
    plan = tenant.plan

    # 4. Calculate the start of the current month
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)

    # 5. Calculate current usage for this tenant and usage type
    current_usage = (
        db.query(UsageEvent)
        .filter(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.usage_type == usage_type,
            UsageEvent.created_at >= month_start
        )
        .all()
    )

    total_usage = sum(event.quantity for event in current_usage)

    # 6. Determine the applicable quota
    if usage_type == "api_call":
        quota = plan.api_call_limit

    elif usage_type == "ai_tokens":
        quota = plan.ai_token_limit

    else:
        raise ValueError("Invalid usage type")

    # 7. Check whether this usage would exceed the quota
    if total_usage + quantity > quota:
        raise ValueError(
            f"{usage_type} quota exceeded"
        )

    # 8. Record the usage event
    usage_event = UsageEvent(
        tenant_id=tenant_id,
        usage_type=usage_type,
        quantity=quantity,
        idempotency_key=idempotency_key
    )

    db.add(usage_event)
    db.commit()
    db.refresh(usage_event)

    return usage_event