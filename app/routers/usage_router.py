from fastapi import APIRouter, Depends, HTTPException, Header 
from sqlalchemy.orm import Session
from app.databases.models import Tenant
from app.databases.database import get_db
from app.schemas.usage import UsageCreate
from app.services.usage_service import record_usage
from app.services.usage_service import record_usage, get_usage_summary

router = APIRouter(
    prefix="/usage",
    tags=["Usage"]
)

def verify_tenant_key(
    tenant_id: int,
    x_tenant_key: str = Header(...),
    db: Session = Depends(get_db)
):
    tenant = (
        db.query(Tenant)
        .filter(Tenant.id == tenant_id)
        .first()
    )

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )

    if tenant.api_key != x_tenant_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid tenant API key"
        )

    return tenant

@router.post("/")
def record_usage_endpoint(
    usage_data: UsageCreate,
    db: Session = Depends(get_db),
    x_tenant_key: str = Header(...)
):
    tenant = (
        db.query(Tenant)
        .filter(Tenant.id == usage_data.tenant_id)
        .first()
    )

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )

    if tenant.api_key != x_tenant_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid tenant API key"
        )

    try:
        usage_event = record_usage(
        db=db,
        tenant_id=usage_data.tenant_id,
        usage_type=usage_data.usage_type,
        quantity=usage_data.quantity,
        idempotency_key=usage_data.idempotency_key,
        input_tokens=usage_data.input_tokens,
        cached_input_tokens=usage_data.cached_input_tokens,
        output_tokens=usage_data.output_tokens,
        reasoning_tokens=usage_data.reasoning_tokens
    )

        return {
    "id": usage_event.id,
    "tenant_id": usage_event.tenant_id,
    "usage_type": usage_event.usage_type,
    "quantity": usage_event.quantity,
    "idempotency_key": usage_event.idempotency_key,
    "input_tokens": usage_event.input_tokens,
    "cached_input_tokens": usage_event.cached_input_tokens,
    "output_tokens": usage_event.output_tokens,
    "reasoning_tokens": usage_event.reasoning_tokens,
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
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(verify_tenant_key)
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