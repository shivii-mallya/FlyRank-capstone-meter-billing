from app.databases.database import SessionLocal
from app.databases.models import Plan


db = SessionLocal()

try:
    free_plan = Plan(
        name="Free",
        api_call_limit=1000,
        ai_token_limit=100000
    )

    pro_plan = Plan(
        name="Pro",
        api_call_limit=10000,
        ai_token_limit=1000000
    )

    db.add(free_plan)
    db.add(pro_plan)
    db.commit()

    print("Free and Pro plans created successfully!")

finally:
    db.close()