# backend/app/services/pine_labs.py

from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.constants import DEFAULT_CURRENCY
from app.exceptions import PineLabsAPIError


class PineLabsClient:
    def __init__(self) -> None:
        self.base_url = settings.pine_labs_base_url.rstrip("/")
        self.api_key = settings.pine_labs_api_key
        self.timeout = httpx.Timeout(10.0)

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=payload,
                    headers=self.headers,
                )
        except httpx.RequestError as exc:
            raise PineLabsAPIError(f"Pine Labs request failed: {exc}") from exc

        if response.status_code >= 400:
            raise PineLabsAPIError(
                message=f"Pine Labs API error: {response.status_code} {response.text}",
                status_code=response.status_code,
            )

        try:
            return response.json()
        except ValueError as exc:
            raise PineLabsAPIError("Pine Labs returned invalid JSON") from exc

    async def create_payment_link(
        self,
        amount: float,
        merchant_id: str,
    ) -> dict[str, Any]:
        payload = {
            "merchantId": merchant_id,
            "amount": amount,
            "currency": DEFAULT_CURRENCY,
        }

        return await self._request(
            method="POST",
            path="/payments/link",
            payload=payload,
        )

    async def check_payment_status(self, payment_ref: str) -> dict[str, Any]:
        return await self._request(
            method="GET",
            path=f"/payments/status/{payment_ref}",
        )

    async def get_reserve_balance(self, merchant_id: str) -> dict[str, Any]:
        return await self._request(
            method="GET",
            path=f"/merchants/{merchant_id}/reserve",
        )