from __future__ import annotations

import hmac
import hashlib
import json

from fastapi import APIRouter, Header, HTTPException, Request

from app.config import settings
from app.services.logger import get_logger

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

logger = get_logger("webhooks")


def verify_signature(payload: bytes, signature: str) -> bool:
    secret = settings.pine_labs_webhook_secret

    computed = hmac.new(
        key=secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed, signature)


@router.post("/pine-labs")
async def pine_labs_webhook(
    request: Request,
    x_signature: str | None = Header(default=None),
):
    raw_body = await request.body()

    if not x_signature:
        raise HTTPException(status_code=400, detail="Missing webhook signature")

    if not verify_signature(raw_body, x_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload = json.loads(raw_body)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = payload.get("event")

    logger.info(
        "webhook_received",
        extra={
            "extra_data": {
                "event": event_type,
                "payload": payload,
            }
        },
    )

    if event_type == "payment.success":
        payment_ref = payload["data"]["payment_ref"]

        logger.info(
            "payment_success",
            extra={"extra_data": {"payment_ref": payment_ref}},
        )

    elif event_type == "payment.failed":
        payment_ref = payload["data"]["payment_ref"]

        logger.info(
            "payment_failed",
            extra={"extra_data": {"payment_ref": payment_ref}},
        )

    elif event_type == "payment.expired":
        payment_ref = payload["data"]["payment_ref"]

        logger.info(
            "payment_expired",
            extra={"extra_data": {"payment_ref": payment_ref}},
        )

    return {"status": "ok"}