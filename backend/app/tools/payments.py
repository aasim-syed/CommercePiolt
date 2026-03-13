from __future__ import annotations

from typing import Any

from app.services.pine_labs import get_pine_labs_provider


async def create_payment_link(
    amount: float,
    merchant_id: str | None = None,
) -> dict[str, Any]:
    provider = get_pine_labs_provider()
    return await provider.create_payment_link(
        amount=amount,
        merchant_id=merchant_id,
    )


async def check_payment_status(
    payment_ref: str,
    current_status: str | None = None,
) -> dict[str, Any]:
    provider = get_pine_labs_provider()
    return await provider.check_payment_status(
        payment_ref=payment_ref,
        current_status=current_status,
    )


async def get_reserve_balance(
    merchant_id: str | None = None,
) -> dict[str, Any]:
    provider = get_pine_labs_provider()
    return await provider.get_reserve_balance(merchant_id=merchant_id)