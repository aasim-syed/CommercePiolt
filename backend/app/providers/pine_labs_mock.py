from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.constants import (
    DEFAULT_CURRENCY,
    STATUS_LINK_CREATED,
    STATUS_PENDING,
)


class PineLabsMockProvider:
    async def create_payment_link(
        self,
        amount: float,
        merchant_id: str | None = None,
    ) -> dict[str, Any]:
        order_id = f"order_{uuid4().hex[:12]}"
        payment_ref = f"pay_{uuid4().hex[:10]}"
        payment_url = f"https://sandbox.payments.local/{payment_ref}"

        return {
            "success": True,
            "payment_ref": payment_ref,
            "order_id": order_id,
            "amount": amount,
            "merchant_id": merchant_id,
            "payment_url": payment_url,
            "status": STATUS_LINK_CREATED,
            "currency": DEFAULT_CURRENCY,
            "message": f"Created payment link for ₹{amount:.2f}.",
            "provider": "mock",
        }

    async def check_payment_status(
        self,
        payment_ref: str,
        current_status: str | None = None,
    ) -> dict[str, Any]:
        status = current_status or STATUS_PENDING

        return {
            "success": True,
            "payment_ref": payment_ref,
            "status": status,
            "message": f"Payment {payment_ref} status: {status}.",
            "provider": "mock",
        }

    async def get_reserve_balance(
        self,
        merchant_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "success": True,
            "merchant_id": merchant_id,
            "available_balance": 154230.50,
            "currency": DEFAULT_CURRENCY,
            "message": "Reserve balance fetched successfully.",
            "provider": "mock",
        }