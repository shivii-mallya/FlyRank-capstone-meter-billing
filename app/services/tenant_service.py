from sqlalchemy.orm import Session

from app.databases.models import Plan, Tenant


def create_tenant(
    db: Session,
    name: str,
    email: str
):
    # Find the Free plan
    free_plan = db.query(Plan).filter(Plan.name == "Free").first()

    if not free_plan:
        raise ValueError("Free plan not found")

    # Create the tenant
    tenant = Tenant(
        name=name,
        email=email,
        plan_id=free_plan.id
    )

    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    return tenant