# backend/app/routes/webhooks.py

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request

from app.services.agent import session_store
from app.services.logger import get_logger

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

logger = get_logger("webhooks")


@router.post("/pine-labs")
async def pine_labs_webhook(request: Request) -> dict[str, str]:
    raw_body = await request.body()

    try:
        payload = json.loads(raw_body)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    event_type = payload.get("event")
    data = payload.get("data", {})
    payment_ref = data.get("payment_ref")

    logger.info(
        "webhook_received",
        extra={
            "extra_data": {
                "event": event_type,
                "payment_ref": payment_ref,
                "payload": payload,
            }
        },
    )

    status_map = {
        "payment.success": "SUCCESS",
        "payment.failed": "FAILED",
        "payment.expired": "EXPIRED",
    }

    if payment_ref and event_type in status_map:
        updated = session_store.update_payment_status(
            payment_ref=payment_ref,
            status=status_map[event_type],
        )

        logger.info(
            "webhook_payment_status_updated",
            extra={
                "extra_data": {
                    "payment_ref": payment_ref,
                    "status": status_map[event_type],
                    "session_updated": updated,
                }
            },
        )

    return {"status": "ok"}