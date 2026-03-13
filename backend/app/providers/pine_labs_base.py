from __future__ import annotations

from typing import Any, Protocol


class PineLabsProvider(Protocol):
    async def create_payment_link(
        self,
        amount: float,
        merchant_id: str | None = None,
    ) -> dict[str, Any]: ...

    async def check_payment_status(
        self,
        payment_ref: str,
    ) -> dict[str, Any]: ...

    async def get_reserve_balance(
        self,
        merchant_id: str | None = None,
    ) -> dict[str, Any]: ...