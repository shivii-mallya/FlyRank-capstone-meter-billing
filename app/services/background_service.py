import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

LOG_FILE = Path("usage_background.log")


def process_usage_background(
    usage_event_id: int,
    tenant_id: int,
    usage_type: str,
    quantity: int,
    max_retries: int = 3
):
    """
    Background job for non-critical usage post-processing.

    The usage event is already committed before this job runs.
    If the background work fails, retry it a few times and log
    the failure instead of affecting the successful API response.
    """

    for attempt in range(1, max_retries + 1):
        try:
            message = (
                f"Background usage processing completed: "
                f"event_id={usage_event_id}, "
                f"tenant_id={tenant_id}, "
                f"usage_type={usage_type}, "
                f"quantity={quantity}"
            )

            with LOG_FILE.open("a", encoding="utf-8") as file:
                file.write(message + "\n")

            logger.info(message)
            return

        except Exception as exc:
            logger.warning(
                "Background usage job failed on attempt %s/%s: %s",
                attempt,
                max_retries,
                exc
            )

            if attempt < max_retries:
                time.sleep(1)
            else:
                logger.error(
                    "Background usage job permanently failed: "
                    "event_id=%s, tenant_id=%s",
                    usage_event_id,
                    tenant_id
                )