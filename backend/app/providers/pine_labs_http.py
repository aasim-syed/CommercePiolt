from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.config import settings
from app.constants import DEFAULT_CURRENCY, STATUS_LINK_CREATED, STATUS_PENDING
from app.exceptions import AgentExecutionError
from app.providers.pine_labs_mock import PineLabsMockProvider
from app.services.pine_labs_client import pine_labs_client


class PineLabsHTTPProvider:
    def __init__(self) -> None:
        self.fallback_provider = PineLabsMockProvider()

    async def create_payment_link(
        self,
        amount: float,
        currency: str | None = None,
        merchant_id: str | None = None,
    ) -> dict[str, Any]:
        resolved_merchant_id = merchant_id or settings.pine_labs_merchant_id
        resolved_currency = (currency or DEFAULT_CURRENCY).upper()

        expire_by = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        amount_minor = int(round(float(amount) * 100))
        reference = f"cp-{int(datetime.now(timezone.utc).timestamp())}"

        payload = {
            "amount": {
                "value": amount_minor,
                "currency": resolved_currency,
            },
            "description": f"CommercePilot payment link for {reference}",
            "expire_by": expire_by,
            "merchant_payment_link_reference": reference,
            "customer": {
                "email_id": "demo@commercepilot.local",
                "first_name": "Commerce",
                "last_name": "Pilot",
                "customer_id": reference,
                "mobile_number": "9999999999",
                "country_code": "91",
                "billing_address": {
                    "address1": "Demo Billing Address",
                    "city": "Bengaluru",
                    "state": "Karnataka",
                    "country": "India",
                    "pincode": "560001",
                },
                "shipping_address": {
                    "address1": "Demo Shipping Address",
                    "city": "Bengaluru",
                    "state": "Karnataka",
                    "country": "India",
                    "pincode": "560001",
                },
            },
        }
        if resolved_merchant_id:
            payload["merchant_metadata"] = {"merchant_id": resolved_merchant_id}

        try:
            response = await pine_labs_client.request(
                "POST",
                "/api/pay/v1/paymentlink",
                payload,
            )
        except AgentExecutionError as exc:
            if "Currency is invalid" not in str(exc):
                raise

            result = await self.fallback_provider.create_payment_link(
                amount=amount,
                currency=resolved_currency,
                merchant_id=resolved_merchant_id,
            )
            result["provider"] = "sandbox_stub"
            result["message"] = f"Payment link created from sandbox stub for {resolved_currency}."
            return result

        response_data = response.get("data", {})
        payment_ref = (
            response_data.get("payment_link_id")
            or response_data.get("payment_id")
            or response_data.get("merchant_payment_link_reference")
            or response.get("payment_link_id")
            or response.get("payment_id")
            or response.get("merchant_payment_link_reference")
        )
        payment_url = response_data.get("payment_link") or response.get("payment_link")

        if not payment_ref:
            raise AgentExecutionError("Pine Labs did not return a payment reference")

        if not payment_url:
            raise AgentExecutionError("Pine Labs did not return a payment URL")

        status = response.get("status") or response_data.get("status") or STATUS_LINK_CREATED

        return {
            "success": True,
            "provider": "pine_labs_http",
            "payment_ref": payment_ref,
            "order_id": response_data.get("payment_link_id") or response.get("payment_link_id"),
            "provider_payment_id": response_data.get("payment_id") or response.get("payment_id"),
            "merchant_payment_link_reference": response_data.get("merchant_payment_link_reference")
            or response.get("merchant_payment_link_reference"),
            "status": status,
            "amount": amount,
            "payment_url": payment_url,
            "currency": (
                response_data.get("amount", {}).get("currency")
                or response.get("amount", {}).get("currency")
                or resolved_currency
            ),
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

        try:
            response = await pine_labs_client.request(
                "GET",
                f"/api/pay/v1/payment/{payment_ref}",
            )
        except AgentExecutionError as exc:
            if "status 404" not in str(exc):
                raise

            response = await pine_labs_client.request(
                "GET",
                f"/api/pay/v1/paymentlink/{payment_ref}",
            )

        response_data = response.get("data", {})
        status = response_data.get("status") or response.get("status") or current_status or STATUS_PENDING

        return {
            "success": True,
            "provider": "pine_labs_http",
            "payment_ref": response_data.get("payment_id") or payment_ref,
            "provider_payment_id": response_data.get("payment_id") or payment_ref,
            "status": status,
            "amount": response_data.get("amount", {}).get("value"),
            "currency": response_data.get("amount", {}).get("currency", DEFAULT_CURRENCY),
            "merchant_id": response_data.get("merchant_id"),
            "message": response.get("message", f"Payment {payment_ref} status: {status}."),
        }

    async def get_reserve_balance(
        self,
        merchant_id: str | None = None,
    ) -> dict[str, Any]:
        resolved_merchant_id = merchant_id or settings.pine_labs_merchant_id

        try:
            response = await pine_labs_client.request(
                "GET",
                "/payouts/v3/payments/funding-account",
                base_url_override=settings.pine_labs_payouts_base_url,
            )
            balance = response.get("balance", {})

            return {
                "success": True,
                "provider": "pine_labs_http",
                "merchant_id": resolved_merchant_id,
                "available_balance": balance.get("value"),
                "currency": balance.get("currency", DEFAULT_CURRENCY),
                "message": response.get("message", "Reserve balance fetched successfully."),
            }
        except AgentExecutionError:
            result = await self.fallback_provider.get_reserve_balance(
                merchant_id=resolved_merchant_id,
            )
            result["provider"] = "sandbox_stub"
            result["message"] = "Reserve balance fetched from sandbox stub."
            return result
