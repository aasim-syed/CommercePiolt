from __future__ import annotations

from uuid import uuid4
from typing import Any

from app.services.pine_labs import pine_labs_client


async def create_payment_link(
    amount: float,
    merchant_id: str | None = None,
) -> dict[str, Any]:
    order_id = f"order_{uuid4().hex[:12]}"

    payload = {
        "merchant_id": merchant_id,
        "amount": amount,
        "order_id": order_id,
    }

    # Replace path with actual Pine Labs endpoint later
    # response = await pine_labs_client.request("POST", "/payments/link", payload)

    # Temporary sandbox stub
    payment_ref = f"pay_{uuid4().hex[:10]}"
    payment_url = f"https://sandbox.payments.local/{payment_ref}"

    return {
        "payment_ref": payment_ref,
        "order_id": order_id,
        "amount": amount,
        "payment_url": payment_url,
    }


async def check_payment_status(
    payment_ref: str,
) -> dict[str, Any]:

    # response = await pine_labs_client.request(
    #     "GET",
    #     f"/payments/{payment_ref}/status",
    # )

    return {
        "payment_ref": payment_ref,
        "status": "PENDING",
    }


async def get_reserve_balance(
    merchant_id: str | None = None,
) -> dict[str, Any]:

    # response = await pine_labs_client.request(
    #     "GET",
    #     f"/merchants/{merchant_id}/reserve",
    # )

    return {
        "merchant_id": merchant_id,
        "available_balance": 154230.50,
        "currency": "INR",
    }