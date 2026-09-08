import os

from dotenv import load_dotenv

load_dotenv()

# Razorpay test credentials
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_PRO_PLAN_ID = os.getenv("RAZORPAY_PRO_PLAN_ID")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

# AI token pricing
# Prices are stored as integer micro-dollars per 1,000 tokens.
# This avoids floating-point money calculations.

AI_INPUT_PRICE_PER_1K = 1_000
AI_CACHED_INPUT_PRICE_PER_1K = 250
AI_OUTPUT_PRICE_PER_1K = 2_000

# API call pricing
API_CALL_PRICE = 10