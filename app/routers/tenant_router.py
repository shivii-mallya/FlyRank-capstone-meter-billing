from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.databases.database import get_db
from app.schemas.tenant import TenantCreate
from app.services.tenant_service import create_tenant


router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"]
)


@router.post("/")
def create_tenant_endpoint(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db)
):
    try:
        tenant = create_tenant(
            db=db,
            name=tenant_data.name,
            email=tenant_data.email
        )

        return {
            "id": tenant.id,
            "name": tenant.name,
            "email": tenant.email,
            "plan": tenant.plan.name
        }

    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )