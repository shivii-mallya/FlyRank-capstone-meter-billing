from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.databases.models import UsageEvent


def record_usage(
    db: Session,
    tenant_id: int,
    usage_type: str,
    quantity: int,
    idempotency_key: str
):
    usage_event = UsageEvent(
        tenant_id=tenant_id,
        usage_type=usage_type,
        quantity=quantity,
        idempotency_key=idempotency_key
    )

    db.add(usage_event)

    try:
        db.commit()
        db.refresh(usage_event)
        return usage_event

    except IntegrityError:
        db.rollback()

        existing_event = (
            db.query(UsageEvent)
            .filter(
                UsageEvent.tenant_id == tenant_id,
                UsageEvent.idempotency_key == idempotency_key
            )
            .first()
        )

        return existing_event