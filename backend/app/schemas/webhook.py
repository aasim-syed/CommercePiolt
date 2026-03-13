from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class PineLabsEvent(str, Enum):
    PAYMENT_SUCCESS = "payment.success"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_EXPIRED = "payment.expired"


class PineLabsWebhookData(BaseModel):
    payment_ref: str


class PineLabsWebhookPayload(BaseModel):
    event: PineLabsEvent
    data: PineLabsWebhookData


class PineLabsWebhookResponse(BaseModel):
    status: str
    event: PineLabsEvent
    payment_ref: str
    updated: bool