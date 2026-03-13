from __future__ import annotations

from fastapi import HTTPException, status

from app.config import settings
from app.constants import STATUS_EXPIRED, STATUS_FAILED, STATUS_SUCCESS
from app.schemas.webhook import PineLabsEvent, PineLabsWebhookPayload
from app.services.session_store import session_store

EVENT_STATUS_MAP = {
    PineLabsEvent.PAYMENT_SUCCESS: STATUS_SUCCESS,
    PineLabsEvent.PAYMENT_FAILED: STATUS_FAILED,
    PineLabsEvent.PAYMENT_EXPIRED: STATUS_EXPIRED,
}


async def process_pine_labs_webhook(
    payload: PineLabsWebhookPayload,
    provided_secret: str | None = None,
    signature: str | None = None,
) -> dict:
    if settings.pine_labs_webhook_secret:
        if provided_secret and provided_secret != settings.pine_labs_webhook_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook secret",
            )

    event = payload.event
    if event not in EVENT_STATUS_MAP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported webhook event: {event}",
        )

    payment_ref = payload.data.payment_ref
    if not payment_ref:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="payment_ref is required in webhook payload",
        )

    updated_status = EVENT_STATUS_MAP[event]
    session_found = session_store.update_payment_status(
        payment_ref=payment_ref,
        status=updated_status,
    )

    return {
        "ok": True,
        "event": event,
        "payment_ref": payment_ref,
        "updated_status": updated_status,
        "session_found": session_found,
        "message": (
            f"Webhook processed for {payment_ref}. "
            f"Updated status to {updated_status}."
            if session_found
            else f"Webhook processed for {payment_ref}, but no matching session was found."
        ),
    }