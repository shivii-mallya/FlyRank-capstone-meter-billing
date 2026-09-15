from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.databases.database import get_db
from app.databases.models import Tenant


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