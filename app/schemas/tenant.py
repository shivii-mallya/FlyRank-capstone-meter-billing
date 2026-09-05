from pydantic import BaseModel, EmailStr


class TenantCreate(BaseModel):
    name: str
    email: EmailStr