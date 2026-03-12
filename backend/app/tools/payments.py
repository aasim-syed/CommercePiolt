# backend/app/tools/payments.py

from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.constants import (
    DEFAULT_CURRENCY,
    STATUS_LINK_CREATED,
    STATUS_PENDING,
)
from app.exceptions import ToolValidationError
from app.services.pine_labs import PineLabsClient

USE_MOCK_PINE_LABS = True

client = PineLabsClient()


async def create_payment_link(
    amount: float,
    merchant_id: str | None = None,
) -> dict[str, Any]:
    if amount <= 0:
        raise ToolValidationError("Amount must be greater than 0.")

    merchant = merchant_id or "demo-merchant"

    if USE_MOCK_PINE_LABS:
        payment_ref = f"pay_{uuid4().hex[:10]}"
        order_id = f"ord_{uuid4().hex[:10]}"

        return {
            "success": True,
            "payment_ref": payment_ref,
            "order_id": order_id,
            "amount": amount,
            "merchant_id": merchant,
            "payment_url": f"https://pay.demo.local/{payment_ref}",
            "status": STATUS_LINK_CREATED,
            "currency": DEFAULT_CURRENCY,
            "message": f"Payment link created for ₹{amount:.2f}",
        }

    return await client.create_payment_link(amount=amount, merchant_id=merchant)


async def check_payment_status(payment_ref: str) -> dict[str, Any]:
    if not payment_ref.strip():
        raise ToolValidationError("payment_ref is required.")

    if USE_MOCK_PINE_LABS:
        return {
            "success": True,
            "payment_ref": payment_ref,
            "status": STATUS_PENDING,
            "message": f"Payment {payment_ref} is currently pending.",
        }

    return await client.check_payment_status(payment_ref=payment_ref)


async def get_reserve_balance(merchant_id: str | None = None) -> dict[str, Any]:
    merchant = merchant_id or "demo-merchant"

    if USE_MOCK_PINE_LABS:
        return {
            "success": True,
            "merchant_id": merchant,
            "available_balance": 124000.00,
            "currency": DEFAULT_CURRENCY,
            "message": "Reserve balance fetched successfully.",
        }

    return await client.get_reserve_balance(merchant_id=merchant)