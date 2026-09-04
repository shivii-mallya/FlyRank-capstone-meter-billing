from fastapi import FastAPI

app = FastAPI(
    title="Usage Metering & Billing Engine",
    description="A backend service for tracking SaaS usage, enforcing quotas, and calculating billing costs.",
    version="1.0.0"
)


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