from pydantic import BaseModel, Field


class UsageCreate(BaseModel):
    tenant_id: int
    usage_type: str
    quantity: int = Field(gt=0)
    idempotency_key: str