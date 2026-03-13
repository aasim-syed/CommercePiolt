from __future__ import annotations

from fastapi import APIRouter, Header

from app.schemas.webhook import PineLabsWebhookPayload, PineLabsWebhookResponse
from app.services.webhook_service import process_pine_labs_webhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/pine-labs", response_model=PineLabsWebhookResponse)
async def pine_labs_webhook(
    payload: PineLabsWebhookPayload,
    x_webhook_secret: str | None = Header(default=None),
    x_signature: str | None = Header(default=None),
):
    result = await process_pine_labs_webhook(
        payload=payload,
        provided_secret=x_webhook_secret,
        signature=x_signature,
    )
    return PineLabsWebhookResponse(**result)