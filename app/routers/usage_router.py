from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.databases.database import get_db
from app.schemas.usage import UsageCreate
from app.services.usage_service import record_usage
from app.services.usage_service import record_usage, get_usage_summary

router = APIRouter(
    prefix="/usage",
    tags=["Usage"]
)


@router.post("/")
def record_usage_endpoint(
    usage_data: UsageCreate,
    db: Session = Depends(get_db)
):
    try:
        usage_event = record_usage(
            db=db,
            tenant_id=usage_data.tenant_id,
            usage_type=usage_data.usage_type,
            quantity=usage_data.quantity,
            idempotency_key=usage_data.idempotency_key
        )

        return {
            "id": usage_event.id,
            "tenant_id": usage_event.tenant_id,
            "usage_type": usage_event.usage_type,
            "quantity": usage_event.quantity,
            "idempotency_key": usage_event.idempotency_key,
            "created_at": usage_event.created_at
        }

    except ValueError as e:
        if "quota exceeded" in str(e):
            raise HTTPException(
                status_code=429,
                detail=str(e)
            )

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/{tenant_id}")
def get_usage_endpoint(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    try:
        return get_usage_summary(
            db=db,
            tenant_id=tenant_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )