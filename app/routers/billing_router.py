from fastapi import APIRouter, HTTPException

from app.services.billing_service import create_pro_subscription

router = APIRouter(prefix="/billing", tags=["Billing"])
from fastapi import Request, Header
from sqlalchemy.orm import Session

from app.databases.database import get_db
from app.services.billing_service import(process_webhook,  create_pro_subscription)
from fastapi import APIRouter, HTTPException, Request, Header, Depends

@router.post("/checkout")
def create_checkout(tenant_id: int):
    try:
        subscription = create_pro_subscription(tenant_id)

        return {
            "message": "Razorpay subscription created successfully",
            "tenant_id": tenant_id,
            "subscription_id": subscription["id"],
            "plan_id": subscription["plan_id"],
            "status": subscription["status"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(...),
    x_razorpay_event_id: str = Header(...),
    db: Session = Depends(get_db)
):
    payload = await request.body()

    try:
        data = await request.json()

        event_type = data.get("event")

        subscription_entity = (
            data.get("payload", {})
            .get("subscription", {})
            .get("entity", {})
        )

        notes = subscription_entity.get("notes", {})
        tenant_id = notes.get("tenant_id")
        subscription_id = subscription_entity.get("id")

        if not subscription_id:
            raise ValueError("Missing subscription ID")

        if not event_type:
            raise ValueError("Missing event type")

        if not tenant_id:
            raise ValueError("Missing tenant_id in subscription notes")

        result = process_webhook(
            db=db,
            payload=payload,
            signature=x_razorpay_signature,
            event_id=x_razorpay_event_id,
            event_type=event_type,
            tenant_id=int(tenant_id),
            subscription_id=subscription_id
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )