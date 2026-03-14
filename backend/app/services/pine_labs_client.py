from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.config import settings
from app.exceptions import AgentExecutionError
from app.services.logger import get_logger

logger = get_logger("pine_labs")


class PineLabsClient:
    def __init__(self) -> None:
        self.base_url = (settings.pine_labs_base_url or "").rstrip("/")
        self.api_key = settings.pine_labs_api_key
        self.client_id = settings.pine_labs_client_id
        self.client_secret = settings.pine_labs_client_secret
        self.grant_type = settings.pine_labs_grant_type or "client_credentials"
        self.timeout = httpx.Timeout(20.0)
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None

    async def _get_access_token(self) -> str:
        if self.api_key:
            return self.api_key

        if (
            self._access_token
            and self._token_expires_at
            and datetime.now(timezone.utc) < self._token_expires_at
        ):
            return self._access_token

        if not self.base_url or not self.client_id or not self.client_secret:
            raise AgentExecutionError("Pine Labs credentials are incomplete")

        token_url = f"{self.base_url}/api/auth/v1/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": self.grant_type,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    token_url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
        except httpx.RequestError as exc:
            logger.exception(
                "pine_labs_token_network_error",
                extra={"extra_data": {"url": token_url}},
            )
            raise AgentExecutionError("Unable to reach Pine Labs auth service") from exc

        if response.status_code >= 400:
            logger.error(
                "pine_labs_token_error",
                extra={
                    "extra_data": {
                        "url": token_url,
                        "status_code": response.status_code,
                        "response": response.text,
                    }
                },
            )
            raise AgentExecutionError(
                f"Pine Labs auth failed with status {response.status_code}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            logger.error(
                "pine_labs_token_invalid_json",
                extra={"extra_data": {"url": token_url, "response": response.text}},
            )
            raise AgentExecutionError("Pine Labs auth returned an invalid response") from exc

        access_token = (
            data.get("access_token")
            or data.get("token")
            or data.get("data", {}).get("access_token")
        )
        if not access_token:
            raise AgentExecutionError("Pine Labs auth did not return an access token")

        expires_in = data.get("expires_in")
        ttl_seconds = int(expires_in) if isinstance(expires_in, (int, float, str)) and str(expires_in).isdigit() else 1800
        self._access_token = str(access_token)
        self._token_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=max(ttl_seconds - 60, 60)
        )
        return self._access_token

    async def _headers(self) -> dict[str, str]:
        token = await self._get_access_token()
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

    async def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        base_url_override: str | None = None,
    ) -> dict[str, Any]:
        resolved_base_url = (base_url_override or self.base_url).rstrip("/")
        url = f"{resolved_base_url}{path}"

        logger.info(
            "pine_labs_request_started",
            extra={
                "extra_data": {
                    "method": method.upper(),
                    "url": url,
                    "has_payload": payload is not None,
                }
            },
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    headers=await self._headers(),
                    json=payload,
                )
        except httpx.RequestError as exc:
            logger.exception(
                "pine_labs_network_error",
                extra={"extra_data": {"url": url}},
            )
            raise AgentExecutionError("Unable to reach Pine Labs service") from exc

        response_text = response.text

        if response.status_code >= 400:
            logger.error(
                "pine_labs_api_error",
                extra={
                    "extra_data": {
                        "url": url,
                        "status_code": response.status_code,
                        "response": response_text,
                    }
                },
            )
            raise AgentExecutionError(
                f"Pine Labs request failed with status {response.status_code}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            logger.error(
                "pine_labs_invalid_json",
                extra={
                    "extra_data": {
                        "url": url,
                        "status_code": response.status_code,
                        "response": response_text,
                    }
                },
            )
            raise AgentExecutionError("Pine Labs returned an invalid response") from exc

        logger.info(
            "pine_labs_request_completed",
            extra={
                "extra_data": {
                    "url": url,
                    "status_code": response.status_code,
                }
            },
        )

        return data


pine_labs_client = PineLabsClient()
