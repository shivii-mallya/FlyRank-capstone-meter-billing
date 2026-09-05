from fastapi import FastAPI

from app.databases.database import Base, engine
from app.databases import models
from app.routers.tenant_router import router as tenant_router

# Create all database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Usage Metering & Billing Engine",
    description="A backend service for tracking SaaS usage, enforcing quotas, and calculating billing costs.",
    version="1.0.0"
)

app.include_router(tenant_router)

@app.get("/")
def root():
    return {
        "message": "Usage Metering & Billing Engine is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }