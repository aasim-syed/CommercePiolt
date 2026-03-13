from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.exceptions import AgentExecutionError
from app.services.logger import get_logger

logger = get_logger("pine_labs")


class PineLabsClient:
    def __init__(self) -> None:
        self.base_url = settings.pine_labs_base_url.rstrip("/")
        self.api_key = settings.pine_labs_api_key
        self.timeout = httpx.Timeout(20.0)

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"

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
                    headers=self._headers(),
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