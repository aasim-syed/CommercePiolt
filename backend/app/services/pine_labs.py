from __future__ import annotations

import httpx
from typing import Any, Dict

from app.config import settings


class PineLabsAPIError(Exception):
    """Raised when Pine Labs API returns an error."""


class PineLabsClient:
    def __init__(self) -> None:
        self.base_url = settings.pine_labs_base_url.rstrip("/")
        self.api_key = settings.pine_labs_api_key

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        self.timeout = httpx.Timeout(10.0)

    async def _request(
        self,
        method: str,
        path: str,
        payload: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        url = f"{self.base_url}{path}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                json=payload,
                headers=self.headers,
            )

        if response.status_code >= 400:
            raise PineLabsAPIError(
                f"Pine Labs API error: {response.status_code} {response.text}"
            )

        return response.json()

    async def create_payment_link(
        self,
        amount: float,
        merchant_id: str,
    ) -> Dict[str, Any]:

        payload = {
            "merchantId": merchant_id,
            "amount": amount,
            "currency": "INR",
        }

        return await self._request(
            "POST",
            "/payments/link",
            payload,
        )

    async def check_payment_status(
        self,
        payment_ref: str,
    ) -> Dict[str, Any]:

        return await self._request(
            "GET",
            f"/payments/status/{payment_ref}",
        )

    async def get_reserve_balance(
        self,
        merchant_id: str,
    ) -> Dict[str, Any]:

        return await self._request(
            "GET",
            f"/merchants/{merchant_id}/reserve",
        )