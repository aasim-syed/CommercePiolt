from __future__ import annotations

from typing import Any

from app.constants import DEFAULT_CURRENCY
from app.services.pine_labs import pine_labs_client
from app.constants import STATUS_PENDING

class PineLabsHttpProvider:
    async def create_payment_link(
        self,
        amount: float,
        merchant_id: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "merchant_id": merchant_id,
            "amount": amount,
        }

        response = await pine_labs_client.request(
            "POST",
            "/payments/link",
            payload,
        )

        return {
            "success": True,
            "payment_ref": response.get("payment_ref"),
            "order_id": response.get("order_id"),
            "amount": response.get("amount", amount),
            "merchant_id": merchant_id,
            "payment_url": response.get("payment_url"),
            "status": response.get("status", "LINK_CREATED"),
            "currency": response.get("currency", DEFAULT_CURRENCY),
            "message": response.get("message", "Payment link created successfully."),
            "provider": "http",
        }

    async def check_payment_status(
        self,
        payment_ref: str,
        current_status: str | None = None,
    ) -> dict[str, Any]:
        response = await pine_labs_client.request(
            "GET",
            f"/payments/{payment_ref}/status",
        )

        status = response.get("status") or current_status or STATUS_PENDING

        return {
            "success": True,
            "payment_ref": payment_ref,
            "status": status,
            "message": response.get("message", f"Payment {payment_ref} status: {status}."),
            "provider": "http",
        }

    async def get_reserve_balance(
        self,
        merchant_id: str | None = None,
    ) -> dict[str, Any]:
        response = await pine_labs_client.request(
            "GET",
            f"/merchants/{merchant_id}/reserve",
        )

        return {
            "success": True,
            "merchant_id": merchant_id,
            "available_balance": response.get("available_balance"),
            "currency": response.get("currency", DEFAULT_CURRENCY),
            "message": response.get("message", "Reserve balance fetched successfully."),
            "provider": "http",
        }