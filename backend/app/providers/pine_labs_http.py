from __future__ import annotations

from typing import Any

from app.config import settings
from app.constants import DEFAULT_CURRENCY, STATUS_PENDING
from app.exceptions import AgentExecutionError
from app.services.pine_labs_client import pine_labs_client


class PineLabsHTTPProvider:
    async def create_payment_link(
        self,
        amount: float,
        merchant_id: str | None = None,
    ) -> dict[str, Any]:
        resolved_merchant_id = merchant_id or settings.pine_labs_merchant_id

        payload = {
            "merchant_id": resolved_merchant_id,
            "amount": amount,
        }

        response = await pine_labs_client.request(
            "POST",
            "/payments/link",
            payload,
        )

        payment_ref = response.get("payment_ref")
        payment_url = response.get("payment_url")

        if not payment_ref:
            raise AgentExecutionError("Pine Labs did not return a payment reference")

        if not payment_url:
            raise AgentExecutionError("Pine Labs did not return a payment URL")

        status = response.get("status", "LINK_CREATED")

        return {
            "success": True,
            "provider": "pine_labs_http",
            "payment_ref": payment_ref,
            "order_id": response.get("order_id"),
            "status": status,
            "amount": response.get("amount", amount),
            "payment_url": payment_url,
            "currency": response.get("currency", DEFAULT_CURRENCY),
            "merchant_id": resolved_merchant_id,
            "message": response.get("message", "Payment link created successfully."),
        }

    async def check_payment_status(
        self,
        payment_ref: str,
        current_status: str | None = None,
    ) -> dict[str, Any]:
        if not payment_ref:
            raise AgentExecutionError("payment_ref is required to check payment status")

        response = await pine_labs_client.request(
            "GET",
            f"/payments/{payment_ref}/status",
        )

        status = response.get("status") or current_status or STATUS_PENDING

        return {
            "success": True,
            "provider": "pine_labs_http",
            "payment_ref": payment_ref,
            "status": status,
            "amount": response.get("amount"),
            "currency": response.get("currency", DEFAULT_CURRENCY),
            "merchant_id": response.get("merchant_id"),
            "message": response.get("message", f"Payment {payment_ref} status: {status}."),
        }

    async def get_reserve_balance(
        self,
        merchant_id: str | None = None,
    ) -> dict[str, Any]:
        resolved_merchant_id = merchant_id or settings.pine_labs_merchant_id

        if not resolved_merchant_id:
            raise AgentExecutionError("merchant_id is required to fetch reserve balance")

        response = await pine_labs_client.request(
            "GET",
            f"/merchants/{resolved_merchant_id}/reserve",
        )

        return {
            "success": True,
            "provider": "pine_labs_http",
            "merchant_id": resolved_merchant_id,
            "available_balance": response.get("available_balance"),
            "currency": response.get("currency", DEFAULT_CURRENCY),
            "message": response.get("message", "Reserve balance fetched successfully."),
        }