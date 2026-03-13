from __future__ import annotations

from fastapi import APIRouter

from app.schemas.webhook import PineLabsWebhookPayload, PineLabsWebhookResponse
from app.services.webhook_service import process_pine_labs_webhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/pine-labs", response_model=PineLabsWebhookResponse)
async def pine_labs_webhook(payload: PineLabsWebhookPayload):
    result = await process_pine_labs_webhook(payload)
    return PineLabsWebhookResponse(**result)