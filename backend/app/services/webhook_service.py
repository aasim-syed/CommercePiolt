from __future__ import annotations

from app.constants import STATUS_EXPIRED, STATUS_FAILED, STATUS_SUCCESS
from app.schemas.webhook import PineLabsEvent, PineLabsWebhookPayload
from app.services.session_store import session_store

EVENT_STATUS_MAP = {
    PineLabsEvent.PAYMENT_SUCCESS: STATUS_SUCCESS,
    PineLabsEvent.PAYMENT_FAILED: STATUS_FAILED,
    PineLabsEvent.PAYMENT_EXPIRED: STATUS_EXPIRED,
}


async def process_pine_labs_webhook(payload: PineLabsWebhookPayload) -> dict:
    status = EVENT_STATUS_MAP[payload.event]
    payment_ref = payload.data.payment_ref

    updated = session_store.update_payment_status(
        payment_ref=payment_ref,
        status=status,
    )

    return {
        "status": "ok",
        "event": payload.event,
        "payment_ref": payment_ref,
        "updated": updated,
    }